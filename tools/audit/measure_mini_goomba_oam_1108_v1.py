"""Measure a scratch-linked native ordinary Goomba draw shortcut on Mini."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import subprocess

from profile_mini_busy_1108_v1 import R, ROM, PIN, N, address, bundle, location, sha, fixture

OUT=R/'build/mini-goomba-draw-1108-v1'
ENTRY=0x5b80
ORIGINAL=0xa3f1
SHARED_OAM=0xbed1
SHARED_POST=0xa4f1
SITES=[0xa188,0xa1b2]
NAMES=['SelectedCharacter','GameEngineSubroutine','HpNativeDrawHi','ObjectVerticalFlip',
       'PlayerFacingDir','SprObject_X_Position','SprObject_PageLoc','ScreenLeft_X_Pos',
       'ScreenLeft_PageLoc','SprObject_Y_Position','SprObject_Y_HighPos','SprObject_SprAttrib',
       'R0','R1','R3','R4','R5','R6','R7','M1','CurrentOAMOffset','RlOutlineBypass',
       'MetaspriteTableLeftLo','MetaspriteTableRightLo']
SOURCE='''
.setcpu "6502"
.segment "TEST"
MiniGoombaDraw:
 cpx #$67
 beq Actor
 cpx #$68
 bne Native
Actor:
 cpy #1
 bcc Native
 cpy #7
 bcs Native
 lda SelectedCharacter
 cmp #41
 bne Native
 lda GameEngineSubroutine
 cmp #8
 bne Native
 lda HpNativeDrawHi,y
 ora ObjectVerticalFlip,y
 ora RlOutlineBypass
 bne Native
 jmp Position
Native:
 jmp DrawMetasprite
Position:
 lda SprObject_X_Position,y
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda SprObject_PageLoc,y
 sbc ScreenLeft_PageLoc
 bne Native
 sta R5
 lda R4
 cmp #248
 bcs Native
 lda SprObject_Y_HighPos,y
 cmp #1
 bne Native
 sta R7
 lda SprObject_Y_Position,y
 cmp #248
 bcs Native
 sta R6
 lda SprObject_SprAttrib,y
 sta R3
 lda #0
 sta M1
 lda PlayerFacingDir,y
 lsr
 bne Left
 lda MetaspriteTableRightLo,x
 bne Pointer
Left:
 lda MetaspriteTableLeftLo,x
Pointer:
 sta R0
 lda #$af
 sta R1
 ; Both immutable pointers have the exact native two-part header 8.
 ; Rejoin native capacity/rotation/emission and the original flash tail.
 ldx CurrentOAMOffset
 lda #8
 jsr SharedOAM
 jmp SharedPost
'''


def compile_leaf(b):
    OUT.mkdir(exist_ok=True)
    stem=OUT/'ordinary-goomba';src=stem.with_suffix('.s');cfg=stem.with_suffix('.cfg')
    src.write_text(''.join(f'{n}=${address(b,n):04x}\n' for n in NAMES)+
                   f'DrawMetasprite=${ORIGINAL:04x}\nSharedOAM=${SHARED_OAM:04x}\nSharedPost=${SHARED_POST:04x}\n'+SOURCE)
    cfg.write_text('MEMORY{T:start=$5b80,size=$100,file=%O;}SEGMENTS{TEST:load=T,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin';obj=stem.with_suffix('.o');raw=stem.with_suffix('.bin')
    subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',raw],check=True)
    obj.unlink()
    return raw.read_bytes(),src


def prove_art(b):
    result={}
    for pose in [1,2]:
        assert address(b,f'METASPRITE_GOOMBA_WALKING_{pose}')==0x66+pose
        for facing in ['LEFT','RIGHT']:
            name=f'MetaspriteData_GOOMBA_WALKING_{pose}_{facing}'
            at=location(b,name);pc=address(b,name)
            exact=b['raw'][at:at+9]
            assert pc>>8==0xaf and exact[0]==8
            assert exact[3:5]==bytes([8,0]) and exact[7:9]==bytes([8,8])
            assert all(x&~0x43==0 for x in [exact[2],exact[6]])
            assert (at-16)//8192==4
            for half,shift in [('Lo',0),('Hi',8)]:
                table=f'MetaspriteTable{facing.title()}{half}'
                assert b['raw'][location(b,table)+0x66+pose]==((pc>>shift)&255)
            result[name]=dict(cpu=f'{pc:04x}',bytes=exact.hex())
    return result


def write(bus,name,value,slot=0):bus[address(bus.bundle,name)+slot]=value


def routine(m,pc,pose,slot,p):
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=0x57,pose,slot,p,239;c.stPushWord(0x5aff)
    touched=[];lowest=c.sp;hits=Counter();m.writes.clear()
    for _ in range(20000):
        if c.pc==0x5b00:break
        if c.pc in [ORIGINAL,SHARED_OAM,0xa5ba]:hits[f'{c.pc:04x}']+=1
        lowest=min(lowest,c.sp)
        assert m[c.pc]!=0,('BRK',hex(c.pc),m.rawtags);c.step()
    else:raise AssertionError(('draw bound',hex(c.pc)))
    assert c.sp==239
    touched=[(a,v) for a,v in m.writes if 0x200<=a<0x304]
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp],cycles=c.processorCycles,minimum_SP=lowest,
                hits=dict(hits),OAM=touched)


def state(m):
    take=lambda x,y:bytes(list.__getitem__(m,slice(x,y)))
    return (take(0,0x100),take(0x15a,0x17b),take(0x200,0x800),take(0x5fe0,0x8000),
            tuple(m.rawtags),tuple(bytes(r) for r in m.ram),tuple(m.ppu_log))


def direct_tests(b,code):
    seed=N.Bus(b);seed.raw_page(1,132);N.put(seed,CurrentBank=132)
    seed[ENTRY:ENTRY+len(code)]=code
    base=[]
    for pose,face,slot,rotation,cursor in product([0x67,0x68],[1,2],range(1,7),[0,4,100,252],[0,4,128,244,248]):
        base.append((pose,face,slot,rotation,cursor,0x42,160,0,0,41,8,0,0,0x20))
    # Cover exact generic behavior at horizontal/vertical clip edges,
    # dynamic pointers, special attrs, capacity wrap and unaligned offsets.
    edges=[]
    for x,y,page,high in [(247,247,0,1),(248,160,0,1),(255,160,0,1),(0,248,0,1),
                           (0,255,0,1),(20,80,1,1),(20,80,255,1),(80,80,0,0),(80,80,0,2)]:
        edges += [(0x67,1,1,252,12,x,y,page,high-1,41,8,0,0,0x2c)]
    edges += [(pose,face,slot,rotate,cursor,80,160,0,0,owner,engine,flip,dyn,attr)
              for pose,face,slot,rotate,cursor,owner,engine,flip,dyn,attr in [
                  (0x66,1,1,4,4,41,8,0,0,3),(0x69,2,1,4,4,41,8,0,0,3),
                  (0x67,1,0,4,4,41,8,0,0,3),(0x68,2,7,4,4,41,8,0,0,3),
                  (0x68,2,1,4,4,0,8,0,0,3),(0x68,2,1,4,4,4,8,0,0,3),
                  (0x68,2,1,4,4,36,8,0,0,3),(0x68,2,1,4,4,41,5,0,0,3),
                  (0x67,1,1,4,4,41,8,0,1,3),(0x67,1,1,4,4,41,8,0x80,0,3),
                  (0x68,1,6,253,244,41,8,0,0,0x4b),(0x68,2,1,4,251,41,8,0,0,0xff),
                  (0x67,1,5,251,247,41,8,0,0,8),(0x67,2,5,4,255,41,8,0,0,0x80)]]
    hist=Counter();fallback=Counter(); minimum=255
    for case in base+edges:
        pose,face,slot,rotation,cursor,x,y,page,high,owner,engine,flip,dyn,attr=case
        a,z=[N.fork(seed) for _ in range(2)]
        for m in [a,z]:
            N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,CurrentOAMOffset=cursor,
                  GuestOamRotationActive=1,RgOamRotation=rotation,ScreenLeft_X_Pos=0,
                  ScreenLeft_PageLoc=0,RlOutlineBypass=0)
            for name,v in [('PlayerFacingDir',face),('SprObject_X_Position',x),('SprObject_PageLoc',page),
                           ('SprObject_Y_Position',y),('SprObject_Y_HighPos',high+1),
                           ('ObjectVerticalFlip',flip),('SprObject_SprAttrib',attr)]:write(m,name,v,slot)
            if dyn:
                write(m,'HpNativeDrawHi',0xaf,slot);write(m,'HpNativeDrawLo',0x2f,slot)
            m[0x200:0x304]=bytes((17*i+31)&255 for i in range(0x104))
        v,w=routine(a,ORIGINAL,pose,slot,0x71),routine(z,ENTRY,pose,slot,0x71)
        assert v['regs']==w['regs'] and v['OAM']==w['OAM'] and state(a)==state(z),(case,v,w)
        minimum=min(minimum,v['minimum_SP'],w['minimum_SP'])
        (fallback if 'a3f1' in w['hits'] else hist)[v['cycles']-w['cycles']]+=1
    return dict(direct_cases=sum(hist.values()),fallback_cases=sum(fallback.values()),
                direct_savings=dict(hist),fallback_savings=dict(fallback),minimum_SP=minimum)


def main_tests(raw,code):
    before=bundle(raw);after=bytearray(raw)
    for pc in SITES:
        at=16+4*8192+pc-0xa000
        assert after[at:at+3]==bytes.fromhex('20f1a3')
        after[at:at+3]=bytes([0x20,ENTRY&255,ENTRY>>8])
    after=bundle(after);rows=[]
    for enemies in [0,1,3,5]:
        pair=[fixture(x,enemies,False,True) for x in [before,after]] if enemies==0 else [fixture(before,enemies,False,True),fixture(before,enemies,False,True)]
        m=pair[1];m.bundle=after
        for w,tag in enumerate(m.rawtags[:]):
            if tag&128:m.raw_page(w,tag)
        m[ENTRY:ENTRY+len(code)]=code
        for epoch in range(2,10):
            results=[]
            for m in pair:
                N.put(m,FrameCounter=epoch,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                results.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
            assert all(results[0][k]==results[1][k] for k in ['A','X','Y','P'])
            assert state(pair[0])==state(pair[1]),(enemies,epoch)
            rows.append(dict(enemies=enemies,epoch=epoch,cycles_before=results[0]['CPU'],cycles_after=results[1]['CPU']))
    return rows


def main():
    raw=ROM.read_bytes();assert sha(raw)==PIN
    b=bundle(raw);assert address(b,'DrawMetasprite')==ORIGINAL
    assert raw[16+4*8192+0x1ed1:16+4*8192+0x1ee2].hex()=='186dde06b056ad0b6cf0068a186d086caa'
    assert raw[16+4*8192+0x4ee:16+4*8192+0x4f6].hex()=='2079a2b0034cb9a5'
    arts=prove_art(b);code,src=compile_leaf(b)
    direct=direct_tests(b,code)
    print('direct',direct,flush=True)
    result=dict(passed=True,ROM_written=False,source_only=True,base_SHA256=PIN,linked_measurement_PC=ENTRY,
                production_funding=False,code_bytes=len(code),source_SHA256=sha(src.read_bytes()),descriptors=arts,
                direct=direct,whole_Main=main_tests(raw,code),sites=SITES,
                scope='CPU-only scratch placement. Shared native OAM writer and post-render tail execute. Full final state and exact OAM write order match; no production lease, ISR or Mesen claim.')
    (OUT/'goomba-measurement.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','code_bytes','direct','whole_Main']}),flush=True)


if __name__=='__main__':main()
