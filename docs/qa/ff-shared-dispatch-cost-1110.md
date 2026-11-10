# FF shared dispatch cost, November 10

Frozen source CPU profile on image `96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd`. Checker `tools/audit/profile_ff_farcall_ancestry_1110.py` SHA256 `9b72fc052d4fc9138e32989eb831e2e4131f06ff673a7045418981eb07935931`.

The actual cold Select/Start path loaded the authenticated FF kernel with 16,400 PPU reads and 8,209 RAM3 writes. Sixteen idle updates and sixteen Right-only updates followed. Player X remained 40 while idle, then reached 66; Y176, engine8 and lives2 remained intact. Every update had six empty enemy slots. Terminal ObjectMetasprite0 was 233 and all 23 other metasprites, nine miscellaneous slots, two block states, seven floatey controls, ten Rg shots and three Samus shot/bomb slots were zero. No actor, terrain, position or stat grant followed the established menu seed.

The 32 updates entered FarCallCommon 3,203 times and its SMC target 4,515 times, approximately 100.09 and 141.09 per Main. First Main cost 53,140 instruction cycles; last 52,897. These are source CPU counts, excluding physical DMA stalls and injected scanline IRQs. This profile does not measure physical cadence or audio output.

| Concrete call site (physical tag:CPU PC) | Calls per Main | Measured responsibility |
| --- | ---: | --- |
| 190:AC13, FwCallEnter | 17 | Authenticated FF worker transport |
| 128:A281 | 6 | Empty enemy slots continue native loop/parser loading; Enemy_Flag0 does not authorize skipping |
| 254:90FA ->161:BEA2 ->217:BC58/BC7B ->NrSide | 4 each | Side-probe dispatch chain, including actual FF terrain queries |
| 255:ED62, KbNativeHeadBridge | 3 | Native head/terrain integration |
| 255:E490 and193:BFFA | 2 each | Native feet integration |

Renderer ancestry, with **overlapping inclusive costs**, was NoLagSoDraw 16,948 -> HuDrawAll 16,756 -> FwNativeDrawAll 16,585 -> DrawAllMetasprites 10,747 cycles/Main. The inner KbDrawDispatch -> ThSharedDrawHot chain cost 6,568 and includes actual FF body drawing. These wrappers are not empty foreign callbacks. Side-dispatch inclusive spans likewise overlap and must not be added together.

The profile records observed memory and AXYP equality at each returned call. For example, the measured QwAdderGate/HotCollisionAdder/NrAdder chain left application memory and AXYP unchanged in these opening FF frames. That observation is not a general no-op contract: owner selection, source callback outputs, terrain, visibility and other states still require their original behavior. Symbol names in the aggregate are nearest debug labels; physical tag/PC and executed target remain the authoritative coordinates, including legacy alias labels.

No global skip or candidate change is qualified. Source review established these obligations:

- EnemiesAndLoopsCore explicitly sends empty slots to ProcLoopCommand unless its parser-task guard excludes them. Skipping empty Enemy_Flag slots would suppress future enemy loading.
- DrawAllMetasprites traverses 24 shuffled positions, updates its shuffle state and executes world-firebar admission once. Its later debris, Samus/other shot publication, floatey and player passes have separate ownership. Any empty nonplayer-metasprite fast path must preserve those operations and their live state.
- Weapon pools being empty does not remove input, cooldown, animation, cursor, palette/CHR publication or lifecycle duties. Existing Samus and Special empty paths explicitly preserve such results.

The separate 5881 source proposal saves 2,728 cycles per empty Main but leaves roughly 50,000 cycles; it does not resolve overwhelming idle lag. Its eight same-entry duplicate-guard redirects and lifecycle/IRQ qualification remain separate from this read-only ancestry profile. No ROM, emulator run, build directory or generated receipt was produced here. The bounded runner used `--max-files 1` and its output root `build/ff-farcall-ancestry-cpu-1110` remained absent.
