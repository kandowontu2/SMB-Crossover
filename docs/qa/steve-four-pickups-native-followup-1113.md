# Steve four-stock-pickup follow-up

The public ROM remains62ba7f54. No ROM, item physics, actor state, helper or
collection criterion changed in this investigation.

The original controller1869b7a8 passed its2027-update native Main/NMI CPU
replay, including exact direct-route input/state streams. Its actual Mesen
run nevertheless failed after3966 physical frames/1819 updates/1935
projections. Three items had been collected and all four prepared; the last
assertion expected a granted Star timer/music after its actor disappeared.
Terminal X1320/Y176,HP6/lives2 differs from the earlier earned1UP/lives3.
Receipt SHA256:
`6604e233bb94995e6b0a7304c7ade402dbc3f0671c30b98b359bed66a78dad79`.
Death/checkpoint restart erasing the actor is a plausible explanation, not
yet a proven event or a proven Star implementation defect.

The separate read-only derivative
`tools/audit/replay_steve_all_pickups_guarded_1113.py` keeps1869 frozen. Its
default controls are unchanged. It adds life-write, injury and KillPlayer
observations, life invariants during item phases, and the tracked actor's
last position. No unexpected death may be mistaken for collection. Its
observation-only Lua SHA256 is
`12a564889e94ec6533c4e79d03bc8a6f88f18896357a2e76fb6e7d656f769282`;
CPU binding SHA256:
`9a666563798e74e7ffdd75495382365601e3c8819df4e1dd29e6a0749c0263b7`.

That derivative passes2027 CPU Main/NMI updates on exact public62, through
actual cold/menu ingress167. All four preparations and collections occur in
dynamic slot5, kinds0/3/1/2. The1UP grants lives2→3 once at projection1257.
Native injury occurs while collecting the second Alpha at1506 and chasing
the Star at1940; no life is lost. The Star is actually collected at
actorX1701/Y163,playerX1689/Y176. After24 further updates: X1693/Y176,
HP4/lives3,pattern5,StarTimer34, all mounted-runtime identities authenticated,
60 matched sprite DMA observations. This is a CPU result, not a new Mesen pass.

The experimental `--defend` branch stops to punch nearby enemies. It is a
frozen negative, not the default or a qualified replay. Its180-update chase
horizon failed with all three lives/HP6 (Lua3cb8a705). Extending that controller
horizon to600 also failed (Lua9fbc1bc9):250 defensive updates let the Star
get ahead, terminalplayerX2030 versus StarX2136/Y99. The change therefore did
not solve the replay and was not represented as gameplay progress. No item
collection assertion was weakened. Both failed variants wrote zero ROM/state
bytes and created no output files.

The next physical run must use the observation-only derivative to establish
the actual life/death sequence before choosing controls or considering a game
repair. The existing25GB free-space guard currently prevents that run; the
guard was not reduced. Previous public62 native full1-1 and two-Alpha checks
remain valid in their recorded scope.

## Physical observation after disk space was freed

The actual Downloads12a observation-only replay now establishes the failure:
Steve dies before collecting the Star. At3795 physical frames/1934 projections,
the guard catches the life decrement before it is mistaken for item erasure.
There are real injuries at X1212 during the second Alpha approach and X1520
during traversal; KillPlayer then runs at X1618/HP0 against a grounded Koopa
while the mature Star is still alive at X1637/Y81. All three previous native
collections remain verified. The actual RMW bus trace includes old/new writes
2/3 for INC and3/2 for DEC; these are not extra life grants. Receipt SHA256
`15b9dde8fda5003776fb896e7074dc2c0c02b3d6bb36129c1780f69bbdcc1e51`.
No Star implementation defect is demonstrated by this run.

A controls-only `--clear-star-path` experiment punches the two approach
Goombas before releasing the Star. Both native defeats and scores occur at
projections1790/1838,HP4/lives3. It still fails: Koopa contact at X1619 and
later Goomba contact at X1771 exhaust health before the ground chase can
collect the Star. The Star remains active at X1789/Y149. Lua SHA256
`cb16d9c4f9b0bcfacdecde6a3a813ed173d1e9a7152fb496eaf354ecda5b4609`,
receipt`2bb01dcdddf37db3be50e364c42edfd73ab1b32940d249ef34d20f53c88ea0b7`.
This is retained as a failed controller experiment, not a ROM change or a
powerup pass. Both runs retained the shared emulator queue and capture
watchdog and wrote zero capture files.

Two later normal-A jump attempts, Lua8be319eb and1d585c40, produce exactly the
same2bb01dcd native failure receipt as the approach-punch experiment. They do
not establish a successful jump or Star pickup and remain experimental. The
current `--clear-star-path` option retains the last failed attempt for further
diagnosis. The default observation-only12a controller remains unchanged.
