"""Prove exact Mini-only shuffle/OAM behavior on the installed fc7d proposal."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import measure_mini_only_goomba_1108_v4 as D

B,P,N,R,OUT=D.B,D.P,D.N,D.R,D.OUT


def build_images():
    path=OUT/'proposal.json';q=json.loads(path.read_text());raw=P.ROM.read_bytes();assert P.sha(raw)==D.PIN
    after=bytearray(raw)
    for z in q['patches']:
        at=z['file_offset'];old=bytes.fromhex(z['old_hex']);new=bytes.fromhex(z['new_hex'])
        assert after[at:at+len(old)]==old and len(old)==len(new)
        after[at:at+len(new)]=new
    assert P.sha(after)==q['expected_memory_only_SHA256']
    return [P.bundle(raw),P.bundle(after)],q


def direct(images,labels):
    seeds=[B.init(b) for b in images];counts=Counter();speed=Counter()
    cases=[]
    for pose,face,rotation,cursor in product([0x67,0x68],[0,1,2,3],range(0,256,4),[0,4,124,240,244,248,252]):
        cases.append((pose,face,1,1,rotation,cursor,128,176,0,1,0,0,0x20))
    for slot,px,py,mode,cursor in product([1,6,7,23],[(247,0),(248,0),(0,255),(7,1)],[(247,1),(248,1),(15,0),(8,2)],
                                          [(0,0,0x23),(0,1,0x03),(0x80,0,0xff),(8,0,0x08)], [0,247]):
        x,page=px;y,high=py;flip,dyn,attr=mode
        cases.append((0x68,2,slot,1,253,cursor,x,y,page,high,flip,dyn,attr))
    for i,(pose,face,slot,active,rotation,cursor,x,y,page,high,flip,dyn,attr) in enumerate(cases):
        pair=[N.fork(m) for m in seeds];results=[]
        for m,pc in zip(pair,[P.ORIGINAL,labels['MiniGoomba']]):
            N.put(m,SelectedCharacter=41,GameEngineSubroutine=8,CurrentOAMOffset=cursor,
                  GuestOamRotationActive=active,RgOamRotation=rotation,ScreenLeft_X_Pos=0,
                  ScreenLeft_PageLoc=0,RlOutlineBypass=0)
            for n,v in [('PlayerFacingDir',face),('SprObject_X_Position',x),('SprObject_PageLoc',page),
                        ('SprObject_Y_Position',y),('SprObject_Y_HighPos',high),('ObjectVerticalFlip',flip),
                        ('SprObject_SprAttrib',attr)]:P.write(m,n,v,slot)
            if dyn and slot<7:
                P.write(m,'HpNativeDrawHi',0xaf,slot);P.write(m,'HpNativeDrawLo',0x2f,slot)
            m[0x200:0x304]=bytes((17*j+31)&255 for j in range(0x104))
            z=P.routine(m,pc,pose,slot,0x71 if i&1 else 0x30)
            results.append(z)
        a,b=results
        assert (a['regs'],a['OAM'],P.state(pair[0]))==(b['regs'],b['OAM'],P.state(pair[1])),(cases[i],a,b)
        name='fallback' if 'a3f1' in b['hits'] else 'clipped' if 'a5ba' in b['hits'] else 'direct'
        counts[name]+=1;speed[(name,a['cycles']-b['cycles'])]+=1
    return dict(cases=dict(counts),savings=[[kind,n,c] for (kind,n),c in speed.items()])


def shuffle(images,labels):
    counts=Counter();results=Counter();trace_sig=[]
    seeds=[P.fixture(b,0,False,False) for b in images]
    for seed in seeds:
        seed.raw_page(1,132);N.put(seed,CurrentBank=132)
    for shuffle,parity,scene in product(range(24),[0,1],['empty','sparse','five','lift','firebar','misc']):
        pair=[N.fork(m) for m in seeds];data=[]
        for m,pc in zip(pair,[D.NATIVE_LOOP,D.ENTRY]):
            b=m.bundle
            N.put(m,SelectedCharacter=41,GameEngineSubroutine=8,CurrentOAMOffset=4,
                  GuestOamRotationActive=1,RgOamRotation=248,ScreenLeft_X_Pos=0,
                  ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,
                  SpriteShuffleOffset=shuffle,FrameCounter=parity,RlOutlineBypass=0)
            m[P.address(b,'ObjectMetasprite'):P.address(b,'ObjectMetasprite')+24]=[0]*24
            for slot in range(6):P.write(m,'Enemy_Flag',0,slot);P.write(m,'Enemy_ID',0,slot)
            slots={'empty':[],'sparse':[1,4],'five':[1,2,3,4,5],'lift':[1,4],'firebar':[1,4],'misc':[1,4,8,18]}[scene]
            for slot in slots:
                pose=0x67+slot%2 if slot<7 else (0 if slot==8 else 0xff)
                P.write(m,'ObjectMetasprite',pose,slot)
                for n,v in [('PlayerFacingDir',1+slot%2),('SprObject_X_Position',80+slot*11),('SprObject_PageLoc',0),
                            ('SprObject_Y_Position',160+slot),('SprObject_Y_HighPos',1),('ObjectVerticalFlip',0),
                            ('SprObject_SprAttrib',slot%4)]:P.write(m,n,v,slot)
            if scene=='lift':
                for n,v in [('Enemy_Flag',1),('Enemy_ID',0x25),('Enemy_State',0x60),('Enemy_BoundBoxCtrl',5)]:P.write(m,n,v,3)
                N.invoke(m,'HpPrepareNativePointers',x=0,y=0)
                assert m[P.address(b,'HpNativeDrawHi')+4]!=0
            if scene=='firebar':
                N.put(m,ObjectOffset=3)
                for n,v in [('Enemy_Flag',1),('Enemy_ID',0x1b),('Enemy_State',0),('Enemy_X_Position',140),
                            ('Enemy_PageLoc',0),('Enemy_Y_Position',112),('Enemy_Y_HighPos',1),
                            ('FirebarSpinState_High',0),('FirebarSpinState_Low',0)]:P.write(m,n,v,3)
                N.invoke(m,'ProcFirebar',x=3,y=0)
            m[0x200:0x304]=[248,0,0,0]*65;m.writes.clear()
            c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,7,91,0x31,225
            draws=[];minimum=c.sp
            for _ in range(20000):
                if c.pc==D.AFTER_LOOP:break
                if c.pc in [P.ORIGINAL,labels['MiniGoomba']]:
                    if c.pc!=P.ORIGINAL or not draws or draws[-1][0]!=c.y:draws.append((c.y,c.x))
                if c.pc==P.address(b,'WorldFirebarDrawAdmission'):draws.append((0,-1))
                minimum=min(minimum,c.sp)
                assert m[c.pc],(scene,shuffle,parity,hex(c.pc));c.step()
            else:raise AssertionError(('shuffle bound',scene,shuffle,parity,hex(c.pc)))
            writes=[(a,v) for a,v in m.writes if 0x200<=a<0x304]
            data.append(((c.a,c.x,c.y,c.p,c.sp),P.state(m),writes,draws,c.processorCycles,minimum))
        a,b=data
        assert a[:4]==b[:4],(scene,shuffle,parity,a[0],b[0],a[3],b[3])
        assert a[3].count((0,-1))==1
        counts[scene]+=1;results[(scene,a[4]-b[4])]+=1
        if shuffle==0:trace_sig.append([scene,parity,a[3],len(a[2]),a[4],b[4],a[5],b[5]])
    return dict(cases=dict(counts),savings=[[k,n,c] for (k,n),c in results.items()],examples=trace_sig)


def main():
    images,q=build_images()
    clear=B.clear_test(images)
    whole=B.mains(images)
    print('whole',whole,flush=True)
    order=shuffle(images,q['labels']);print('shuffle',order['cases'],flush=True)
    leaf=direct(images,q['labels'])
    receipt=dict(passed=True,CPU_only=True,ROM_written=False,base_SHA256=D.PIN,memory_only_SHA256=q['expected_memory_only_SHA256'],
                 whole_GameCore=whole,ordered_shuffle=order,leaf=leaf,clear=clear,
                 foreign_actor_route='The delivered native InitObjectLoop and both visible-actor DrawMetasprite JSRs remain exact. The only new entry is existing Mini DrawFast far target; legacy full clear costs 15 cycles per draw sequence, not per actor.',
                 bindings={str(p):P.sha(p.read_bytes()) for p in [Path(__file__),Path(D.__file__),OUT/'proposal.json',R/'src/metasprite_engine.s',P.ROM]})
    (OUT/'CPU.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k]for k in ['passed','leaf','clear']}),flush=True)


if __name__=='__main__':main()
