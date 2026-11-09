"""Fund the measured native Goomba terrain/movement without growing OBJECT."""
from collections import Counter
from itertools import product
from pathlib import Path
import argparse
import json
import re
import subprocess

import measure_mini_active_actor_1108_v1 as A

R,N,OUT=A.R,A.N,A.OUT
MOVE=0xaa3d
MOVE_END=0xaa8e
TERRAIN=0xbf1e
TERRAIN_END=0xbfdf
DISPATCH_CALL=0xa4c8
ORIGINAL_MOVE=bytes.fromhex('a000b51f2940d019b51f0ab030b51f2920d05db51f2907f024c905f004c903b03020ce8ca000b51fc902f00c2940f00db517c92ef007d0034c838ca001b547481002c8c8187992a9954720838c68954760')
MOVEMENT='''
.export GroundedMove,MoveEnd
MoveNormalEnemy:
 ldy #0
 lda Enemy_State,x
 beq GroundedMove
 and #$40
 bne Fall
 lda Enemy_State,x
 bmi Steady
 and #$20
 bne Defeated
 lda Enemy_State,x
 and #7
 beq Steady
 cmp #5
 beq Fall
 cmp #3
 bcs Revive
Fall:
 jsr MoveD_EnemyVertically
 ldy #0
 lda Enemy_State,x
 cmp #2
 beq MoveHorizontalTail
 and #$40
 beq Steady
 lda Enemy_ID,x
 cmp #$2e
 beq Steady
 ldy #1
Steady:
 lda Enemy_X_Speed,x
 pha
 bpl :+
 iny
 iny
:
 clc
 adc XSpeedAdderData,y
 sta Enemy_X_Speed,x
 jsr MoveEnemyHorizontally
 pla
 sta Enemy_X_Speed,x
 rts
GroundedMove:
 ; Native steady Y0/Y2 add zero. This is the same native 4.4 integrator.
 jsr MoveEnemyHorizontally
 lda Enemy_X_Speed,x
 rts
MoveEnd:
'''
DIRECT='''
.export GoombaDispatch,ActorEnd
GoombaDispatch:
 cmp #6
 bne OtherEnemy
 ; Exactly reproduce JumpEngine's consumed JSR return and pointer scratch.
 ; MoveNormalEnemy reloads Y before any read.
 pla
 sta R4
 pla
 sta R5
 lda #<MoveNormalEnemy
 sta R6
 lda #>MoveNormalEnemy
 sta R7
 clc
 jmp MoveNormalEnemy
OtherEnemy:
 jmp JumpEngine
ActorEnd:
'''


