"""Profile actual DK Jr GameLoop before and against the opening native pipe."""
from collections import Counter
from pathlib import Path
import json

import prepare_dkjr_current_route_1110_v1 as R

I, N = R.I, R.I.N


def main():
    raw, _, cookie, _ = R.pinned_inputs()
    b = I.SYMBOLS.bundle()
    b['raw'] = raw
    labels = json.loads(R.V.LAYOUT.read_text())['labels']
    hooks = {(2 if labels[name] >= 0xc000 else 3, labels[name]): name for name in [
        'DkNativeMain', 'DkjrNativePhase', 'DkjrNativeShiftCamera', 'DkjrNativeTerrainHook',
        'DkjrNativeWorldBuild', 'DkjrNativeRefreshPlatforms', 'DkjrNativeCarryEvent',
        'DkjrNativeSourcePhase', 'DkjrNativePublishAnchor']}
    hooks.update({(193, 0xaee2): 'CoCheckCode', (254, 0x958b): 'NativeSide'})
    N.Bus = I.C.C.C.C.V.ControllerBus
    m = N.fresh(b)
    N.put(m, CrossoverMenuIndex=27)
    for name in ['MenuResolveCharacter', 'QueueSelection', 'DrawSelectionPreview']:
        N.invoke(m, name)
    assert N.get(m, 'SelectedCharacter') == 28
    N.put(m, CrossoverMenuButtons=0, SavedJoypad1Bits=32, SavedJoypad2Bits=0, VRAM_Buffer1_Offset=0)
    N.invoke(m, 'CrossoverMenuInput')
    assert N.get(m, 'SelectedCharacter') == 40
    N.put(m, CrossoverMenuButtons=0, SavedJoypad1Bits=16, VRAM_Buffer1_Offset=0)
    start = N.invoke(m, 'CrossoverMenuInput')
    N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue', a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(m, 'PauseRoutine', a=0)

    active = None
    terminal = None
    last_command = None
    cpu = N.NesMPU
    profiles = {label: dict(calls=Counter(), banks=Counter(), pcs=Counter(), game=[], nmi=[])
                for label in ['idle', 'open_walk', 'wall']}

    class Trace(cpu):
        def step(self):
            pc, start = self.pc, self.processorCycles
            tag = m.rawtags[(pc - 0x8000) // 8192] if pc >= 0x8000 else -1
            if (tag, pc) == (3, 0xb46d) and m.ram[2][0x8e8] > m.ram[2][0x8e9]:
                left = m.ram[2][0x8de] + 256*m.ram[2][0x8df]
                right = m.ram[2][0x8e0] + 256*m.ram[2][0x8e1]
                if 64 < (right - left) & 0xffff:
                    raise AssertionError(('Actual source horizontal scan escapes its width bound',
                        hex(pc), tag, start, left, right, list(m.ram[2][0x8db:0x8f0])))
            if not active:
                return super().step()
            if (tag, pc) in hooks:
                active['calls'][hooks[tag, pc]] += 1
            result = super().step()
            cost = self.processorCycles - start
            active['banks'][str(tag)] += cost
            active['pcs'][f'{tag}:{pc:04x}'] += cost
            return result

    def tick(keys, label=None):
        nonlocal active, last_command
        m.controller_pad = keys
        N.put(m, SavedJoypadBits=keys, SavedJoypad1Bits=keys, SavedJoypad2Bits=0,
              A_B_Buttons=keys & 192, Left_Right_Buttons=keys & 3, Up_Down_Buttons=keys & 12,
              NmiDisable=255)
        active = profiles[label] if label else None
        last_command = dict(keys=keys, pre=state())
        z = N.invoke(m, 'GameLoop')
        if active:
            active['game'].append(z['CPU'])
        active = None
        N.consume(m)
        I.C.clear(m)

    def world(low, high):
        return N.get(m, low) + 256*N.get(m, high)

    def state():
        return dict(x=world('Player_X_Position', 'Player_PageLoc'), y=N.get(m, 'Player_Y_Position'),
                    camera=world('ScreenLeft_X_Pos', 'ScreenLeft_PageLoc'),
                    source_x=m.ram[2][0x00], source_y=m.ram[2][0x01],
                    source_state=m.ram[2][0x6b], ready=m.ram[2][0x8fe],
                    native_state=N.get(m, 'Player_State'), engine=N.get(m, 'GameEngineSubroutine'),
                    lives=N.get(m, 'NumberofLives'))

    N.NesMPU = Trace
    try:
        for setup in range(650):
            if N.get(m, 'OperMode_Task') == 3 and N.get(m, 'GameEngineSubroutine') == 8 and m.ram[2][0x8fe] == 2:
                break
            tick(0)
        else:
            raise AssertionError(('Cold GameLoop bound', state()))
        assert all(bytes(m.ram[k][0x1fe0:0x1ff0]) == cookie for k in [2, 3])
        for _ in range(12):
            tick(0, 'idle')
        for _ in range(12):
            tick(1, 'open_walk')
        jumps, held_until, next_jump, pipe_hop = [], -1, 0, False
        wall_first, wall_last = None, None
        for age in range(1250):
            s = state()
            x = s['x']
            if s['lives'] != 2 or s['engine'] == 11 or s['source_state'] == 5:
                break
            near = []
            for slot in range(6):
                if (0 < N.get(m, 'Enemy_Flag', slot) < 128 and N.get(m, 'Enemy_ID', slot) == 6 and
                        not N.get(m, 'Enemy_State', slot) & 32 and N.get(m, 'Enemy_Y_Position', slot) >= 172):
                    wx = N.get(m, 'Enemy_X_Position', slot) + 256*N.get(m, 'Enemy_PageLoc', slot)
                    if 8 <= wx-x <= 30:
                        near.append(wx)
            if s['source_state'] == 1 and s['native_state'] == 0 and age >= next_jump:
                if x < 424 and near or (424 <= x < 448 and s['y'] == 176 and not pipe_hop):
                    pipe_hop = x >= 424
                    held_until, next_jump = age + 8, age + 47
                    jumps.append(dict(age=age, enemy=min(near) if near else None, **s))
            label = 'wall' if 430 <= x < 448 and pipe_hop and age > next_jump else None
            if label and not wall_first:
                wall_first = s
            if label:
                wall_last = s
            tick(1 | (128 if age < held_until else 8 if pipe_hop else 0), label)
            if len(profiles['wall']['game']) >= 24:
                break
    except AssertionError as error:
        terminal = dict(error=str(error), last_command=last_command, maps=m.rawtags[:])
    finally:
        N.NesMPU = cpu

    summary = {}
    for label, values in profiles.items():
        cycle = values['game']
        summary[label] = dict(updates=len(cycle), mean_CPU=sum(cycle)/len(cycle) if cycle else None,
                              max_CPU=max(cycle) if cycle else None, banks=values['banks'].most_common(),
                              hot_PCs=values['pcs'].most_common(18), calls=values['calls'])
    output = dict(passed=bool(wall_last), ROM_written=False, memory_only_SHA256=R.PIN, setup_frames=setup,
                  final=state(), terminal=terminal, wall_first=wall_first, wall_last=wall_last, jumps=jumps, profiles=summary,
                  scope='Real menu selection, parser, source controls and GameLoop with hardware-style CPU-side controller input. No level/actor/health seed. Not Mesen cadence.')
    (R.OUT/'wall-profile.json').write_text(json.dumps(output, indent=2) + '\n')
    print('Natural GameLoop wall', output['passed'], state(), [(k, v['updates'], v['mean_CPU']) for k,v in summary.items()], flush=True)


if __name__ == '__main__':
    main()
