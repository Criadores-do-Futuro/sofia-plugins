# The Floor: applies to every text

No text goes out without passing here: script, hook, caption, critique, analysis and every reply in the conversation. The Floor sits above the creator's voice, the style of a reference and the examples in the method. FL1, FL2 and FL3 are also covered by the mechanical checks below (MC1, MC2 and MC3).

- **FL1.** **No em dash (—).** Use a comma, period, colon or parentheses.
- **FL2.** **No "it's not X, it's Y" template** and none of its variations ("it's not just X", "X isn't the problem, Y is", "this isn't about X, it's about Y"). State Y.
- **FL3.** **No filler adverbs ending in -ly** (really, literally, basically, simply, actually, honestly, totally, completely, definitely, truly, clearly, obviously). Cut them. The sentence is almost always better without them. Words like "only", "early" or "daily" are fine when they carry meaning.
- **FL4.** **No rhetorical questions**, the kind you ask only to answer right away. State it. Two questions stay: the CTA question, which expects an answer from the viewer, and a question that came from an audience comment and became the creator's own line.
- **FL5.** **No clichés and no AI phrasing.** The lists are in [no AI-speak](no-ai-speak.md).
- **FL6.** **No data without a source.** Numbers, dates, cases and quotes only with a source you opened. Without a source, the sentence goes, or stays without the number.
- **FL7.** **An audience comment becomes the creator's line.** Save it exactly as written, without the @ and without the name of whoever wrote it. In the script it goes in as if the creator were saying it: no quotation marks and no metalanguage. Never "in the comments", "someone commented", "some people say", "a lot of people", "people", "followers" or "bubble". Adjust only the minimum for it to make sense. A comment does not become the hook on its own: a conflict or provocation comment with many likes can be one of the opening options, and the creator chooses. See [facts and sources](facts-and-sources.md).

## Mechanical checks (MC)

These are the rules a machine can check. If the Sofia tools are available in this session, run `check_script` on every finished hook, script, edited excerpt and caption before showing the text (its rules live in [checks.json](checks.json)). It returns points to review, not required fixes: each one is an automatic signal to check in context, it can be a false positive (for example "train journey"), and the tool covers only part of the Floor, so the rest of the review still applies. Without the tools, check these by hand. A "fail" is fixed before delivery. A "warning" is fixed unless there is a reason to keep it, and then you tell the creator the reason in one line.

- **MC1** (fail). No em dash.
- **MC2** (fail). No filler -ly adverbs.
- **MC3** (fail). None of the binary-contrast templates from [no AI-speak](no-ai-speak.md): state it directly.
- **MC4** (fail). Results are compared with "the profile's normal", with no statistics term ("median", "average views", "percentile").
- **MC5** (fail). A comment goes in as the creator's line, without metalanguage.
- **MC6** (fail). None of the banned phrases from [no AI-speak](no-ai-speak.md).
- **MC7** (fail). On-screen text has 3 to 5 words, on up to 2 lines.
- **MC8** (fail). The spoken hook has 1 to 3 short sentences, with no word count. The tool uses 15 words on the first sentence as its own reference, not as a rule of the method.
- **MC9** (fail). The hook does not open with a greeting or an introduction.
- **MC10** (warning). The problem is said with "you", not in the first person.
- **MC11** (warning). Three sentences in a row with the same length.
- **MC12** (warning). A question only in the final CTA or when it came from a comment.
- **MC13** (warning). A number that does not appear in the research of the video brief.
- **MC14** (warning). A sentence that opens with "what", "why" or "how" in place of a statement.
- **MC15** (warning). Passive voice: say who does it.
- **MC16** (fail). An idea declares its format, structure and addictive elements.

`check_script` also estimates the spoken length at 160 words per minute. That pace is the tool's reference, not a rule of the method: treat it as an estimate, because the creator's real pace decides.
