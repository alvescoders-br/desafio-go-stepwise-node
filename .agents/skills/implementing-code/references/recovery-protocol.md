# Recovery Protocol — File Loss / Integrity Break

Read this reference **only** when one of the integrity-break signals below fires. In a clean run you do not need this file.

This protocol exists because of a real failure mode: an `Edit` / `Write` collision wipes a large file mid-phase, and the agent then spends tens of thousands of tokens scavenging Spotlight (`mdfind`), `.DocumentRevisions-V100`, IDE local history, or build caches looking for a backup that does not exist. The correct answer is almost always one `git` command.

---

## Integrity-break signals (when to read this file)

Any one of these is enough to enter recovery:

- A file you wrote earlier in this session is now empty, truncated, or its line count dropped by more than 50%.
- A file you wrote earlier in this session is no longer parseable (compiler / linter reports it as completely broken in a way that does not match your last edit).
- A `Read` you just performed shows content that does not match the IMPL-STATE record for that file.
- An `Edit` tool call returned success but the file size on disk is now zero or vastly smaller than expected.
- Any message you would naturally phrase as *"the file was accidentally wiped"*, *"let me check for backups"*, or *"let me find the original."*

If none of these fire, do not enter recovery — keep working.

---

## The protocol (in order — do not skip steps)

```
1. STOP. Do NOT search for backups outside git. Specifically: do NOT run
   mdfind, ls .DocumentRevisions-V100, ls .kotlin/sessions, find build/.transforms,
   query JetBrains local history, or open any IDE-specific cache. These paths
   are dead ends and consume thousands of tokens for zero recovery probability.

2. RESTORE FROM GIT (the only authoritative source):

     git -C {source_path} status --short -- <path>
     git -C {source_path} checkout HEAD -- <path>

   This restores the file to its committed state. If you have been making
   per-phase wip commits as Phase B requires, this gives you the latest
   completed phase as your baseline.

   IF git reports `<path>` as untracked OR `git checkout HEAD -- <path>` fails:
     → The file was created in this session and never committed.
     → SKIP to step 4 (fail-fast) — there is no recovery.

3. REPLAY FROM IMPL-STATE:

   READ {progress_folder_path}/IMPL-STATE-{session_id}.md
   FIND files_touched entries for <path> that are status=COMPLETED.
   For each entry, the IMPL-STATE row records what action was applied
   (CREATE | MODIFY) and references the plan step.

   Re-apply the edits in their original order. Use the same Edit / Write
   tool pattern you used the first time — but now from the restored baseline,
   not from in-memory content.

   After each replayed edit, IMMEDIATELY append to IMPL-STATE files_touched
   (Rule 4 / EOL-append). Do not batch. Recovery is exactly when batching
   loses the most progress.

4. FAIL-FAST (only if step 2 had no git baseline AND IMPL-STATE has no record):

   The file is unrecoverable. Do NOT improvise content from memory — that
   is fabrication. Call:

     stepwise session exec-fail --session {session_id} {capability} \
       --message "Integrity break on {path}: no git baseline, no IMPL-STATE record. Manual restore required."

5. CONTINUE PHASE B from the failed file's entry.
   Do NOT restart the phase. Do NOT re-run files that were COMPLETED before
   the integrity break — IMPL-STATE already records them as done.
```

---

## Why bash scavenger hunts are banned

Concrete cost data from a real run that did this wrong:

| Step | Tokens consumed | Recovery probability |
|------|-----------------|----------------------|
| `mdfind` Spotlight queries | ~5 K | 0% (Spotlight does not index file content history) |
| `ls .DocumentRevisions-V100` | ~3 K | <1% (requires Time Machine; not in CI / containers) |
| `find` in `.kotlin/sessions` | ~4 K | 0% (build cache, not source) |
| `find build/.transforms` | ~6 K | 0% (build artefacts, not source) |
| JetBrains local history probes | ~8 K | 0% (only exists if the file was edited inside IntelliJ) |
| Re-reading the wiped file 5+ times to "see what's left" | ~20 K | 0% — the file is the wiped file |
| **`git checkout HEAD -- <path>`** | **<1 K** | **~95% (assuming per-phase commits)** |

The agent that triggered this protocol's creation burned ~50 K tokens on the first six rows before stumbling onto the correct fix. Do not repeat that.

---

## Prerequisite: per-phase commits

This protocol only works if Phase B has been making per-phase wip commits as required. If `git log --oneline {source_path}` shows no `wip(impl): ...` commits for the current run, the recovery baseline is whatever was committed before the session started — possibly far behind. In that case step 2 still works but you may lose more than one file's worth of in-session edits, and you must replay more of IMPL-STATE.

This is the operational reason the per-phase commit rule in `phase-b-execute.md` is non-negotiable. Skipping it does not save time — it deletes your only recovery surface.

---

## Memory Bank note

After recovering, log the integrity break in IMPL-STATE under `repair_log` (or, if outside REPAIR mode, under `deviations`) with:

- The file path
- The detected signal (which integrity-break trigger fired)
- The recovery method (git checkout vs. fail-fast)
- The number of IMPL-STATE entries that had to be replayed

This is how `calibrating-execution` learns whether the protocol is firing and whether it succeeds.
