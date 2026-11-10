"""Print one current-ROM CPU controller route; write no receipts or ROMs.

The fixture starts in the established cold native menu arena. After genuine
Select/Start, only the controller peripheral and normal-NMI scheduler change.
Actual GameLoop, 1-1 parsing, item production and FF callbacks execute intact.
This is CPU-model evidence, not Mesen or hardware/cadence qualification.
"""
from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools'), str(R / 'tools/audit')]
import check_hogan_current_bounded_v1 as N
import assess_dkjr_menu_current_1103_v11 as UI
import audit_current_menu_indicators_1102_v1 as Symbols
from check_tmnt_render_oa import address, location

ROM = R / 'build/complete-roster-native-1110/candidate.nes'
PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'


class ControllerBus(N.Bus):
    def __getitem__(self, at):
        if isinstance(at, int) and at in (0x4016, 0x4017):
            port = at - 0x4016
            index = getattr(self, 'serial_index', [0, 0])
            value = ((getattr(self, 'controller_pad', 0) >> (7-index[port])) & 1
                     if port == 0 and index[port] < 8 else 0)
            index[port] += 1
            self.serial_index = index
            return value
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if isinstance(at, int) and at == 0x4016 and value & 1:
            self.serial_index = [0, 0]
        return super().__setitem__(at, value)


def clear_logs(m):
    for name in ('writes', 'ram_writes', 'ppu_log', 'blocked'):
        getattr(m, name).clear()


