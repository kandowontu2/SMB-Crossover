# Bub/Bob private cadence measurement

Parent Downloads remains
`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
Root ran both identities serially in actual Mesen using ordinary menu and
controller inputs. These are private measurements, not a local delivery or
full-stage qualification. No screenshot, video, state or receipt file exists.
The existing bounded two-file Bub component was reused throughout.

The source proposal and caller/interrupt qualifications are in
`bub-native-noops-1113.md`, source commit477d9352. Module SHA256 is
`6770cb6c8c9a0fe73eebd8c2c9b4c112ee55dc81def05c9aaf280b5a14e718e6`.
`run_bub_noop_cadence_1113.py` enforces the exact proposal/inverse and named
UI-only versus combined variant. It has no installation or release action.

## Measured ordinary empty windows

Each row applies independently to Bub and Bob. The first natural Goomba is
observed only after the empty windows: actual Goomba352/184, player128/176.

| Candidate | Idle Main/source updates | Idle physical frames | Idle lag NMI | Walking Main/source updates | Walking physical frames | Walking lag NMI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Public7ef baseline | 48 | 96 | 72 | 36 | 72 | 54 |
| UI-only e76 | 48 | 96 | 72 | 36 | 72 | 54 |
| UI + empty loops f88 | 48 | 76 | 52 | 36 | 64 | 46 |

The UI-only shortcut is behaviorally positive but has **no measured cadence
gain** in these windows. The explicit combination reduces the physical time
for the same idle work by 20/96 (20.8%), and walking work by 8/72 (11.1%).
This is still lagging; it is not a 60Hz or global performance claim. It counts
actual completed Main/source updates, including the native catch-up return,
not body-draw calls, rendered animation frames or the Mesen UI lag counter.

All four candidate runs have 138 Main entered, returned and source updates;
71 normal returns and67 catch-up returns, SP252, zero source updates outside
pending Main and both lives. Walking moves X40 to75, and every physical frame
in the measured windows polls input. Terminal X128/Y176 remains healthy.

| Candidate / identity | ROM SHA256 | Lua SHA256 | Native receipt SHA256 | Total physical |
| --- | --- | --- | --- | ---: |
| UI / Bub | `e76d9bc4c30127f834392e9b4de0a356128fd580b64ea399abc75ba062190179` | `6b3190c5862d7c06b6fe85034a1599451e9f2556fc38103a253bc26d0c5b61ed` | `b17bb6ac1bb27e8d878245cb87f3e4341d1d25d78f2069a08516e60a752504c2` | 617 |
| UI / Bob | `e76d9bc4c30127f834392e9b4de0a356128fd580b64ea399abc75ba062190179` | `c9cd47b211a6eca71f9babf1b6dc574924c66d084117936a0dffe444a1d582a9` | `71abcff4c2ed2c6ea9643c05c5acde1fb1eb07b3e025a352e479f3c3794cdbff` | 638 |
| Combined / Bub | `f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7` | `5d1baa5693c8a40abf5a9d31f0f1834c27324a02fd7abf6205dab7c4801e39ea` | `6f5f4cf22f0cd04eb4e73dbb982bf5e2cc62b3d72079de0e10b3e4907c9b90b2` | 569 |
| Combined / Bob | `f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7` | `79c3859f14c6b32546e04fa82376a605e3884c2222d6efad2d0b29cedf798d4d` | `febd68b8aac2f279e682597dec74677beba044590e148a228d739cbe13645ffa` | 590 |

The material combined gain justifies proceeding to full-stage, naturally
earned item/bubble combat and relevant foreign-route qualification. Those
remain open. No UI-only/native-short-window result substitutes for them.
Root owns the sole Mesen queue and later byte-verified local delivery.
GitHub releases must remain empty; no patch asset is authorized.
