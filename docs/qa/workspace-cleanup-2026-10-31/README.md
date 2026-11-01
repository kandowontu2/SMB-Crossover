# October31 build-cache cleanup

Build cache: 458,452 files / 56,666,828,329 bytes before;
5,508 files / 816,524,109 bytes after.
Removed 452,945 superseded files; net reduction 55,850,304,220 bytes.
Independent whole-workspace check: 4,258,457,032 bytes.

Current ROMs and actual link objects for Contra Force f476, campaign6f9f,
Thomas3fe868 and Hogan99b9 remain available and hash-checked. The installed
Downloads ROM is f476 and was unchanged by cleanup. Frozen source/native
packets, working source, Git and original donors remain. 471 directory
links were removed nonrecursively; their targets were not deleted or traversed.

`build/_recovery/legacy-sources-2026-10-31.zip` holds source/recipes/JSON
receipts and selected legacy debug inputs, deduplicated by content. It is
303,994,516 bytes, with262201 original paths and41836 unique payloads.
Every payload was verified before deletion. SHA256:
`61edc74c6ae009468b39f01a65d07ec01930abd9daaeb7be3589708f78f9dcd8`.
The archive remains local and is intentionally ignored by Git. No bulk
rehydration is authorized. Search and restore exact required files only:

```powershell
python tools/audit/restore_compacted_build_source_v1.py --find campaign-menu
python tools/audit/restore_compacted_build_source_v1.py --path EXACT/PATH
```

Superseded ROM/object/debug/listing copies and raw captures/logs were pruned.
Historical receipts still describe their original runs; expanded paths may
now be absent. They must not be described as live or silently marked passed.
Storage-guard source changed intentionally; older guard revisions remain in
Git/checkpoint source. Future builds must bind the new guards and use actual
current recipes, rather than expanding historical proof graphs.

Hard limits are now5GB/20000 files across build/,256MB/1000 files per task,
and128MB/64files/fourPNG per capture. Artifact producers must use the bounded
runner described in AGENTS.md. It checks live growth, stops only its owned
process tree on violation and removes only that new disposable output root.
Ten isolated guard checks passed, including a real owned-process overflow
termination/cleanup. Actual compiler admission and oversized-capture rejection
also passed after cleanup, with no output creation. Aggregate fixtures in
memory; never create per-case/per-frame forests.
