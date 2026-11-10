# Isolated Sonic native PointRead source qualification

PASS, stdout only, against public ROM SHA256 `c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f`. No ROM, emulator run or build output was made. `build/sonic-native-point-read-1110` does not exist. The qualified source files below are frozen at these hashes; further work must use a new derivative.

| Source | SHA256 |
|---|---|
| `tools/reference/sonic_sms_native_point_read_1110.py` | `fc135d40cb35d115d4854db00b29943b57ee9a454b7cff58f65e2a2e6ddf8eff` |
| `tools/audit/check_sonic_native_point_read_1110.py` | `7a145e8b6797252d7fa256dd10be9ad47b9a559080a59892311c40c3ee5f32aa` |
| Existing in-memory assembler dependency `tools/reference/sonic_sms_compact_cold_worker_1110.py` | `9be550fe16764fd0eeef3f429d453883fc26edf1d8f4710423eebc8d04939bd2` |

The assembled leaf is365 bytes, SHA256 `82ee77ec5d6923e2e28e7bec31c9fb8a9b55922ec72dd525b1be74e61749771d`. Proposed test addresses are RAM3 B600..B76D and a22-byte private argument/output/scratch block RAM2 C100..C116, both half-open. These addresses and lifetimes are **not allocations**. The builder accepts explicit code/scratch parameters for future relocation. It modifies no frozen Sonic core, metadata, previous checker or native hook.

The signature takes16-bit worldX and16-bit screenY. Success returns C1, A=the actual native metatile, X=its full exact attribute byte and Y=the native buffer index0..207, with cell origin and buffer selection in the proposed private output block. Failure returns C0/A=X=Y=0 plus a nonzero Status distinguishing vertical OOB, initial loading, unstable parser phase, inconsistent ring cursor, invalid capacity or outside interval. **Failure is unavailable/OOB, not an empty traversable floor.** The future world/viewport bridge must handle it explicitly.

The accepted interval is `[floor(actual screen-left pixel/16), committed parser end)`, after ColumnSets becomesFF. Behind-camera retained cells are excluded deliberately. It does not claim full historical residency of all32 ring slots. Original area-start witnesses are not reliable after entrance setup, and this leaf invents no provenance RAM. Stable native phases0/4 leave the cursor on an unwritten column; phases1/2/3/5/6/7 have already committed that column. The leaf rejects phase>=8, CurrentColumnPos>=16, inconsistent BlockBufferColumnPos, and queryable length outside1..32.

Actual source witnesses were rebound to current bytes: PRG2:A09B task handler, A0C1 backwards task table, A0E6 column increment/ring wrap, fixed126:95D8/95DC native buffer-address table/leaf, InitializeArea's12-set count and AreaParserTaskControl's ColumnSets decrement. MTileAttribute EF36 is byte-identical in fixed119/120/125/127, SHA256 `02ca3678ee8114a3eb336262b9472ee9929237a31f39d5b6886886dc252b8470`.

Qualification used315,463 actual6502 PointRead calls:

- 106,496 calls: all256 exact metatiles in every one of13×16 cells of both actual native buffers0300/03D0, with exact current attributes and varying pixel offsets.
- 65,536 calls: every16-bit vertical coordinate, accepting only32..239.
- 135,760 calls: parser phases,16px seams, world-page crossings, camera offsets, interval edges and distant same-parity aliases.
- 1,071 calls: invalid cursor/phase/loading/capacity states and exact capacity edges.
- 8 calls: the16-bit world's final frontier65536, without wrapping to page0.
- 6,592 calls along actual native parser episodes described below.

The finite subtotal is308,871; the real-parser subtotal is6,592. Separately,32 calls to the actual fixed GetBlockBufferAddr establish every native column pointer. Each successful leaf call performs exactly one native buffer read and one attribute read. Every rejected call performs neither. Valid calls cost585..589 CPU cycles with minimumSP222 for the two-byte return address. There are no ZP addressing modes, subroutine calls, SMC or mapper writes. Runtime write guards admit only the declared private output/scratch bytes and the return-stack pair; native buffers, all host ZP, headers, shared DFD0..DFD2 mailbox, PPU state and maps remain intact.

For starting pages0 and1, the checker executed actual AreaParserTaskControl12 times each, observing exactly24 initially written world columns and ColumnSets0B→FF. It rejected the next eight not-yet-written ring slots. It then executed actual AreaParserTaskHandler64 times per episode; all eight stable phases occurred eight times each. The checker tracked all13 native writes for each genuine producer call, proved the committed frontier from those writes, and compared PointRead throughout. Final parser cursors were40/56, with40 genuinely produced world columns per episode. This includes native column15/16 and31/0 ring transitions. These are actual parser calls, not a hand-written producer substitute.

Reproduction command, writing zero files:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/sonic-native-point-read-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_sonic_native_point_read_1110.py --output build/sonic-native-point-read-1110
```

This is only a native cell reader. It does not classify native16px geometry into donor32px shapes, implement water/one-way/support behavior, initialize Sonic, advance its clock, render its full body, admit raw43 or prove ordinary-frame/gameplay behavior. The actor, shape adapter, native effects and lifecycle remain future work. No RAM or code interval is granted by capacity or by these tests.
