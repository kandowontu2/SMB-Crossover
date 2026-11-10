# Prince fourth-pipe floor diagnosis — source snapshot, November 10

The private landing repair `build/prince-landing-native-1110/candidate.nes`
(`34d2146263ef4eb950d957824c75899d49b53d80f7f30e584e0cbb694fc9bbf4`)
passes the immediate X891 Easy landing in root's native run. This note records
the subsequent CPU diagnosis and an **unfunded, unqualified source proposal**.
No proposed ROM, receipt, emulator capture, or other build file was written.
Public c10 and the frozen previous-sole v1 source/proofs remain unchanged.

## First incorrect write

`check_prince_fourth_route_1110.py` constructs an explicitly translated CPU
scene using the actual current native `GetAreaDataAddrs` / `AreaParserCore`
1-1 data, then executes real GameLoop and normal NMI. The parser cursor and
32-column ring are initialized once; subsequent terrain streams normally.
The fourth pipe is X912..943, top Y144: cap bytes `$10/$11`, shaft `$14/$15`.
The first gap is X1104..1135. Direct source point queries return the correct
solid carry for the real pipe and clear carry for the gap.

The apparent X913→947 roll displacement is accumulated native wall separation,
not a large original movement instruction. The first incorrect native write is:

| Update | State / causal action |
| --- | --- |
| 102 | Source center X905, native X897; C084 physical sole213, C086213, Delta8, native DY0. Original logical anchor is208. |
| 102 | Native feet find ordinary floor `$54`; residue R4=5. `GuestLandingWindow` rejects it because DY0 retains the five-pixel native band. No native side probe ran first. |
| 102 | `RosterGuestFootContactSide` sees two floor feet and chooses R0=2 from X897's low nibble. `SamusStopAtWallBanked`, bank138:`$A2E6`, writes native X897→911. |
| 103 | Original `PpHostImportX`, RAM3:`$B3D6`, imports911+8. Original script RAM3:`$A1EC` adds only2. |
| 104–105 | Left probes now lie inside the real pipe; native separation propagates X913→927→943. |

`trace_prince_fourth_tunnel_1110.py` records the actual source/native writes,
call/return registers, R0..R7, queries and body boxes. The first embedded box
occurs after the incorrect native correction; the tick102 box was still wholly
left of the pipe. No sweep, movement clamp, guard immunity or pipe bypass is
justified by this evidence.

## Preserved proposal and scope

`tools/reference/prince_native_foot_motion_1110.s` is103 bytes at proposed
RAM2:`$D4D7..$D53E`, inside the existing v1-owned padding. It replaces only the
existing four-byte `PpNativeAdder`, RAM3:`$BD3E`, with `JMP $D4D7` plus NOP.

The worker admits a native BG surface only when the physical sole is on page0,
its source logical anchor `(C084 − Delta + 3)` equals the current metatile top
or its already authenticated one-pixel typed-support offset, and at least one
actual native foot (X+2 / X+14) has solid at that top and empty immediately
above. It projects **native BG Y** to that actual surface. Native feet/side
collision still execute afterward. It retains A/X/P, returns Y6/C1, and leaves
R0..R7 and source actor/state RAM2:`C000..C7FF` untouched. It uses existing
source-owned point-query variables/SMC; no new RAM, helper actor or physics
state is allocated. It does not import native Y into original donor physics.

Thirteen direct source-geometry cases pass: static/subphase/exact floor,
typed-cap one-pixel support, logical anchor inside floor (rejected), deep
descending (rejected), rising airborne (rejected), covered floor (rejected),
embedded pipe (rejected), beside-pipe floor, gap (rejected), one-foot lip, and
X page carry. Four controller replays retain third-cap support, original jump
admission, X891/HP5 landing, and the authentic next-update HP5→4 hard-fall debit.
They remove the phantom pipe crossing and remain at X897 until real enemy
contact. **No fourth-pipe crossing or full1-1 completion is qualified.**

This is a RAM-patch CPU proposal. A new ordinary cold load/cookie, native pose
comparison, interrupt/pause/life/scripted-engine coverage and current-hash
Mesen crossing remain required before publication.

Cold canonical packed runtime/metadata grow `[6386,5668]`→`[6386,5732]`: the
fixed45056-byte carrier is64 compressed bytes short. Exact packet overlap
packing preserves all239 decoded geometries but saves only8 compressed bytes,
leaving56 short. Reordering and exhaustive single-dictionary-slot searches do
not fund the rest. The unchanged254-byte actual6502 decoder roundtrips exact
8159/6092/1607-byte runtime/metadata/state images in the optimizer diagnostic.
No larger allocation or new decoder was used.

## Zero-output reproduction and frozen source hashes

Run from the workspace in PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python tools/audit/run_bounded_build_v1.py --output build/prince-postlanding-audit-1110 --resume --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_native_foot_motion_1110.py --direct
```

Omit `--direct` for the four controller replays. Use the same bounded command
with `tools/audit/trace_prince_fourth_tunnel_1110.py` for the unpatched causal
trace, or `tools/audit/prince_lossless_dict_opt_1110.py` for the unchanged-decoder
dictionary search. All diagnostics retain zero files; the empty output root
is absent after completion. Fixtures stay in memory.

| Source | SHA256 |
| --- | --- |
| `tools/reference/prince_native_foot_motion_1110.s` | `98dd9c59e473a3952a7002b634e806bf5f1f5aa9654c54eb9094b5d01104997e` |
| `tools/audit/check_prince_native_foot_motion_1110.py` | `438250e4dd3955e8db70e09adb982e07a143c4fbc9998b2b4063c015fa252eee` |
| `tools/audit/trace_prince_fourth_tunnel_1110.py` | `29d2d2f6a8689235cb373ffa576ade9484e0f88d0e0ca2bc49b0c2931160f789` |
| `tools/audit/check_prince_fourth_route_1110.py` | `b63dba738081bb5ee066b10d98bfdd38529277e03ead742bed55724dacd00e94` |
| `tools/audit/prince_lossless_dict_opt_1110.py` | `c4dcbab0f3380bf442d6842a503e4408b38b5b97eefd90393110c901a899c3b7` |
