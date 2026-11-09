"""Actual native IRQ, lag NMI and nested cuts for the Mini-only shuffle path."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import check_mini_only_goomba_1108_v5 as C

D,B,P,N,R,OUT=C.D,C.B,C.P,C.N,C.R,C.OUT
CPU=N.NesMPU


def main():
    images,q=C.build_images();b=images[1]
    qualified=json.loads((OUT/'CPU.json').read_text())
    assert qualified['passed'] and qualified['memory_only_SHA256']==q['expected_memory_only_SHA256']
    deepest={};counts=Counter();fore_low=255;isr_low=255

    def clone(c):
        z=CPU(memory=N.fork(c.memory),pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        return z

    def snapshot(c):
        m=c.memory
        return (c.a,c.x,c.y,c.p&0xef,c.sp,tuple(m.rawtags),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'),
                bytes(m[3:13]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),bytes(m[0x200:0x304]),
                N.get(m,'CurrentOAMOffset'),N.get(m,'GuestOamRotationActive'),N.get(m,'RgOamRotation'),
                N.get(m,'SpriteShuffleOffset'),tuple(bytes(x) for x in m.ram))

    def interrupt(c,kind,collect=False):
        nonlocal isr_low
        z=clone(c);ret=(z.pc,z.sp);before=snapshot(z);last=len(z.memory.writes)
        if kind=='lag_NMI':
            assert N.get(z.memory,'NmiDisable')==255;z.nmi()
        else:
            assert not z.p&4;z.irq()
        for _ in range(15000):
            if (z.pc,z.sp)==ret:break
            isr_low=min(isr_low,z.sp)
            if collect and not z.p&4:
                tag=z.memory.rawtags[(z.pc-0x8000)//8192] if z.pc>=0x8000 else -1
                key=(tag,z.pc,N.get(z.memory,'SelectedCharacter'))
                if key not in deepest or z.sp<deepest[key].sp:deepest[key]=clone(z)
            assert z.memory[z.pc];z.step()
        else:raise AssertionError(('actual interrupt bound',kind,ret,hex(z.pc)))
        assert snapshot(z)==before,('live draw state changed',kind,ret)
        assert not any(0x200<=at<0x304 or at==0x4014 for at,_ in z.memory.writes[last:])
        counts[kind]+=1

    fixture=P.fixture(b,0,False,False)
    for scene,parity,p in product(['clear_Mario','clear_Mega','fast','clipped','full','lift','firebar','ordinary'],[0,1],[0x21,0x25]):
        m=N.fork(fixture);m.raw_page(1,132);N.put(m,CurrentBank=132)
        owner=0 if scene=='clear_Mario' else 3 if scene=='clear_Mega' else 41
        N.put(m,SelectedCharacter=owner,GameEngineSubroutine=8,OperMode=1,FamilyMainCommit=1,
              NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30,Mirror_PPUCTRL=160,
              CurrentOAMOffset=248 if scene=='full' else 4,GuestOamRotationActive=1,
              RgOamRotation=252,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,
              ScreenRight_PageLoc=0,SpriteShuffleOffset=17,FrameCounter=parity)
        m[0x200:0x304]=bytes((17*i+31)&255 for i in range(0x104))
        m[P.address(b,'ObjectMetasprite'):P.address(b,'ObjectMetasprite')+24]=[0]*24
        for i in range(6):P.write(m,'Enemy_Flag',0,i);P.write(m,'Enemy_ID',0,i)
        P.write(m,'ObjectMetasprite',0x66 if scene=='ordinary' else 0x67,1)
        for name,v in [('PlayerFacingDir',1),('SprObject_X_Position',248 if scene=='clipped' else 128),
                       ('SprObject_PageLoc',0),('SprObject_Y_Position',176),('SprObject_Y_HighPos',1),
                       ('ObjectVerticalFlip',0),('SprObject_SprAttrib',0x20)]:P.write(m,name,v,1)
        if scene=='lift':
            for n,v in [('Enemy_Flag',1),('Enemy_ID',0x25),('Enemy_State',0x60),('Enemy_BoundBoxCtrl',5)]:P.write(m,n,v)
            N.invoke(m,'HpPrepareNativePointers',x=0,y=0)
        if scene=='firebar':
            N.put(m,ObjectOffset=2)
            for n,v in [('Enemy_Flag',1),('Enemy_ID',0x1b),('Enemy_State',0),('Enemy_X_Position',140),
                        ('Enemy_PageLoc',0),('Enemy_Y_Position',112),('Enemy_Y_HighPos',1),
                        ('FirebarSpinState_High',0),('FirebarSpinState_Low',0)]:P.write(m,n,v,2)
            N.invoke(m,'ProcFirebar',x=2,y=0)
        is_clear=scene.startswith('clear_')
        c=CPU(memory=m,pc=B.CLEAR-2 if is_clear else D.ENTRY);c.a,c.x,c.y,c.p,c.sp=83,0,1,p,219
        seen=set()
        for _ in range(20000):
            if c.pc==(B.CONTINUE if is_clear else D.AFTER_LOOP):break
            mapped=c.pc>=0xa000 and c.pc<0xc000 and m.rawtags[1]==132
            if is_clear:watched=B.CLEAR<=c.pc<D.ENTRY or B.SHARED_CLEAR<=c.pc<=B.SHARED_CLEAR+192
            else:watched=D.ENTRY<=c.pc<B.CONTINUE or D.NATIVE_RENDER<=c.pc<0xa4f6
            if mapped and watched and c.pc not in seen:
                seen.add(c.pc);fore_low=min(fore_low,c.sp)
                interrupt(c,'lag_NMI',collect=True)
                if not c.p&4:interrupt(c,'IRQ')
            assert m[c.pc];c.step()
        else:raise AssertionError(('foreground bound',scene,hex(c.pc)))
        assert c.sp==219 and seen
    for cut in deepest.values():interrupt(cut,'nested_IRQ')
    assert isr_low>0x7a
    receipt=dict(passed=True,source_only=True,ROM_written=False,base_SHA256=D.PIN,
                 memory_only_SHA256=q['expected_memory_only_SHA256'],cuts=dict(counts),
                 nested_distinct=len(deepest),minimum_foreground_SP=fore_low,minimum_ISR_SP=isr_low,
                 protected='Live stack, AXYP, maps, SMC, scratch3..12, exact OAM through303, no lag DMA; complete shared native fallback and static area state unchanged.',
                 bindings={str(p):P.sha(p.read_bytes()) for p in [Path(__file__),OUT/'proposal.json',OUT/'CPU.json',
                           R/'src/reset.s',R/'src/metasprite_engine.s',P.ROM]})
    (OUT/'async.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['passed','cuts','minimum_foreground_SP','minimum_ISR_SP']}),flush=True)


if __name__=='__main__':main()
