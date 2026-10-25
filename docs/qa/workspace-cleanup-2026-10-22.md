# Workspace cleanup — October 22, 2026

The user's latest request sets the workspace limit to **30,000,000,000 bytes**,
superseding earlier 100 GB references in historical reports. Cleanup reduced the
folder from **92.2 GB to 25.6 GB**, leaving about **4.4 GB** of headroom.

**66,577,815,999 bytes across 135,247 files** were moved by same-volume directory
rename to:

`C:\Users\kando\Videos\SMB Crossover Archive\2026-10-22-workspace-cleanup`

No files were deleted. All archived file sizes and modification times were
verified; the archive also contains SHA-256 hashes for 1,294 media files. Source,
assets, tools, tests, reference files, current ROMs and the HR/GO/GA manifests
were verified unchanged during the move (7,985 protected files).

The archive retains older roster attempts and searches, old playthrough and
profiling folders, historical checkpoint tests and older roster checkpoints.
The workspace retains current root replay work, Bass searches, current and
recent named checkpoints, the complete verification/model dependency tree,
and the `Playthrough Videos` delivery folder.

The machine-local `workspace-archive.json` records every moved directory. A
second receipt, complete file inventory and media hashes live in the archive.
The cleanup evidence is `build/verification/workspace-cleanup-hz/`.

Use `tools/workspace_storage.py` to report the current size, or its `--locate`
argument to find an original workspace path in the archive without copying it
back. The route and branch runners can read archived input/ROM paths. Showcase
and route-guidance tools find their historical templates there as well.

The route runner clamps even older larger budget arguments to 30 GB; captures
retain their existing space reservations and per-segment storage checks. Branch
searches reserve 150 MB before launching. Future large jobs must fit below this
limit; archive older evidence first when more headroom is needed.

This cleanup changes storage and tooling only. The broader game fixes, roster
coverage and final recording goal remain active.
