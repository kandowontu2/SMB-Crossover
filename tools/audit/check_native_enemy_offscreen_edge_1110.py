"""Qualify shared enemy near-right publication against the existing native leaf."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import re
import subprocess
import tempfile

import check_native_actor_bounds_1110 as B
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at


D,P,N,M,R=B.D,B.P,B.N,B.M,B.R
SOURCE=R/'tools/reference/native_enemy_offscreen_edge_1110.s'
PEAK=R/'build/mini-90a8-enemy-profile-1110/capture/instruction-sample.json'
AUDIO=R/'src/rogue_dawn_audio_upper_raw_v4.s'
ENTRY,END,FALLBACK=0xb893,0xb8f5,0x8ae9
OLD=bytes.fromhex('e006b05bb5a5c901d055b5bec920904fc9e0b04b38b576ed1f078503b55ded1d07d03ca503f038'
                  '38ad2007f576850aad1e07f55dd029a50ac9189023a9008da10585038a1869018507b5be49ff850aa9048508'
                  'a9208509a900a00118a60d604ce98a')


def census(raw):
    code=raw[16:16+128*8192]
    bank=code[:8192]
    assert [(0xa000+i,target) for i,op in enumerate(bank[:-2]) if op in (0x20,0x4c)
            and ENTRY<=(target:=bank[i+1]+256*bank[i+2])<END]==[(0xa45d,ENTRY),(0xbd1c,0xb8bd)]
    D.check_span(raw,0,0xbd17,bytes.fromhex('c901f002a04cbdb805'))  # DrawBlock LDY/LDA operands.
    assert raw.count(bytes.fromhex('2093b8'),16,16+128*8192)==1
    packet=re.compile(rb'\xa9(.)\x8d\x6c\x01\xa9\xb8\x8d\x6d\x01\xa9\x80\x20\x5a\x01',re.S)
    packets=[(hit.start()//8192,0xa000+(hit.start()&8191),hit[1][0]) for hit in packet.finditer(code)
             if ENTRY&255<=hit[1][0]<END&255]
    assert packets==[(118,0xbd19,ENTRY&255)],packets
    audio=bytes.fromhex('02b83494bf024c93b84294bf025a93b8')
    assert '.byte $02,$b8,$34,$94,$bf,$02,$4c,$93,$b8,$42,$94,$bf,$02,$5a,$93,$b8' in AUDIO.read_text()
    jumps=[]
    at=-1
    while (at:=code.find(bytes.fromhex('4c93b8'),at+1))>=0:
        assert code[at-6:at+10]==audio
        jumps.append((at//8192,0xa000+(at&8191)))
    assert jumps==[(91,0xbc7f),(91,0xbdd6)]
    assert bytes.fromhex('6c93b8') not in code
    D.check_span(raw,126,0x8b47,bytes.fromhex('bd638b'))
    D.check_span(raw,126,0x8b63,bytes.fromhex('7f3f1f0f0703010080c0e0f0f8fcfeff'))
    D.check_span(raw,0,END,bytes.fromhex('ada105d008a9009da8054c2e9f4cc2a1'))
    return dict(native_absolute=[0,0xa45d],smb2_packet=packets[0],embedded_audio_data=jumps)


def link(raw,out):
    callers=census(raw)
    D.check_span(raw,0,ENTRY,OLD)
    assert len(OLD)==END-ENTRY
    with tempfile.TemporaryDirectory(prefix='offscreen-link-',dir=out) as td:
        tmp=Path(td)
        cfg,obj,blob=(tmp/f'edge.{suffix}' for suffix in ('cfg','o','bin'))
        cfg.write_text('MEMORY { W:start=$b893,size=$62,file=%O,fill=yes,fillval=$ea; } '
                       'SEGMENTS { WORKER:load=W,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',blob],check=True)
        data=blob.read_bytes()
    assert len(data)==len(OLD) and data.rstrip(b'\xea')[-3:]==bytes.fromhex('4ce98a')
    patch=dict(file_offset=D.offset(0,ENTRY),physical_PRG=0,CPU_half_open=[ENTRY,END],
               old_hex=OLD.hex(),new_hex=data.hex())
    return install(raw,[patch]),patch,callers


def make_leaf(raw):
    m=bytearray(65536)
    for bank,pc in ((0,0xa000),(126,0x8000),(127,0xe000)):
        at=D.offset(bank,pc)
        m[pc:pc+8192]=raw[at:at+8192]
    return N.NesMPU(memory=m)


def direct(before,after):
    a,b=[make_leaf(q) for q in (before,after)]
    totals=Counter()

    def check(left,right,x,y,high,slot,offset,p):
        rows=[]
        for c in (a,b):
            m=c.memory
            m[:0x800]=bytes((i*17+left+p)&255 for i in range(0x800))
            m[0x071d:0x0721]=bytes((left>>8,right>>8,left&255,right&255))
            for addr,value in ((0x76,x&255),(0x5d,x>>8),(0xa5,high),(0xbe,y)):
                m[(addr+slot)&255]=value
            m[0x0d]=offset
            c.a,c.x,c.y,c.p,c.sp,c.pc=117,slot,19,p,248,ENTRY
            c.processorCycles=0
            c.stPushWord(STOP-1)
            run(c,lambda q:(q.pc,q.sp)==(STOP,248))
            rows.append((registers(c,0xef),bytes(m[:0x100]),m[0x5a1],c.processorCycles))
        old,new=rows
        assert old[:-1]==new[:-1],(left,right,x,y,high,slot,offset,p,old[0],new[0],
                                  [(i,u,v) for i,(u,v) in enumerate(zip(old[1],new[1],strict=True)) if u!=v],old[2],new[2])
        left_rel=(x-left)&65535
        right_rel=(right-x)&65535
        role=('edge' if right_rel<24 else 'interior') if (
            0<left_rel<256 and right_rel<256 and high==1 and 32<=y<224 and slot<6) else 'stock'
        totals[role,old[-1]-new[-1]]+=1

    for left,delta,rel,y,high in product(
        (0,1,56,255,256,582,32767,32768,65480,65535), (0,97,240,255,256,305,32768,65535),
        (-257,-1,0,1,15,22,23,63,127,199,200,223,231,232,239,240,247,248,249,255,256,257,511),
        (0,31,32,184,223,224,255),(0,1,2),
    ):
        slot=(left+rel+y)%6
        check(left,(left+delta)&65535,(left+rel)&65535,y,high,slot,(slot+y)%6,(0x20,0xe1)[y&1])
    for slot,rel in product(range(6,256),(0,228,249,65535)):
        check(582,837,(582+rel)&65535,184,1,slot,(slot+5)&255,0x69)
    return dict(cases=sum(totals.values()),cycles=[[role,delta,n] for (role,delta),n in sorted(totals.items())])


def whole(before,after):
    images=[P.bundle(q) for q in (before,after)]
    seeds=B.cold_pair(images,(0,2,25,32,41))
    records=[]
    for owner,profile in product(seeds,(PEAK,B.LATE)):
        scene=json.loads(profile.read_text())['scene']
        pair=[B.scene_seed(slim_fork(seed),scene) for seed in seeds[owner]]
        runs=[]
        for key in (scene['keys'],0,0,1,1,193,193,0):
            rows=[]
            for m in pair:
                m.writes.clear()
                m.ram_writes.clear()
                m.ppu_log.clear()
                M.controls(m,key)
                c=cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
                visits=[]

                def collect(q):
                    if D.bank_pc(q)==(128,ENTRY):
                        x=m[(0x76+q.x)&255]+256*m[(0x5d+q.x)&255]
                        visits.append([q.x,(x-m[0x71f]-256*m[0x71d])&65535])

                run(c,lambda q:(q.pc,q.sp)==(STOP,252),collect)
                oam=[(i,v) for i,v in m.writes if 0x200<=i<0x300]
                rows.append((semantic(c),bytes(m[D.SMC]),oam,visits,c.processorCycles))
            assert rows[0][:-1]==rows[1][:-1],(owner,profile,key)
            runs.append([rows[0][-1]-rows[1][-1],rows[0][-2]])
            for m in pair:
                N.consume(m)
        records.append(dict(owner=owner,scene=profile.parent.parent.name,updates=runs))
    return records


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=B.ROM.read_bytes()
    assert P.sha(raw)==B.PIN
    image,patch,callers=link(raw,args.output)
    leaf=direct(raw,image)
    print('Leaf',leaf,flush=True)
    loops=whole(raw,image)
    for row in loops:
        print(row['owner'],row['scene'],[r[0] for r in row['updates']],flush=True)
    refs=Path(__file__),SOURCE,B.ROM,PEAK,B.LATE,AUDIO,R/'src/common.s',R/'src/enemy_offscreen_fast.s',R/'src/smb2_roster_main_v2.s'
    out=dict(passed=True,parent_SHA256=B.PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
             patches=[patch],ingress=callers,leaf=leaf,whole_GameLoop=loops,
             bindings={str(p):P.sha(p.read_bytes()) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':
    main()
