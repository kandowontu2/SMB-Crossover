# Independent root review of the Bub palette mapper

This is source-component evidence, not native gameplay qualification.
The source-only allocation is
`bub-native-palette-current-source-1115.json`, SHA256
`0daf2ece6fb9511132716478580ac61ba3c9c248f919f440a5a0f083bbdcb59c`.

Root independently composes the image directly from the allocation's four
old/new spans and the declared complete code/art cookie recipe, without
calling the helper composer. Exact candidate SHA256:
`174fa29cf05ce1d14526ea3778c74b33a3858301c81da49b982e0ca2200ab0b4`.
Only49 bytes differ within52 owned bytes; inverse restores exact official40a.
Cookie is `a72702972671056c12e3e4be9b97af56`. No ROM file is written.

The actual29 emitted bytes execute in393,216 6502 components: identities
0/1/255, both load entries, all256 input attributes, all128 valid status
values, and two X/Y pairs including the last real sprite row. Only Bub's
low palette3 maps to0. Returned A/NZ match that mapping; X/Y/SP/CVID and
upper attribute bits are exact. Original source attributes/identity remain
unchanged; all writes are stack writes, minimum SP233. Component costs are
24/27/37/38/40/41 cycles, excluding the caller's JSR. This does not prove
the complete NativePair, map/ISR lifecycle, native graphics or frame cadence.

Terminal receipt:
`cf25708c73a5653a741251edeaf83ed72c14d5bbcaf80d7e4811fa585c626ff0`.
Runner `tools/audit/check_bub_palette_mapper_root_1115.py`, bounded absent
output root `build/bub-palette-root-review-1115`, max1/600s/zero files.

Root separately checks the frozen helper C/F file hashes, portable roundtrip
and all six compiled native controller APIs: composer1b3e655b, factory9ce50ca8.
The native three-scene controllers are Bubd373fa20 and Bobd76f7bfe; natural
1-Up controllers are Bubb99a9c2f and Bob0acc0bc6. Full source gameplay,
ownership, palette lifecycle and reached ISR are the helper's separate gates.
The private native runner is prepared but must not stage/launch before its
separate exact source-qualified native allocation exists.
