"""Rebind both sparse-render components to the exact composed memory image."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_native_sparse_world_draw_1110 as Shared
import check_mini_movement_prefix_1110 as Move
from prepare_mini_lane_audio_native_1110 import verify_payload


R, P, N = Shared.R, Shared.P, Shared.N
ROOT = R/'build/native-sparse-world-draw-1110'
PINS = dict(world='a0abfe9298fb0e482613c954a58b61c9a7456f81dfd7754ebd6478f638d292ae',
            shot='d320dfda505b1b17e4ac0d2fa84526b40f9eb64a57b6f82f638b3ce5a9b8e97f')
SCENES = {
    'two_lifts_three_Goombas': R/'build/mini-dd-clear-and-nmi-profile-1110/capture/instruction-sample.json',
    'three_lifts_three_Goombas': R/'build/mini-90a8-enemy-profile-1110/capture/instruction-sample.json',
}


def compose(raw, output):
    groups = {}
    refs = {Path(__file__), Move.KERNEL, Shared.HOST, Path(Move.__file__),
            Path(Move.Q.Edge.__file__), *SCENES.values()}
    for role, pin in PINS.items():
        path = output/f'{role}.json'
        assert P.sha(path.read_bytes())==pin
        proof = json.loads(path.read_text())
        assert proof['passed'] and proof['parent_SHA256']==Shared.PIN
        for binding, digest in proof['bindings'].items():
            bound = Path(binding)
            assert P.sha(bound.read_bytes())==digest, binding
            refs.add(bound)
        refs.add(path)
        groups[role] = proof
    spans = [range(row['file_offset'],row['file_offset']+len(bytes.fromhex(row['old_hex'])))
             for proof in groups.values() for row in proof['patches']]
    assert sum(map(len,spans))==len(set().union(*spans))
    isolated = {role:Shared.install(raw,p['patches']) for role,p in groups.items()}
    assert all(P.sha(isolated[role])==p['expected_memory_only_SHA256'] for role,p in groups.items())
    minus = dict(world=isolated['shot'],shot=isolated['world'])
    final = Shared.install(minus['world'],groups['world']['patches'])
    assert final==Shared.install(minus['shot'],groups['shot']['patches'])
    assert raw[:16]==final[:16] and raw[1048592:]==final[1048592:]
    for image in (raw,final,*minus.values()):
        verify_payload(image,Move.KERNEL)
    return final, minus, groups, refs


def strict_game_loop(pair, key):
    hist = [[],[]]

    def seen(side, cpu):
        if Shared.bank_pc(cpu)==(132,Shared.Fire.ENTRY):
            m = cpu.memory
            hist[side].append(tuple((N.get(m,'Enemy_ID',i), N.get(m,'Enemy_Flag',i)) for i in range(6)))

    a,b = [Shared.play(m,key,lambda c:seen(side,c)) for side,m in enumerate(pair)]
    assert a[:2]==b[:2] and a[3]==b[3], (key,hist,a[0],b[0])
    assert a[2]==b[2] or Shared.without_world_transport(a[2])==b[2], (key,hist)
    assert hist[0]==hist[1], hist
    return a[4]-b[4],hist[0]


def mini(before, after):
    pairs = []
    original = Shared.Match.KERNEL
    Shared.Match.KERNEL = Move.KERNEL
    try:
        seeds = [Shared.Match.cold(Shared.bundle(raw),41)[0] for raw in (before,after)]
    finally:
        Shared.Match.KERNEL = original
    pairs.append(('cold_menu', seeds, [0]*24+[1]*112))
    for role,path in SCENES.items():
        scene = Move.Q.read_scene(path)
        pair = [Move.Q.Edge.prepare(seed,scene,False).memory for seed in seeds]
        pairs.append((role,pair,[scene['keys'],0,0,192,192,1,193,0]*3))

    rows = []
    for role, pair, keys in pairs:
        saved, ids = Counter(),Counter()
        for key in keys:
            cycles, actors = strict_game_loop(pair,key)
            saved[cycles]+=1
            ids.update(actors)
            for m in pair:
                N.consume(m)
                m.ppu_log.clear()
        assert ids, (role,'no shuffled world admission')
        rows.append(dict(role=role,updates=len(keys),savings=dict(saved),
                         ingress=[[list(s),n] for s,n in sorted(ids.items())]))
    assert any(any((0x25,1) in s for s,n in row['ingress']) for row in rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT)
    args = parser.parse_args()
    raw = Shared.HOST.read_bytes()
    assert P.sha(raw)==Shared.PIN
    final, minus, groups, refs = compose(raw,args.output)
    print('Composed exact memory SHA',P.sha(final),flush=True)
    shot = dict(foreground=Shared.shots(minus['shot'],final),
                vectors=Shared.vectors(minus['shot'],final,'shot'))
    assert shot=={key:groups['shot'][key] for key in shot}
    print('Exact final-minus shot leaf and real vectors PASS',flush=True)
    world = dict(foreground=Shared.world_leaf(Shared.bundle(minus['world']),Shared.bundle(final)),
                 vectors=Shared.vectors(minus['world'],final,'world'))
    assert world=={key:groups['world'][key] for key in world}
    print('Exact final-minus world offsets, actual castle/small lifts and real vectors PASS',flush=True)
    world['nested_vectors'] = Shared.FireIRQ.vectors(Shared.bundle(minus['world']),Shared.bundle(final),{
        'patches':[dict(start=Shared.WORLD_LO,end_exclusive=Shared.WORLD_HI)]})
    print('World real nested IRQ and positive special draw publication PASS',flush=True)
    world['whole'] = Shared.whole(minus['world'],final)
    assert json.loads(json.dumps(world['whole']))==groups['world']['whole']
    mini_checks = {role:mini(before,final) for role,before in minus.items()}
    mini_checks['both']=mini(raw,final)
    print('Strict Mini cold and crowded GameLoop comparisons PASS',flush=True)
    report = dict(passed=True,ROM_written=False,parent_SHA256=Shared.PIN,
                  expected_memory_only_SHA256=P.sha(final),
                  groups={role:q['patches'] for role,q in groups.items()},
                  component_SHA256=PINS,final_minus_SHA256={role:P.sha(before) for role,before in minus.items()},
                  final_minus=dict(shot=shot,world=world),Mini=mini_checks,
                  bindings={str(path):P.sha(path.read_bytes()) for path in sorted(refs)})
    dest = args.output/'combo.json'
    assert not dest.exists()
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print('Final-minus proof SHA',P.sha(dest.read_bytes()),flush=True)


if __name__=='__main__':
    main()
