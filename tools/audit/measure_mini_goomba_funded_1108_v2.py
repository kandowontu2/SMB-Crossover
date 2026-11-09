"""Same-bank ordinary-Goomba proposal funded by an identical native OAM clear."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import subprocess

import measure_mini_goomba_oam_1108_v1 as P

N,R,OUT=P.N,P.R,P.OUT
CLEAR=0xa032
SHARED_CLEAR=0xa32c
CONTINUE=0xa0f2
WORKER=0xa038
EXTENT=CONTINUE-CLEAR
HIDE=bytes(k for i in range(64) for k in [0x8d,4*i,2])
off=lambda pc:16+4*8192+pc-0xa000


def assemble(b):
    first=' lda SelectedCharacter\n cmp #41\n bne Native\n'
    assert P.SOURCE.count(first)==1
    source=P.SOURCE.replace(first,'').replace('MiniGoombaDraw:\n','MiniGoombaDraw:\n'+first)
    stem=OUT/'funded-goomba';src=stem.with_suffix('.s');cfg=stem.with_suffix('.cfg')
    src.write_text(''.join(f'{n}=${P.address(b,n):04x}\n' for n in P.NAMES)+
                   f'DrawMetasprite=${P.ORIGINAL:04x}\nSharedOAM=${P.SHARED_OAM:04x}\nSharedPost=${P.SHARED_POST:04x}\n'+source)
    cfg.write_text(f'MEMORY{{T:start=${WORKER:04x},size=${CONTINUE-WORKER:04x},file=%O;}}SEGMENTS{{TEST:load=T,type=ro;}}\n')
    cc=R/'tools/Windows/cc65/bin';obj=stem.with_suffix('.o');blob=stem.with_suffix('.bin')
    subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',blob],check=True)
    obj.unlink()
    return blob.read_bytes(),src


def control(op,pc):return bytes([op,pc&255,pc>>8])


def bind(raw,body):
    assert raw[off(CLEAR):off(CONTINUE)]==HIDE and raw[off(SHARED_CLEAR):off(SHARED_CLEAR)+192]==HIDE
    assert raw[off(CLEAR)-2:off(CLEAR)]==bytes.fromhex('a9f8')
    assert raw[off(CONTINUE):off(CONTINUE)+3]==bytes.fromhex('8ede06')
    assert raw[off(SHARED_CLEAR)+192]==0x60
    changes=[(CLEAR,HIDE,(control(0x20,SHARED_CLEAR)+control(0x4c,CONTINUE)+body).ljust(EXTENT,b'\xea'))]
    changes.extend((pc,control(0x20,P.ORIGINAL),control(0x20,WORKER)) for pc in P.SITES)
    new=bytearray(raw)
    for pc,old,after in changes:
        at=off(pc);assert raw[at:at+len(old)]==old and len(old)==len(after)
        new[at:at+len(after)]=after
    return bytes(new),[dict(physical_PRG=4,CPU_half_open=[pc,pc+len(old)],file_offset=off(pc),old_hex=old.hex(),new_hex=after.hex())
                       for pc,old,after in changes]


def init(b):
    m=N.Bus(b);m.raw_page(1,132);N.put(m,CurrentBank=132)
    return m


def ownership(b):
    raw=b['raw']; bank4=raw[off(0xa000):off(0xc000)]
    # No 16-bit jump/JSR operand anywhere in bank4 names the removed interior.
    # The dynamic offset clear in source refers to the retained OAMClear copy.
    absolute=[(0xa000+i,bank4[i],int.from_bytes(bank4[i+1:i+3],'little')) for i in range(len(bank4)-2)
              if bank4[i] in [0x20,0x4c] and CLEAR<=int.from_bytes(bank4[i+1:i+3],'little')<CONTINUE]
    assert not absolute,absolute
    refs=[]
    for n,s in b['syms'].items():
        try:a=P.address(b,n); i=P.location(b,n)
        except (ValueError,KeyError,TypeError):continue
        if (i-16)//8192==4 and CLEAR<=a<CONTINUE:refs.append([n,a])
    assert not refs,refs
    engine=(R/'src/metasprite_engine.s').read_text()
    assert '::MmReserveClear:' in engine and 'adc #<OAMClear' in engine and 'OAMClear:\n.repeat 64, I' in engine
    assert (R/'src/megaman_weapons.s').read_text().count('jmp MmReserveClear')==2
    return dict(original_strip=[CLEAR,CONTINUE],retained_strip=[SHARED_CLEAR,SHARED_CLEAR+192],
                direct_absolute_JSR_JMP_or_symbol_ingress_into_old_interior=absolute+refs,
                source_refs='Two existing MegaMan/Proto JMPs target preserved MmReserveClear at A030. Dynamic tail clear computes an offset into retained OAMClear at A32C.')


def clear_test(bundles):
    count=0; span=[]
    for x,y,flags in product([0,4,64,252,255],[0,7,255],[0x20,0x31,0x74,0xf1]):
        pair=[]
        for b in bundles:
            m=init(b);m[0x200:0x300]=bytes(range(256))
            c=N.NesMPU(memory=m,pc=CLEAR-2);c.a,c.x,c.y,c.p,c.sp=73,x,y,flags,239
            for _ in range(1000):
                if c.pc==CONTINUE:break
                c.step()
            else:raise AssertionError(('clear bound',hex(c.pc)))
            pair.append((P.state(m),(c.a,c.x,c.y,c.p,c.sp),[(a,v) for a,v in m.writes if 0x200<=a<0x300],c.processorCycles))
        assert pair[0][:-1]==pair[1][:-1],(x,y,flags)
        assert pair[0][2][-64:]==[(0x200+4*i,248) for i in range(64)]
        span.append(pair[1][-1]-pair[0][-1]);count+=1
    assert set(span)=={15}
    return dict(paired_clear_cases=count,native_clear_cycles_added=15)


def compare_draw(bundles):
    init_buses=[init(b) for b in bundles]
    direct=Counter();fallback=Counter();foreign=Counter()
    basic=[(0x67+pose,1+face,1,41,8,0,0,1,rot,cur,128,176,0,1,0x20)
           for pose,face,rot,cur in product(range(2),range(2),range(0,256,4),range(0,256,4))]
    edges=[(pose,face,slot,41,8,flip,dyn,rotactive,rot,cur,x,y,page,high,attr)
           for (x,y,page,high),(flip,dyn,attr),(pose,face),(rotactive,rot,cur),slot in product(
               [(247,247,0,1),(248,176,0,1),(255,176,0,1),(120,248,0,1),(120,255,0,1),
                (80,80,1,1),(80,80,255,1),(80,80,0,0),(80,80,0,2),(80,80,0,1)],
               [(0,0,8),(0x80,0,3),(0,1,3),(16,0,0xff)],[(0x67,1),(0x68,2)],
               [(0,0,0),(1,4,252),(1,253,247),(1,252,240)], [1,6])]
    others=[(pose,face,slot,owner,engine,0,0,1,4,4,80,160,0,1,3)
            for pose,face,slot,owner,engine in product([0x66,0x67,0x68,0x69],[1],[0,1,7],range(42),[5,8])]

    def foreign_ingress(m,pc,pose,slot,p):
        # Native first LDA/LSR overwrites A/N/Z/C, before any alternate
        # Ryu/Samus flash leaf can need its own complete runtime scene.
        c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=0x57,pose,slot,p,237
        for _ in range(12):
            if c.pc==0xa3f5:break
            c.step()
        else:raise AssertionError(('foreign exact ingress bound',hex(c.pc)))
        return dict(regs=[c.a,c.x,c.y,c.p,c.sp],OAM=[],cycles=c.processorCycles)

    for i,case in enumerate(others+edges+basic):
        pose,face,slot,owner,engine,flip,dyn,active,rotate,cur,x,y,page,high,attr=case
        results=[]
        for m0,pc in zip(init_buses,[P.ORIGINAL,WORKER]):
            m=N.fork(m0)
            N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,CurrentOAMOffset=cur,
                  GuestOamRotationActive=active,RgOamRotation=rotate,ScreenLeft_X_Pos=0,
                  ScreenLeft_PageLoc=0,RlOutlineBypass=0)
            for n,v in [('PlayerFacingDir',face),('SprObject_X_Position',x),('SprObject_PageLoc',page),
                        ('SprObject_Y_Position',y),('SprObject_Y_HighPos',high),('ObjectVerticalFlip',flip),
                        ('SprObject_SprAttrib',attr)]:P.write(m,n,v,slot)
            if dyn:
                P.write(m,'HpNativeDrawHi',0xaf,slot);P.write(m,'HpNativeDrawLo',0x2f,slot)
            m[0x200:0x304]=bytes((17*i+31)&255 for i in range(0x104))
            runner=foreign_ingress if owner!=41 else P.routine
            try:z=runner(m,pc,pose,slot,0x71 if i&1 else 0x30)
            except AssertionError as exc:raise AssertionError(('case',case,hex(pc))) from exc
            results.append((z,P.state(m)))
        (a,sa),(b,sb)=results
        assert a['regs']==b['regs'] and a['OAM']==b['OAM'] and sa==sb,(case,a,b)
        group=foreign if owner!=41 else fallback if 'a3f1' in b['hits'] else direct
        group[a['cycles']-b['cycles']]+=1
    return dict(direct=dict(direct),fallback=dict(fallback),foreign=dict(foreign))


def mains(bundles):
    rows=[]
    for actors in [0,1,3,5]:
        pair=[P.fixture(b,actors,False,True) for b in bundles]
        for frame in range(2,10):
            results=[]
            for m in pair:
                N.put(m,FrameCounter=frame,SavedJoypadBits=0,SavedJoypad1Bits=0,
                      VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                results.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
            assert all(results[0][k]==results[1][k] for k in ['A','X','Y','P'])
            assert P.state(pair[0])==P.state(pair[1]),(actors,frame)
            rows.append([actors,frame,results[0]['CPU'],results[1]['CPU']])
    return rows


def main():
    raw=P.ROM.read_bytes();assert P.sha(raw)==P.PIN
    b=P.bundle(raw); closure=ownership(b);code,src=assemble(b)
    assert len(code)<=CONTINUE-WORKER
    after,patches=bind(raw,code);pair=[b,P.bundle(after)]
    clears=clear_test(pair);frames=mains(pair);print('native paired Main and clear',clears,flush=True)
    draws=compare_draw(pair)
    receipt=dict(passed=True,ROM_written=False,source_only=True,base_SHA256=P.PIN,
                 expected_memory_only_SHA256=P.sha(after),patches=patches,whole_Main=frames,
                 control_ingress=closure,source_SHA256=P.sha(src.read_bytes()),worker_bytes=len(code),
                 measured_draws=draws,clear=clears,descriptors=P.prove_art(b),
                 scope='Exact existing clear strip deduplication funds one same-bank Mini Goomba worker. Direct and fallback full final state and ordered OAM writes exact. Actual IRQ/FF cut proof and Mesen pending.')
    (OUT/'goomba-funded-v2.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k]for k in ['passed','expected_memory_only_SHA256','worker_bytes','measured_draws','clear']}),flush=True)


if __name__=='__main__':main()
