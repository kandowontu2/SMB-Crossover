"""Add a passive NMI timing observer to a fresh exact-source Fighter route.

No existing packet or helper is modified. Original route assertions, controller,
bounded capture driver and failure endpoint remain in place.
"""
from pathlib import Path
import argparse
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import current_smb2_ff_route_1030_v1 as B


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--source-handoff', type=Path, required=True)
    p.add_argument('--expected-source-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.identity, a.mode, a.frames = 'ff-fighter', 'easy', 8000
    B.prepare(a)
    out = a.output.resolve()
    ready = json.loads((out / 'ready.json').read_text(encoding='utf-8'))
    raw, syms, address, location, hook = B.C.linked(a.rom.resolve())
    names = ['NonMaskableInterrupt', 'SamusFreezeUpdateScreen',
             'PnHudPreUpdateScreen', 'PnPaletteScreenUpdate',
             'SamusFreezeFlushPalette', 'BankSwitchCHR',
             'OAMandReadJoypad', 'PostDmaMaskEnable', 'UpdateScreen',
             'FastNmiPaletteCapture', 'FastNmiPaletteScrollRestore']
    hooks = []
    for name in names:
        assert name in syms, name
        hooks.append(hook(name))
    end = hook('NonMaskableInterrupt', tail=True)
    end['name'] = 'NMI-return'
    hooks.append(end)
    ram = {n: address(n) for n in [
        'SelectedCharacter', 'OperMode', 'OperMode_Task',
        'GameEngineSubroutine', 'Player_X_Position', 'Player_PageLoc',
        'DisableScreenFlag', 'NmiDisable', 'VRAM_Buffer_AddrCtrl',
        'VRAM_Buffer1_Offset', 'VRAM_Buffer1', 'SmFreezePalettePending',
        'SmFreezeLastBlue',
    ]}
    observer = R / 'tools/audit/ff_nmi_budget_observer_1030_v1.lua'
    run = out / 'run.lua'
    text = run.read_text(encoding='utf-8')
    anchor = 'dofile(' + B.C.lua(B.C.SCRIPT.as_posix()) + ')'
    assert text.count(anchor) == 1
    addition = 'FF_NMI_PROFILE=' + B.C.lua(dict(ram=ram, hooks=hooks)) + '\n'
    addition += 'dofile(' + B.C.lua(observer.as_posix()) + ')\n'
    run.write_text(text.replace(anchor, addition + anchor), encoding='utf-8')
    deps = {str(run): B.C.sha(run), str(observer): B.C.sha(observer),
            str(Path(__file__).resolve()): B.C.sha(__file__)}
    ready['bindings'].update(deps)
    ready['passive_NMI_profile'] = dict(hooks=hooks, ram=ram,
                                       original_assertions_unchanged=True)
    (out / 'ready.json').write_text(json.dumps(ready, indent=2) + '\n', encoding='utf-8')
    packet = out / 'native-packet.json'
    h = json.loads(packet.read_text(encoding='utf-8'))
    h['bindings'].update(deps)
    h['ready_sha256'] = B.C.sha(out / 'ready.json')
    h['passive_NMI_profile'] = True
    packet.write_text(json.dumps(h, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(prepared=str(packet), sha256=B.C.sha(packet),
                          launched=False, original_assertions_unchanged=True)))


if __name__ == '__main__':
    main()
