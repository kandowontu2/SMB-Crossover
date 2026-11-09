"""Qualify the exact world-render no-special admission without changing real draws."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_native_brick_coin_draw_1110_v1 as V
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at
from check_mini_visibility_dispatch_1110_v1 import memory


R,P,N=V.R,V.P,V.N
ROM=R/'build/mini-body-platform-native-1110/candidate.nes'
PIN='14a4e10058c683605344564d118202970da6ccae4482bf1dfca76b9ad743aacc'
SOURCE=R/'tools/reference/native_firebar_admission_1110_v1.s'
GIRDER=R/'build/native-girder-draw-1110/proof.json'
PROFILE=R/'build/mini-body-peak-1110/capture/instruction-sample.json'
ENTRY,LEGACY,FINISH=0xa261,0xba23,0xbea4
STOP=0x5b00
SCENE_START=0xa038
TYPES=set(range(0x1b,0x23))|{0x2b,0x2c}
FAST_IDS={i for i in range(256) if i&0xdc==4}


def compose(raw,out):
    funding=json.loads(GIRDER.read_text())
    assert funding['passed'] and funding['symbols']['WorkerEnd']==LEGACY
    for item in funding['patches']:
        V.preimage(raw,item['start'],bytes.fromhex(item['new_hex']))
    bank=raw[V.offset(0xa000):V.offset(0xa000)+8192]
    edges=[0xa000+i for i in range(len(bank)-2) if bank[i:i+3]==bytes.fromhex('2061a2')]
    assert edges==[0xa06d,0xa08d,0xa195,0xa1bf]
    for branch,caller in ((0xa05c,0xa06d),(0xa07b,0xa08d),(0xa179,0xa195),(0xa1a3,0xa1bf)):
        V.preimage(raw,branch,bytes((0xf0,caller-branch-2)))
    with tempfile.TemporaryDirectory(prefix='world-admit-',dir=out) as folder:
        tmp=Path(folder)
        cfg,obj,binary,labels=(tmp/f'admission.{s}' for s in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { A:start=$a261,size=$15,file=%O; L:start=$ba23,size=$14,file=%O; '
                       'F:start=$bea4,size=9,file=%O,fill=yes,fillval=$ea; } '
                       'SEGMENTS { ADMIT:load=A,type=ro; LEGACY:load=L,type=ro; FINISH:load=F,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',labels],check=True)
        code=binary.read_bytes()
        syms={cols[2][1:]:int(cols[1],16) for line in labels.read_text().splitlines()
              if len(cols:=line.split())==3}
    assert len(code)==50 and syms==dict(NoSpecialWorldDraw=ENTRY,LegacyWorldDraw=LEGACY,ClearFirebarSlot=FINISH)
    changes=[]
    for pc,old,new in (
        (ENTRY,bytes.fromhex('8d6a01a9018d6c01a9ad8d6d01a9c7205a014c85a2'),code[:21]),
        (LEGACY,b'\xea'*20,code[21:41]),
        (FINISH,b'\xea'*9,code[41:]),
    ):
        at=V.preimage(raw,pc,old)
        changes.append(dict(physical_PRG=4,start=pc,end_exclusive=pc+len(old),
                            file_offset=at,old_hex=old.hex(),new_hex=new.hex()))
    return install(raw,changes),changes,syms


def setup(b):
    m=N.fresh(b)
    m.raw_page(1,132)
    N.put(m,CurrentBank=132,NmiDisable=255,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
          DisableScreenFlag=0,Mirror_PPUMASK=30,SelectedCharacter=41,AreaType=0,
          Player_X_Position=24,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,
          ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,
          GuestOamRotationActive=1,RgOamRotation=204,CurrentOAMOffset=12,FrameCounter=5)
    for i in range(6):
        slot(m,'Enemy_ID',i,6 if i&1 else 0x25)
        slot(m,'Enemy_Flag',i,1)
    return m


def slot(m,name,index,value):
    m[P.address(m.bundle,name)+index]=value


def render(seed,entry=ENTRY,p=0x21,visit=None):
    m=slim_fork(seed)
    c=cpu_at(m,entry,234,p,x=0x31,y=0x59)
    c.a=0
    run(c,lambda q:(q.pc,q.sp)==(STOP,234),visit)
    oam=[(a,v) for a,v in m.writes if 0x200<=a<0x300]
    writes=[(a,v) for a,v in m.writes if not 0x17b<=a<0x200]
    return (registers(c,0xef),live_stack(c),memory(m),oam,writes,m.ram_writes),c.processorCycles


def fork_image(seed,b):
    m=slim_fork(seed)
    m.bundle=b
    m.raw_page(1,132)
    return m


def equal(a,b,fast):
    if not fast:
        assert a==b,(a[:2],b[:2],a[3:5],b[3:5])
        return
    assert a[:2]==b[:2] and a[3]==b[3] and a[5]==b[5],(a[:2],b[:2])
    left,right=a[2],b[2]
    assert left[:3]==right[:3] and left[4:]==right[4:]
    assert all(x==y or 0x15a+i in (0x162,0x16a,0x16c,0x16d,0x179)
               for i,(x,y) in enumerate(zip(left[3],right[3])))
    assert without_transport(a[4])==b[4],(a[4],b[4])


def without_transport(writes):
    prefix=[(0x16a,0),(0x16c,1),(0x16d,0xad),(0x162,199),(0x145,199),(0x5115,199)]
    start=next(i for i in range(len(writes)) if writes[i:i+len(prefix)]==prefix)
    end=start+len(prefix)
    assert writes[end]==(0x7eb4,255)
    assert writes[end+1][0]==0x179 and writes[end+2:end+4]==[(0x145,132),(0x5115,132)]
    return writes[:start]+[writes[end]]+writes[end+4:]


def exhaustive_admission(seed):
    # The gate reads six IDs and never uses flags. Exercise every ID/flag
    # pair in compiled code, across all positions over the flag sweep.
    m=slim_fork(seed)
    ident=P.address(m.bundle,'Enemy_ID')
    flag=P.address(m.bundle,'Enemy_Flag')
    reached=Counter()
    c=N.NesMPU(memory=m,pc=ENTRY)
    for i,v in product(range(256),repeat=2):
        index=v%6
        m[ident+index]=i
        m[flag+index]=v
        c.pc,c.a,c.x,c.y,c.p,c.sp=ENTRY,0,17,59,0x21,232
        for _ in range(55):
            if c.pc in (LEGACY,FINISH):
                break
            c.step()
        assert c.pc==(FINISH if i in FAST_IDS else LEGACY),(i,v,hex(c.pc))
        reached[c.pc]+=1
        m[ident+index]=6
        m[flag+index]=1
    assert not FAST_IDS&TYPES and len(FAST_IDS)==8
    return dict(pairs=sum(reached.values()),fast=reached[FINISH],legacy=reached[LEGACY])


def positive_seed(old,ident,index,x=110,rotate=1):
    m=setup(old)
    N.put(m,SelectedCharacter=18,FrameCounter=5,ObjectOffset=index,GuestOamRotationActive=rotate,
          AreaPointer=0x62,WorldNumber=1)
    for n,v in (('Enemy_ID',ident),('Enemy_Flag',1),('Enemy_State',0),('Enemy_X_Position',x),
                ('Enemy_PageLoc',0),('Enemy_Y_Position',112),('Enemy_Y_HighPos',1)):
        slot(m,n,index,v)
    if ident<0x23:
        N.invoke(m,'InitEnemyObject',x=index)
        N.invoke(m,'ProcFirebar',x=index)
        assert N.get(m,'FirebarPartCount',index) in (6,12),(ident,index,N.get(m,'FirebarPartCount',index))
    m.raw_page(1,132)
    N.put(m,CurrentBank=132,CurrentOAMOffset=12)
    return m


def qualifies(old,new):
    seed=setup(new)
    q=exhaustive_admission(seed)
    hist=Counter()
    positive=[]

    def pair(base,role,p=0x21,entry=ENTRY,fast=False):
        rows=[render(fork_image(base,b),entry,p) for b in (old,new)]
        a,b=rows
        equal(a[0],b[0],fast)
        hist[role,a[1]-b[1]]+=1
        return rows

    for indices in combinations(range(6),3):
        m=setup(old)
        for i in range(6):
            slot(m,'Enemy_ID',i,6 if i in indices else 0x25)
        pair(m,'three_goombas_three_lifts',fast=True)

    for ident,index in product(sorted(TYPES),(1,4)):
        m=positive_seed(old,ident,index)
        (a,b)=pair(m,'actual_firebar' if ident<0x23 else 'actual_small_lift')
        assert a[0][3] and b[0][3],(ident,index)
        positive.append(dict(id=ident,slot=index,OAM_writes=len(a[0][3]),
                             parts=N.get(m,'FirebarPartCount',index) if ident<0x23 else None))
        for flag,rotation in product((0,1,2,0x7f,0x80,0xff),(0,1,0x81)):
            slot(m,'Enemy_Flag',index,flag)
            N.put(m,GuestOamRotationActive=rotation)
            pair(m,'special_states',p=0xe5)

    for ident,index,flag in product(range(256),(0,2,5),(0,1,0x80)):
        m=setup(old)
        slot(m,'Enemy_ID',index,ident)
        slot(m,'Enemy_Flag',index,flag)
        pair(m,'foreign_direct',fast=ident in FAST_IDS)

    for owner,parity,shape in product((0,1,2,5,10,13,18,24,33,34,37,41),(0,1),('fast','firebar','small')):
        m=setup(old) if shape=='fast' else positive_seed(old,0x1b if shape=='firebar' else 0x2b,1)
        N.put(m,SelectedCharacter=owner,FrameCounter=parity)
        a,b=[render(fork_image(m,im),SCENE_START) for im in (old,new)]
        if shape=='fast':
            assert a[0][:4]==b[0][:4] and a[0][5]==b[0][5]
            assert without_transport(a[0][4])==b[0][4]
        else:
            equal(a[0],b[0],False)
        hist['whole_shuffled_world',a[1]-b[1]]+=1
    return dict(admission=q,comparisons=sum(hist.values()),positive_draws=positive,
                timings=[[role,delta,cases] for (role,delta),cases in sorted(hist.items())])


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=ROM.read_bytes()
    assert P.sha(raw)==PIN
    image,patches,syms=compose(raw,args.output)
    report=qualifies(P.bundle(raw),P.bundle(image))
    result=dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),
                patches=patches,symbols=syms,**report,
                bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),SOURCE,ROM,GIRDER,PROFILE)})
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','patches','positive_draws')}),flush=True)


if __name__=='__main__':
    main()
