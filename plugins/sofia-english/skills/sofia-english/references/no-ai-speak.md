# No AI-speak

Applies to every Sofia text: script, hook, caption, critique, analysis and replies in the conversation. The seven items of [the Floor](floor.md) always apply. This piece holds the rules, the lists and the examples. The rules below were adapted from [stop-slop](https://github.com/hardikpandya/stop-slop), by Hardik Pandya (MIT license), for spoken American English.

Part of these rules is mechanical (em dashes, filler -ly adverbs, the contrast templates, the phrases on the lists below, rhetorical setup questions, passive voice, three sentences of the same length). If the Sofia tools are available, `check_script` returns points to review for part of them (they can be false positives); the rest is checked by whoever reviews, by the codes below.

## The eight rules

- **NS1.** **Get to the point.** No announcing what you are about to say.
- **NS2.** **Avoid formulas.** No binary contrast, no list by negation, no setup question in place of a statement.
- **NS3.** **Someone does something.** Every sentence has a person acting. Lifeless things with human verbs ("the algorithm decides to punish you", "the pain is asking for") go.
- **NS4.** **Be specific.** Name, number, place, time. "Always", "never" and "everyone" only when they are true.
- **NS5.** **Put the viewer in the scene.** "You" beats "people". The concrete detail beats the abstract idea.
- **NS6.** **Vary the rhythm.** Mix short and long sentences. Two items beat three. End each paragraph in a different way.
- **NS7.** **Trust the listener.** State it. No softening, no justifying, no explaining your own joke.
- **NS8.** **Cut the quotable line.** If a line looks built to be screenshotted, rewrite it.

## Words and phrases that give AI away

**Throat-clearing (cut it and go straight in):** "The truth is", "Let me tell you something", "I'm going to be honest", "To be honest", "Here's the thing", "The point here is", "It turns out", "You know what's worse", "Pay attention to this", "Let me tell you a story".

**Emphasis crutches (delete, don't replace):** "Period.", "Full stop.", "Let that sink in.", "And that matters because", "Make no mistake", "I'll say it again:".

**Filler -ly adverbs.** The usual ones: really, literally, basically, simply, actually, honestly, totally, completely, definitely, truly, clearly, obviously, exactly, quickly, easily, mainly, practically. Cut them. The sentence is almost always better without them.

**Padding:** "At the end of the day", "It's important to note", "It's worth noting", "In today's fast-paced world", "In today's world", "In a world where", "When it comes to", "In a way", "So to speak", "Needless to say".

**Corporate jargon:** unlock, leverage, deep dive, dive deep, game-changer, paradigm shift, take a step back, on the same page, next level, level up, move the needle, circle back.

**Clichés and crutches:** journey, "let's dive in", "let's get into it", "here you go", "think outside the box", "step out of your comfort zone", "it changed my life", "the secret is", "believe in yourself", "buckle up", "embark", "revolutionary", "unleash", "harness the power", "elevate", "delve", "tapestry", "realm", "a testament to", "navigate the landscape". Generic metaphors and emoji in the middle of the text also go.

**Commenting on your own text:** "In this video you'll learn", "But that's a topic for another video", "As I said earlier", "Let's break it down", "First things first", "Spoiler alert:", "Pro tip:", "Without further ado".

**Documentary words:** fascinating, remarkable, "however", "it's worth highlighting", "furthermore", "moreover", "additionally", "in summary", "in conclusion", "to sum up".

## Banned templates

| Template | Why it goes | What to do |
|---|---|---|
| "It's not X. It's Y." / "X isn't the problem, Y is" / "This isn't about X, it's about Y" | A telegraphed twist, one of the most common marks of AI text | State Y directly |
| "It's not just X, it's also Y" | Sits on the fence | Pick one |
| "It looks like X. It's actually Y." | A textbook reveal | Say what it is |
| "It's not A. It's not B. It's C." | Fake suspense | Say C |
| "X. That's it. That's all." | Fake simplicity | A full sentence |
| "What if [the same idea again]?" | Philosopher pose | Make the statement |
| "Think about it:" / "Check this out:" | A setup that leads nowhere | Cut |
| "And that's okay." | Permission nobody asked for | Cut |
| "Stops being X and becomes Y" | Textbook transformation | Say what changed |
| "The algorithm punishes you", "the pain is asking for", "the content delivers" | A lifeless thing acting like a person | Say who acts |
| A sentence that opens with "What", "Why" or "How" in place of the statement | Setup question | State it |
| An em dash in the middle of a sentence | An AI rhythm crutch | Comma, period, colon or parentheses |

A real doubt of the audience goes in as a statement, in their voice: "And now you're thinking anyone without money gets left out." A question that came from an audience comment and became the creator's line keeps its words. The CTA question, which expects an answer from the viewer, also stays.

## Bad and good

Invented examples, only to show the shape. Don't copy the sentences: copy the swap.

| Bad | Good | What changed |
|---|---|---|
| "The problem isn't the algorithm. It's your hook." | "Your hook loses people at second two." | Stated it directly |
| "The truth is, nobody tells you this, but the store closed." | "The store closed." | Cut the throat-clearing |
| "Basically, the company laid off half the team." | "The company laid off half the team." | Removed the -ly adverb |
| "The pain is asking for a quick fix." | "Someone in pain wants it fixed today." | A person acts |
| "People these days don't have time." | "You open your phone on the bus and you have four minutes until your stop." | Put you in the scene |
| "And why does that matter? Because the price went up." | "The price went up, and the people who bought every week started buying once a month." | Swapped the question for the statement and its consequence |
| "It's fast, cheap and efficient." | "It's fast and cheap." | Two items |
| "Marta quit." | "The store manager, Marta, quit." | Context before the name |
| "It's important to highlight that the information hasn't been confirmed." | "That's what the neighbor told the police. The police haven't confirmed it yet." | The caveat became part of the story |
| "Now let's talk about the price." | "And that card had a limit: two thousand dollars." | The transition came out of a concrete detail |
| "She made a decision that changed everything." | "She sold the car and opened the store with the money." | Said what happened |
| "This may have allegedly caused problems." | "The company says the delay came from there." | Doubt only where it's real, with who claims it |

A template with variables for a direct start: "{Something that happened}. And now {who} is afraid of {possible consequence}." Fill it only with facts that have a source.

## Quick check before delivering

- **NS9.** Any filler -ly adverb left? Cut it.
- **NS10.** Passive voice? Find who does it and make them the subject.
- **NS11.** A lifeless thing with a human verb? Name the person who acts.
- **NS12.** A sentence starting with "what", "why" or "how" in place of the statement? State it.
- **NS13.** Any "the truth is", "here's the thing", "let's dive in" or another phrase from the lists? Cut it.
- **NS14.** Any contrast template from the table? State the second half directly.
- **NS15.** Three sentences in a row with the same length? Break one.
- **NS16.** A paragraph ending in a quotable line? Vary it.
- **NS17.** An em dash anywhere? Swap it for a comma, period, colon or parentheses.
- **NS18.** A vague claim ("the implications are huge")? Say what the implication is.
- **NS19.** A distant narrator ("people these days")? Put the person in the scene with "you".
- **NS20.** A comment on the structure of the text itself? Delete it.

## Score before delivering

- **NS21.** The text scores at least 35 out of 50 on the scorecard below, rating each dimension from 1 to 10. Below that, rewrite.

| Dimension | Question |
|---|---|
| Direct | Does it state, or announce that it's about to state? |
| Rhythm | Does it vary, or sound like a metronome? |
| Confidence | Does it respect the listener's intelligence? |
| Authenticity | Does it sound like a person or a machine? |
| Density | Is there anything left to cut? |

## Speech has its own rules

**A short fragment works in speech** as long as it carries information. "Three days. No answer." passes. "That's it. That's all. That's the secret." fails: emphasis with no content.

**Repetition on purpose works in speech.** Repeating the same word to mark rhythm works in audio. Use it with intent, at most once per script.

**"And", "So" and "But" can open a sentence.** That's how people talk.

The binary contrast ("it's not talent, it's obsession") shows up a lot in scripts written with AI. It sounds deep, and the effect disappears once you state the second half directly.

---

## License of the source material

The rules in this piece were adapted from [stop-slop](https://github.com/hardikpandya/stop-slop), by Hardik Pandya, distributed under the MIT license. The original notice follows, unchanged, as the license requires.

```
MIT License

Copyright (c) 2025 Hardik Pandya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
