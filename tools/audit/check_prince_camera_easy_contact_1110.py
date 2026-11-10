"""Reproduce Prince's native Easy landing contact and record its ingress."""

import argparse
import json
from pathlib import Path

import prepare_prince_camera_roof_native_1110 as Roof


R, N, Seam, Route = Roof.R, Roof.N, Roof.Seam, Roof.Route
OUT = R / 'build/prince-camera-easy-contact-1110'
PRIOR = Roof.OUT / 'native'
CAPTURE = PRIOR / 'capture'
PIN = Roof.PIN


def evidence():
    ready = Roof.read(PRIOR / 'ready.json')
    binding, full, diagnostic = (Roof.read(CAPTURE / name) for name in
                                 ('binding.json', 'full11.json', 'prince-diagnostic.json'))
    assert all(row['ROM_sha256'] == PIN for row in (ready, binding, full, diagnostic))
    assert binding['ready_sha256'] == Roof.sha(PRIOR / 'ready.json') and binding['exit_code'] == 1
    assert (full['admitted'], full['state']['world_x'], full['HP'], full['final_lives']) == (1188, 891, 0, 2)
    jump = full['route']['third_roof']
    assert (jump['request_Main'], jump['admission_Main'], jump['far_ground_Main']) == (1121, 1123, 1188)
    samples = jump['samples']
    assert [a['x'] for a in samples[0]['actors']] == [829, 853]
    assert [a['x'] for a in samples[-1]['actors']] == [859, 883]
    assert (samples[-1]['Main'], samples[-1]['player']['physical_foot']) == (1184, 196)
    contact, = diagnostic['first_pipe_route']['precontacts']
    assert (contact['enemy']['id'], contact['enemy']['slot'], contact['enemy']['x']) == (6, 1, 885)
    assert contact['native_player_world'] == [893, 186, 905, 210]
    assert contact['native_enemy_world'] == [888, 198, 898, 204]
    assert (contact['native_DY'], contact['native_state'], contact['behavior']) == (0, 0, 0)
    return ready, jump, contact


def cap_fixture():
    template, _, _ = Route.Current.current()
    assert Roof.sha(Roof.ROM) == PIN
    env, model, labels, _ = Roof.Climb.Earned.fixture(dict(template, raw=Roof.ROM.read_bytes()))
    Seam.terrain(model, Roof.terrain)
    Seam.layout(model, 811 - 255, 678, scroll=0)
    Route.install_group(model)
    pad = 0
    starts = dict(((0, 1), (8, 0), (51, 8), (106, 9), (112, 8)))
    for tick in range(172):
        pad = starts.get(tick, pad)
        Route.controls(env, model, labels, pad)
    row = Roof.Recovery.sample(model, 172)
    assert (row['x'], row['y'], row['foot'], row['hp'], row['lives']) == (723, 112, 145, 5, 2)
    assert [(a['id'], a['dir'], a['x']) for a in row['actors']] == [(6, 1, 785), (6, 1, 809)]
    return env, model, labels


def shift_goombas(model, shift):
    for actor in Route.actors(model):
        slot = actor['slot']
        x = actor['x'] + shift + slot
        for name, value in (('Enemy_X_Position', x & 255), ('Enemy_PageLoc', x >> 8)):
            model[Route.I.address(model.bundle, name) + slot] = value


