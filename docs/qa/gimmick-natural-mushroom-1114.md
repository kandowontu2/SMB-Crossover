# Mr Gimmick: natural mushroom, November 14

The controller uses the actual title, roster, Start, native question block,
emerging actor and physical collector on the installed F11 ROM. It writes no
game state and creates no capture files. The original controller is SHA256
`41654ed1dac0e6aacf4905619fb68b18cf806c454e267cd6ae54fcae061671e4`.

Source run 62984 and actual Downloads Mesen run 81769 both reach the physical
mature mushroom, invoke the original GmPickup callback, increase capacity
and refill health from 2 to 3, queue original cue `$45`, erase the actor and
complete 25 further GmMovement calls alive. Cue production is observed;
audible output and the complete item ensemble are not qualified here.

Both runs deliberately **fail the overall acceptance gate**: the six-digit
native score rises from 10 to 110, an award of 100, rather than the expected
1,000. The score assertion has not been weakened. The source receipt is
`2a46abb0650ca89ae94fc242b860df6d784acdb3e5f025c7e7451968dcff5f1e`;
the native receipt is
`ca5c0b4ddbeb8cc66cea62a9b23e07e7ca52dcd4e6afd26832a135cf7bb45708`.

Native observations: birth Main529/frame611 at 336/135; mature
Main593/frame685 at 336/119; actual collector Main672/frame783 at 416/174,
player414/176. Terminal Main698/frame809, player430/176, health/capacity3,
lives2, Star0. Source observations have their own clock and are not labeled
as native timing. Pre/post Downloads hashes and sidecar guards are unchanged.

Inspection identifies the shared native floatey-number digit table at
PRG126 CPU `$89B6`, file1034694. With six score digits, its control6
`DigitModifier[3]=1` adds100. Its source comment and popup control represent
1,000. The same table currently awards10 for a100-point enemy. Any repair
must preserve the following extra-life entry and the existing fixed PCs.
Manual coin/time awards are separate consumers and are not qualified by this
pickup test.

The earlier 40583 run failed metadata setup before gameplay because the
checker used a next-function address from another bank. The test now uses
the actual symbol sizes. That harness failure is not a game defect.
