# Rogue HUD area-transition cause and detached fit — 2026-11-16

Actual cb95 has a confirmed HUD continuity defect: the native area redraw clears the E/M row, but the optional Rogue writer's health/ammo cache and dirty0 survive. The eligible writer then suppresses every unchanged-value packet. This is separate from the already closed1-1 missile-picture latency lead, whose native terminal really displays E191 M004.

Frozen passive facade `tools/audit/replay_rogue_hud_continuity_cb95_1116.py`, SHA `c229563433813c269dfe63a22e71da2e60bfff32dff10c5207ed2c39f9ef596d`, accepts exact owning cb95. Native Lua is `64cbc38b6e9d5cf00c5ce6251bc59c21eb4111a6d01c2a1bac3b0b2a326288e5`; source-only Lua is `d01caaef21cff19a1ed50fd30330d7c0d708b5dcd01b48c6ad1c76ad2a14eedb`. Exact observer removal restores qualified Bomb Lua3395 with all controls, stock/score/worker assertions and endpoints intact. It adds aggregate guards/commits/cache writes and at most10 actual transition milestones, no PNGs or per-frame dumps. Native alone reads both actual nametable rows; the source gate makes no PPU claim.

Source58968 **PASS**, outer `409ec94dec27073096ed35832006ea9c89d3dc9bd8f196da9c49e2bc99d29ff5`, inner `70501154a225e3fd7c29245f17475726e56cd60d98232da495aaeabaeb469df5`.5082 Main/3982 Dispatch+Step+Life balance, executed registration22 exec/17 write/two events. Removing only `hud_continuity` exactly equals the complete original Bomb38899 receipt. In underground area192,377 Hud attempts include261 eligible, all261 cache-equal, with **zero packets/dirty/cache writes**. Cache5, cached health10h/19h and dirty0 survive actual EnterScene, native status redraw and active1-2. The queue is not starved. Absent `build/rogue-hud-continuity-source-1116`, max1/600s/0files.

Root independently ran actual Downloads native86516 **PASS**, receipt `dd0dae085d90d268801c500b0a62553600b70861bd519777d42d55d5d512203b`. Removing only the observer exactly matches original functional Bomb728a. MF Main1917 shows E191 M005. From actual native-status area41/Main4237 through underground area192/terminal5138, actual NT2023 and2423 are eleven blanks24h. Underground has381 attempts/236 eligible, all236 cache-equal and no packet/dirty/cache writes. Actual native pixels therefore confirm the same cause; source counters were not relabelled as pixels.

## Detached existing-tail proposal

`plan_rogue_hud_scene_dirty_cb95_1116.py`, SHA `ad1b325160693fa653209b326d598b093a3159a8a41f0c1bc6075e150ca154a2`, API `descriptor(rawcb95)`, freezes exact14B fit. Detached terminal receipt `e2d1f78e81791817d1835553eac6d35a89b75c099937d78951a44792268debe8`. No proposed instruction, candidate image or game/UI CPU is executed. Existing linker metadata and twelve retained simple source procedures reassemble byte-exact to installed cb95.

Only proposed range: PRG95:B78F..B79C, file784287..784300 inclusive,14 owned/10 changed, no new RAM or growth. Old `203daf900820c3b1a9018d7c5c60` (SHA `d77d0743777676557cf6176642e2389610e5f56d6914237e4b1155c196deabc5`) becomes `900b20c3b1a9018d8e7d8d7c5c60` (SHA `23afbbfbec33ba2f28c9f6499132db9e5e09f656721b37c0df9f0e454e011739`). Predicted image SHA `79fd089f80b06038e68b968d2ff80d09caba72a133735b3fef6bb86ffa3ed2df` is streamed from old bytes plus that descriptor, not a composed candidate.

```asm
; Actual old private tail
jsr RdHostEnabled
bcc Done
jsr RdTxMovementBegin
lda #1
sta RdColorRequest
Done:rts

; Detached same14B proposal
bcc Done                    ; exact three helpers' actual admission result
jsr RdTxMovementBegin
lda #1
sta InvDirty                ;7D8E, existing HUD invalidation owner
sta RdColorRequest
Done:rts
```

The existing ColorRequest store B799 and Done RTS B79C remain exact. It requests a redraw once per explicit session/life/scene boundary; ordinary eligibility, packet ownership, retraction and cache acknowledgement stay unchanged.

Actual current chain is public wrappers B77D/B783/B789 → respective AB80/ABD6/AB9D lifecycle helper → BCDE `RdItSyncLifecycle` → B78F private Dirty → BCE4 `RdItSyncStatus`. `tools/prepare_rogue_dawn_host_items_v3.py` SHA `1cc3ea0bda8e5ebdcda423b5a8368391f64f7e5fcdcef9087366e182b8ff2eb6` explicitly retargets exactly those three old Dirty JMPs to SyncLifecycle. Actual public callers are RdLifeFresh B8B1→B77D and RdLifeArea B8FA→B783/B900→B789. Current bank95's whole-word census into all14 tail bytes contains only BCDF's JSR operand; there are no raw95/DF typed farcall/table triples anywhere in PRG. Only linker labels are the entry and unchanged Done. The tail is not source-exported and has no published indirect descriptor.

The helpers first call the actual SelectedCharacter2/RdVariant1 guard. Foreign exits return its C0 plus A/NZ; owning session/life tails end at EnterScene→ImportPosition's explicit SEC, giving C1. Jumps/JSR into SyncLifecycle do not change flags. MovementBegin PHP/PHA and PLA/PLP restore full input AXYP, and do not change X/Y. Final LDA1 fixes A/NZ on the owning path; V/D/I and admission C remain unchanged. On a rejected helper the removed second guard would reread unchanged identity and reproduce the same A/NZ/C0. Arbitrary manual private calls with invented C are outside this closed ingress contract, not silently generalized.

Independent read-only review agrees with the exact current caller/byte/carry/AXYP proof and finds no prelease blocker. One interrupt nuance is explicit: NMI `SoundTestAudioTick` temporarily writes SelectedCharacter; all Tick/Stopped paths restore its saved value before returning. RdVariant has no ISR writer and neither Dirty nor SyncLifecycle is called by an ISR. The contract relies on complete RTI restoration of identity/registers/P/mapping, including carry, not an assertion that NMI never writes identity. Actual new reached IRQ/busyNMI cuts must still qualify that contract after a lease.

Static RP2A03 private-tail cycle estimate is114→88 owning (−26), foreign-character32→9 and foreign-variant40→9. These are once-per-lifecycle estimates, not proposed-CPU measurements or an idle cadence claim. Exact IRQ/busyNMI/identity-stability and full return/stack/mapping checks are still required under a root source lease. This document authorizes no overlay, native run, physical candidate or delivery.
