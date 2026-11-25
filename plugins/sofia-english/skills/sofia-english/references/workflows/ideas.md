# Workflow: video ideas

Read [behavior](../behavior.md) first. This workflow covers the brainstorm: theme, bubble, seed, format, structure and the idea itself. Research has its own workflow ([research](research.md)); the two run side by side and in any order.

Nothing blocks the next step. The creator can start anywhere. When you reach a step, check what is missing from earlier ones (subject research, bubble research, comments, references), say in one sentence why it makes the video better and offer to do it together. Never suggest skipping on your own. If the creator wants to move on without it, move on without insisting. There is no minimum number of findings, comments or references.

## 1. Load the method before thinking

Load it in this task, not from memory. If the Sofia tools are available in this session, `read_method_piece` opens any piece by id; otherwise read the local files. Read:

- [formats](../formats/README.md), the requested format's own file and the structure that format points to ([structures](../structures/README.md));
- [addictive elements](../addictive-elements/README.md) (with the hierarchy);
- [principles](../principles.md), [universal rules](../universal-rules.md) and [no AI-speak](../no-ai-speak.md);
- [breaking the bubble](../breaking-the-bubble.md) and [commander's intent](../commanders-intent.md);
- the analyzed example of the format, if there is one in `examples/` (analysis, person-storytelling, visual-storytelling, split-screen, green-screen);
- [idea template](../idea-template.md), [archetypes, niches and bubbles](../knowledge/archetypes-niches-bubbles.md) and [principles examples](../knowledge/principles-examples.md).

A piece already read in this conversation, and still in it, doesn't need to be read again. A summary piece ([principles summary](../principles-summary.md), [no AI-speak summary](../no-ai-speak-summary.md)) does not replace the full piece. If the requested format doesn't exist by that name, say which one you understood and why.

## 2. The basics, one or two questions at a time

Reuse what the creator already told you. Ask only what is missing, at most two questions per message, the most valuable first.

**Block 1, the basics:**
1. What is the video's theme?
2. What's your niche, and who do you want as a client (Who it's for)?
3. What idea do you want the audience to walk away believing (the commander's intent)? If the creator profile already has commander's intent notes, start from them. If not, offer to build them together with [commander's intent](../commanders-intent.md), one question at a time, and save only with their OK.

**Block 2, the bubble and the emotion:**
4. Which bubble does this theme call? What is it saying about the theme right now? Is there controversy or a split opinion?
5. What emotion does your audience already carry about it (anger, frustration, curiosity, fear, hope)?
6. Is there a character, real case or situation your audience already knows that connects to the theme?
7. Is there a popular belief about the theme (a sacred belief of the bubble) that is wrong or that you disagree with?

**Block 3, the creative context:**
8. Is there a reference video you like?
9. Which recording formats can you actually produce? (The catalog has 23; see [formats](../formats/README.md).)
10. Any constraint on length, tone or subject?

If the creator doesn't know the idea, help: which universal conflict does the theme touch for the most people? What emotion does the audience already bring? What argument exists in the bubble? What is the common ground between the theme and what they sell?

## 3. Start from what already worked

If the creator shares their numbers (screenshots or an export) or an earlier profile evaluation ([analyze](analyze.md)), find what performed above the profile's normal: theme, format, structure, type of video. A winner becomes more ideas like it: a variation, a continuation, the same mechanism with another subject. Check the creator's swipe file for saved templates, if they keep one.

**A number is not a decision.** A video that underperformed doesn't mean the creator decided to drop that theme. If the data clashes with a rule saved in the creator profile, show the conflict and ask. The idea can't contradict the conclusion you drew from the data.

## 4. The bubble

Every Sofia script tries to break into a bubble, so the video has a better chance to spread, and plants a seed of what the creator sells.

- If the creator profile lists bubbles, and you are sure which one this is, use it without asking. If in doubt, show the closest ones and suggest one.
- If none fits, choose a new one with the creator by step 1 of [breaking the bubble](../breaking-the-bubble.md): familiarity (what they're a fan of or live every day) and closeness to the goal (what connects to what they sell). The bubble is named after a subject or a community, with one of the 6 types. A name that describes a state or a difficulty goes in "Who it's for".
- Bubble research (most-liked comments, vocabulary, what moves the bubble, references) follows [bubble research](../bubble-research.md); see [research](research.md).
- Then talk with the creator: what caught their attention, what surprised them, what they agree with. That conversation often produces the idea.

## 5. The brainstorm with Sofia's team

- **In Claude Code**, open in parallel the `ideas-strategist` (directions and questions), the `bubble-specialist` in propose mode (candidate bubbles and research plan) and, if there is already a theme, the `researcher`. Talk with the creator one question at a time and record each decision in the video brief right away. Consult the team again only when an answer changes the direction. When closing the idea, the `structure-reviewer` and the `bubble-specialist` review it.
- **Without agents** (Claude on the web or mobile, ChatGPT, Codex without subagents), run the same roles one after another as passes: see [passes](../passes.md).

## 6. Propose 3 to 5 ideas

Use the [idea template](../idea-template.md). Each idea names the format, the structure and the addictive elements, with the point where each element appears, and respects the format's rule (in Analysis, the analyzed subject is someone from outside who entertains, never the creator's own profile). Each idea also says the bubble it tries to break into and the seed it plants: the pillar, the sentence and the type of CTA (hidden or direct). The seed comes from the commander's intent notes or from what the creator told you; without them, ask before inventing.

Turn the Rubik's cube until you find the bridge between the theme and the seed. A forced connection doesn't count.

Before moving on, be honest with the creator:
- Is the theme big enough, does it reach a lot of people?
- Is there real conflict in the viewer's head?
- Does the audience recognize the subject fast?
- Is there a real common ground between the bubble and the commander's intent?

If the theme is small or weak, say so and suggest how to widen it ("This subject is a bit narrow and may not interest many people. Which bigger problem of your audience connects to it?").

Before showing the ideas, check them: if the Sofia tools are available, run `check_script` on the titles and possible hooks and check each point it returns in context (it can be a false positive); check MC16 (format, structure and elements declared) and the IT rules of the template by hand.

## 7. The approved idea becomes a video brief

Keep the approved idea in the video brief in the conversation (see [script](script.md) for the brief's fields): the theme, Who it's for, the bubble, the line "Seed ({pillar}): {the sentence}", the format and the structure. A rejected idea is noted as rejected so it doesn't come back. With file tools and the creator's OK, save the brief to `sofia-english/briefs/<slug>.md` in the chosen folder ([files](../files.md)).

## 8. The structure

With the research ready, choose the structure and write what goes in each block, in short bullets tied to the findings, before any spoken text: see [structures](../structures/README.md). Format, structure, elements and principles must fit together. The creator approves the structure before the hook ([hooks](hooks.md)).