def build(b):
    old,terrain=A.terrain_source()
    out=OUT/'funded';src=out.with_suffix('.s');cfg=out.with_suffix('.cfg')
    move=OUT/'funded-motion.bin';actor=OUT/'funded-ground.bin'
    syms=set(A.NAMES)|{'MoveD_EnemyVertically','XSpeedAdderData','JumpEngine'}
    defs=''.join(f'{n}=${A.address(b,n):04x}\n' for n in sorted(syms))
    defs+='Defeated=$aaad\nRevive=$aa8e\nMoveHorizontalTail=$aab0\n'
    src.write_text(defs+'.setcpu "6502"\n.segment "MOVE"\n.org $aa3d\n'+MOVEMENT+'\n.reloc\n.segment "TERRAIN"\nTerrain:\n'+terrain+DIRECT)
    cfg.write_text(f'MEMORY{{M:start=${MOVE:04x},size=${MOVE_END-MOVE:04x},file="{move.as_posix()}";'
                   f'T:start=${TERRAIN:04x},size=${TERRAIN_END-TERRAIN:04x},file="{actor.as_posix()}";}}'
                   'SEGMENTS{MOVE:load=M,type=ro;TERRAIN:load=T,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin';obj=out.with_suffix('.o');lab=out.with_suffix('.lbl')
    subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',out.with_suffix('.bin'),'-Ln',lab],check=True)
    obj.unlink()
    return move.read_bytes(),actor.read_bytes(),{n:int(v,16)for v,n in re.findall(r'^al ([0-9A-F]+) \.(\w+)$',lab.read_text(),re.M)},src


def compose(raw,move,actor,labels):
    out=bytearray(raw);patches=[]
    assert labels['MoveEnd']==MOVE_END and labels['ActorEnd']<=TERRAIN_END
    assert len(move)==MOVE_END-MOVE and len(ORIGINAL_MOVE)==len(move)
    oldterrain=(OUT/'ground-reference.bin').read_bytes();assert len(oldterrain)==TERRAIN_END-TERRAIN
    d=labels['GoombaDispatch']
    for pc,old,new in [(MOVE,ORIGINAL_MOVE,move),(TERRAIN,oldterrain,actor.ljust(len(oldterrain),b'\xea')),
                       (DISPATCH_CALL,bytes.fromhex('20098a'),bytes([0x20,d&255,d>>8]))]:
        at=16+pc-0xa000
        assert raw[at:at+len(old)]==old,(hex(pc),raw[at:at+len(old)].hex(),old.hex())
        out[at:at+len(new)]=new
        patches.append(dict(physical_PRG=0,CPU_half_open=[pc,pc+len(old)],file_offset=at,old_hex=old.hex(),new_hex=new.hex()))
    return bytes(out),patches


def call(m,pc,x,y,p,a=0x51):
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,239;c.stPushWord(0x5aff)
    low=c.sp
    for _ in range(18000):
        if c.pc==0x5b00:break
        low=min(low,c.sp);assert m[c.pc],(hex(c.pc),pc,x,y,p);c.step()
    else:raise AssertionError(('native actor bound',pc,hex(c.pc)))
    assert c.sp==239
    return (c.a,c.x,c.y,c.p,c.sp),c.processorCycles,low


def setslot(m,name,x,value):m[A.address(m.bundle,name)+x]=value


def check_move(images):
    counts=Counter();seeds=[N.Bus(b)for b in images]
    for m in seeds:m.raw_page(1,128);N.put(m,CurrentBank=128)
    cases=product(range(6),[0,1,2,3,4,5,7,0x20,0x40,0x80,0xff],
                  [0,1,8,16,127,128,0xf8,255],[0,1,0x7f,255],[0x20,0x71])
    for x,state,speed,force,p in cases:
        outcomes=[]
        for seed in seeds:
            m=N.fork(seed);N.put(m,ObjectOffset=x,FrameCounter=0x39,PrimaryHardMode=1)
            for name,value in [('Enemy_ID',6),('Enemy_State',state),('Enemy_X_Speed',speed),
                               ('Enemy_X_Position',255 if speed<128 else 0),('Enemy_PageLoc',12),
                               ('Enemy_Y_Position',184),('Enemy_Y_HighPos',1),('EnemyIntervalTimer',2),
                               ('Enemy_X_MoveForce',force)]:setslot(m,name,x,value)
            regs,cycles,low=call(m,0xa4ba,x,17,p)
            outcomes.append((regs,A.state(m),cycles,low))
        u,v=outcomes
        assert u[:2]==v[:2],(x,state,speed,force,p,u[0],v[0])
        counts[(state,u[2]-v[2])]+=1
    return [[state,saving,num] for (state,saving),num in sorted(counts.items())]


def check_main(images):
    results=[]
    for n,terrain,parser in [(0,False,False),(1,False,False),(3,False,True),(5,False,False),(3,True,False)]:
        pair=[A.fixture(b,n,terrain,parser) for b in images]
        row=[]
        for frame in range(2,26):
            z=[]
            for m in pair:
                key=129 if 8<=frame<18 else 0
                N.put(m,FrameCounter=frame,SavedJoypadBits=key,SavedJoypad1Bits=key,
                      VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                z.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
            assert all(z[0][k]==z[1][k]for k in ['A','X','Y','P']) and A.state(pair[0])==A.state(pair[1]),(n,frame,z)
            row.append(z[0]['CPU']-z[1]['CPU'])
        results.append(dict(actors=n,terrain=terrain,parser=parser,cycle_savings=row))
    return results


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--precheck',action='store_true');args=ap.parse_args()
    raw=A.BASE.read_bytes();assert A.sha(raw)==A.PIN
    b=A.bundle(raw);move,actor,labels,src=build(b)
    print('extents',len(move),len(actor),labels,flush=True)
    new,patches=compose(raw,move,actor,labels);pair=[b,A.bundle(new)]
    m=check_main(pair)
    print('Main',[(r['actors'],min(r['cycle_savings']),max(r['cycle_savings']))for r in m],flush=True)
    if args.precheck:return
    c=check_move(pair)
    result=dict(passed=True,ROM_written=False,CPU_only=True,base_SHA256=A.PIN,expected_memory_only_SHA256=A.sha(new),
                patches=patches,labels=labels,source_SHA256=A.sha(src.read_bytes()),move_cases=c,whole_GameCore=m,
                scope='Two existing bank0 source footprints plus sole native dispatch operand. Terrain removes only five dead-stack pushes, preserves all live state. Actual async, full non-Goomba movement and cold/clip controls still pending.')
    (OUT/'funded-v2.json').write_text(json.dumps(result,indent=2)+'\n')
    print(A.sha(new),flush=True)


if __name__=='__main__':main()
