import AVFoundation
import CoreGraphics
import Foundation
import ImageIO
import Vision

struct FaceSample: Codable {
    let time: Double
    let centerX: Double
    let centerY: Double
    let top: Double
    let bottom: Double
    let width: Double
    let height: Double
    let confidence: Float
}

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(1)
}

let arguments = CommandLine.arguments
guard arguments.count == 3 else {
    fail("uso: rastrear-rosto <video> <saida.json>")
}

let inputURL = URL(fileURLWithPath: arguments[1])
let outputURL = URL(fileURLWithPath: arguments[2])
let asset = AVURLAsset(url: inputURL)
let durationTime: CMTime
do {
    durationTime = try await asset.load(.duration)
} catch {
    fail("não foi possível ler a duração: \(error.localizedDescription)")
}
let duration = CMTimeGetSeconds(durationTime)
guard duration.isFinite, duration > 0 else {
    fail("duração de vídeo inválida")
}

let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceBefore = CMTime(value: 1, timescale: 30)
generator.requestedTimeToleranceAfter = CMTime(value: 1, timescale: 30)

var samples: [FaceSample] = []
let interval = 0.25
var timestamp = 0.0

while timestamp <= duration {
    let requested = CMTime(seconds: timestamp, preferredTimescale: 600)
    guard let result = try? await generator.image(at: requested) else {
        timestamp += interval
        continue
    }
    let sample: FaceSample? = autoreleasepool {
        let image = result.image
        let actual = result.actualTime

        let request = VNDetectFaceRectanglesRequest()
        let handler = VNImageRequestHandler(cgImage: image, orientation: .up, options: [:])
        guard (try? handler.perform([request])) != nil,
              let face = request.results?.max(by: {
                  $0.boundingBox.width * $0.boundingBox.height < $1.boundingBox.width * $1.boundingBox.height
              }) else {
            return nil
        }

        let box = face.boundingBox
        let top = 1 - Double(box.maxY)
        let bottom = 1 - Double(box.minY)
        return FaceSample(
            time: CMTimeGetSeconds(actual),
            centerX: Double(box.midX),
            centerY: (top + bottom) / 2,
            top: top,
            bottom: bottom,
            width: Double(box.width),
            height: Double(box.height),
            confidence: face.confidence
        )
    }
    if let sample {
        samples.append(sample)
    }
    timestamp += interval
}

guard !samples.isEmpty else {
    fail("nenhum rosto detectado")
}

do {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    try encoder.encode(samples).write(to: outputURL, options: .atomic)
    print("rastrear-rosto: \(samples.count) amostras em \(outputURL.path)")
} catch {
    fail("não foi possível salvar o tracking: \(error.localizedDescription)")
}
