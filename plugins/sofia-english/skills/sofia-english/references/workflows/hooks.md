# Workflow: hooks and recording style

Read [behavior](../behavior.md) first. This is the stage between the approved structure and the script. It also covers a request for hooks only, without a full video brief.

## Before writing

Read [how to make the hook](../hook.md), [the hold zone](../hold-zone.md) and [hooks that work](../knowledge/hooks-that-work.md) in full, plus the format's file (its "Hook type this format asks for" line) and the analyzed example of the format, if there is one. If the Sofia tools are available, `read_method_piece` opens any of them by id. Use everything together: the method, the format and structure of the video brief, the research, the bubble (vocabulary, what moves it, comments and references) and what the creator profile says about the creator's voice.

If the creator sends a reference video at this stage, analyze it before suggesting any hook ([analyze](analyze.md)).

## Write and review

- **In Claude Code**, the `hook-writer` agent writes 8 to 10 options; then the `dont-do-reviewer`, `hook-reviewer`, `voice-reviewer` and `bubble-specialist` review together, in parallel. Tell the creator in one line that the team is writing and reviewing.
- **Without agents**, run the same roles as passes ([passes](../passes.md)).
- **The mechanical check:** if the Sofia tools are available in this session, run `check_script` on each option and check each point it returns in context (it can be a false positive, and it covers only part of the Floor; its 15-word limit on the first sentence is a tool reference, not a rule of the method); without them, check MC1 to MC16 by hand ([the Floor](../floor.md)).
- At most 2 rounds of fixes. What still fails goes to the creator as a short note.

## What to show

Show 3 to 5 hooks and 2 recording styles, with one line saying they passed review. The number of hooks follows the creator's saved preference; with no preference, show 3 and ask if they'd like to see more (with their OK, remember the answer in the creator profile).

Each hook follows [how to make the hook](../hook.md): in 2 seconds it says what the video is about and what the viewer gets, and comes with the spoken line (1 to 3 short sentences, the subject in the first words), the on-screen text (3 to 5 words) and what appears in the first 2 to 3 seconds, all three about the same thing, plus one line saying why it hooks and where the video pays the promise. Each hook promises something the hold zone can confirm in the next seconds.

- **Hook 1 is always a belief shock:** it contradicts what the audience believes and says what they wish were true. Show the belief, the desire and where the video pays it off.
- **Different types:** the options use different types from [hooks that work](../knowledge/hooks-that-work.md), and each type fits the format.
- **The slide:** every hook is the opening of the slide ([breaking the bubble](../breaking-the-bubble.md)): identification or conflict, in the bubble's words.
- **A comment as the opening:** a conflict or provocation comment with many likes can become one of the options, as the creator's line, keeping the part that grabs and putting the subject in the same sentence or the next. The creator chooses. Tell them, outside the hook, which comment it came from.
- **No result promises** ("you'll grow", "you'll make money") and no greeting, announcement, rhetorical question or "did you know".

```
Hook 1: [the spoken line, 1 to 3 short sentences]
On-screen text: [3 to 5 words, up to 2 lines]
Opening: [what appears in the first 2 to 3 seconds, and the movement]
Subject and gain: [what it's about] / [what the viewer gets]
Uses: [principles and addictive elements]
Why it works: [one line, and where the video pays the promise]
```

## The creator's choice

Wait for the answer. Ask which one caught their attention most; they can pick, combine or write a better version. Record the chosen hook (spoken line only), its opening and on-screen text, and the chosen recording style in the video brief. A choice of only the hook or only the style is kept, and the script waits for both. A rejected hook or style is noted so it doesn't come back.

Learn from the choice. If the creator asks for more hooks, ask whether they want to see that number every time and, with a yes, remember it in the creator profile. If they tweak the chosen hook (swap a word, shorten it, change the tone), ask in one line whether to keep that as their way for future hooks.

If the creator says they want to talk about the hook, talk only about the hook. The rest of the script waits.

## Hooks only, without a video brief

Ask for the subject, the audience and the format (one or two questions at most), read the pieces above and the format's hook type, and deliver 3 options in the block above, after the same review and mechanical check.
