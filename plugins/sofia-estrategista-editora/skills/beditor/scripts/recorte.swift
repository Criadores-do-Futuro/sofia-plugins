// recorte.swift — separa o sujeito do fundo com o Vision do proprio macOS.
//
// Rosto de pessoa real nao se gera (`catalogo-visual.md`), e nao precisa sair da
// maquina para ser recortado: o Vision faz a mascara de primeiro plano local,
// sem rede, sem servico de terceiro, sem conta. Entra um quadro do take, sai um
// PNG com alpha.
//
// compilar: swiftc -O recorte.swift -o recorte
// usar:     recorte entrada.png saida.png

import Foundation
import Vision
import CoreImage
import AppKit

func morra(_ m: String) -> Never {
    FileHandle.standardError.write((m + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
guard args.count == 3 else { morra("uso: recorte <entrada> <saida.png>") }
let entrada = URL(fileURLWithPath: args[1])
let saida = URL(fileURLWithPath: args[2])

guard let origem = CIImage(contentsOf: entrada) else { morra("nao consegui ler \(args[1])") }

let pedido = VNGenerateForegroundInstanceMaskRequest()
let leitor = VNImageRequestHandler(ciImage: origem, options: [:])
do {
    try leitor.perform([pedido])
} catch {
    morra("Vision falhou: \(error.localizedDescription)")
}

guard let r = pedido.results?.first, !r.allInstances.isEmpty else {
    morra("nenhum sujeito encontrado no quadro")
}

// todas as instancias juntas: o rosto e o corpo costumam vir separados
let buffer: CVPixelBuffer
do {
    buffer = try r.generateMaskedImage(ofInstances: r.allInstances,
                                       from: leitor,
                                       croppedToInstancesExtent: false)
} catch {
    morra("nao consegui aplicar a mascara: \(error.localizedDescription)")
}

let recortada = CIImage(cvPixelBuffer: buffer)
let ctx = CIContext()
guard let espaco = CGColorSpace(name: CGColorSpace.sRGB) else { morra("sem espaco de cor") }
do {
    try ctx.writePNGRepresentation(of: recortada, to: saida,
                                   format: .RGBA8, colorSpace: espaco)
} catch {
    morra("nao consegui escrever o PNG: \(error.localizedDescription)")
}
print("recorte: \(saida.path)")
