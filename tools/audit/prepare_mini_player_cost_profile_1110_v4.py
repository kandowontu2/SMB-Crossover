"""Measure the native player path inside one controller-reached Mini update."""
from pathlib import Path
import prepare_mini_actor_cost_profile_1110_v3 as calls
import profile_mini_busy_1108_v1 as symbols


def prepare(output, rom, source, refs, **kwargs):
    bundle = symbols.bundle(rom.read_bytes())
    names = ('GameRoutines', 'PlayerCtrlRoutine', 'PlayerMovementSubs',
             'MegaManCollisionBox', 'VvScrollBridge', 'ScrollHandler',
             'GetPlayerOffscreenBits', 'RelativePlayerPosition',
             'LmBoundingBoxGate', 'SamusAfterBGCollisionBridge',
             'RyuSourceBodyAfterBGBridge', 'MegaManCheckPit')
    rows = []
    for name in names:
        pc = symbols.address(bundle, name)
        bank = (symbols.location(bundle, name)-16)//8192
        rows.append(f'MiniProfileHooks["{name}"]={{{pc},{bank}}}')
    anchor = '-- This observer is appended to the controller so it can share its phase and'
    assert source.count(anchor) == 1
    source = source.replace(anchor, '\n'.join(rows)+'\n'+anchor)
    calls.prepare(output, rom, source, {*refs, Path(__file__)}, **kwargs)


if __name__ == '__main__':
    calls.actors.profile.prepare = prepare
    calls.actors.profile.main()
