# Retired Thomas debug cleanup

Removed only seven superseded compiler candidate.dbg files. Active Steve, Karnov and DK Jr workers confirmed they do not use these inputs. All four current symbol-provider files below are preserved byte for byte. Source files, compiler recipes, source/native checkpoints, original-game debug files, the recovery archive, ROMs and user files remain. No archives or backups were created. Historical recipes that directly read these retired debug files need their exact debug input regenerated before replay.

|Retired build path|Bytes|SHA256|
|---|---:|---|
|thomas-late-lifts-1102-v1/candidate.dbg|36274498|cd6bd8b09a01d111c44b670511987d5b8015faebeb6d43964999426b08ee56bb|
|thomas-melee-stack/candidate.dbg|36269220|e4a328e67bde8fa3087474889dac432b86a1b70466ee98d22e049f9f4aa8c18b|
|thomas-lift-carry/candidate.dbg|36268734|ad0c85a787d70be61ad35b763ca5a3d9d9ea8a67d9c716da74d4188f3ef8a36f|
|thomas-native-carry/candidate.dbg|36267833|66c124a4ae2d5193069febeb6113179eeb190c7b9f2d16ca380e6f9108834dcb|
|thomas-pipe-lifts/candidate.dbg|36266747|15852791b3b2852a51d5e44e4d3bac192713fc979b5f922055a9d9eb3df28135|
|thomas-natural-host-1031-v6/candidate.dbg|36257212|78a9fa8667910d921a452b5e68f77cb443a37ceb455f3a08857e7840934b32ca|
|thomas-adapter/candidate.dbg|36252723|b7908bedfbd8005e081ab2f1d5d07c319c94b01fc803e944360d6d5fd4295070|

Preserved current symbol providers:

- roster-combined-1101-v3/candidate.dbg: `5ed30a2606470398a991927a89ef87b75262d3d39642827eb5a535ea963c9ce3`
- kirby-approach-owner-1101-v3/candidate.dbg: `cada90f529ff56f943eed27979a51d723f4273c2a077274a35eee5d115fa1e54`
- bub-menu-candidate-1102-v2/combined-event.dbg: `a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4`
- thomas-current-candidate-1102-v3/candidate.dbg: `a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4`

Storage receipt:

```json
{
  "before": {
    "build_bytes": 3123116524,
    "build_files": 19998,
    "build_byte_cap": 5000000000,
    "build_file_cap": 20000
  },
  "after": {
    "build_bytes": 2869259557,
    "build_files": 19991,
    "build_byte_cap": 5000000000,
    "build_file_cap": 20000
  },
  "free_before": 24824971264,
  "free_after": 24904916992
}
```
