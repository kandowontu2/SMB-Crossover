"""Qualify compact box offsets in the native enemy-pair loop on d998."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_enemy_ordinary_dispatch_1110 as Q
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at


N, P, D, R = Q.N,Q.P,Q.D,Q.R
SOURCE = R/'tools/reference/native_enemy_pair_offsets_1110.s'
START, ENTRY, END, BOX = 0x98d0,0x98d7,0x9958,0x9514
CALL, COMPARE_DONE = 0xa485,0xa49a
OLD = bytes.fromhex('7fbfdfeff7fbfda50e4a90ecad5307f0e7b517c915b06ec911f06ac90df066bda805d061'
                    '204b9bca305b86049848b510f04cb517c915b046c911f042c90df03ebda805d0398a0a0a186904'
                    'aa201495a60da4049020b51f191f002980d011b93d063dc998d018b93d061dc998993d06205899'
                    '4c4e99b93d063dd098993d0668a8a604ca10a5a60d60')


def census(raw):
    assert len(OLD)==END-START
    D.check_span(raw,126,START,OLD)
    D.check_span(raw,0,CALL,bytes.fromhex('20d7982096a4'))
    D.check_span(raw,0,0xa496,bytes.fromhex('b517c92e'))
    D.check_span(raw,126,0x98c8,bytes.fromhex('6080402010080402'))
    D.check_span(raw,126,BOX,bytes.fromhex('8409a901850ab95806dd5806'))
    resident = raw[16:16+128*8192]
    for op, addr, hits in ((0x20,ENTRY,[(0,CALL)]),(0x4c,ENTRY,[]),(0x3d,START,[(126,0x9948)])):
        key = bytes((op,addr&255,addr>>8))
        found = [(i//8192,(0x8000 if i//8192==126 else 0xa000)+i%8192)
                 for i in range(len(resident)-2) if resident[i:i+3]==key]
        assert found==hits,(key.hex(),found)
    assert (R/'src/object.s').read_text().count('jsr EnemiesCollision')==1
    collision = (R/'src/collision.s').read_text()
    assert collision.count('ClearBitsMask')==2 and collision.count('SetBitsMask')==3
    game = (R/'src/game.s').read_text()
    assert 'cpx #$06' in game and game.count('EnemiesAndLoopsCore')==2
    return dict(sole_ordinary_actor_JSR=[0,CALL],caller_kills_A_N_Z_C_at=0xa49a,
                actual_slot_schedule=[0,1,2,3,4,5],
                exact_fixed_126_table_reader=[0x9948], preserved_public_entry=ENTRY)


def link(raw,out):
    assert P.sha(raw)==Q.PIN
    caller = census(raw)
    cc = R/'tools/Windows/cc65/bin'
    with tempfile.TemporaryDirectory(prefix='pair-link-',dir=out) as temporary:
        t = Path(temporary)
        cfg,obj,binary,lbl = (t/f'pair.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { A:start=$98D0,size=$88,file=%O; } SEGMENTS { PAIR:load=A,type=ro; }\n')
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
        data = binary.read_bytes()
        labels = {p[2][1:]:int(p[1],16) for s in lbl.read_text().splitlines() if (p:=s.split())}
    assert len(data)==len(OLD) and labels['PairOffsets']==START and labels['EnemiesCollision']==ENTRY
    assert data[:0x11]==bytes((4,8,12,16,20,24,28))+OLD[7:0x11]
    p = dict(file_offset=D.offset(126,START),physical_PRG=126,CPU_half_open=[START,END],
             old_hex=OLD.hex(),new_hex=data.hex())
    return install(raw,[p]),p,labels,caller


def actor_fixture(seed,slot,eid,prior,state=0,otherstate=0,first=(103,155,117,171),
                  second=(122,155,136,171),priorflag=1,visible=0,othervisible=0,offscreen=0,
                  area=1,frame=1,flags=0x21):
    m = slim_fork(seed)
    N.put(m,ObjectOffset=slot,AreaType=area,FrameCounter=frame,Enemy_OffscreenBits=offscreen,
          NmiDisable=255,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,Mirror_PPUMASK=30,
          VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
    m.raw_page(1,128)
    N.put(m,CurrentBank=128)
    for i in range(6):
        m[0x10+i] = 0
        m[0x17+i] = 0
        m[0x1f+i] = 0
        m[0x05a8+i] = 0
        m[0x063d+i] = (i*0x41+offscreen)&255
    for i,kind,enemy_state,active,mask,rectangle in (
        (max(slot-1,0),prior,otherstate,priorflag,othervisible,second),
        (slot,eid,state,1,visible,first),
    ):
        for at,value in ((0x10,active),(0x17,kind),(0x1f,enemy_state),(0x05a8,mask)):
            m[at+i] = value
        at = 0x065c+4*i
        m[at:at+4] = bytes(rectangle)
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    return cpu_at(m,CALL,252,flags,x=slot,y=90)


def at_join(c):
    return D.bank_pc(c)==(128,COMPARE_DONE)


def state(c):
    m = c.memory
    return (semantic(c),live_stack(c),bytes(m[D.SMC]),
            tuple((i,v) for i,v in m.writes if not 0x100<=i<0x200 or 0x15a<=i<0x17b))


def direct(before,after):
    seeds = Q.cold([P.bundle(q) for q in (before,after)])[0]
    stats = Counter()

    def check(role,**kw):
        results = []
        for seed in seeds:
            c = actor_fixture(seed,**kw)
            visited = Counter()
            def watch(z):
                if D.bank_pc(z) in ((254,BOX),(254,END)):
                    visited[z.pc] += 1
            run(c,at_join,watch)
            results.append((state(c),visited,c.processorCycles))
        a,b = results
        assert a[:-1]==b[:-1],(role,kw,a[1],b[1],
                              [(i,len(x) if hasattr(x,'__len__') else x,len(y) if hasattr(y,'__len__') else y)
                               for i,(x,y) in enumerate(zip(a[0],b[0],strict=True)) if x!=y])
        stats[role,a[-1]-b[-1]] += 1

    for eid,side in product(range(256),(0,1)):
        check('id',slot=2,eid=eid if side else 6,prior=6 if side else eid)
    for slot,area,frame,flag,mask,nibble in product(range(6),range(4),(0,1),(0,1,128),(0,0x40),(0,15,255)):
        check('admission',slot=slot,eid=6,prior=6,area=area,frame=frame,priorflag=flag,
              othervisible=mask,offscreen=nibble,visible=mask if frame==0 else 0,
              flags=0xe1 if slot&1 else 0x24)
    boxes = ((103,155,117,171),(117,155,130,171),(117,171,130,183),
             (107,159,113,164),(0,0,0,0),(255,255,255,255),(250,0,7,17),
             (0,248,12,3),(250,250,7,10),(9,158,26,172))
    for first,second,state0,state1 in product(boxes,boxes,(0,0x20,0x80),(0,0x20,0x80)):
        check('rectangles_and_reaction',slot=3,eid=0,prior=6,first=first,second=second,
              state=state0,otherstate=state1)
    return [[role,saving,count] for (role,saving),count in sorted(stats.items())]


def whole(before,after):
    return Q.whole(before,after)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=True)
    before = Q.BASE.read_bytes()
    after,p,labels,caller = link(before,out)
    print('Link',P.sha(after),labels,flush=True)
    unit = direct(before,after)
    print('Actual caller paths',sum(row[2] for row in unit),flush=True)
    frames = whole(before,after)
    inputs = (Path(__file__),SOURCE,R/'src/collision.s',R/'src/object.s',R/'src/game.s',Q.LATE)
    receipt = dict(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                   patches=[p],labels=labels,source_ingress=caller,actual_caller_cases=unit,whole_GameLoop=frames,
                   bindings={str(path.resolve()):P.sha(path.read_bytes()) for path in inputs})
    receipt['supersedes'] = dict(image='f9061c90c210233f284b1c0e31665f94130235d923de323ccd11dae0240947a9',
                                 reason='Initial external branch encoding reached predecessor NOP at $98C7, costing two cycles on parity and water rejection.')
    (out/'proof-v2.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':
    main()
