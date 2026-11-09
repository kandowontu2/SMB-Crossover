"""Exercise real IRQ/FF boundaries on the two funded OAM lanes."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import measure_mini_goomba_funded_1108_v2 as B

P,N,OUT=B.P,B.N,B.OUT
CPU=N.NesMPU


def main():
    manifest_path=OUT/'goomba-funded-v2.json'
    grant=json.loads(manifest_path.read_text());raw=P.ROM.read_bytes();assert P.sha(raw)==P.PIN==grant['base_SHA256']
    new=bytearray(raw)
    for row in grant['patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex'])
        assert new[at:at+len(old)]==old
        new[at:at+len(old)]=after
    assert P.sha(new)==grant['expected_memory_only_SHA256']
    b=P.bundle(new);counts=Counter();deepest={}; min_fore=255; min_isr=255

    def clone(c):
        m=N.fork(c.memory);z=CPU(memory=m,pc=c.pc);z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        return z

    def snapshot(c):
        m=c.memory
        return (c.a,c.x,c.y,c.p&0xef,c.sp,tuple(m.rawtags),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'),
                bytes(m[3:13]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),bytes(m[0x200:0x304]),
                N.get(m,'CurrentOAMOffset'),N.get(m,'GuestOamRotationActive'),N.get(m,'RgOamRotation'),
                tuple(bytes(x) for x in m.ram))

    def interrupt(c,kind,collect=False):
        nonlocal min_isr
        z=clone(c); ret=(z.pc,z.sp); before=snapshot(z);last=len(z.memory.writes)
        if kind=='lag_NMI':
            assert N.get(z.memory,'NmiDisable')==255;z.nmi()
        else:
            assert not z.p&4;z.irq()
        for _ in range(15000):
            if (z.pc,z.sp)==ret:break
            min_isr=min(min_isr,z.sp)
            if collect and not z.p&4:
                tag=z.memory.rawtags[(z.pc-0x8000)//8192] if z.pc>=0x8000 else -1
                key=(tag,z.pc,N.get(z.memory,'SelectedCharacter'))
                if key not in deepest or z.sp<deepest[key].sp:deepest[key]=clone(z)
            assert z.memory[z.pc];z.step()
        else:raise AssertionError(('actual ISR did not return',kind,ret,hex(z.pc)))
        assert snapshot(z)==before,('live render context changed',kind,ret)
        assert not any(0x200<=at<0x304 or at==0x4014 for at,_ in z.memory.writes[last:])
        counts[kind]+=1

    for scenario,p in product(['clear_mario','clear_megaman','fast','rotated','full','clipped','override','foreign'],[0x21,0x25]):
        m=B.init(b)
        owner=0 if scenario=='clear_mario' else 3 if scenario in ('clear_megaman','foreign') else 41
        N.put(m,SelectedCharacter=owner,GameEngineSubroutine=8,OperMode=1,FamilyMainCommit=1,
              NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30,Mirror_PPUCTRL=160,
              CurrentOAMOffset=248 if scenario=='full' else 4,GuestOamRotationActive=1,
              RgOamRotation=252 if scenario=='rotated' else 0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
        m[0x200:0x304]=bytes((17*i+31)&255 for i in range(0x104))
        for name,v in [('PlayerFacingDir',1),('SprObject_X_Position',248 if scenario=='clipped' else 128),
                       ('SprObject_PageLoc',0),('SprObject_Y_Position',176),('SprObject_Y_HighPos',1),
                       ('ObjectVerticalFlip',0),('SprObject_SprAttrib',0x20)]:P.write(m,name,v,1)
        if scenario=='override':P.write(m,'HpNativeDrawHi',0xaf,1);P.write(m,'HpNativeDrawLo',0x2f,1)
        is_clear=scenario.startswith('clear')
        c=CPU(memory=m,pc=B.CLEAR-2 if is_clear else B.WORKER)
        c.a,c.x,c.y,c.p,c.sp=83,0 if is_clear else 0x67,1,p,219
        if not is_clear:c.stPushWord(0x5aff)
        seen=set()
        for _ in range(1000):
            if c.pc==(B.CONTINUE if is_clear else 0x5b00):break
            relevant=(B.CLEAR<=c.pc<B.WORKER or B.SHARED_CLEAR<=c.pc<=B.SHARED_CLEAR+192 if is_clear
                      else B.WORKER<=c.pc<B.CONTINUE or P.SHARED_OAM<=c.pc<0xbf33)
            if relevant and c.pc not in seen:
                seen.add(c.pc);min_fore=min(min_fore,c.sp)
                interrupt(c,'lag_NMI',collect=True)
                if not c.p&4:interrupt(c,'IRQ')
            assert m[c.pc];c.step()
        else:raise AssertionError(('foreground bound',scenario,hex(c.pc)))
        assert c.sp==219
    for cut in deepest.values():interrupt(cut,'nested_IRQ')
    assert min_isr>0x7a
    receipt=dict(passed=True,source_only=True,ROM_written=False,base_SHA256=P.PIN,memory_only_SHA256=P.sha(new),
                 cuts=dict(counts),nested_distinct=len(deepest),minimum_foreground_SP=min_fore,minimum_ISR_SP=min_isr,
                 protected='Live stack, AXYP, maps, SMC, scratch3..12, full OAM and overrun bytes through303. No FF/IRQ OAM writes or DMA.',
                 bindings={str(p):P.sha(p.read_bytes()) for p in [Path(__file__),manifest_path,P.R/'src/reset.s',P.R/'src/metasprite_engine.s',P.ROM]})
    (OUT/'goomba-funded-async-v3.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['passed','cuts','minimum_foreground_SP','minimum_ISR_SP']}),flush=True)


if __name__=='__main__':main()
