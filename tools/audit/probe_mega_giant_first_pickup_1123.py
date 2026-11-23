"""Exact-current Giant opening: real reset/menu/controller; stdout-only CPU witness.

No gameplay fields, actors, blocks, or collector positions are seeded.  The
normal-NMI scheduler is a source model, not physical Mesen cadence evidence.
At most five temporary assembler files are used and removed by the linker.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_ff_white_mushroom_current_1110 as W
import check_mega_giant_resident_1110 as Giant
import profile_ff_empty_cpu_v2_1110 as Profile

N = W.N
R = W.R
PIN = '3ce7788d62e6818bd487f9de49c141d7f7caff28081c80a94388b2aa12371550'
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


class ColdBus(W.ControllerBus):
    boot_vblank = True

    def __getitem__(self, at):
        if at == 0x2002 and self.boot_vblank:
            self.toggle = 0
            return 0x80
        return super().__getitem__(at)


def binding(raw, out):
    assert sha256(raw).hexdigest() == PIN
    b = dict(W.Symbols.bundle(), raw=raw)
    data, labels = Giant.assemble(out, b)
    offset = 0
    checked = []
    for bank, start, end in Giant.PAGES:
        expected = bytearray(data[offset:offset + end - start])
        offset += end - start
        if start == 0xb09e:
            expected[0xb174 - start:0xb180 - start] = bytes.fromhex('a405a95191094cf59e') + b'\xea' * 3
        elif start == 0xbc40:
            assert expected[0xbcde - start:0xbce3 - start] == bytes.fromhex('a50620f59e')
            expected[0xbcde - start:0xbce3 - start] = bytes.fromhex('2074b1eaea')
        elif start not in (0xb744, 0xafa7):
            continue
        # Later authenticated draw workers own the resident padding, outside
        # the linked collision bodies.  Bind those bodies, then the crush leaf
        # separately; do not pretend the obsolete zero fill is current code.
        if start == 0xb09e:
            expected = expected[:0xb15c-start]
        elif start == 0xb744:
            expected = expected[:0xb86b-start]
        actual = Giant.native_slice(raw, bank, start, len(expected))
        assert actual == expected, ('Current Giant source preimage', bank, hex(start),
            [(hex(start+i), a, e) for i, (a, e) in enumerate(zip(actual, expected)) if a != e][:8])
        checked.append(dict(bank=bank, pc=start, size=len(expected), SHA256=sha256(actual).hexdigest()))
    leaf = bytes.fromhex('a405a95191094cf59e') + b'\xea' * 3
    assert Giant.native_slice(raw, 90, 0xb174, len(leaf)) == leaf
    checked.append(dict(bank=90, pc=0xb174, size=len(leaf), SHA256=sha256(leaf).hexdigest()))
    descriptor = Giant.native_slice(raw, 84, 0xbef8, 8)
    assert descriptor == bytes.fromhex('020101d600d400ff'), descriptor.hex()
    return b, labels, dict(ROM_SHA256=PIN, checked=checked, descriptor=descriptor.hex())


def run(out, image=None, require_pickup=False):
    parent = ROM.read_bytes()
    b, labels, bound = binding(parent, out)
    raw = parent if image is None else image
    b = dict(b, raw=raw)
    m = ColdBus(b)
    get = lambda name, i=0: N.get(m, name, i)
    addr = lambda name: W.address(b, name)
    idle = addr('IdleLoop')
    c = N.NesMPU(memory=m, pc=None)
    c.reset()
    for boot_steps in range(300000):
        if c.pc == idle:
            break
        assert m[c.pc], ('Reset BRK', hex(c.pc))
        c.step()
    else:
        raise AssertionError('Reset bound')
    m.boot_vblank = False
    epochs = 0
    active_updates = 0
    events = []
    counts = Counter()
    powerup_births = []
    saw_actor = False
    contacts = []
    collector = []
    growth = []
    completed = None
    resumed = []

    def state():
        return dict(epoch=epochs, active=active_updates,
            x=get('Player_X_Position') + 256 * get('Player_PageLoc'),
            y=get('Player_Y_Position'), status=get('PlayerStatus'), size=get('PlayerSize'),
            engine=get('GameEngineSubroutine'), lives=get('NumberofLives'),
            world=get('WorldNumber'), level=get('LevelNumber'),
            owner=get('SelectedCharacter'), variant=get('MarioVariant'),
            growth_active=get('GuestPowerupActive'), growth_age=get('GuestPowerupAge'),
            score=list(m[addr('Player1ScoreDisplay'):addr('Player1ScoreDisplay')+6]),
            camera=get('ScreenLeft_X_Pos') + 256 * get('ScreenLeft_PageLoc'))

    points = {(218, labels['GiantSweepEffect']): 'sweep', (218, 0xb174): 'as_brick',
              (254, 0x9ef5): 'head'}
    for name in ('PowerUpObjHandler', 'HandlePowerUpCollision', 'MarioSourcePowerupCollision',
                 'MarioSourceBeginPowerup', 'BrickShatter', 'BumpBlock', 'SetupPowerUp'):
        if name in b['syms']:
            points[((W.location(b, name) - 16) // 8192 | 128, addr(name))] = name

    def finish(cpu, stop, observe):
        for _ in range(500000):
            if (cpu.pc, cpu.sp) == stop:
                return
            pc = cpu.pc
            if observe and pc >= 0x8000:
                name = points.get((m.rawtags[(pc - 0x8000) // 8192], pc))
                if name:
                    counts[name] += 1
                    if name in ('HandlePowerUpCollision', 'MarioSourcePowerupCollision', 'MarioSourceBeginPowerup'):
                        collector.append(dict(event=name, **state(), slot=cpu.x,
                            id=get('Enemy_ID', cpu.x), kind=get('PowerUpType', cpu.x),
                            actor_state=get('Enemy_State', cpu.x),
                            actor_x=get('Enemy_X_Position', cpu.x) + 256*get('Enemy_PageLoc', cpu.x),
                            actor_y=get('Enemy_Y_Position', cpu.x)))
                    if name in ('sweep', 'as_brick', 'head'):
                        cell = (m[9] + 256 * m[10] + m[5]) & 0xffff
                        q = dict(event=name, **state(), pc=pc, tile=m[cell], cell=cell,
                            row=m[5], original=m[6], query_x=m[8], A=cpu.a, X=cpu.x, Y=cpu.y,
                            native_box=list(m[0x658:0x65c]))
                        if len(events) < 40:
                            events.append(q)
                        if name == 'sweep':
                            contacts.append(q)
            assert m[pc], ('Native BRK', hex(pc), m.rawtags)
            cpu.step()
        raise AssertionError(('Main bound', hex(cpu.pc)))

    def step(pad=0, observe=False):
        nonlocal epochs, active_updates, saw_actor, completed
        m.controller_pad = pad
        W.clear_logs(m)
        Profile.normal_nmi(m)
        cpu = N.NesMPU(memory=m, pc=idle)
        cpu.sp, cpu.p = 255, 0x31
        cpu.stPushWord(0xe33b)
        finish(cpu, (idle + 12, 252), observe)
        assert not m.blocked
        epochs += 1
        if (get('OperMode'), get('OperMode_Task'), get('GameEngineSubroutine')) == (1, 3, 8):
            active_updates += 1
        actors = [(i, get('Enemy_State', i), get('PowerUpType', i),
            get('Enemy_X_Position', i) + 256 * get('Enemy_PageLoc', i), get('Enemy_Y_Position', i))
            for i in range(6) if get('Enemy_Flag', i) and get('Enemy_ID', i) == 0x2e]
        if actors and not saw_actor:
            powerup_births.append(dict(**state(), actors=actors))
        saw_actor = bool(actors)
        if get('GuestPowerupActive'):
            growth.append(dict(epoch=epochs, age=get('GuestPowerupAge'), status=get('PlayerStatus'),
                size=get('PlayerSize'), timer=get('TimerControl')))
        elif growth and completed is None:
            completed = state()
        elif completed is not None and len(resumed) < 25:
            resumed.append(state())

    for title in range(180):
        if get('CrossoverMenuState') == 2:
            break
        step(16 if title == 40 else 0)
    else:
        raise AssertionError(('Title/menu bound', state(), get('CrossoverMenuState')))
    assert get('CrossoverMenuIndex') == get('SelectedCharacter') == 0
    for _ in range(9):
        step(0)
        step(32)
        selected_name = W.UI.menu_name(m)[0]
        step(0)
    assert get('MarioVariant') == 9 and get('SelectedCharacter') == 0
    menu = dict(**state(), name=selected_name)
    assert menu['name'] == 'MEGA GIANT MARIO', menu
    step(16)
    for _ in range(600):
        if (get('OperMode'), get('OperMode_Task'), get('GameEngineSubroutine')) == (1, 3, 8):
            break
        step()
    else:
        raise AssertionError(('Stage entry bound', state()))
    assert get('CheatInvincible') == get('CheatStartLevel') == 0
    first = state()
    print(json.dumps(dict(event='binding_and_entry', binding=bound, boot_instructions=boot_steps,
        menu=menu, first=first)), flush=True)
    first_contact_at = None
    for _ in range(500):
        step(1, True)
        assert (get('SelectedCharacter'), get('MarioVariant'), get('NumberofLives')) == (0, 9, 2), state()
        if any(q['tile'] == 0xc1 for q in contacts) and first_contact_at is None:
            first_contact_at = active_updates
        if require_pickup and len(resumed) == 25:
            break
        if not require_pickup and first_contact_at is not None and active_updates - first_contact_at >= 60:
            break
    assert first_contact_at is not None, ('No authored Mushroom block reached', state())
    cells = sorted({q['cell'] for q in contacts})
    result = dict(source_CPU_only=True, Mesen_run=False, controller_only=True,
        ROM_SHA256=sha256(raw).hexdigest(), parent_SHA256=PIN,
        script_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        first=first, terminal=state(), events=events, counts=dict(counts),
        powerup_births=powerup_births, final_cells={hex(at): m[at] for at in cells},
        collector=collector, growth=growth, growth_completed=completed, resumed=resumed,
        active_returns_after_first_contact=active_updates-first_contact_at,
        outputs_retained=0, normal_NMI_model=True, physical_cadence_qualified=False)
    canonical = json.dumps(result, sort_keys=True, separators=(',', ':'))
    print(json.dumps(dict(result=result, receipt_SHA256=sha256(canonical.encode()).hexdigest())), flush=True)
    assert not list(out.rglob('*')), 'Temporary assembly files retained'
    if require_pickup:
        assert any(q['kind'] == 0 and q['actor_state'] >= 6 for q in collector), 'No mature actual Mushroom collector'
        assert growth and {q['age'] for q in growth} == set(range(60)), 'All sixty original growth clocks'
        assert completed and completed['status'] == 1 and completed['size'] == 0
        assert len(resumed) == 25 and all(q['status'] == 1 and q['lives'] == 2 and q['engine'] == 8 for q in resumed)
        assert resumed[-1]['x'] > completed['x'] and resumed[-1]['y'] == 176
        def score(q):
            return int(''.join(map(str, q['score'])))
        assert score(resumed[-1]) - score(collector[-1]) >= 1000, 'Actual score credit'
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(exist_ok=True)
    run(args.output)
