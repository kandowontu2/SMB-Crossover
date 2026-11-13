# Current native roster follow-up: Bowsers and Bubble Bobble

All runs use actual Downloads ROM
`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
The patch guard is clear before and after. No ROM or runtime state changes,
videos, screenshots, per-frame files or private nightly installations occur.
Root retains one Mesen queue and the bounded existing two-file output task.

## Both Bowsers clear non-shortcut World1-1

`replay_bowsers_current_1113.py` reaches visible roster position26 with real
Down/Right input; Select once chooses SMB1 Bowser. The current menu path was
also independently checked through actual native UI.key instructions.

The ordinary route adapts the retained historical SMB1 CPU policy: Right,
fresh eight-update jumps for pipes/walls/pits/enemies, and periodic fresh B.
It never requests a helper or shortcut pipe. It observes every actual
GameLoop return by return PC/SP, authenticating current native code and the
complete terrain-attribute table. Both lives, live original Bowser runtime,
selected identity and positive source health remain required throughout.

| Identity | Physical frames | All returned Main | Final health | Lua SHA256 | Native receipt SHA256 |
|---|---:|---:|---:|---|---|
| SMB3 Bowser | 5,692 | 3,391 | 33 | `0be5c10a092f5214821a033b4bbf8e7028847febacc92abb8853ed77d3af0c46` | `74ce9aa524b67939fc6ec77edda6139afd526fa6da230c2faf255cff78720b6b` |
| SMB1 Bowser | 7,362 | 4,426 | 2 | `0c09bb637a4fda2eac517adcf6f5bd0602f610e39e9d130714f6859d63e69856` | `f1e11736613b7128b0361fd303b5c71c2ed478e46e27b8f787d628b75749818d` |

Each crosses all six pipes and the full overground route, observes native
flagpole/castle/entrance states, and ends at X40/Y176 in underground AreaType2,
level1, engine8, with both lives and25 consecutive grounded quiet updates.
No helper is needed. SMB3 return counts are normal2,011/catch-up1,380;
SMB1 counts are2,502/1,924. These are genuine physical full-stage passes,
superseding the earlier startup-only evidence gap for this exact build.

An earlier SMB1 controller729d6118 also cleared1-1 (receipt31afd645), but only
counted25 cumulative active next-level updates and stopped while falling.
The final controller above strengthens that endpoint to real underground
grounding and25 consecutive quiet updates. It changes no game behavior.
The initial recipe attempt failed before Mesen because an unused symbol
`TimerExpiredFlag` was absent; that unused binding was removed.

Scope remains one Easy/default non-shortcut route per identity, not every
powerup, all difficulty modes, acoustic fidelity, every animation or zero lag.
The general101-identity completion goal remains unfinished.

### Both natural mushroom/flower routes also pass

Root subsequently runs each frozen `replay_bowser_natural_powerups_1113`
controller against actual Downloads through the same bounded queue.

| Identity | Physical frames / all Main | Lua SHA256 | Receipt SHA256 |
|---|---|---|---|
| SMB3 Bowser | 2473 /1266 | `58d777bc44d5b7ff370ace86b20a76e57f69f6f70e11e0cc57940a263f4e4de1` | `f4150018d5e33cafb81742d56073df58322fa2651e996d59f8f20278331bed1d` |
| SMB1 Bowser | 2897 /1617 | `d23ba56d64b6efacc3ba21463717df4764623bba3b10100073758f3cb5d2fb63` | `fea00aef1e959e421dff959332b8728a936645182cb3c72e22e2fb744a2f46e1` |

Both reveal real question blocks336/1248 by original head contact, observe
birth and maturity, and use the actual native collector on slot5. Mushroom
and flower each erase, queueSFX32/popup6, grant tier0→1→2, run exactly60
bank-qualified BwPowerupTick calls, then resume. Each run also completes60
resumed gameplay updates after the second upgrade, retaining both lives.

SMB3: mushroom actor409/184 at player397/176; flower1248/119 at1263/124,
health33→34 on the flower. Terminal1352/176, health34. SMB1: mushroom407/184
at395/176, health4→5; flower1248/119 at1260/117, health3→5. Terminal1319/129,
health5. The second endpoint is still in a normal jump; this pickup route
does not replace the separate grounded underground full-stage qualification.
No helpers, captures, code or runtime writes occur. These are the current
host's tier/health semantics, not a claim of a new donor-boss weapon.

Native Star/1UP and every other powerup family remain separate coverage.

## Bub/Bob: native empty-scene baseline

`profile_bub_empty_native_1113.py` authenticates the current private Bubble
carrier, both complete runtime identities, current native hooks and all39
IdleLoop bytes. Root runs both pure factories using
`run_bub_empty_native_1113.py` against actual Downloads.

| Identity | Lua SHA256 | Native receipt SHA256 | Total physical frames |
|---|---|---|---:|
| Bub | `34687e8faf3e5c150f41c55678a835410741a7b81d00c27e23489a10f3502666` | `b9747162cddee652a5fe4798cf2d4a73d405189c11ce85a612f441a53863c7e8` | 617 |
| Bob | `2839c0217a5cf1fa35201af979bbfb68c6f289089d630e899bd1885b84817f2f` | `12af2d4556d62637339174588e7bf0e24725177eaf49dcd74f7dd54594dfb57b` | 638 |

Both produce the same measured empty windows:

| Window | Physical frames | Returned Main | Original source updates | Frames with input poll | Native NmiSkipped delta | X |
|---|---:|---:|---:|---:|---:|---|
| Idle | 96 | 48 | 48 | 96 | 72 | 40 to40 |
| Walk | 72 | 36 | 36 | 72 | 54 | 40 to75 |

At nominal60Hz these are30 original source updates per second. This is a
gameplay-cadence result, not a claim about Mesen's UI lag-frame definition.
The game-owned skipped-NMI counter and actual input-poll counts are reported
separately. No live native actors exist in either measured window. Afterwards
the real parser produces the first Goomba at world352/Y184 as player reaches
128. Each complete probe has138 entries,138 returns and138 source calls,
with zero source calls outside a pending Main. Normal return82BE/SP252 occurs71
times; catch-up return82D0/SP252 occurs67 times. Both lives remain.

The corrected native walk travels35 pixels in36 updates; the CPU model
travels36 with the same phase policy. Input sampling and native scheduling
are distinct, so whole-route frame changes must not be credited to an
optimization without checking actual movement/source-call trajectories.

### Retained observer failures

The initial3735099b controller attempted repeated Left to reach visible25.
That stays within a row and fails at frame496 before any gameplay; receipt
`9c25de45aaa48c8d7f4f1de20148b4322a18e80c4d8b8e56b53f98625939310e`.
The corrected real path is Down8, Down16, Down24, Right25, then Select for
Bub/Bob. This is a harness error, not a ROM bug.

The subsequent9d06ce99/f1176514 observers watched only the normal return82BE.
They passed their local assertions but counted half the actual source calls:
idle48 counted Main/source96 in192 frames. Receipts7e5700a6/ad0c7bee remain
diagnostic records, not a15Hz performance claim. The native catch-up caller's
JSR82CD returns82D0; counting both qualified return sites fixes that omission.

The current source model attributes about45,507 cycles to an empty idle Main;
14 full owner checks account for9,266 cycles. A proposed isolated no-op UI
shortcut would save less than4%, so it is not presented as a verified lag
repair. Larger source-faithful changes remain under investigation. This
baseline delivers no new ROM or IPS; the existing Latest asset is unchanged.

The separate passive native cost probes also pass with unchanged phase
positions, Main/source counts and physical cadence. Bub uses Luaa5b78804,
receipt `16cbe30dd8340fb7ed616884b978f8eb26c18dc7f94e6b69156ebedbc7db8eea`;
Bob uses Lua5d3267b7, receipt
`5d03c9b3b33d9d923943a7504b9b7c7dfd7b9621670f6c0a152d584a61ee306c`.
Their elapsed routine profiles include interrupts and nested calls; the
buckets must not be summed. Bub's idle GameLoop totals2,231,681 cycles over48
calls, about46,493 per call. Native source draw occurs24 times in the same96
physical frames because catch-up omits drawing:15 source body-draw calls per
nominal second, distinct from display refresh rate and from30 source updates.
This remains a measured baseline, not an optimization result.

The corrected private empty-loop candidatea77a71cf is then measured with
strict new cookie/code authentication. Both identities pass the same basic
windows, but idle remains48 Main/source in96 physical frames. Walking36
updates takes71 rather than72 frames; positions, real first enemy and lives
match. Bub receipt
`4f2658e807bb2f5812cd854b5a02adc37e7f4afd416fd0acb2bf9814fbc3538b`;
Bob receipt
`9741a91bf2f08ac56d6ad2b4f7e32b3f1f7efa0bf6b76b70af7cec5bd4511040`.
The modeled2,430-cycle saving does not deliver a material native cadence gain
by itself. It remains private in a separate two-file/2.11MB component output;
it is not installed, released or described as a lag fix. Broader release
qualification is deferred while larger transport costs are investigated.
