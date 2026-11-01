# Karnov carrier proposal: unallocated, frozen source audit

**Carrier granted: false.** This packet changes no ROM, menu, native loader,
shared service, installed nightly or allocation. The current whole-host source
inventory is bound to `e8d35a95ffe8e396dc1d8b32ca78d57d376fc14de9a2f4b37754012448fde09a`. The earlier design/menu
fixtures are explicitly bound to frozen85 `f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1`;
all other CHR bytes match the current image outside Karnov399..411.

## Established bounds

- Karnov body407..411 has448 unused bytes, in relative runs0+32,896+160,
  1984+96,3040+32,4000+128. All256 original poses,64 host profiles, the
  original cold portrait and seven8x16 shot patterns are included. Original
 134 patterns are32-byte8x16 pairs, not16-byte tiles.1040B cannot fit there.
- Proposed selected-C2 worker C900..CD0F is1040B. A1280-byte transfer would
  lease C900..CDFF including240 zero padding. Audited original actor/options,
  clear/weapons/health/pickup state operands do not reachC900 even with a
  conservative full0..255 indexed domain. Context endsC864, metadata beginsD000.
- Proposed pages1019 and1020 follow the exact50-page SMB3Plus emission969..1018.
  Its3584 legal selector combinations and90 existing menu identities avoid
  those pages. Zero fill and segment absence are supporting facts only.
-690 exact declared source units were read;76 writer units and15 legal typed
  selector groups are catalogued in other-consumer-closure.json. Indexed
  recovery objects were read in memory and are retained by path/hash only.

## Loader source fragment and bounded evidence

Rows0..7 retain CHR399..406 to A3 bank3 C000..DFFF. Row8 proposes CHR1019
to C2 C900..CCFF; row9 proposes CHR1020 first256B to C2 CD00..CDFF. No
unverified RAM opcode executes during cold loading.

The helper source assembles to70B. Replacing old destination setup with a
three-byte helper call reclaims5B before water-table alignment; replacing the
old mapper prefix reclaims10B. Existing copy/verify loops use a row-specific
page count and ten rows.70B of helper/tables would fit the genuine802B ROM29
tail beside713B pickups, leaving19B. The pre-table85B gap would fit66B of
pickup helper, leaving19B. These are measured funding proposals, not grants.

The190B prototype extracts the original byte-copy, verify and final cookie
publication owners and links the70B helper at the proposed old tailBC8E. It
executes in an explicit synthetic mapper image: one success plus five injected
readback failures. All10 readbacks precede paired-cookie publication; failures
deny both cookies. Success performs18964 buffered reads in296908 CPU cycles,
minimum foreground SP218. It omits the real outer guard/save/PPU restoration.

## Exact remaining closure before any allocation

1. Run the actual current ArCacheEnsure/ArCacheLoad carrier into the mapper,
   then enumerate every201 cached descriptor header CHR field and the fallback
   input path. Exact indexed source is
   build/arthur-physical-clock-v1/joint/arthur/cache-runtime.s:40 and173..185;
   descriptor pointer roots areC000/C094/C128. ArCachePublishFast reads field1
   through(R0),Y and publishes mode83. Nominal Arthur868..880 emission is not
   sufficient evidence. Keep this a single aggregate receipt, not201 files.
2. Close every transitive live producer of CurrentCHRBank and X5ChrMode into
   X5WidePublication/X5Direct0..11, including copied RAM kernels and retained
   inactive-window shadows across scene/death/pause/character transitions.
   The generic publisher can represent all1024 pages. Exact current source is
   build/bt-ready-menu-1031-v2/joint/src/mmc5_expanded.s.
3. Close SsChrActive/SsChrPhysical/X5SpecialChrUpper into X5Write4 and
   InvHudActive/InvHudPhysical/X5HudChrUpper into X5Write8, including every
   producer and cancellation transition. Typed Parodius tables are bounded;
   that does not establish all persistent override values.
4. Complete reachable publication inventory for ARTHUR_CACHE_EXEC, QW_STREAM,
   FF_STREAM, BT_STREAM, BW_STREAM and CF_CARRIER. The15 typed groups prove
   their listed legal selectors only; a writer search is not transitive closure.

Only after1019/1020 is proved unreferenced may root allocate it, integrate the
real forced-blank loader, authenticate the added worker in a new cookie
revision, and test cold/warm/rejected readback and PPU/bank restoration. Actual
Main depth and all live IRQ/NMI seams still need measurement. Combat's earlier
service-entry SP224/minimum ISR SP136 is13B above SMC7B at that entry only;
it does not qualify deeper Main call paths. Root owns integration/native queue.

No donor ROM, full PRG, dependency source tree, per-frame state or emulator
capture is included. This is source/CPU design evidence, not native gameplay
or nightly qualification.
