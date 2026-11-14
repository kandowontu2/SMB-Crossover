# Explicit current421 input adapter, November 14

`current_smb2_hidden_input_1114.py` adds a separate typed wrapper for exact
`421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f`.
It does not change the frozen fa66 normalizer, default APIs, response composer,
CLI, grants, emulator controls or installer. Adapter SHA256:
`d9014c60e6294bc8eb92a8e24ab0dfdb84af428e5b3654dbb48cbd75ca67956b`.

The explicit entry is `normalize(raw421, kind='hidden-421')`. It uses the
portable response inverse to exactfa66, then delegates to
`current_smb2_cheat_input_1114.normalize(..., kind='cheat-fa66')` to recover
exact12397. It retains the three strict provenance steps, exposes read-only
`.fa66` and `.postbg` views, and requires `.preserve()` before a separately
qualified legacy component result can carry current fixes. Normalization alone
is metadata/source reuse, not a candidate or delivery.

`preserve(legacy_result, legacy_result_SHA256=..., allowed_component_offsets=...)`
requires the exact independently qualified12397-based output PIN and complete
component ownership. It delegates restoration of all66 fa66 changes to the
frozen normalizer, then restores the complete201-byte hidden-response envelope.
Every allowed component byte must avoid all201 hidden bytes and all252 bytes
of the existing complete cheat-owner/resident envelopes, including unchanged
bytes in those regions. It verifies110 hidden changes plus66 fa66 changes
retained, all176 current changes protected, every unowned byte exact and
every actual component change equal to the pinned legacy result.

Frozen dependencies remain:

- fa66 normalizer: `f973573e52a2c752da3531ee6bc3706dc8e1096b79cc0fab2740ad4f0fb20f34`.
- Portable response composer: `7d8e2210a38952902694efcbb5334ae9b704902679b6353e43834f361bbee71a`.
- Hidden resource grant: `fc69deed91f0d5c3aa09345733d8052e80dba4a4a6acd0e25e31c7a56d24b67f`.
- Hidden behavior supplement: `5b881c4e1a28152ce9b4a09c61fe1877e40d86bfb1d01b1ce4795e97462e2358`.

## Source validation PASS

Bounded session28360 is terminal exit0. The checker reads root's retained
exact421 candidate in `build/smb2-flag-native-1113/candidate.nes` without
changing it, forbids mutable Downloads reads and `Cache.parent_image()` lookup,
and traps file writes. Cold binding caches are cleared before validation.

Identity inverse/roundtrip preserves exact421. The old fa66/postbg APIs retain
their strict inputs, and the old fa66 entry rejects421. A one-byte synthetic
ownership unit proves a permitted outside component delta while retaining all
current bytes; that unit is not a game proposal. There are480 strict rejected
cases: all453 individual protected-byte overlap requests, dirty current or
legacy images, wrong/missing kinds and PINs, wrong size, forged provenance,
unowned changes and invalid ownership indices. The rejected-case aggregate
SHA256 is `551711a2fa848bf52cb700148e3953b8a1075a9ab8ee1cfbb3292f3be93a759c`.
No per-case fixtures or files are emitted. Actual Downloads read attempts:0.

## Actual disjoint DK composition, source-only

The checker executes the retained actual DK recipe, rather than inventing a
component delta:

- DK composer SHA256: `c5885ac48e48ae21f50fefd7be595fa456b6644ff145b012ef121b2562290f6b`.
- Exact12397-based DK result: `16c71bc6fb6427ddb0c43dc41d687e768bb4f86015a23204398023fbf3856bd1`.
- Independently delegated fa66+DK result: `a5942300cd677a9c62b1f3ff312552216766de8fcca8d93f8939143f3f650625`.
- New exact421+DK result: **`df130d5dba8d21e74f5bc2899aad4d77b681381c8f8dfa34b72b392131eedada`**.

The complete11,433-byte DK ownership set is disjoint from all453 protected
current bytes. Exactly846 DK bytes change from421. Both independent orders
agree: apply only the actual846-byte DK delta to421, or apply the110 hidden
changes to independently verifieda594. Removing the846 DK changes recovers
exact421; removing all176 current changes recovers exact16c71. The actual
DK inverse also recovers exact12397. Complete hidden and cheat envelopes and
all other current bytes match421 exactly.

This adds no new ROM capacity, RAM, CHR, geometry or helper. It does not repair
the retained DK native final-handoff negative or qualify the combined image
for native play or installation. Root owns all CLI changes, Mesen and delivery.
No ROM, patch, capture, backup, release or generated build file was written.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-hidden-current-input-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_smb2_hidden_input_1114.py --dk-component
```
