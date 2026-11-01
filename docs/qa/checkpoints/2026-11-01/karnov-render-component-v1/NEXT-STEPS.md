# Next: shared integration and combat

This is an unimplemented integration approach, separate from the passing evidence
in handoff.json. Continue actual integration; do not repeat component bookkeeping
or treat this plan as a native playthrough or usable 86th character.

## Source funding for the real dispatch

Use a dedicated runtime character ID 34 for Karnov, while retaining Rygar's menu
slot and Select alternate. Existing legal runtime IDs are 0..33. This avoids
testing the shared alternate byte on every Rygar hook and permits the original
families, including their existing alternate combinations, to retain their routes.
Audit direct ID-indexed tables before admitting 34 to actual gameplay.

A possible exact source funding arrangement:

1. Current bank 29 B400 is occupied data, not free space. It is inside
   MarioWaterCoast::ProductHi, a 256-byte multiplication table at B38E..B48E.
   The source macro is MmMultiplyRoutine in the actual build input
   build/bt-ready-menu-1031-v2/joint/src/megaman_physics.s, expanded by water.s.
   Do not modify those retained inputs. Copy just the macro source privately.
2. For that one macro expansion, relocate ProductHi's exact 256 bytes into the
   already granted residual bank-29 padding, with the same low address byte 8E.
   This preserves indexed-read page crossings and therefore instruction timing.
   There are three local LDA/ADC indexed consumers in the macro. Verify all
   consumers, exact table values, changed operands and math/ABI/cycles. Do not
   replace the arithmetic or use MMC5's multiplier: Protoman audio uses it.
3. Keep the old table's emitted extent exactly 256 bytes: 114 bytes FF, the
   genuine 108-byte KrServiceVeneers at B400, then 34 bytes FF. The relocated
   table and private veneers can exchange this storage without moving the
   legacy menu helper, Rush reset, or other existing public endpoints.
4. KrServiceVeneers now shares the existing B400 page and zero low byte of
   FwServiceVeneers/ThServiceVeneers. Use the existing ThFFBankReady transport
   with bank(KrServiceVeneers)|80; assert the shared high/low contract.
5. Put a five-byte KrUnionBank helper (LDA bank, JMP ThFFBankReady) in HuVine's
   existing five-byte pad. Add CMP #34 / BEQ KrUnionBank after the existing
   LDA SelectedCharacter at HuGenericIndex. This costs four body bytes.
6. Put the existing five-byte HuQClass body (CMP #25 / JMP HuS2Decide) in
   HuMovement's five-byte pad. Replace its old location with JMP HuQClass,
   saving two contiguous bytes. Existing Thomas foreign paths must still enter
   it with the original A and retain their flags/stack ABI.
7. Move the unchanged 32-byte HuExtendedBT body before HuLo. Its selector is
   then nearby, so the old JMP HuExtendedBT after CMP #30 can become BNE:
   that path is already known not equal. This saves one byte. Along with the
   existing one-byte pad before HuResolve, it funds the new four-byte selector.
   Preserve HuResolve at BA54 and the whole union's C000 limit.
8. Reassemble the union as source, replace only its object in the actual linker
   command, and relocate its internal data/helper references normally. Verify
   exported ingress addresses, all 85 legal character/alternate destinations,
   A/X/Y/P/SP/SMC contracts, and real ISR cuts. Only the newly assigned ID 34
   should gain a different route. No raw-ID alias removal is necessary.

The exact emitted table, role and consumer proofs are still required before this
arrangement can be considered granted or complete. Current rendering build has
not moved this table or changed the shared dispatch.

## Menu and scene ownership

FmResolve's Native tail is currently `farcall HuResolve,jmp` in the exact
build/hogan-thomas-current/src/full_roster_menu.s input. A private copy can call
a bank-29 KrMenuResolve wrapper with the same-sized farcall; that wrapper can
call HuResolve and then map selected Rygar + alternate bit 1 to ID 34. The main
entrypoint directly includes full_roster_menu.s, so an exact local copy resolves
without copying a tree. Keep the bit for menu/continue identity even though
gameplay dispatch uses ID 34.

Do not mark FmPending's Karnov branch ready until ROM-only portrait/color/name
handlers exist. Current kernel code is unavailable before cold loading. A static
idle packet in bank 29 can be read through that bank's C alias, as existing Bowser
previews do, without executing unauthenticated RAM. Original idle body uses five
cells, page 408, foreground palette 28/16/0F. Convert source offsets from center/
foot to the native portrait anchor and preserve the actual original OAM order.

Locate the real ThSceneInit consumer from the linker/import graph and wrap its
existing source callback with the selected Karnov cold load/constructor. Do not
assume the full Thomas resident has spare bytes. Current KrConstruct is a cold
new-life constructor that clears source state. Split new-life construction from
area/world reconciliation so earned upgrades do not disappear on every area
transition. Do not publish readiness until code, state, metadata and context agree.

## Gameplay still required

- Native projectile contacts, destructible bricks/boxes, enemy damage, impact
  animation, score placement, and original SFX. Current callback terrain is empty.
- Native enemy-stomp bounce reconciliation. The easy/hard contact flags alone
  do not make the original actor consume the native upward bounce velocity.
- Original health/injury, Super Fireball and options/stock/drop/activation rules,
  water behavior, and original audio. Do not report fixture-set weapon levels as
  earned upgrades or reuse another character's tracks as completed music.
- Low-jump traversal: ordinary jump rises 48px, boots 88px. Verify tall pipes and
  all audited gaps with the proper source ability or existing native platforms.
- Own HUD/name/portrait/death/vine/pickup paths for ID 34; inspect direct tables
  before allowing an unknown legacy ID to index them.
- Native cold-start controller tests, 1-1 and shortcut, real item collection,
  head bumps, camera, actual eight-sprites-per-scanline behavior and frame timing.
  Use one owned Mesen queue with the watchdog and capture limits in AGENTS.md.

The original projectile patterns are already packed in verified unused pairs
0,23..28 of body page 3. They use even tiles C0/EE/F0/F2/F4/F6/F8 in P0 window 3,
physical CHR page 410. World windows 4..7 must remain untouched. Pose metadata is
in conditional C2/D000; farcalls unmap A3, so do not point the native renderer at
an A3-only packet. Body hurt blinking keeps the real state's CHR selection.

The active output remains build/karnov-host-resource-base-1101-v1. Reuse it while
unqualified; preserve this compact source snapshot rather than copying the tree.
The Downloads nightly is still the tested 85-character f6415a64 build.
