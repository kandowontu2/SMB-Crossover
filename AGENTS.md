# Workspace storage rules

## Current gameplay priority

- Prioritize making every roster character playable and able to clear 1-1.
- Defer extended cosmetic polishing to the later per-character review.
- Address overwhelming lag while idle or walking without enemies; zero lag is
  not an acceptance requirement for this pass.
- Where a character cannot traverse 1-1 with their intended abilities, reuse
  existing native platform actors as helpers. Verify the assisted crossing.
- Maintain `docs/qa/helper-platform-inventory-1101.md`; final reporting must name
  every affected character/alternate and each helper's stage and world-pixel
  location, distinguishing initial height and left edge versus center.

## Nightly delivery

- Publish usable character updates frequently to
  `C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`.
- Replace that file directly. The user explicitly requests **no backup copies**.
- Verify installed bytes against the tested candidate and record verification
  scope. A GitHub push alone is not a nightly delivery.
- Current active handoff: `docs/qa/continuation-current.json`.
- Before and after delivery, run `python tools/audit/nightly_patch_guard_v1.py
  C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`. A same-name
  IPS/BPS/UPS can silently overwrite the nightly through Mesen's automatic
  patch loading. Resolve stale generated patches before claiming delivery;
  do not delete unrelated user patches. Test the Downloads launch context,
  not only an isolated build path. On November 1 a stale October 31 IPS
  caused Karnov to remain locked despite the new ROM being installed.

The user has twice had to intervene over excessive generated files. Storage is
a hard requirement, not a reason to create more archives or raise a cap.

- Keep the entire workspace below 70 GB decimal.
- Keep `build/` below **5 GB decimal and 20,000 files**, including archives.
- One task's temporary outputs must stay below **256 MB and 1,000 files**.
- Emulator captures: at most **128 MB, 64 files and four PNGs per run**. No
  videos, image sequences, per-frame PPU/state dumps or lossless capture forests
  unless the user explicitly requests that new capture and approves its size.
- Run the shared storage preflight before creating build outputs. If a limit
  would be exceeded, prune the task's superseded generated outputs first. Stop
  if useful work cannot fit; never increase these limits automatically.
- Every source test, extractor, compiler recipe or other artifact producer must
  run through `python tools/audit/run_bounded_build_v1.py --output build/TASK
  -- COMMAND...`, with its exact new output root. The wrapper monitors growth
  during execution, kills only its owned process tree on violation and removes
  that invocation's disposable partial outputs. Read-only inspections need no
  wrapper. Emulator runs also retain their capture watchdog.
- To continue the same unfinished task, the bounded runner accepts `--resume`.
  Use it only for your own unqualified output directory. It refuses a root
  containing a completed `source-stage.json` or `binding.json`. On a resumed
  job's limit violation, preexisting files are retained; prune your partial
  outputs before retrying. This avoids making another full build per retry.
- Storage inventories and explicitly scoped cleanup can run directly so they
  can repair an already exceeded cap; this exception does not authorize builds.
- Keep one active output per component. Do not copy whole source/reference
  trees, carry previous builds into successors, or retain every debug/object
  revision. Reuse read-only inputs. Preserve unique source in Git or an existing
  compact checkpoint, then remove disposable generated copies.
- Keep test fixtures in memory and aggregate results into a small receipt.
  Never create a directory or JSON file per test case, frame or permutation.
- Do not recursively rehydrate historical proof/dependency graphs. Restore only
  the exact inputs required by the current compiler/linker recipe, on demand.
- The legacy source recovery archive is indexed and deduplicated. Do not extract
  the whole archive. Frozen source/native packets in `docs/qa/checkpoints/` and
  the installed ROM in Downloads are retained.
- Root owns the single Mesen queue and cleanup. Agents must budget outputs and
  report their active paths. Do not let several workers create independent
  copies of the same large debug, source or asset trees.

Before resuming after the October 31 storage incident, read
`docs/qa/workspace-cleanup-2026-10-31/result.json` and the current continuation
note. Older receipts describe historical runs; cleanup may have removed their
disposable expanded outputs. Do not silently claim those paths are still live.
