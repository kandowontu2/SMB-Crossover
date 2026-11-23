"""Private carry priority trial using the Prince's existing lift allocation."""

from types import SimpleNamespace

import compose_prince_oneup_lift_1123 as Cold

Lift = Cold.Lift


def plan(raw):
    source = Lift.F.ASM
    once = Lift.F.Q.P.G.First.once
    source = once(source, 'Material:\n jsr $bde2\n bne MaterialDone\n php',
                  'Material:\n php')
    source = once(source, ' plp\nMaterialDone:\n rts\nSupport:',
                  ' plp\n jsr $bde2\n rts\nSupport:')
    # Existing Support already requires the authenticated lift, native
    # carrier flag, exact player plane and stock grounded state. Give that
    # surface priority before the original query sees the floor below it.
    fixture = SimpleNamespace(**dict(vars(Lift.F), ASM=source))
    replan = Lift.F.Q.P.clone(Lift.plan, dict(F=fixture))
    return replan(raw)


def compose(raw):
    return Cold.compose(raw, plan)
