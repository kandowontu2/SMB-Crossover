# Prince contact and original-control diagnosis, November 10

Frozen source-only diagnosis on in-memory candidate
`c3fb87bcbab3a9ad2d3537f9444797fee50344c8a08195d8b9b4b02ff309bba3`,
whose combined parent is
`d07012de9762e93ca76cb283ba84e9b8a9a7bd532364fd94ce4ca6101687cb72`.
The funded floor component and its prior proof remain unchanged. No ROM,
Mesen run, receipt, capture, helper or gameplay patch was produced here.

These are explicitly translated CPU scenes using the existing successful
third-cap fixture, actual native fourth-pipe parser data, GameLoop and normal
NMI. Fourth pipe is X912..943/top144; its native cap cells are10/11 and shaft
cells14/15. Scene initialization includes translated player/enemy placement;
observers seed no inventory, stomp, damage, protection or crossing outcome.
Neither fourth-pipe nor full1-1 crossing is qualified.

The separate natural A attempt remains unarmed throughout: source sword
`C6EE=0`, with none of the protected attack actions62/69/74. The historical
strike test supplied sword2 and native enemy box3 explicitly. Actual Goombas
use box9; the current proxy's literal `CMP #3` rejects both the live Goomba and
flattened state4. That difference alone does not justify broadening enemy
eligibility or supplying an unearned sword.

The shared protection audit establishes the complete actual stomp-to-contact
chain:

| Update | Actual event and existing protection |
|---|---|
|90|Player X891/HP5; native `FE:9806 EnemyStomped` defeats slot1 to state4, sets its collision bit, increments StompTimer0→1 at `C2:B91B`, and returns native DY=FC. Normal NMI preserves these values.|
|91|Native Main `FE:8345` decrements StompTimer1→0 before Prince update. Original hardfall `3:A28E` debits exactly one HP5→4. No Prince body-contact callback occurs.|
|91..98|Flattened slot1 still overlaps. GuestBodyContactBridge returns C0; native per-enemy collision-bit suppression skips injury.|
|142|First contact with the other, live Goomba: slot0/X886 versus playerX897. Its own collision bit0→1. StompTimer, InjuryTimer, StarInvincibleTimer, GuestHurtKind, GuestHurtTicks and GuestInvulTicks are all0. `FE:974A ChkETmrs` and `FE:976C InjurePlayer` execute, then `3:BD22`→original defender `2:DADD`. Original unarmed `3:A342` drains HP4→0 inside this one callback.|

The neighbor contact is52 updates after the stomp. Existing timer and per-slot
contact policies work; they grant no remaining protection at that contact.
No grace, immunity, health or donor hardfall change is justified.

Two fixed continuations distinguish original controls. The observer compares
all source bytes outside the oracle's real stack page and returned AXYP at
each actual DecodeInput call with original donor5:839F. Each continuation
passes85 actual calls, including the unchanged successful third climb, and a
separate all256-controller-byte differential at the actual fourth-route state.
Original donor SHA256 is
`5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4`.
This is input-decoder parity, not whole-engine donor parity.

Native SavedJoypad1Bits is copied unchanged to C40A at `3:B3A6` on source
phase2. Original5:83FF..840B decodes Up8→C03C and Down4→C03D; original facing
maps Right1 to forward C03A for the observed facing255. No Up mapping fault is
found.

| Continuation after landing91 | Actual original control result |
|---|---|
|Up only,08|Action17 enters at102; action49 enters at113 with pose109, Down0, action17 and4E4=0. Original5:8ACC..8AE5 selects49 on that Down-release condition. No fourth WorldAlign executes before live-neighbor contact142. Calling49 a roll initiated by Up is unsupported.|
|Up+Right,09|Wall material20 leads original action30 at93 and105, with actual WorldAlign at `2:C40B`, called by original7:F52E. Both inputs use CellX896/Y10; surfaces are206 then208. Action17 is an intermediate recovery at102; action49 is not selected. Standing pose15/mode0 occurs at121, then original wall action32 is selected.|

The original standing-Up branch explains the last distinction:
original7:D7EC requires pose15; D7F3/D7F5 rejects horizontal C040!=0 before
testing Up at D7F7. At121 Up+Right has C040=1 and Up8, so that branch exits.
The successful third climb uses Up alone/C040=0. Releasing Right once the
original standing pose is reached is a causal future controller step, not a
qualified crossing.

The wall observer also verifies actual probes920/936 see the fourth pipe and
return wall20; a descending sweep can report top144. Original32px CellX896
versus native pipe-left912 remains a geometry question. The recorded Align
inputs are insufficient to prove the first incorrect source/native state.
Do not change CellX, clamp donor motion, add a helper, or relax collision based
on these failed controls. No helper placement is proposed or inventoried.

All new sources below are frozen; further changes require derivatives.

| Source | SHA256 |
|---|---|
|`tools/audit/check_prince_natural_attack_1110.py`|`3a7dc79aaad710062c591dc19572a23c11034eba54f9743facdbe736ebb3830f`|
|`tools/audit/trace_prince_fourth_wall_1110.py`|`0a6b48ddf541e60276d538b5c9960c14b07ce9907b069829fb18b5e1d730fb24`|
|`tools/audit/check_prince_stomp_grace_1110.py`|`41503638cb87aa3ff62aa37820127af9d16779b25aa2c10e5c63a75937b65998`|
|`tools/audit/check_prince_up_control_1110.py`|`c5a16cdf6833369c352130946c6949df527442101e6d4fef3ec95be7ab7b35ac`|

Zero-output reproduction: set `PYTHONDONTWRITEBYTECODE=1`, then run each source
through `python -B tools/audit/run_bounded_build_v1.py --output build/TASK
--max-files 1 --timeout 600 -- python -B SOURCE`. Matching TASK names are
`prince-attack-audit-1110`, `prince-fourth-wall-1110`,
`prince-stomp-grace-1110`, and `prince-up-control-1110`. Run the last checker
once without arguments for09 and once with `--pad 8` for08. Each successful
invocation retains zero files and removes its empty reservation directory.
