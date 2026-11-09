"""Qualify one fewer mapper stage for the ordinary post-draw palette reset."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_actor_bounds_irq_1110 as I
import check_native_enemy_offscreen_edge_irq_1110 as Q
from check_mini_funded_actor_1108_v3 import install, run
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP


B,D,P,N,R=Q.B,Q.D,Q.P,Q.N,Q.R
SOURCE=R/'tools/reference/shared_palette_reset_1110.s'
ENTRY,END,START,JOIN=0xbd9c,0xbdf5,0x8484,0x8496
OLD=bytes.fromhex('ad02604918f01d491af030a9008d6a01a9218d6c01a9aa8d6d01a9bf8d620168684c61018d6a01'
                  'a94f8d6c01a9bf8d6d01a9d68d620168684c6101adee5f4901d0c98d6a01a9d38d6c01a9bc8d6d01'
                  'a9f98d620168684c6101')
PACKET=(0x162,0x16a,0x16c,0x16d,0x179)


def link(raw,out):
    D.check_span(raw,79,ENTRY,OLD)
    D.check_span(raw,126,0x8450,bytes.fromhex('ad9c07f02f'))
    D.check_span(raw,126,START,bytes.fromhex('8d6a01a99c8d6c01a9bd8d6d01a9cf205a01'))
    D.check_span(raw,1,0xa54c,bytes.fromhex('ad870529fc8d870560'))
    D.check_span(raw,126,0x88b1,bytes.fromhex('a9a78d6c01a9bd8d6d01a9874caa94'))
    prg=raw[16:16+128*8192]
    bank=prg[79*8192:80*8192]
    assert not [(i,to) for i,op in enumerate(bank[:-2]) if op in (0x20,0x4c,0x6c)
                and ENTRY<=(to:=bank[i+1]+256*bank[i+2])<END]
    assert [(i//8192,i&8191) for i in range(len(prg)-14) if prg[i:i+14]==bytes.fromhex(
        'a99c8d6c01a9bd8d6d01a9cf205a')]==[(126,0x487)]
    with tempfile.TemporaryDirectory(prefix='palette-link-',dir=out) as td:
        tmp=Path(td)
        cfg,obj,binary=(tmp/f'pal.{s}' for s in ('cfg','o','bin'))
        cfg.write_text('MEMORY { W:start=$bd9c,size=$59,file=%O,fill=yes,fillval=$ea; } '
                       'SEGMENTS { WORKER:load=W,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        data=binary.read_bytes()
    assert len(data)==len(OLD)==END-ENTRY and data[-5:]==b'\xea'*5
    patch=dict(physical_PRG=79,CPU_half_open=[ENTRY,END],file_offset=D.offset(79,ENTRY),
               old_hex=OLD.hex(),new_hex=data.hex())
    return install(raw,[patch]),patch


def take_context(seed,scene):
    c=I.prepare(seed,scene)
    run(c,lambda q:D.bank_pc(q)==(254,START))
    return c


def set_route(c,owner,alt,auth,attr,flags):
    m=c.memory
    N.put(m,SelectedCharacter=owner)
    m[0x5fee]=alt
    if owner==25:
        m[0x5fff]=m[0x5fff]|1 if auth else m[0x5fff]&0xfe
    m[0x587]=attr
    c.a,c.p=0,flags


def snapshot(c):
    m=c.memory
    return (semantic(c),bytes(m[D.SMC]),tuple((a,v) for a,v in m.writes if 0x200<=a<0x300 or a==0x587))


def with_seeds(before,after,kernel=Q.KERNEL,kernel_sha=Q.KERNEL_PIN):
    images=[P.bundle(q) for q in (before,after)]
    with Q.cold_kernel(kernel,kernel_sha):
        seeds=B.cold_pair(images,Q.OWNERS)
    return images,seeds,json.loads(Q.E.PEAK.read_text())['scene']


def routes(images,seeds,scene):
    base={owner:take_context(rows[0],scene) for owner,rows in seeds.items()}
    totals=Counter()

    def compare(owner,alt,auth,attr,flags):
        result=[]
        for im in images:
            c=fork(base.get(owner,base[0]),im)
            set_route(c,owner,alt,auth,attr,flags)
            run(c,lambda q:D.bank_pc(q)==(254,JOIN))
            result.append((snapshot(c),c.processorCycles,[v for a,v in c.memory.writes if a==0x5115]))
        a,b=result
        assert a[0]==b[0],(owner,alt,auth,attr,flags,a[0][1:],b[0][1:])
        role='dragon' if owner==24 else 'rogue' if owner==2 and alt==1 else 'smb2' if owner==25 else 'native'
        if role=='native':
            assert a[2]==[207,191,129,191,215] and b[2]==[207,129,215],(owner,a[2],b[2])
        else:
            assert a[2]==b[2],(owner,a[2],b[2])
        totals[role,a[1]-b[1]]+=1

    for owner,alt,attr,flags in product(range(42),(0,1,255),(0,3,0x23,0xff),(0x21,0x25,0xe0,0x69)):
        compare(owner,alt,True,attr,flags)
    for attr in range(256):
        compare(41,0,True,attr,0x21)
    for alt,attr,flags in product((0,1,255),(0,0x23,0xff),(0x20,0xe5)):
        compare(25,alt,False,attr,flags)
    return [[role,delta,n] for (role,delta),n in sorted(totals.items())]


def whole(before,after,kernel=Q.KERNEL,kernel_sha=Q.KERNEL_PIN):
    _,seeds,scene=with_seeds(before,after,kernel,kernel_sha)
    results=[]
    modes=product((0,1,4,8),(1,2),(0,1))
    scenarios=list(modes)
    for owner,(star,high,interval) in product(seeds,scenarios):
        pair=[]
        for m in seeds[owner]:
            c=I.prepare(m,scene)

            def visit(q):
                if D.bank_pc(q)==(254,0x844a):
                    N.put(q.memory,StarInvincibleTimer=star,Player_Y_HighPos=high,
                          IntervalTimerControl=interval,Player_SprAttrib=0x23)

            run(c,lambda q:(q.pc,q.sp)==(STOP,252),visit)
            pair.append((snapshot(c),c.processorCycles))
        a,b=pair
        assert a[0]==b[0],(owner,star,high,interval,a[0][1:],b[0][1:])
        saving=a[1]-b[1]
        assert (saving==0)==bool(star or high>=2),(owner,star,high,interval,saving)
        results.append([owner,star,high,interval,saving])
    return results


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=Q.ROM.read_bytes()
    assert P.sha(raw)==Q.PIN
    image,patch=link(raw,args.output)
    cases=routes(*with_seeds(raw,image))
    print('Palette route cases',cases,flush=True)
    loops=whole(raw,image)
    refs=(Path(__file__),SOURCE,Q.ROM,Q.KERNEL,Q.E.PEAK,R/'src/mmc5.s',R/'src/player.s',R/'src/game.s',
          R/'src/smb2_roster_main_gates_fast_v3.s',R/'src/rogue_dawn_host_ui_v1.s')
    out=dict(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
             patches=[patch],route_cycles=cases,whole_GameLoop=loops,
             bindings={str(p):P.sha(p.read_bytes()) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['expected_memory_only_SHA256'],len(loops),flush=True)


if __name__=='__main__':
    main()
