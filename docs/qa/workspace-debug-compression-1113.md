# Debug-symbol filesystem compression

Further Mesen work stopped before launch when C: had24,643,072,000 free
bytes, below the existing25GB minimum plus capture reservation. The build
folder remained3,123,074,992 logical bytes and19,998 files. No storage or
capture cap was increased and no emulator started on that rejected run.

Root inventoried only the existing build tree. Its retained `.dbg` symbol
files include many36–46MB text outputs that current and historical tools
may still read. Their paths and data were preserved using standard NTFS
filesystem compression (`compact /C /F /I /Q`), not new archive files or
WOF/reparse compression. Every resolved target was checked beneath the
absolute build root, and every file's SHA256 was compared before and after.

The completed operation verifies241 files, identical logical bytes and
paths, no reparse points and zero new files. C: free space was24,599,683,072
bytes at its start and25,476,505,600 at completion. These are whole-drive
observations; concurrent writes outside this cleanup can also affect them.
The next observation was25,403,363,328 and a guarded native test was admitted.

The reviewable cleanup recipe is `tools/audit/compress_debug_symbols_1113.ps1`.
Run it with `pwsh` (PowerShell7). Without `-Apply` it only inventories and
hashes. The retained ROMs, sources,
checkpoints and recovery ZIP were not deleted, copied or rehydrated. Build
logical-byte accounting is unchanged; the disk uses fewer physical clusters.
Other projects and user sessions were left untouched.

The optional `-IncludeBuildBinaries` pass also applies transparent compression
to retained `.o`, `.map` and build-only `.nes` files. That operation verifies
580 files in total, unchanged hashes/paths and zero new files. Its whole-drive
readings are23,751,495,680 before and23,922,532,352 after. The following
observation is23,912,488,960: concurrent drive use has consumed the earlier
headroom despite the unchanged logical build inventory. New native runs are
therefore held by the original guard again. Source/CPU work continues with
zero generated outputs; no outside-project files were modified or deleted.

A bounded PowerShell7 dry run of the saved recipe also passes. The first
legacy `powershell.exe` invocation lacked Get-FileHash and stopped before
modifying anything; the recipe now explicitly requires PowerShell7.