def run(env, seed, labels, shift=30):
    model = N.fork(seed)
    shift_goombas(model, shift)
    stage = 'run'
    events, contacts, samples, phase = {}, [], [], []
    cpu = N.NesMPU
    at = 0
    assert bytes(model.ram[3][0x136e:0x1372]) == bytes.fromhex('a50fc908')
    watch = {'HostUpdate': (3, 0xb36e),
             'BodyBridge': (255, Route.I.address(model.bundle, 'GuestBodyContactBridge')),
             'Injury': (254, Route.I.address(model.bundle, 'InjurePlayer')),
             'StompDecision': (254, Route.I.address(model.bundle, 'ChkForPlayerInjury')),
             'MotionExport': (2, 0xda98),
             'Contact': (3, 0xbd22)}
    lookup = {point: name for name, point in watch.items()}

    def entry(c, name):
        return dict(name=name, pc=c.pc, sp=c.sp, at=at, a=c.a, x=c.x, y=c.y, p=c.p,
                    stack=bytes(model[0x101+c.sp:0x200]).hex(), maps=model.rawtags[:],
                    C=bytes(model.ram[2][0x84:0x88]).hex(),
                    source_mode=model.ram[2][0x618], source_action=model.ram[2][0x616],
                    native_state=N.get(model, 'Player_State'), native_DY=N.get(model, 'Player_Y_Speed'))

    class Trace(cpu):
        def step(self):
            if self.memory is model and 82 <= at and self.pc >= 0x8000:
                bank = model.rawtags[(self.pc - 0x8000) // 8192]
                point = lookup.get((bank, self.pc))
                if point:
                    phase.append(entry(self, point))
                if point == 'Contact':
                    snapshot = Roof.Recovery.sample(model, at)
                    slot = N.get(model, 'ObjectOffset')
                    snapshot['slot'] = slot
                    snapshot['oldfoot'] = int.from_bytes(model.ram[2][0x86:0x88], 'little')
                    left = snapshot['camera_left']
                    snapshot['player'] = [v+(left if i in (0, 2) else 0)
                                          for i, v in enumerate(model[i] for i in range(0x658, 0x65c))]
                    snapshot['enemy'] = [v+(left if i in (0, 2) else 0) for i, v in
                                         enumerate(model[i] for i in range(0x65c+4*slot, 0x660+4*slot))]
                    contacts.append(snapshot)
            return super().step()

    N.NesMPU = Trace
    try:
        for at in range(96):
            row = Roof.Recovery.sample(model, at)
            x, y, foot, actors = (row[key] for key in ('x', 'y', 'foot', 'actors'))
            if row['hp'] == 0 or row['engine'] != 8 or row['lives'] != 2:
                stage = 'death'
                break
            if stage == 'run' and 745 <= x <= 752 and abs(y - 112) <= 2 and Roof.Recovery.running(model, row):
                events['request'] = row
                stage = 'takeoff'
            if stage == 'takeoff' and row['action'] == 4:
                events['admission'] = row
                stage = 'flight'
            if stage == 'flight':
                if at % 4 == 3:
                    samples.append(row)
                if x >= 784 and y == 176 and Roof.Recovery.grounded(model, row):
                    events.setdefault('land', row)
                if x >= 872 and 'land' in events and len(actors) == 2 and all(a['x']+13 < x+2 for a in actors):
                    stage = 'clear'
                    break
            pad = {'run': 1, 'takeoff': 129, 'flight': 1}[stage]
            Route.controls(env, model, labels, pad)
    finally:
        N.NesMPU = cpu
    return dict(shift=shift, result=stage, events=events, contacts=contacts, phase=phase,
                samples=samples, terminal=row)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    out = cli.parse_args().output.resolve()
    assert out == OUT and not out.exists()
    _, jump, contact = evidence()
    env, seed, labels = cap_fixture()
    old = run(env, seed, labels)
    assert old['result'] == 'death'
    assert old['terminal']['x'] == contact['world_x']
    assert old['contacts'][0]['player'] == contact['native_player_world']
    assert old['contacts'][0]['enemy'] == contact['native_enemy_world']
    print(old['contacts'], [q for q in old['phase'] if q['at'] == 90], flush=True)
    out.mkdir()
    refs = (Path(__file__), Path(Roof.__file__), Roof.ROM, PRIOR / 'ready.json', CAPTURE / 'binding.json',
            CAPTURE / 'full11.json', CAPTURE / 'prince-diagnostic.json')
    data = dict(passed=True, ROM_sha256=PIN, native_V5_landing_contact=contact,
                native_roof_trajectory=jump, reproduction=old, source_fix_pending=True,
                scope='Explicit CPU model of the captured natural Goomba positions. Genuine source motion, '
                      'native enemy walking and controller inputs after that setup.',
                bindings={str(p.relative_to(R)): Roof.sha(p) for p in refs})
    (out / 'cpu.json').write_text(json.dumps(data, separators=(',', ':'))+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
