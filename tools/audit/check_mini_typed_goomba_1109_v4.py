"""Rebase exact renderer pair and test actual vectors in Mini's typed draw."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import measure_mini_typed_goomba_1109_v3 as V

A,N,R,OUT=V.A,V.N,V.R,V.OUT
CURRENT=R/'build/mini-columns-transport-1109/candidate.nes'
PIN='ee9b3f55e010f7673a046e6dbc20b220b13cd83dcc95f95c799e6f9def565f6b'


def main():
    paths=[OUT/'measurement.json',OUT/'typed-goomba.json']
    rows=[json.loads(path.read_text())['patch'] for path in paths]
    raw=CURRENT.read_bytes()
    assert A.sha(raw)==PIN
    image=V.install(raw,rows)
    b=A.bundle(image)
    old=A.bundle(raw)
    shuffle=A.address(b,'SpriteShuffleOffset')

    class DrawBus(N.Bus):
        forbid_shuffle_read=False

        def __getitem__(self,address):
            if self.forbid_shuffle_read:
                assert address!=shuffle,'A native callee read the intermediate shuffle cursor'
            return super().__getitem__(address)

    old_bus=N.Bus
    N.Bus=DrawBus
    try:
        seed=A.fixture(b,0,False,False)
    finally:
        N.Bus=old_bus
    seed.raw_page(1,132)
    N.put(seed,CurrentBank=132,NmiDisable=255)
    deepest={}
    counts=Counter()
    minima=[255,255]

    def state(c):
        m=c.memory
        return (V.registers(c,0xef),V.live_stack(c),bytes(m[:13]),bytes(m[0x15a:0x17b]),
                bytes(m[0x200:0x304]),bytes(m[0x6000:0x8000]),tuple(m.rawtags),tuple(map(bytes,m.ram)),
                tuple(N.get(m,n) for n in ('CurrentBank','CurrentBankC','CurrentOAMOffset','RgOamRotation')),
                list.__getitem__(m,shuffle))

    def clone(c,original=False):
        m=V.slim_fork(c.memory)
        if original:
            m.bundle=old
            for index,tag in enumerate(m.rawtags[:]):m.raw_page(index,tag)
        z=N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=V.registers(c)
        return z

    def interrupt(c,kind):
        z=clone(c)
        before=state(z)
        ret=z.pc,z.sp
        if kind=='lag_FF':
            assert N.get(z.memory,'NmiDisable')==255
            z.nmi()
        else:
            assert not z.p&4
            z.irq()

        def visit(q):
            minima[1]=min(minima[1],q.sp)
            if kind=='lag_FF' and not q.p&4:
                tag=q.memory.rawtags[(q.pc-0x8000)//8192] if q.pc>=0x8000 else -1
                key=tag,q.pc
                if key not in deepest or q.sp<deepest[key].sp:deepest[key]=clone(q)

        V.run(z,lambda q:(q.pc,q.sp)==ret,visit)
        after=state(z)
        assert after[:5]==before[:5] and after[6:]==before[6:],(kind,ret,[i for i,(a,b) in enumerate(zip(after,before))if a!=b])
        if after[5]!=before[5]:
            assert kind=='lag_FF'
            ref=clone(c,original=True)
            ref.nmi()
            V.run(ref,lambda q:(q.pc,q.sp)==ret)
            assert state(ref)==after and ref.memory.writes==z.memory.writes
            counts['full_original_audio_SRAM_parity']+=1
        assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in z.memory.writes)
        counts[kind]+=1

    for phase,parity,scene,p in product([0,17],[0,1],['ordinary','clip','full','flash','firebar'],[0x20,0x24]):
        m=V.slim_fork(seed)
        N.put(m,SpriteShuffleOffset=phase,FrameCounter=parity,GuestOamRotationActive=1,RgOamRotation=248,
              CurrentOAMOffset=248 if scene=='full' else 4,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,
              ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,RlOutlineBypass=0)
        start=A.address(b,'ObjectMetasprite')
        m[start:start+24]=bytes(24)
        for i in [1,4]:
            for n,v in [('ObjectMetasprite',0x67+i%2),('PlayerFacingDir',1 if i==1 else 2),
                        ('SprObject_X_Position',247 if scene=='clip' else 100),('SprObject_PageLoc',0),
                        ('SprObject_Y_Position',174),('SprObject_Y_HighPos',1),('ObjectVerticalFlip',0),
                        ('SprObject_SprAttrib',0x28 if scene=='flash' else 0x20)]:
                V.D.P.write(m,n,v,i)
        if scene=='firebar':
            V.V.init(m,3,0x1b,1,41,1)
            N.put(m,SpriteShuffleOffset=phase,FrameCounter=parity)
        m.writes.clear()
        c=N.NesMPU(memory=m,pc=V.ENTRY)
        c.a,c.x,c.y,c.p,c.sp=83,7,23,p,211
        seen=set()

        def visit(z):
            if m.rawtags[1]==132 and z.pc==0xa051:
                m.forbid_shuffle_read=True
            if m.rawtags[1]!=132 or not (V.ENTRY<=z.pc<V.END or 0xbead<=z.pc<0xbf33):return
            key=z.pc,z.sp,z.p&4
            if key in seen:return
            seen.add(key)
            minima[0]=min(minima[0],z.sp)
            interrupt(z,'lag_FF')
            if not z.p&4:interrupt(z,'IRQ')

        V.run(c,lambda z:z.pc==V.AFTER_STORE,visit)
        assert c.sp==211 and m.forbid_shuffle_read and seen
    for c in deepest.values():interrupt(c,'nested_IRQ')
    assert minima[1]>0x7a and all(counts[n] for n in ['lag_FF','IRQ','nested_IRQ'])
    receipt=dict(passed=True,CPU_only=True,ROM_written=False,base_SHA256=PIN,memory_only_SHA256=A.sha(image),
                 actual_cuts=dict(counts),minimum_foreground_SP=minima[0],minimum_ISR_SP=minima[1],
                 scope='Exact bank71 and Mini-only bank4 compose over delivered ee9b. Every reached typed-draw cut with actual lag FF and IRQ, native clip/full/flash/firebar lanes and deepest lag-handler IRQ contexts. No intermediate shuffle cursor read by reached descendants or vectors. Full live stack/AXYP/SMC/maps/private SRAM/OAM strict.',
                 bindings={str(p):A.sha(p.read_bytes()) for p in [Path(__file__),Path(V.__file__),CURRENT,*paths,R/'src/reset.s',R/'src/metasprite_engine.s']})
    (OUT/'typed-goomba-current-vectors.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Current typed render',A.sha(image),'actual vectors',dict(counts),'minSP',minima,flush=True)


if __name__=='__main__':main()
