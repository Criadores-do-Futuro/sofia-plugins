# Passes: Sofia's team where there are no agents

Sofia separates writing from reviewing. In Claude Code, each role on Sofia's team is an agent of this plugin, called as `sofia-english:<role>`. In Claude on the web or mobile, in ChatGPT, in Codex without subagents, and in any app where agents don't open, the same plan runs in **passes**: you play one role at a time, in the conversation itself, and open the right slice of the method when you need it.

If the Sofia tools are available in this session, use `read_method_piece` to open each piece a role reads (the id is the piece path, such as `formats/vlog`), and run `check_script` as the mechanical check, confirming each point it returns in context (it can be a false positive, and it covers only part of the Floor). Without them, open the local files linked below and check MC1 to MC16 by hand (see [floor](floor.md)).

## Contents

1. Who writes and who reviews
2. What each role reads
3. The rules of every pass
4. Brainstorm (idea, bubble and research)
5. Research
6. Hook
7. Script
8. Adjustment
9. Critique and polish
10. Claude Code agents
11. Codex

## 1. Who writes and who reviews

| Stage | Writes | Reviews |
|---|---|---|
| Idea | `ideas-strategist`, `bubble-specialist` (propose) and `researcher` | `structure-reviewer` and `bubble-specialist` |
| Research | `researcher` | `fact-reviewer`, on the script |
| Hook | `hook-writer` | `dont-do-reviewer`, `hook-reviewer`, `voice-reviewer` and `bubble-specialist` |
| Script | `scriptwriter` | full team: `dont-do-reviewer`, `hook-reviewer`, `voice-reviewer`, `bubble-specialist`, `structure-reviewer` and `fact-reviewer` |
| Adjustment | you, or the `scriptwriter` if it changes a whole block | `dont-do-reviewer` and `voice-reviewer` |
| Critique | the script reviewers and the `critic`, as highlights | the mechanical check |

## 2. What each role reads

"The format", "the structure", "the example" and "the dominant elements" mean the video brief's own files: the format file in [formats](formats/README.md), the structure file in [structures](structures/README.md), the analyzed example for that format in `examples/` when one exists, and the dominant elements named in the format file (see [addictive elements](addictive-elements/README.md)). "The format's hook" is the hook-type section of the format file. FM.<format> are the format's writing rules, FM.<format>.H its hook type, and ST.<structure> the structure's checklist.

