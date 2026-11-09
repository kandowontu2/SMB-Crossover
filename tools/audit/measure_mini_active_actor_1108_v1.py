"""Measure exact ordinary active-enemy fast paths with a CPU-only scratch link."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import re
import subprocess

from profile_mini_busy_1108_v1 import R,N,bundle,address,location,sha,fixture

BASE=R/'build/mini-frame-budget-1108/candidate.nes'
PIN='e90d30c1c9636be6eb304a7b3b1506b862f8171dc2773d809482e25b0a5417df'
OUT=R/'build/mini-active-actor-1108-v1'
SITES={'Box':(0xa466,0xb8f5),'Terrain':(0xa482,0xbf1e),'Motion':(0xa490,0xa4ba)}
NAMES='R0 R1 R2 R3 R4 R5 R6 R7 ObjectOffset Enemy_OffscreenBits EnemyOffscrBitsMasked Enemy_BoundBoxCtrl Enemy_Rel_XPos Enemy_Rel_YPos BoundingBox_UL_Corner BoundingBox_LR_Corner CheckRightScreenBBox SelectedCharacter Enemy_ID Enemy_State RgEnemyStun Enemy_X_Speed MoveEnemyHorizontally Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_MovingDir Block_Buffer_1 BlockBufferAddr Local_eb BBChk_E EnemyToBGCollisionDet Goomba BoundBoxCtrlData'.split()
SOURCE='''
.setcpu "6502"
.segment "TEST"
.export Box,Motion,Terrain,ActorEnd
Box:
 lda Enemy_OffscreenBits
 bne NativeBox
 lda Enemy_BoundBoxCtrl,x
 cmp #3
 bne NativeBox
 lda #0
 sta EnemyOffscrBitsMasked,x
 txa
 clc
 adc #1
 sta R0
 asl
 asl
 tay
 lda Enemy_Rel_XPos
 clc
 adc #2
 sta BoundingBox_UL_Corner,y
 clc
 adc #12
 sta BoundingBox_LR_Corner,y
 lda Enemy_Rel_YPos
 clc
 adc #9
 sta BoundingBox_UL_Corner+1,y
 clc
 adc #12
 sta BoundingBox_LR_Corner+1,y
 ldx R0
 ; The clip leaf overwrites R1/R2 and restores native X/A/flags.
 jmp CheckRightScreenBBox
NativeBox:
 jmp $b8f5

Motion:
 lda SelectedCharacter
 cmp #41
 bne NativeMotion
 lda Enemy_ID,x
 cmp #6
 bne NativeMotion
 lda RgEnemyStun,x
 ora Enemy_State,x
 bne NativeMotion
 ; Match JumpEngine's live pointer scratch for the native id6 row.
 lda #$ca
 sta R4
 lda #$a4
 sta R5
 lda #$3d
 sta R6
 lda #$aa
 sta R7
 ; Source steady Y0/Y2 adders are both zero. The exact native movement
 ; routine consumes the original speed without a same-value save/restore.
 jsr MoveEnemyHorizontally
 lda Enemy_X_Speed,x
 rts
NativeMotion:
 jmp $a4ba
'''


def terrain_source():
    source=(R/'src/ground_goomba_terrain.s').read_text()
    a=source.index('  ; Preserve the native early'); z=source.index('.endproc',a)
    old=source[a:z]
    start=old.index('  ; Exact native direction-specific side cell')
    end=old.index('  ; Keep the actual native ADC',start)
    new=old[:start]+'''  ; Reuse the exact foot pointer. X+8 advances the column iff bit3
  ; was set, and the right side is always one column beyond X here.
  lda Enemy_X_Position,x
  and #8
  beq SideColumn
  dec R6
SideColumn:
  lda Enemy_MovingDir,x
  cmp #1
  bne Left
  inc R6
  lda Enemy_X_Position,x
  adc #15
  bne SideX
Left:
  lda Enemy_X_Position,x
SideX:
  sta R5
'''+old[end:]
    start=new.index('  ; Native BBChk_E last pushes');end=new.index('  lda Enemy_MovingDir,x',start)
    new=new[:start]+'''  ; Those five native push/pop bytes are below the live SP at return.
  ; No foreground reader can observe them before a new push overwrites them.
'''+new[end:]
    return old,new


def assemble(b):
    OUT.mkdir(exist_ok=True)
    old,terrain=terrain_source()
    def build(stem,text,start):
        p=OUT/stem;src=p.with_suffix('.s');cfg=p.with_suffix('.cfg')
        defs=''.join(f'{n}=${address(b,n):04x}\n' for n in NAMES)
        defs+='NativeEnemySideQueryReturn=$a12e\n'
        src.write_text(defs+text)
        cfg.write_text(f'MEMORY{{P:start=${start:04x},size=$300,file=%O;}}SEGMENTS{{TEST:load=P,type=ro;}}\n')
        cc=R/'tools/Windows/cc65/bin';obj=p.with_suffix('.o');out=p.with_suffix('.bin');lab=p.with_suffix('.lbl')
        subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',out,'-Ln',lab],check=True)
        obj.unlink()
        return out.read_bytes(),{n:int(v,16) for v,n in re.findall(r'^al ([0-9A-F]+) \.(\w+)$',lab.read_text(),re.M)}
    original,_=build('ground-reference','.setcpu "6502"\n.segment "TEST"\n'+old,0xbf1e)
    p=16+0x1f1e; expect=b['raw'][p:p+193]
    assert original==expect,[(i,hex(a),hex(z)) for i,(a,z) in enumerate(zip(original,expect)) if a!=z][:16]
    return build('actor-probe',SOURCE+'\nTerrain:\n'+terrain+'\nActorEnd:\n',0x5b80)


def state(m):
    take=lambda a,z:bytes(list.__getitem__(m,slice(a,z)))
    return (take(0,0x100),take(0x15a,0x17b),take(0x200,0x800),take(0x5fe0,0x8000),
            tuple(m.rawtags),tuple(bytes(r) for r in m.ram),tuple(m.ppu_log))


def images(raw,code,labels,lanes):
    output=bytearray(raw)
    for name in lanes:
        pc,before=SITES[name];at=16+pc-0xa000
        assert output[at:at+3]==bytes([0x20,before&255,before>>8])
        target=labels[name]
        output[at:at+3]=bytes([0x20,target&255,target>>8])
    return [bundle(raw),bundle(output)]


def measure_main(raw,code,labels,lanes):
    result=[]
    before,after=images(raw,code,labels,lanes)
    for actors in [0,1,3,5]:
        pair=[fixture(b,actors,False,True) for b in [before,before]]
        m=pair[1];m.bundle=after
        for i,tag in enumerate(m.rawtags[:]):
            if tag&128:m.raw_page(i,tag)
        m[0x5b80:0x5b80+len(code)]=code
        rows=[]
        for frame in range(2,18):
            regs=[]
            for m in pair:
                keys=0 if frame<8 else 129
                N.put(m,FrameCounter=frame,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                regs.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
            assert all(regs[0][k]==regs[1][k] for k in ['A','X','Y','P']), (actors,frame,regs)
            assert state(pair[0])==state(pair[1]), (actors,frame,[(hex(a),pair[0][a],pair[1][a])for a in list(range(256))+list(range(512,2048))+list(range(0x5fe0,0x8000)) if pair[0][a]!=pair[1][a]][:24])
            rows.append([regs[0]['CPU'],regs[1]['CPU']])
        result.append(dict(actors=actors,frames=rows,min_saved=min(a-z for a,z in rows),max_saved=max(a-z for a,z in rows)))
    return result


def main():
    raw=BASE.read_bytes();assert sha(raw)==PIN
    b=bundle(raw);code,labels=assemble(b)
    at=location(b,'BoundBoxCtrlData');assert raw[at+12:at+16]==bytes([2,9,14,21])
    results={}
    for name,lanes in [(n,[n])for n in SITES]+[('all',list(SITES))]:
        results[name]=measure_main(raw,code,labels,lanes)
        print(name,[(row['actors'],row['min_saved'],row['max_saved']) for row in results[name]],flush=True)
    report=dict(passed=True,ROM_written=False,source_only=True,base_SHA256=PIN,
                fixture_PC=0x5b80,production_funding=False,code_bytes=len(code),labels=labels,results=results,
                scope='Exact cartridge Main CPU comparison. Complete actor gameplay, box, OAM, persistent memory, AXYP, mapper/SMC equal; dead stack outside live SP may differ. No ROM, native or async claim.')
    (OUT/'measurement.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
