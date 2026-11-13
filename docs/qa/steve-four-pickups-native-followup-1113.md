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
