# Battletoads final source ingress and lifecycle checkpoint

All helper checks use actual owning input 571:
`5715bb7e3c772350a2a7420ec9061eabd948964a8789e5d348c49d3cfb3c57ee`.
The opcode model remains frozen in commit41179074, source SHA
`41bdc432cd30e50e77c303f276c9da711445c687c770aa337de27b8fed78da5b`.
The original proposal181956ce and its 347-byte envelopes are unchanged.

## Frozen reader classification

`tools/audit/audit_battletoads_native_service_ingress_1114.py` SHA256
`fce35918e77ac3eec1448967e709141111bdbfb92a82f4173a7a07ebe8a57c13`.
Default session95241 is terminal PASS for the current loader/decoder census;
`--static` session9447 is terminal PASS for the exact descriptor/consumer
classification. The default census alone still labels further classification
pending; the static result supplies that separate evidence.

The actual AE00 cold loader executes all seven current common owners37..43
under its forced-blank component contract. It authenticates the current code
and metadata headers after copying/decoding. No health, actor, terrain or
position values are seeded. The actual descriptors are:

| Owner | Pointer | Rows/code rows | Physical source pages |
| ---: | --- | --- | --- |
| 37 | AFD2 | 8/6 | 728..735 |
| 38 | BF93 | 2/0 | 617,619 |
| 39 | AFE5 | 9/8 | 301,305,337,362,363,440,819,666,441 |
| 40 | DFE0 in RAM2 | 2/0 | 960,961 |
| 41 | B9F9 | 1/0 | 967 |
| 42 | AFCB | 2/2 | 991,992 |
| 43 | AFFA | 1/0 | 328 |

The current pointer planes at PRG65:AB91/AB98 feed indexed loads at AF0E/AF13
into R3/R4. Cookie planes ABAF/ABB7 feed AF19/AF1E into their data pointer.
These are copy/authentication data descriptors, not executable target tables.
No descriptor pointer is one of the moved side entries. Page values are
bounded CHR indices, not CPU control addresses.

Thirteen actual Nr selector implementations and all65 entries of their
five-entry low/high/bank planes are decoded from current PRG124. None targets
the moved fixed prefix or a moved internal PRG33 address. The only standard
bank33:BEA2 farcall is the resident side shortcut at file1036542. No standard
farcall immediate pair targets the moved internal entries.

Prince's exact45-page authenticated packet is independently decoded into its
8159-byte runtime,6112-byte metadata and1607-byte staged state. Its only matching
control transfer is RAM3:BF03 `JMP BEDE`; both instruction and target are inside
the same A000..BFFF RAM3 view. It cannot enter PRG33. The same result appears in
the actual common-loader output. The other six common owners have no matching
target words in their final code or metadata.

The registered raw executable carriers FF_STREAM, BW_STREAM, BT_STREAM,
CF_CARRIER, QW_STREAM, KR_KERNEL_IMAGE, ARTHUR_CACHE_EXEC and WF_TEMPLATE_CHR
are separately scanned. All are clear of moved target words except BT's36
ordinary private absolute data operands. Those are LDA/LDX/LDY/STA/indexed
AND/EOR data accesses in RAM3, not JSR/JMP into PRG33. All24 current WWF copy
pages are decoded from WfPageSourceTable and lie within the scanned immutable
template domain629..667, including reused page667. Thus the roster's scatter
table does not select an omitted executable page. Rogue's declared CORE/HOST/
HOST_AUX executable segments are resident PRG; its CHR backdrop/pose data is
not silently treated as a decoded CPU program.

The fixed prefix has one retained compiler symbol reference. The compact DBG
keeps its reference ID52854 but no line/span records; the audit does not claim
those missing records were recovered. The retained typed source has its sole
symbolic JMP. All four actual current runtime copies in PRG119/120/125/127 have
identical35-byte contexts and exact `4CA7E4` instructions; their four operand
updates are included in the lease. No archive was expanded and no historical
producer ran. The PRG65 local BEE2 branches and the Prince RAM3 branch retain
their own A000-mapped namespace; the lexical PRG100 music-container BEDE match
does not grant entry to PRG33. These classifications accompany the literal
census; the census alone is not the proof.

No unresolved changed executable ingress remains inside these current
declared cache, selector and public-target domains. This is not a claim about
fabricated pointers or unaligned non-public router entries.

## Frozen lifecycle receipt

`tools/audit/check_battletoads_native_service_lifecycle_1114.py` SHA256
`8c4aa4d364337e6db657ac4b44d5ee1a80689208dfe08f0edbeaf61688afd1f3`.
Session99393 is terminal PASS for the following exact component scope:

- Genuine compiled cold construction,32 ordinary Right updates, Start,
  64 paused updates, Start and8 resumed updates. All106 parent/overlay Main
  results match RAM/state/maps/full SMC/VRAM. Pause values129/1 and resumed128
  are checked by bit0.
- Actual BtRetire clears the owning marker and preserves parent/overlay state.
  Retired movement0/draw2 and NoOp9/29 each return C0 with matching AXYP/SP and
  application/physical RAM.
- Public owning DeathStart slot7 is explicitly requested. It enters native
  state1/engine11 at98/176,HP47/lives2. The following360 ordinary neutral Main
  results match parent and overlay on all checked state, maps, RAM, full SMC
  and VRAM.

The death request is a component operation, not a natural enemy/pit collision.
Both parent and overlay remain in engine11/lives2 after360 updates while Y
evolves and wraps. This identical preexisting component limitation is retained;
no natural death/respawn success is claimed. No direct health/actor/engine/
position/terrain/ability writes produce the test state.

Initial44897 completed pause/resume and retirement, then misclassified inherited
dead-stack bytes441..448 as live globals using a shallower call's minimum SP.
The final comparison uses the already proven preceding Main watermark184.
Actual registers and return SP remain checked separately; SMC and all declared
lower globals remain protected. This is a fixture correction, not an opcode
change.

Cold/compiled alternate selection and the actual1-1→1-2 area transition are
also covered by the full Rash83887/Zitz49793 model receipts in the preceding
QA. The new code's92 IRQ/92 busy-NMI cuts and12+12 matched parent events remain
separately scoped there.

## Handoff

Every producer runs through the bounded wrapper with output root
`build/battletoads-native-service-model-1114`, max-files1. The root remains absent:
zero generated files, ROMs, captures or emulator processes from this helper.

Root reviewed these scoped results and issued the separate private composition/
native grant `allocations/battletoads-native-service-candidate-1114.json`, SHA
`c01100b1b055eb7a590c3afa46e1d89fc4684b18f3495441325e17bbf5529684`.
Root7957 composed private candidate
`ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01`,
160 changes within347 bytes, all unowned bytes including score10/BT8192/cookie/
BtCheck exact. At this checkpoint root55363 owns native cadence testing;
Downloads is still571. This source checkpoint is not a native performance or
delivery claim. New optimization changes are on hold pending root measurements.