def run():
    raw = ROM.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    b = Symbols.bundle()
    b['raw'] = raw
    original_bus = N.Bus
    N.Bus = ControllerBus
    try:
        m = UI.seed(b, 21)
    finally:
        N.Bus = original_bus
    assert N.get(m, 'SelectedCharacter') == 22 and N.get(m, 'FfVariant') == 0
    UI.key(m, 32)
    assert N.get(m, 'FfVariant') == 1
    menu_name = UI.menu_name(m)[0]
    assert menu_name == 'FF WHITE MAGE', menu_name
    start = UI.key(m, 16)
    assert N.get(m, 'CrossoverMenuState') == 0
    N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(m, 'PauseRoutine', a=0)

    idle = address(b, 'IdleLoop')
    loop = address(b, 'GameLoop')
    assert bytes(m[idle+9:idle+12]) == b'\x20' + loop.to_bytes(2, 'little')
    native = {}
    for name in ('PowerUpObjHandler', 'NrPickupCollision', 'HandlePowerUpCollision',
                 'FwHostCollect', 'KillPlayer', 'PlayerBGCollision'):
        if name in b['syms']:
            native[((location(b, name)-16)//8192 | 128, address(b, name))] = name
    native.update({(3, 0xbb60): 'FfHostCollect', (3, 0xad65): 'FfPickup',
                   (3, 0xbc1d): 'FfHostBeginFreeze', (3, 0xbc40): 'FfHostPowerupTick',
                   (3, 0xaabc): 'FfMovement'})
    hits = Counter()
    trace = deque(maxlen=24)
    freeze, collected, cold, recovered = None, None, None, None
    pending_collect = None
    pending_tick = None
    ticks = []
    items = []
    jump_start = -100
    opening = 'approach'
    updates = 0
    active_updates = 0

    def state():
        return dict(epoch=epoch, x=N.get(m, 'Player_X_Position') + 256*N.get(m, 'Player_PageLoc'),
                    y=N.get(m, 'Player_Y_Position'), state=N.get(m, 'Player_State'),
                    engine=N.get(m, 'GameEngineSubroutine'), lives=N.get(m, 'NumberofLives'),
                    power=m[0x5fc5], earned=m[0x5fc6], heal=m[0x5fc7],
                    active=N.get(m, 'GuestPowerupActive'), age=N.get(m, 'GuestPowerupAge'),
                    timer=N.get(m, 'TimerControl'))

    def actors():
        return [dict(slot=i, flag=N.get(m, 'Enemy_Flag', i), id=N.get(m, 'Enemy_ID', i),
                     state=N.get(m, 'Enemy_State', i), kind=N.get(m, 'PowerUpType', i),
                     x=N.get(m, 'Enemy_X_Position', i) + 256*N.get(m, 'Enemy_PageLoc', i),
                     y=N.get(m, 'Enemy_Y_Position', i)) for i in range(6)]

    def observe(c):
        nonlocal freeze, collected, pending_collect, pending_tick
        if pending_tick and (c.pc, c.sp) == pending_tick:
            ticks[-1]['returned'] = state()
            pending_tick = None
        if pending_collect and (c.pc, c.sp) == pending_collect:
            if N.get(m, 'GuestPowerupActive'):
                collected = dict(**state(), carry=bool(c.p & 1),
                                 sound=N.get(m, 'Square2SoundQueue'),
                                 erased_flag=N.get(m, 'Enemy_Flag', collect_slot),
                                 floaty=N.get(m, 'FloateyNum_Control', collect_slot))
            pending_collect = None
        if c.pc < 0x8000:
            return
        point = (m.rawtags[(c.pc-0x8000)//8192], c.pc)
        label = native.get(point)
        if not label:
            return
        hits[label] += 1
        if label == 'KillPlayer':
            raise AssertionError(('native KillPlayer', state(), actors()))
        if label == 'FfHostCollect':
            pending_collect = (m[0x100+((c.sp+1)&255)] +
                               256*m[0x100+((c.sp+2)&255)] + 1, c.sp+2)
        elif label == 'FfHostBeginFreeze':
            assert freeze is None, ('duplicate freeze', state())
            freeze = dict(**state(), actor=actors()[collect_slot])
        elif label == 'FfHostPowerupTick' and N.get(m, 'GuestPowerupActive'):
            ticks.append(state())
            pending_tick = (m[0x100+((c.sp+1)&255)] +
                            256*m[0x100+((c.sp+2)&255)] + 1, c.sp+2)

    try:
        for epoch in range(1800):
            current = state()
            ready = (N.get(m, 'OperMode'), N.get(m, 'OperMode_Task'), current['engine']) == (1, 3, 8)
            pad = 0
            if ready:
                assert N.get(m, 'SelectedCharacter') == 22 and N.get(m, 'FfVariant') == 1
                assert N.get(m, 'CheatInvincible') == N.get(m, 'CheatStartLevel') == 0
                assert current['lives'] == 2
                assert (N.get(m, 'WorldNumber'), N.get(m, 'LevelNumber'), N.get(m, 'AreaAddrsLOffset')) == (0, 0, 5)
                if cold is None:
                    cold = current
                    assert current['x'] == 40 and current['power'] == current['heal'] == 0
                    assert any(m[address(b, 'Block_Buffer_1'):address(b, 'Block_Buffer_1')+416])
                    print(json.dumps(dict(event='active_1_1', state=current)), flush=True)
                active_updates += 1
                if collected:
                    assert (current['power'], current['earned'], current['heal']) == (1, 1, 1), current
                    assert not current['active'] and not current['timer']
                    recovered = recovered or current
                    pad = 1
                    if current['x'] >= recovered['x'] + 16:
                        break
                else:
                    item = next((a for a in actors() if a['flag'] == 1 and a['id'] == 46), None)
                    if item:
                        if not items:
                            items.append(dict(player=current, actor=item))
                            print(json.dumps(dict(event='natural_item', item=items[-1])), flush=True)
                        gap = item['x']-current['x']
                        if abs(gap) < 20 and item['y'] < current['y']-16 and current['state'] == 0 and updates-jump_start > 45:
                            jump_start = updates
                        pad = int(gap > 3) | (2 if gap < -3 else 0) | (128 if updates-jump_start < 23 else 0)
                    elif opening != 'clear':
                        near = any(a['flag'] == 1 and a['id'] == 6 and a['state'] < 32 and
                                   20 <= a['x']-current['x'] <= 40 for a in actors())
                        if opening == 'approach' and near and current['state'] == 0:
                            jump_start = updates
                            opening = 'hop'
                        if opening == 'hop':
                            pad = int(current['x'] < 300) | (128 if updates-jump_start < 23 else 0)
                            if updates-jump_start > 10 and current['state'] == 0 and current['y'] == 176:
                                opening = 'clear'
                        else:
                            pad = 1
                    else:
                        gap = 330-current['x']
                        if abs(gap) > 2:
                            pad = 1 if gap > 0 else 2
                        elif current['state'] == 0 and updates-jump_start > 45:
                            jump_start = updates
                        pad |= 128 if updates-jump_start < 23 else 0
                updates += 1
            collect_slot = next((a['slot'] for a in actors() if a['flag'] == 1 and a['id'] == 46), 5)
            m.controller_pad = pad
            clear_logs(m)
            N.consume(m)
            c = N.NesMPU(memory=m, pc=idle)
            c.sp, c.p = 255, 0x31
            c.stPushWord(0xe33b)
            for instruction in range(250000):
                if (c.pc, c.sp) == (idle+12, 252):
                    break
                observe(c)
                assert m[c.pc], ('BRK', epoch, hex(c.pc), m.rawtags)
                c.step()
            else:
                raise AssertionError(('instruction bound', epoch, hex(c.pc)))
            after = state()
            trace.append(dict(input=pad, **after))
            if epoch % 100 == 0:
                print(json.dumps(dict(event='progress', **after)), flush=True)
            assert not m.blocked
        else:
            raise AssertionError(('controller bound', state(), actors()))
        assert cold and items and freeze and collected and recovered
        assert items[0]['actor']['kind'] == 0
        assert collected['carry'] and collected['sound'] == 0x20 and collected['erased_flag'] == 0 and collected['floaty'] == 6
        assert len(ticks) == 60 and [s['age'] for s in ticks] == list(range(60))
        assert all(s['engine'] == 9 and s['active'] == 1 for s in ticks)
        assert all(s['returned']['engine'] == 9 and s['returned']['active'] == 1 and
                   s['returned']['timer'] == 255 for s in ticks[:-1])
        assert (ticks[-1]['returned']['engine'], ticks[-1]['returned']['active'],
                ticks[-1]['returned']['timer'], ticks[-1]['returned']['age']) == (8, 0, 0, 60)
        assert (state()['power'], state()['earned'], state()['heal']) == (1, 1, 1)
        assert hits['PlayerBGCollision'] == hits['FfMovement'] > 100
        assert list(m.vram[0x3f11:0x3f14]) == [0x16, 0x30, 0x36]
        assert any(m[0x200+4*i] < 240 for i in range(64))
        assert sha256(ROM.read_bytes()).hexdigest() == PIN
        return dict(passed=True, ROM_sha256=PIN, CPU_controller_only=True, Mesen_run=False,
                    stage='1-1', class_name='White Mage', cold_menu=menu_name, cold=cold,
                    item=items[0], collected=collected, transformation_ticks=len(ticks),
                    first_tick=ticks[0], last_tick=ticks[-1], recovered=recovered,
                    terminal=state(), calls=dict(hits),
                    PPU_palette_P0=list(m.vram[0x3f11:0x3f14]),
                    OAM_shadow_visible_records=sum(m[0x200+4*i] < 240 for i in range(64)),
                    scope='Actual current GameLoop/native parser/controller pickup and FF recovery; no scripted gameplay state/terrain/actor writes. Logical normal NMI scheduling; not physical frame timing or Mesen graphics qualification.')
    except Exception:
        print(json.dumps(dict(passed=False, ROM_sha256=PIN, CPU_only=True,
                              calls=dict(hits), freeze=freeze, collected=collected,
                              ticks=len(ticks), trace=list(trace), terminal=state())), flush=True)
        raise


if __name__ == '__main__':
    try:
        print(json.dumps(run()), flush=True)
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
