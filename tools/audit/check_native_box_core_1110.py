"""Qualify exact shared BoundingBoxCore arithmetic without stack traffic."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_actor_bounds_irq_1110 as I
import check_native_enemy_offscreen_edge_irq_1110 as Q
from check_mini_funded_actor_1108_v3 import install, registers, run
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, lag_pcs


B,D,P,N,R=Q.B,Q.D,Q.P,Q.N,Q.R
SOURCE=R/'tools/reference/native_box_core_1110.s'
PROFILE=Q.E.PEAK
ENTRY,END=0x9f4e,0x9f90
OLD=bytes.fromhex('8603b97c058505b9710585048a0a0a48a8bd45060a0aaaa504187d0de2995806a504187d0fe2995a06'
                  'e8c8a505187d0de2995806a505187d0fe2995a0668a8a60360')


def link(raw,out):
    at=D.offset(126,ENTRY)
    assert len(OLD)==END-ENTRY and raw[at:at+len(OLD)]==OLD
    prg=raw[16:16+128*8192]
    interior=[(i//8192,i&8191,op,to) for i,op in enumerate(prg[:-2]) if op in (0x20,0x4c,0x6c)
              and ENTRY<(to:=prg[i+1]+256*prg[i+2])<END]
    assert interior==[(2,0x14fb,0x4c,0x9f82)],interior
    assert prg[2*8192+0x14f5:2*8192+0x14ff]==bytes.fromhex('87078922ae214c829f34')
    assert '.byte $87, $07, $89, $22, $ae, $21, $4c, $82, $9f, $34' in (R/'src/level_tiles.s').read_text()
    for target in range(ENTRY+1,END):
        assert not bytes((0xa9,target&255,0x8d,0x6c,1,0xa9,target>>8,0x8d,0x6d,1)) in prg
    with tempfile.TemporaryDirectory(prefix='bbox-link-',dir=out) as td:
        tmp=Path(td)
        cfg,obj,blob=(tmp/f'box.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { W:start=$9f4e,size=$42,file=%O,fill=yes,fillval=$ea; } '
                       'SEGMENTS { WORKER:load=W,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',blob],check=True)
        after=blob.read_bytes()
    assert len(after)==len(OLD) and after[-5:]==bytes.fromhex('60eaeaeaea')
    patch=dict(file_offset=at,physical_PRG=126,CPU_half_open=[ENTRY,END],old_hex=OLD.hex(),new_hex=after.hex())
    return install(raw,[patch]),patch


def leaves(before,after):
    cpus=[Q.E.make_leaf(im) for im in (before,after)]
    memory=bytes((i*29+7)&255 for i in range(0x800))
    saves=Counter()
    for slot,ctrl in product(range(256),range(256)):
        rows=[]
        entry_y=(5*slot+ctrl)&255
        for c in cpus:
            m=c.memory
            m[:0x800]=memory
            m[0x645+slot]=ctrl
            m[0x571+entry_y]=(slot+ctrl)&255
            m[0x57c+entry_y]=(slot-ctrl)&255
            c.pc,c.a,c.x,c.y,c.p,c.sp=ENTRY,99,slot,entry_y,(0x20,0xe1,0x25,0xa4)[slot&3],248
            c.processorCycles=0
            c.stPushWord(STOP-1)
            run(c,lambda q:(q.pc,q.sp)==(STOP,248))
            rows.append((registers(c,0xef),bytes(m[:256]),bytes(m[0x200:0x800]),c.processorCycles))
        a,b=rows
        assert a[:-1]==b[:-1],(slot,ctrl,a[0],b[0])
        saves[a[-1]-b[-1]]+=1
    assert saves=={11:65536}
    return dict(cases=sum(saves.values()),cycles_saved=11)


def vectors(before,after,kernel=Q.KERNEL,kernel_sha=Q.KERNEL_PIN):
    images=[P.bundle(q) for q in (before,after)]
    with Q.cold_kernel(kernel,kernel_sha):
        seeds=B.cold_pair(images,Q.OWNERS)
    scene=json.loads(PROFILE.read_text())['scene']
    lag,regular=lag_pcs(seeds[41][1])
    counts,points,deepest=Counter(),set(),{}
    minima=[255,255]

    def compare(c,kind):
        rows=[]
        for side,image in enumerate(images):
            z=fork(c,image)

            def observe(q):
                minima[1]=min(minima[1],q.sp)
                owner=N.get(q.memory,'SelectedCharacter')
                if side and kind=='FF' and not q.p&4 and (owner not in deepest or q.sp<deepest[owner].sp):
                    deepest[owner]=fork(q)
                    deepest[owner].memory.vector_floor=None

            I.interrupt(z,kind,lag,regular,observe)
            rows.append((semantic(z),z.memory.writes[:],z.processorCycles))
        assert rows[0]==rows[1],(D.bank_pc(c),kind)
        counts[kind]+=1

    for owner in seeds:
        for side,seed in enumerate(seeds[owner]):
            c=I.prepare(seed,scene)
            seen=set()

            def visit(q):
                tag,pc=D.bank_pc(q)
                key=pc,q.sp,q.p&4
                if tag!=254 or not ENTRY<=pc<END or key in seen:
                    return
                seen.add(key)
                points.add((side,pc))
                minima[0]=min(minima[0],q.sp)
                compare(q,'FF')
                if not q.p&4:
                    compare(q,'IRQ')

            run(c,lambda q:(q.pc,q.sp)==(STOP,252),visit)
            assert seen
    for c in deepest.values():
        compare(c,'IRQ')
    resumes=[]
    for owner,kind in product(seeds,('FF','IRQ')):
        pair=[]
        for m in seeds[owner]:
            c=I.prepare(m,scene)
            run(c,lambda q:D.bank_pc(q)==(254,ENTRY))
            I.interrupt(c,kind,lag,regular)
            run(c,lambda q:(q.pc,q.sp)==(STOP,252))
            pair.append((semantic(c),bytes(c.memory[D.SMC]),
                         [(a,v) for a,v in c.memory.writes if 0x200<=a<0x300]))
        assert pair[0]==pair[1],(owner,kind)
        resumes.append((owner,kind))
    return dict(cuts=dict(counts),nested_IRQ=len(deepest),sites=sorted(points),minimum_SP=minima,
                paired_GameLoop_resumes=resumes)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=Q.ROM.read_bytes()
    assert P.sha(raw)==Q.PIN
    image,patch=link(raw,args.output)
    leaf=leaves(raw,image)
    loops=Q.whole(raw,image)
    vectors_result=vectors(raw,image)
    profile=json.loads(PROFILE.read_text())['foreground_opcodes']['126:9f4e']
    assert profile==9
    paths=(Path(__file__),SOURCE,Q.ROM,PROFILE,R/'src/collision.s',R/'src/level_tiles.s')
    q=dict(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
           patches=[patch],leaf=leaf,whole_GameLoop=loops,vectors=vectors_result,peak_projection_cycles=33,
           bindings={str(p):P.sha(p.read_bytes()) for p in paths})
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(q['expected_memory_only_SHA256'],leaf,vectors_result['cuts'],len(vectors_result['paired_GameLoop_resumes']),flush=True)


if __name__=='__main__':
    main()
