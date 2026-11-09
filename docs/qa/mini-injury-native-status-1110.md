# Mini Mario powered injury status

The CPU injury fixture starts with the authenticated Mini actor, native `PlayerStatus=1`, and no injury immunity. It calls the actual `ForceInjury` at physical PRG126 `$9771`. The native call through physical PRG78 `$B990` returns carry clear and `A=$29`. The `STA PlayerStatus` at physical PRG126 `$97A4` consequently stores 41 in `$075B`.

This is preexisting behavior. The strict offscreen comparison and the post-scroll repair both enter engine 10 with timer `$FF`, preserve the same status value and complete all 39 injury movement updates with both lives. The helper repair changes only native lift admission after scroll. Powered damage tier and subsequent powerup behavior need separate qualification.

The exact CPU fixture and bound receipt are `tools/audit/check_mini_helper_injury_irq_1110.py` and `build/mini-helper-injury-1110/irq.json`. This is a CPU observation. The fixture uses native injury, normal NMI and GameLoop, with held Right supplied at the controller read boundary.
