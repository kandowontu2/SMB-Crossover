# Current Battletoads timing attribution

This task adds read-only observers, not game instructions or a performance
proposal. Root owns all native runs, ROM files, installation and cleanup.
All producer roots remain absent at
`build/battletoads-carry-attribution-1115 --max-files 1 --timeout 600`;
every source run produces zero files. Frozen2c1/93af/C/F and their assertions
are untouched. No authentication check, audio, input, timer, actor, map,
physics, CHR or helper is changed.

## Native evidence that motivated the observer

Root74702 actual ACE profile **PASS**, receipt
`07f374ae854702a6f413c098cb32d162557c0bccd13ecacebf33da7e66809c0a`.
It reproduces19 missed-read frames among47 complete idle frames and15/32
Right. Representative normal Main is25004 exclusive+3523 interrupt cycles
idle,24930+3496 Right; catch-up Main is16729+120 and16999+120 respectively.
Regular NMI idle29 calls total149141 exclusive, range4299..6876; Right17
calls total87471 exclusive, range4298..6408. Busy NMI19/16 calls spans
2740..3403/3376; hardware IRQ is120 cycles. All160 getters return. Wf and
BtCheck each have206 returns (idle125,Right81), with Wf419 including Bt325.
There is no HuResolve call in the measured phases. Therefore three checks
per complete physical/catch-up Main is not a valid assumption. Aggregate
Main averages hide the normal/catch-up distinction.

## Frozen source interfaces

| File | SHA-256 |
| --- | --- |
|`replay_battletoads_carry_attribution_1115.py`|`295354c0371cedac5ca78922324888e287e96b43f117a64d8430284a3396dfc4`|
|`check_battletoads_carry_attribution_1115.py`|`11da80f9e75d1a255777d550a55162f18c917cdaf707d01e143a34dc96ff0cd1`|
|`replay_battletoads_attribution_7fb_1115.py`|`fa3d4dbc85517e38a9af7ef1b4f18d546bf7e8f91c7cc73fb724b81a90df5508`|
|`check_battletoads_attribution_7fb_1115.py`|`5a406331e85d6da6b39e54d925dff65179c2184e954645e1ecb9708eee4c8191`|

The ACE factory accepts only
`aceedaf2151fdf673b489a742831a0844abbb3837e0bcba68408d3ba5c3a4cfe`.
Its exact LF Lua is
`b920e93a73317fcb9e250922b1bbd61785823858453251e9e2b63d4a0476882c`.
The current7fb factory accepts only
`7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0`.
Its exact LF Lua is
`6b3371c8111759feda51a57fa8b37cbd23e5ac1717b8acc7945048d3fab73709`.
Both expose `controller(raw)`, `config(raw)`, `metadata(raw)` and
`load_current_image()`. Their observer body SHA is identical:
`43a0c070bab7c90e4c8714e7934c34cb6ee2f73deb56dda701af2ead38f4445a`.

The7fb facade calls only the strict portable
`compose_prince_hidden_point67_ace_1115.inverse` (source SHA
`1fce2b546003860e31da49723c3ac185a25b5420e2ba88143434516c59a4ee27`)
to recover ACE for bindings. All actual7fb CPU bytes are retained. All PRG
outside the Prince cookie, entire BT8192 cache, published BT header and all
timing preimages are exact. Current ROM pin and actual hook-bank hashes are
refreshed. The frozen ACE factory still rejects7fb; no old API is widened.

## Observed spans and accounting

The same48 completed idle/32 Right Main controls and literal-read/budget
observation remain. The2c1 Main/IRQ/NMI/software-RTI logic remains unchanged.
Each Main is classified by its actual mapped BtCheck, BtDraw and whole-render
entry counts: for example `checks3/BTdraw1/render1` versus
`checks2/BTdraw0/render0`. These are observations, not assumed schedules.
Class rows retain entry/exit frame, SP, NmiDisable and NmiSkipped. Between-Main
time records wall and completed outer-ISR contribution separately; its first
measured Main has no preceding measured gap.