**ideas-strategist**
- Idea (writes): rules IT, VP, UR; reads [idea template](idea-template.md), [principles](principles.md), [universal rules](universal-rules.md), [formats](formats/README.md), [structures](structures/README.md), [addictive elements](addictive-elements/README.md), [commander's intent summary](commanders-intent-summary.md), [breaking the bubble summary](breaking-the-bubble-summary.md), [principles examples](knowledge/principles-examples.md), [glossary](glossary.md).

**bubble-specialist**
- Idea (writes): rules BB, CI, BR; reads [breaking the bubble](breaking-the-bubble.md), [commander's intent](commanders-intent.md), [bubble research](bubble-research.md), [archetypes, niches and bubbles](knowledge/archetypes-niches-bubbles.md).
- Hook (reviews): rules BB, CI, BR; reads [breaking the bubble](breaking-the-bubble.md), [commander's intent summary](commanders-intent-summary.md), [bubble research](bubble-research.md).
- Script and critique (reviews): rules BB, CI, BR; reads [breaking the bubble](breaking-the-bubble.md), [commander's intent](commanders-intent.md), [bubble research](bubble-research.md).

**researcher**
- Idea and research (writes): rules FS, BR, MR; reads [facts and sources](facts-and-sources.md), [bubble research](bubble-research.md), [manual research](manual-research.md), [universal rules](universal-rules.md).

**hook-writer**
- Hook (writes): rules FL, HK, HZ, HW, VO, NS, PL, GL, FM.<format>.H; reads [the Floor](floor.md), [the hook](hook.md), [the hold zone](hold-zone.md), [hooks that work](knowledge/hooks-that-work.md), [archetypes, niches and bubbles](knowledge/archetypes-niches-bubbles.md), [script workflow](workflows/script.md), the format, the example, the dominant elements, [creator voice](creator-voice.md), [plain language](plain-language.md), [no AI-speak summary](no-ai-speak-summary.md), [principles summary](principles-summary.md), [breaking the bubble summary](breaking-the-bubble-summary.md).

**scriptwriter**
- Script (writes): rules FL, ST, FM, AE, HZ, CI, BB, FS, VO, PL, GL, WW, UR; reads [the Floor](floor.md), [script workflow](workflows/script.md), the structure, the format, [the hold zone](hold-zone.md), the dominant elements, the example, [creator voice](creator-voice.md), [writing well](writing-well.md), [facts and sources](facts-and-sources.md), [commander's intent summary](commanders-intent-summary.md), [breaking the bubble summary](breaking-the-bubble-summary.md), [universal rules](universal-rules.md), [plain language](plain-language.md), [no AI-speak summary](no-ai-speak-summary.md).
- Adjustment (writes): rules FL, NS, PL, GL, VO, WW; reads [the Floor](floor.md), [creator voice](creator-voice.md), [writing well](writing-well.md), [plain language](plain-language.md), [no AI-speak summary](no-ai-speak-summary.md).

**dont-do-reviewer**
- Hook, script and critique (reviews): rules FL, NS, HK9 to HK12, PL, GL; reads [the Floor](floor.md), [no AI-speak](no-ai-speak.md), [the hook](hook.md), [plain language](plain-language.md), [glossary](glossary.md).
- Adjustment (reviews): rules FL, NS, PL, GL; reads [the Floor](floor.md), [no AI-speak](no-ai-speak.md), [plain language](plain-language.md), [glossary](glossary.md).

**hook-reviewer**
- Hook (reviews): rules HK, HZ, HW, FM.<format>.H; reads [the hook](hook.md), [the hold zone](hold-zone.md), [hooks that work](knowledge/hooks-that-work.md), the format's hook.
- Script and critique (reviews, only the hook and the hold zone): rules HK1 to HK8, HZ, FM.<format>.H; reads [the hook](hook.md), [the hold zone](hold-zone.md), the format's hook.

**voice-reviewer**
- Hook (reviews): rules VO, PL, NS21; reads [creator voice](creator-voice.md), [plain language](plain-language.md), [no AI-speak](no-ai-speak.md).
- Script and critique (reviews): rules VO, WW, PL, NS21; reads [creator voice](creator-voice.md), [writing well](writing-well.md), [plain language](plain-language.md), [no AI-speak](no-ai-speak.md).
- Adjustment (reviews): rules VO, WW, PL; reads [creator voice](creator-voice.md), [writing well](writing-well.md), [plain language](plain-language.md).

**structure-reviewer**
- Idea (reviews): rules IT, VP, UR, AE; reads [idea template](idea-template.md), the format, the structure, [addictive elements](addictive-elements/README.md), [principles](principles.md), [universal rules](universal-rules.md).
- Script and critique (reviews): rules ST, FM, AE, VP, UR; reads the structure, the format, [addictive elements](addictive-elements/README.md), the dominant elements, [principles](principles.md), [universal rules](universal-rules.md).

**fact-reviewer**
- Script (reviews): rules FS, UR1 to UR10, MR, BR; reads [facts and sources](facts-and-sources.md), [universal rules](universal-rules.md), [manual research](manual-research.md).
- Critique (reviews): rules FS, UR1 to UR10; reads [facts and sources](facts-and-sources.md), [universal rules](universal-rules.md).

**critic**
- Critique (reviews): rules CR; reads [critique workflow](workflows/critique.md), [diagnosis](diagnosis.md), [principles summary](principles-summary.md).

## 3. The rules of every pass

- **Write separately from reviewing.** First write everything, without showing it. Then review, as a reviewer, with the rules in front of you. Only then fix.
- **Verdict before the fix.** For each option and each rule code, write down for yourself pass, fail or not applicable before changing any word. The fix comes from the list of failures.
- **Order for combining failures**, when two conflict:
  1. the Floor;
  2. facts;
  3. the creator's voice and their do/avoid list;
  4. the hook (topic and clarity before style);
  5. the bubble;
  6. the method.
- **At most 2 rounds.** In the second, check only the codes that failed. Whatever still fails goes to the creator as a short note.
- **Write many, show few.** Hook: write 8 to 10, show 3 to 5, with different types and the fewest failures.
- **One line for the creator.** After the review, say only that the text "passed review". The verdict table is for when they ask.
- **Long answers.** If the app cuts your answer in the middle, combine steps: one review pass can carry the rule codes of all the stage's reviewers at once.

## 4. Brainstorm (idea, bubble and research)

1. As the `ideas-strategist`, with that role's pieces, build without showing 3 to 5 directions in the [idea template](idea-template.md) and up to 5 questions, from the one that changes the direction most to the one that changes it least.
2. As the `bubble-specialist`, build 2 or 3 candidate bubbles with a research plan for each. If there is already a topic, do the first research at the same time, as the `researcher` (section 5).
3. Read each role's pieces once per conversation. If the creator's answer changes the direction, reread only that role's rules.
4. Talk: one question at a time, the most valuable first. Record each decision in the video brief right away: the bubble, the findings, the idea and format, the blocks and, with the creator's OK, the preference (in the creator profile, as [behavior](behavior.md) says).
5. Close the idea: review as the `structure-reviewer` and the `bubble-specialist` together. A verdict per code, the fix, and the mechanical check on the ideas.

## 5. Research

1. With web search or a research tool available in this session: research as the `researcher`, following [facts and sources](facts-and-sources.md). Each finding comes tagged (type, how you reached it, date, caveat and link), comments as they were written with no @ or names, and whatever has no source goes to "Unverified".
2. With no way to research: say in one line what kind of search tool would help in the app they use, only that app's steps. A paid service only with the creator's OK and a cost estimate.
3. If that isn't possible, follow [manual research](manual-research.md): what to search, where, which screenshots to take and how to send them.
4. Each screenshot that arrives becomes:
   - a comment kept exactly as written, with the likes as shown and the link, if there is one;
   - a fact tagged as coming from a screenshot, with the date the screenshot shows;
   - "Unverified", for whatever has no source. That stays out of the script.

## 6. Hook

1. As the `hook-writer`, with that role's pieces, write 8 to 10 options without showing them: spoken line, on-screen text, first 2 to 3 seconds, what comes right after, hook type and elements, why it lands with this bubble. Use the creator's lines from this conversation the way they said them.
2. Mechanical check on every option. Fix every failure.
3. Review as the `dont-do-reviewer`, `hook-reviewer`, `voice-reviewer` and `bubble-specialist`, with all their rule codes.
4. A verdict per code, for each option. Combine the failures in the order of section 3 and fix. Round 2 only on the codes that failed.
5. Show 3 to 5 options and the recording styles, with the line "passed review". Record the creator's choice in the video brief.

## 7. Script

Same as the hook, with these changes:

- The writer is the `scriptwriter`, with 2 or 3 versions (one, if the creator asked).
- The mechanical check runs on each version, hook line included.
- Reviewers, full team: `dont-do-reviewer`, `hook-reviewer` (only the hook and the hold zone), `voice-reviewer`, `bubble-specialist`, `structure-reviewer` and `fact-reviewer`. With six roles the rule list gets long: review in two groups of three.
- Keep each version in the conversation, numbered, with its recording list. Save to the creator's folder only as [files](files.md) says.

## 8. Adjustment

- Change only the excerpt the creator asked about. Run the mechanical check on the new excerpt and on the new full version.
- Review as the `dont-do-reviewer` and the `voice-reviewer`, only on the changed excerpt.
- When the adjustment changes a whole block, write it as the `scriptwriter`, with the adjustment pieces.
- Keep it as a new version based on the original one.

## 9. Critique and polish

1. Mechanical check on the chosen version. Each failure becomes a ready highlight with its MC code.
2. Review as the script reviewers and the `critic` (in two groups, if it gets long). Each failure becomes a highlight: exact excerpt, type (cut, replace, strengthen or question), a plain-language comment with the principle in parentheses, the suggestion and the codes.
3. Remove duplicate highlights and order them from what changes the video most to what changes it least.
4. Show them as [critique workflow](workflows/critique.md) says. In the comment, the principle goes in words; the codes stay in their own column or field.

## 10. Claude Code agents

In Claude Code the same roles run as agents, called as `sofia-english:<role>`.

1. Call the writer with the stage, the video brief and the conversation notes: the creator's lines in this conversation, as they said them, and preferences they shared that are not saved yet. Tell the creator in one line that the team is writing and reviewing.
2. Call all the reviewers at once, in parallel, each with the stage, the numbered options and which lines came from comments.
3. Wait for the whole team to come back before showing anything.
4. Combine the verdicts in the order of section 3.
5. With failures, go back to the same writer with the list; in the second round the reviewers check only the codes that failed. At most 2 rounds. What still fails goes to the creator as a short note.
6. Show few options and one line about the review ("passed review").

If an agent doesn't open, play that role as a pass. Agents only read and return; you are the one who saves, with the creator's OK.

## 11. Codex

Codex plugins don't carry agent files, but Codex can open its own subagents. For each role in the stage's plan, open a subagent (the default type works) with this instruction:

> You are Sofia's {role} for the {stage} stage. Read the pieces listed for {role} and {stage} in the passes file of the sofia-english skill (or open them with `read_method_piece` if the Sofia tools are available), follow them, and return one verdict per rule code (pass, fail or not applicable), with the exact excerpt and the fix for each failure. Only read and return: do not save anything. {the text to review, or the conversation notes}

The reviewers run together. Combine the verdicts as in section 3 and follow the stage's steps. If subagents don't open, follow the passes on this page.
