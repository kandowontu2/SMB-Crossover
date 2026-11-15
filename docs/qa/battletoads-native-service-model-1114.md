# Battletoads leased native-service model

Root's conditional source-model lease is
`docs/qa/allocations/battletoads-native-service-research-1114.json`, SHA256
`be498c276f02b7602ea8ef60f7b0f2a6bb288e6c5488d72914ad3c52a4c83068`.
The source proposal remains frozen in commit181956ce. This lease permits
executing exact347B physical-PRG envelopes in the source CPU model, not ROM
composition, Mesen, or delivery.

`check_battletoads_native_service_model_1114.py` retains the actual owning input
bytes in `bundle['raw']` and overlays reads only at the three declared PRG
envelopes/four prefix operands. On actual571
`5715bb7e3c772350a2a7420ec9061eabd948964a8789e5d348c49d3cfb3c57ee`,
160 model bytes differ inside the347B envelope. The entire BT8192 cache,
16-byte cookie, full public BtCheck and ten score-table bytes are untouched.
The explicit frozen typed571→Score.inverse→F11 boundary supplies only compatible
navigation metadata; actual CPU code/data remain571 with the leased read view.

## Actual-opcode CPU profile

Session62884 terminal PASS, genuine compiled Rash cold/Start followed by four
neutral warm updates, idle48 and Right32. Every measured scheduler iteration
has one actual GameLoop entry and return. Parent and overlay agree after every
Main on game RAM including native below-stack globals, physical RAM, OAM,
VRAM, maps, CHR state and the complete33-byte end-of-Main SMC block. All80
samples have zero active enemies, HP47/lives2/power0/Star0/Y176; idle stays40,
Right reaches83/camera1. Minimum SP184.

| Phase | Main | Parent mean cycles | Overlay mean cycles | Saving each Main |
| --- | ---: | ---: | ---: | ---: |
| Idle | 48 | 36604.0625 | 27528.0625 | 9076 |
| Right | 32 | 36864.5625 | 27788.5625 | 9076 |

BtRouter calls fall12→7/Main; full CfOrBtCheck/BtCheck calls12→5/Main. Actual
native query totals remain three head and four side calls/Main. Battletoads
contributes one of those heads; the other two native head-entry calls already
exist in the parent. New BT pass sites execute exactly one/four times. The
profile reports actual reached instruction PCs throughout the new code.

Initial45559 completed all48 idle paired state comparisons and the router7/
check5 assertions, then rejected a harness assumption that *total* native head
queries equal the single BT callback. No terminal positive was claimed for
that attempt. The successor counts the exact new BT pass PCs separately and
requires the total native queries to match the parent. No proposed opcode
changed in this correction.

These are source CPU cycles, not physical frame cadence. Root's parent idle
Mesen86156 remains48Main/72physical; no improved native cadence is claimed.

## Active scope

New-PC session32589 terminal PASS:92 reached instruction boundaries,92 actual
unmasked IRQ and92 Main-busy NMI cuts, minimum SP192. Immediate AXYP/SP,
maps, complete SMC, live stack and physical RAM agree with the captured state;
all CPU-global effects match the unmodified current571 ISR from the same
captured context. Full Main continuation agrees on every physical RAM/VRAM/map,
global and terminal register with the equally interrupted oracle.

Three earlier harness negatives are retained:77696 wrongly assumed no ISR
may change globals;70278 assumed final whole-Main registers equal a run without
an interrupt;59692 extended that assumption to all private scratch. Final32589
identifies the effects as **busy NMI**, not IRQ (the earlier progress message
mislabelled them). Busy NMI advances E1/E3 and native audio workspace plus
NmiSkipped; it also causes two private clock bytes at offsets7904/7905 to end
1→2/0→1 compared with no NMI. Basic position/HP/lives/variant remain unchanged.
These effects match current571 and are not masked or seeded away. The normal
regular-NMI arm is unreachable at the captured Main-busy PCs; zero such forced
arms are claimed. IRQ has no corresponding global effects in this receipt.

Both current571 full-stage overlays are terminal PASS:

| Identity/session | Receipt SHA256 |
| --- | --- |
| Rash83887 | 4b00da9d4b593856b806c6aee3014b8cddf79889d96c62382b8f36c252d57d5d |
| Zitz49793 | 632de84f0b0c296cb54a6f9a36a2101ebda797e7d56a242dfadb23710be47aaa |

Each reaches4003 actual Main entries/returns,2863 original BT steps/58 in1-2,
flag2805/castle2868/entrance3406, then25 living grounded1-2 updates at40/176,
Y-high1, HP43/lives2/power0/Star0. Names and variants0/32 come from compiled
Select/Start. The frozen ordinary policy is unchanged; only its configuration
is rebound to owning571 for the model. No native-controller qualification or
hardware frame count is implied by these source receipts.

Decoded census95241 invokes the actual common AE00 loader for all7 owners
37..43 with its forced-blank component contract, authenticates their current
descriptor/header and scans resulting code/metadata. It also independently
authenticates/decodes the3Prince packet streams. Only one direct-control word
matches a moved address: Prince RAM3:BF03 JMP BEDE. That is an intra-RAM3 jump,
not PRG33 ingress. Other current raw executable carriers have no moved words,
apart from BT's ordinary private BEE2/BEEF/etc absolute data operands. Descriptor,
split-plane and executable/data classification remain pending; this census
alone is not called closure. No historical producer or archive was restored.

All-owner actual-opcode ABI, final decoded/indirect ingress and broader
lifecycle qualification remain pending.

Actual-opcode component5633 passed2,048 cases (896head/896side/128 eachNoOp9/29)
with all128 valid statuses, exact native AXYP/SP/physical RAM/maps and minimum
SP193. Savings are1674/head,1462/side,792/NoOp. The new side-tail BNE atBEFE
crosses fromBF00 backtoBEE2, costing one cycle per query and explaining the
four-cycle difference from the earlier static9080 estimate.

Paired-events6259 adds actual parent571-versus-overlay validation at12 common
function entries: head, four side indices3..6 and seven surviving router
slots0/12/13/2/29/34/9. All12 IRQ and12 busy-NMI pairs finish the complete Main
with identical registers, globals, full SMC, physical RAM, OAM, VRAM and maps;
minimum SP184. The two private bytes mentioned above are now symbol-bound
`BtSrc_FrameCounter`/`BtSrc_FrameCounter_Even`, BEE0/BEE1 (also `BtState` base).
Initial89080 only failed because it included the parent's obsolete router10/14
contexts that the overlay intentionally bypasses; no opcode changed.

Fault22523 passed every16 individual cookie corruptions plus absent8192 cache:
17 full BtCheck rejects,85head/85side native-oracle matches,17 each private
movement0/draw2 rejects and NoOp9/29 C0 returns. A CPU execution trap observes
zero unvalidated private instructions and physical RAM remains untouched by
the queries. The invalid-cache terrain rejection change is intentional; full
public checking/private service rejection remains intact.

The actual opcode model is frozen at source SHA256
`41bdc432cd30e50e77c303f276c9da711445c687c770aa337de27b8fed78da5b`.
Independent bounded commands use this file with `--profile`, `--units`,
`--faults`, `--interrupts`, `--paired-events`, or `--stage --identity rash|zitz`.
No test output files are written. The unallocated proposal181956ce remains
unchanged. Natural death/retirement and final reader classification remain
scoped work, not silently promoted from these component tests.

All producers use `build/battletoads-native-service-model-1114`, max-files1,
stdout/in-memory only. No ROM/captures/output tree are produced. Root alone
owns native validation and any later allocation/delivery decision.