Additional actual points are:

| Function | Actual mapping |
| --- | --- |
|AudioUpdate|PRG127:F05D|
|DrawAllMetasprites|PRG4:A000|
|MetaspriteRenderLoop|PRG4:A5BA|
|BlockBufferColli_Head/Side|PRG126:9587/958B|
|BtMovement|RAM3:AE67|
|BtGraphics|RAM3:B01D|
|BtDraw|RAM3:B0ED|
|Original BtPhysicsStep|RAM3:A094|

The original step binds the actual current BtCoreStep:AED2 JMP bytes
`8ef8be4c94a0`, rather than trusting its virtual donor segment. Every callback
authenticates its actual physical mapping and current opcode bytes. A RAM3
point cannot be admitted as a same-address ROM or other-owner alias.

Function timing ends at the actual stack-derived caller PC/SP return,
including RTS and excluding the caller's JSR. Main function spans subtract
completed outer hardware IRQ/NMI spans. AudioUpdate is tagged by the actual
active regular/busy-NMI frame and subtracts that frame's completed child ISR
time. Audio nested inside NMI and source/render spans nested inside Main
overlap: do not add their inclusive costs together. There are at most32 output
sparse rows and32 additional aggregate groups; the prior18-group bound remains.
The final output replaces the prior sparse row list with these classified
rows, leaving all prior aggregate timings intact. No full state/PPU dump or
capture is produced.

## Terminal source gates

ACE strict16652 **PASS**, receipt
`d7c3dc2fceb7c5bc25a068758c14674e8eb1b9305a2bbdea30f477e654b1946d`:
LF compilation, exact current code/step bindings, dirty/wrong input rejection
and no mutable Nightly rereads pass.

ACE callback99507 **PASS**, receipt
`29dac32869d757afa30f0f40ea3b94c48c2b7728e71b614a8647929ffdc109dc`.
The actual compiled Rash constructor/current ACE model executes ordinary
controls. All1120 additional function entries return:80 each movement,
original step, graphics, draw, whole render, metasprite render and AudioUpdate;
head240/side320. Prior160 getters and240 each Wf/BtCheck also acknowledge.
There are28 rows, no pending Main/ISR/getter/service/attribution spans, and
48/32 source Main classify as three-check/full-render. This source scheduler
alone does not reproduce natural hardware catch-up.

ACE actual-vector fixture25197 **PASS**, receipt
`40ce494b1cf08a71fc91d0e4c3a670eaf4a5290ea817266e0d6aec96d10af524`.
It injects one real hardware IRQ during NMI AudioUpdate and one real busy NMI
at a reached source-step instruction; no gameplay flag/state is seeded.
The freshly vectored first instruction is observed before executing it.
Nested IRQ120 is subtracted once from AudioUpdate. The busy NMI executes
AudioUpdate and naturally produces one source two-check/no-draw catch-up Main.
All actual entries return and pending counts remain zero. The source classes
are idle47 full/one catch-up plus32 full Right. This is an explicit vector
fixture, not a natural physical cadence or FPS result.

During this work root delivered Prince7fb and97939 actual Downloads full+Star
repeats passed. Already loaded ACE jobs remain versioned. The first7fb checker
invocation stopped on a Python spacing typo before input load; it was corrected
before qualification, with no observer or game semantics changed.

Current7fb strict97281 **PASS**, receipt
`52530b6314595d52df178ca61df19e09192f35b8765dbec3f2eec29d51262280`:
exact original body, actual code/cache transfer, fresh current hook bank
hashes, LF compilation, dirty/wrong input rejection and zero mutable rereads.
Root explicitly requested no duplicate full7fb callback run. Prior ACE
ordinary/vector pairing proofs and code/body equality transfer the observer
safety; current native return pairing and budget remain root's next test.

All helper source jobs are terminal. No performance patch, funding assumption,
header-check unroll, allocation, mounted image, native helper or delivery is
introduced. Attribution of the biggest concrete native cost precedes any
further optimization proposal.
