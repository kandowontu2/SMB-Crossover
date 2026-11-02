# Metal Storm no-shot overhead followup

Private candidate `build/metal-storm-idle-shots-1101-v41/candidate.nes`, SHA256
`27dee145eead745dfe94cc6e4734a88fdd03811c7f7c3c9d1ee55e54d3057318`.
Installed in Downloads and tested from that exact path; no backup created.

The existing native service profile calls the shot callback on every active
idle/walk update. Even without shots, it saved/restored eight scratch bytes and
the mapper-call operands, then looped over both inactive slots. The new ten-byte
entry tests the two original active flags and returns handled when both are
inactive. It runs inside the existing authenticated C2 service; both complete
cache headers are still checked first. Source movement and attack behavior are
unchanged. The renderer occupies 2,985 of its 3,072 bytes.

The actual public callback falls from 1,764 to 1,355 CPU cycles with no shots,
saving 409 cycles per call. Active-shot cases cost 11 additional cycles. This
is a modest optimization, not evidence of 60fps or a whole-frame improvement.

Verification: 792 differential cases preserve returned AXYP, native non-stack
RAM, final mapper state, source actor state and lifecycle context, including
all 32 single-byte header corruptions, paused/inactive states and either/both
active slots. Differences are confined to unused renderer scratch. The existing
source-table/contact suite also passes 300 rectangle cases and six excluded
object cases, including actual native defeat/score/SFX and source shot retirement.

Root-owned native queue: prepare using
`prepare_metal_storm_idle_shots_native_1101_v41.py`, then run `idle/run.py`
and `route/run.py` under the bounded wrapper. These reuse the unchanged
predecessor controllers (120 physical idle and walking frames; complete 1-1
through active 1-2). No emulator was launched by the audit agent.

This is based on installed v40, not the private Shinobi successor. Integration
must preserve newer unrelated ROM changes by applying only verified changed
bytes from v40 to this candidate. No Downloads file or continuation was changed.

Native verification: full1-1 through active1-2 passed in5480 physical frames, both lives retained. Idle/walk completed80/78 updates per120 physical frames, unchanged throughput; mean cycles32229.4/34043.0, exactly409 belowv40. Downloads cold launch/select/idle/walk also passed. No full roster or all-powerup claim.
