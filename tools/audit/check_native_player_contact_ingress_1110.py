"""Exercise real pickup and Bowser ingresses and the retained hot GameLoop."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_player_contact_offset_1110 as S
from check_mini_funded_actor_1108_v3 import install, run


M, N, P, D, Q, R = S.M,S.N,S.P,S.D,S.Q,S.R


def ingress(before,after):
    seeds = S.cold(before,after)
    samples = Counter()
    for owner,slot,kind,version in product(range(42),(0,5),(0,1,2,3),(0,1)):
        pair = [S.context(seed,owner,slot,0x2e,8,0x21,state=0x80,version=version)
                for seed in seeds.get(owner,seeds[0])]
        for c in pair:
            m = c.memory
            m[P.address(m.bundle,'PowerUpType')+slot] = kind
            c.pc = 0xb7f2        # The actual owner router just after DrawPowerUp.
            run(c,lambda z:z.pc in (S.ENTRY,0xb809))
            if c.pc==S.ENTRY:
                assert c.x==m[0x0d]==slot,(owner,slot,kind,version,c.x,m[0x0d])
        a,b = pair
        assert D.bank_pc(a)==D.bank_pc(b) and S.stable(a)==S.stable(b)
        samples['pickup_to_native' if a.pc==S.ENTRY else 'pickup_retained_by_owner'] += 1

    for owner,slot in product(seeds,(0,5,6,7,15,31,63,255)):
        pair = [S.context(seed,owner,slot,0x2d,8,0x21) for seed in seeds[owner]]
        for c in pair:
            m = c.memory
            m[(0x1f+slot)&255] = 0
            c.pc = 0xa8f9        # Bowser half's actual relative and bounding-box path.
            run(c,lambda z:z.pc==S.ENTRY)
            assert c.x==m[0x0d]==slot,(owner,slot,c.x,m[0x0d])
        assert S.stable(pair[0])==S.stable(pair[1])
        samples['bowser_legal' if slot<6 else 'bowser_extended'] += 1
    assert samples['pickup_to_native'] and samples['bowser_extended']
    return dict(samples)


def whole(before,after,labels):
    seeds = S.cold(before,after)
    actual = Q.read_scene(S.PROFILE)
    late = Q.read_scene(R/'build/mini-90a8-late-profile-1110/capture/instruction-sample.json')
    rows = []
    for owner,(name,scene),flags in product(seeds,(('dd1460',actual),('four_goombas',late)),(0x21,0x65)):
        pair = [Q.Edge.prepare(seed,scene,False) for seed in seeds[owner]]
        counts = []
        for side,c in enumerate(pair):
            N.put(c.memory,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
            c.p = flags
            sites = Counter()

            def visit(z):
                tag,pc = D.bank_pc(z)
                if tag==254 and pc in (S.ENTRY,S.OLD_OFFSET if side==0 else labels['InlineOffset']):
                    assert z.x==z.memory[0x0d],(owner,name,side,hex(pc),z.x,z.memory[0x0d])
                    sites['ingress' if pc==S.ENTRY else 'offset'] += 1

            run(c,Q.at_end,visit)
            counts.append(sites)
        a,b = pair
        assert counts[0]==counts[1] and S.stable(a)==S.stable(b),(owner,name,flags,counts)
        saving = a.processorCycles-b.processorCycles
        rows.append(dict(owner=owner,scene=name,flags=flags,calls=dict(counts[0]),cycles_saved=saving))
    assert all(row['cycles_saved']>0 for row in rows if row['owner']==41)
    return rows


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    path,dest = out/'proof.json',out/'ingress.json'
    assert out.is_relative_to(R/'build') and not dest.exists()
    saved = json.loads(path.read_text())
    before = S.BASE.read_bytes()
    assert saved['passed'] and saved['parent_SHA256']==P.sha(before)==S.PIN
    for name,digest in saved['bindings'].items():
        assert P.sha(Path(name).read_bytes())==digest,name
    after = install(before,saved['patches'])
    assert P.sha(after)==saved['expected_memory_only_SHA256']
    live = ingress(before,after)
    loops = whole(before,after,saved['labels'])
    refs = (Path(__file__),Path(S.__file__),path,S.PROFILE,
            R/'build/mini-90a8-late-profile-1110/capture/instruction-sample.json')
    receipt = dict(passed=True,ROM_written=False,parent_SHA256=S.PIN,expected_memory_only_SHA256=P.sha(after),
                   ingress=live,whole_GameLoop=loops,bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    dest.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(live,[row for row in loops if row['owner']==41],flush=True)


if __name__=='__main__':
    main()
