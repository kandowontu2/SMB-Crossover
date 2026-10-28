"""Finite linked Celeste art/state/interrupt contracts, not a native playthrough."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from prepare_celeste_mario_controls import Native,fresh

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def invoke(q,name,a=0,x=0,y=0,sp=0xfd):
    s=q.b['syms'][name];g=q.b['segs'][s['seg']];pc=address(q.b,name)
    window=(pc-0x8000)//8192;bank=(int(g['ooffs'],0)-16)//8192
    q.m.page(window,bank)
    if window in (1,2):q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
    c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,0x30,sp;c.stPushWord(0x5aff)
    low=c.sp;pcs=[]
    for _ in range(100000):
        if c.pc==0x5b00:
            assert c.sp==sp,(name,c.sp,sp)
            return c,low,pcs
        pcs.append(c.pc);c.step();low=min(low,c.sp)
    raise AssertionError(('timeout',name,hex(c.pc),q.m.banks))

def qfresh(b):
    _,q=fresh(b);q.put(NmiDisable=255,Sprite0HitDetectFlag=0,DisableScreenFlag=1)
    return q

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    b=scoped_load(a.rom);rows=[];art=[];interrupts=[]
    core=next(g for g in b['segs'].values()if g.get('name')=='"CELESTE_MARIO_CORE"')
    assert int(core['start'],0)==0xb000 and int(core['size'],0)<=4096
    assert(int(core['ooffs'],0)-16)//8192==98
    assets=json.loads((ROOT/'chr/characters/celeste-mario-assets.json').read_text())
    patterns=(ROOT/'chr/characters/celeste-mario.chr').read_bytes()
    assert b['raw'][16+128*8192+740*1024:16+128*8192+756*1024]==patterns
    for r in assets['records']:
        q=qfresh(b);label=f'CmArt{r["pose"]}{"R"if r["face"]==1 else"L"}'
        src=address(b,label);pointer=src+0x2000
        invoke(q,'CmGraphicsBank');assert q.m.banks[2]==98
        expected=bytes([4*len(r['parts'])]+[v for part in r['parts']for v in part])
        assert bytes(q.m[pointer:pointer+len(expected)])==expected
        assert b['raw'][location(b,label):location(b,label)+len(expected)]==expected
        for offset in [0,128,236,252]:
            q.put(R0=pointer&255,R1=pointer>>8,R3=0,R4=96,R5=0,R6=112,R7=1,
              CurrentOAMOffset=offset,GuestOamRotationActive=0)
            c,_,_=invoke(q,'MetaspriteRenderLoop')
            if offset+expected[0]>=256:assert not c.p&1
            else:
                assert c.p&1 and q.get('CurrentOAMOffset')==offset+expected[0]
                got=bytes(q.m[0x200+offset:0x200+offset+expected[0]])
                want=bytes(v for tile,attr,y,x in reversed(r['parts'])for v in [112+y,tile,attr,96+x])
                assert got==want,(label,offset,got,want)
        q.put(R0=pointer&255,R1=pointer>>8)
        invoke(q,'PlayerRemoveOutlines')
        filtered=q.get('R0')+256*q.get('R1')
        assert bytes(q.m[filtered:filtered+len(expected)])==expected
        art.append(dict(pose=r['pose'],facing=r['face'],parts=len(r['parts']),source_pointer=pointer,outline_exact=True))
    # Compiled native ProcessPlayerAction versus the port's pose/timer owner.
    for state,face,water,timer,anim in itertools.product([0,1,2,3,6],[1,2],[0,1],[0,3],[0,1,2]):
        n=Native();q=qfresh(b)
        n.put(ridingenemyslot=255,holdingenemyslot=255,PlayerSize=0,Player_State=state,
          PlayerFacingDir=face,Player_MovingDir=face,PlayerXSpd=16 if face==1 else 240,
          Player_XSpeedAbsolute=16,PlayerYSpd=1,Left_Right_Buttons=face,SwimmingFlag=water,
          PlayerAnimTimer=timer,PlayerAnimTimerSet=4,PlayerAnimCtrl=anim,JumpSwimTimer=4)
        q.put(CmState=state,Player_State=1 if state==6 else state,PlayerFacingDir=face,Player_MovingDir=face,
          Player_X_Speed=16 if face==1 else 240,Player_XSpeedAbsolute=16,Player_Y_Speed=1,
          Left_Right_Buttons=face,SwimmingFlag=water,PlayerAnimTimer=timer,PlayerAnimTimerSet=4,
          PlayerAnimCtrl=anim,CmJumpTime=4)
        c=n.call('ProcessPlayerAction',7);invoke(q,'CmGraphics')
        assert q.get('CmPose')==c.a//2,(state,face,water,timer,anim,c.a,q.get('CmPose'))
        assert [q.get(k)for k in ['PlayerAnimTimer','PlayerAnimCtrl']]==[n.get(k)for k in ['PlayerAnimTimer','PlayerAnimCtrl']]
        rows.append(dict(check='native-action-pose',state=state,facing=face,water=water,timer=timer,animation=anim))
    for state,crouch,wall,speed,moving in [(0,4,0,0,1),(1,4,0,0,1),(1,0,10,1,1),
      (0,0,10,0,1),(0,0,0,16,2),(0,0,0,0,1)]:
        n=Native();q=qfresh(b)
        n.put(ridingenemyslot=255,holdingenemyslot=255,PlayerSize=0,Player_State=state,CrouchingFlag=crouch,
          WallJumpLeniencyTimer=wall,PlayerXSpd=speed,Player_XSpeedAbsolute=speed,Player_MovingDir=moving,PlayerFacingDir=1)
        q.put(CmState=state,Player_State=state,CrouchingFlag=crouch,CmWallGrace=wall,Player_X_Speed=speed,
          Player_XSpeedAbsolute=speed,Player_MovingDir=moving,PlayerFacingDir=1)
        c=n.call('ProcessPlayerAction',7);invoke(q,'CmGraphics');assert q.get('CmPose')==c.a//2
        rows.append(dict(check='native-crouch-wall-skid-idle',state=state,crouch=crouch,wall=wall,speed=speed,moving=moving))
    # Genuine pickup/life/loaded-scene/identity transitions in the selected overlay.
    q=qfresh(b);q.put(CmTier=2);q.put(NumberofLives=4);invoke(q,'CmEnsure');assert q.get('CmTier')==2
    before=list(q.m[0x5c00:0x5c80]);q.put(AreaPointer=0xc2);invoke(q,'CmEnsure');assert before==list(q.m[0x5c00:0x5c80])
    q.put(CmDashTimer=9,AreaType=2,AreaAddrsLOffset=7);invoke(q,'CmEnsure');assert q.get('CmDashTimer')==0 and q.get('CmTier')==2 and q.get('CmArea')==71
    q.put(CmDashTimer=9);invoke(q,'CmEnter');assert q.get('CmDashTimer')==0 and q.get('CmTier')==2
    q.put(NumberofLives=3);invoke(q,'CmEnsure');assert q.get('CmTier')==0
    rows.append(dict(check='life-gain-preserve-death-reset-future-pointer-ignore-loaded-scene-enter'))
    for raw in [0,1]:
        q=qfresh(b);q.put(PowerUpType=raw,ObjectOffset=2)
        for expected in [1,2,2]:
            c,_,_=invoke(q,'CmPickup');assert c.p&1 and q.get('CmTier')==expected and q.get('PlayerStatus')==expected
        rows.append(dict(check='source-pickup-wall-then-dash',raw_type=raw,tiers=[1,2,2]))
    q=qfresh(b);q.put(PowerUpType=2);before=bytes(q.m[0x5c00:0x5c80])+bytes(q.m[0x5f98:0x5fa0])
    c,_,_=invoke(q,'CmPickup');assert not c.p&1 and before==bytes(q.m[0x5c00:0x5c80])+bytes(q.m[0x5f98:0x5fa0])
    for stock,offset in itertools.product([0,1],[0,77,78,80]):
        q=qfresh(b);q.put(CmDashStock=stock,CmPalette=0,VRAM_Buffer1_Offset=offset)
        invoke(q,'CmUi')
        if offset<78:
            want=bytes([0x3f,0x11,3,0x16 if stock else 0x21,0x27,1,0])
            at=address(b,'VRAM_Buffer1')+offset
            assert bytes(q.m[at:at+7])==want and q.get('VRAM_Buffer1_Offset')==offset+6
            before=bytes(q.m[at:at+7]);invoke(q,'CmUi');assert before==bytes(q.m[at:at+7])and q.get('VRAM_Buffer1_Offset')==offset+6
        else:assert q.get('VRAM_Buffer1_Offset')==offset and q.get('CmPalette')==0
        rows.append(dict(check='palette-charge-cache-and-queue-bound',stock=stock,offset=offset))
    q=qfresh(b)
    for at in [0x5bff,0x5c80,0x5f97,0x5fa0]:q.m[at]=0xa7
    invoke(q,'CmEnter')
    assert all(q.m[at]==0xa7 for at in [0x5bff,0x5c80,0x5f97,0x5fa0])
    for tier in [0,1,2]:
        q=qfresh(b);q.put(CmTier=tier,CmDashTimer=9,CmDashReady=3)
        c,_,_=invoke(q,'CmInjuryStatus');assert c.a==bool(tier)
        c,_,_=invoke(q,'CmInjuryStart');assert bool(c.p&1)==bool(tier)
        assert q.get('CmTier')==max(0,tier-1)
        rows.append(dict(check='declared-crossover-tier-injury',tier=tier))
    for char,variant in itertools.product(range(22),range(5)):
        q=qfresh(b);q.put(SelectedCharacter=char,MarioVariant=variant);before=bytes(q.m[0x5c00:0x5c80])+bytes(q.m[0x5f98:0x5fa0])
        c,_,_=invoke(q,'CmEnabled');assert bool(c.p&1)==(char==0 and variant==4)
        assert before==bytes(q.m[0x5c00:0x5c80])+bytes(q.m[0x5f98:0x5fa0])
    rows.append(dict(check='explicit-foreign-admission',identities=22,variants=5,other_entries_require_root_admission=True))
    for function in ['CmMovement','CmDraw']:
        q=qfresh(b);q.put(SavedJoypadBits=129,A_B_Buttons=128,Left_Right_Buttons=1,Up_Down_Buttons=0)
        _,_,pcs=invoke(q,function);seams=[pcs[i]for i in [0,4,12]]
        for kind,lag,target in itertools.product(['IRQ','NMI'],[False,True],seams):
            q=qfresh(b);q.put(NmiDisable=255 if lag else 0,SavedJoypadBits=129,A_B_Buttons=128,Left_Right_Buttons=1,Up_Down_Buttons=0)
            oldstep=NesMPU.step;fired=[False];interrupt_low=[255]
            smc=[address(b,k)+d for k,d in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
            def step(c):
                if not fired[0]and c.pc==target and q.m.banks[1]==98:
                    fired[0]=True
                    before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[z]for z in smc),bytes(q.m[0x101+c.sp:0x200]))
                    if kind=='NMI':c.nmi()
                    else:
                        c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
                    for _ in range(50000):
                        interrupt_low[0]=min(interrupt_low[0],c.sp)
                        oldstep(c)
                        if c.pc==before[5]and c.sp==before[4]:break
                    else:raise AssertionError(('interrupt-timeout',function,kind,hex(c.pc)))
                    after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[z]for z in smc),bytes(q.m[0x101+c.sp:0x200]))
                    assert before==after,(function,kind,before,after)
                oldstep(c)
            NesMPU.step=step
            try:_,low,_=invoke(q,function,sp=0xc0)
            finally:NesMPU.step=oldstep
            assert fired[0];interrupts.append(dict(function=function,kind=kind,lag=lag,PC=target,entry_SP=192,minimum_SP=min(low,interrupt_low[0]),AXYP_PC_SP_banks_five_SMC_live_stack_exact=True))
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(a.rom),core_bytes=int(core['size'],0),art=art,rows=rows,interrupts=interrupts,
      scope=__doc__,limits=['CPU typed arenas and blank-screen interrupt seams; no native PPU/deadline/crowding claim.',
      'Movement/AfterBG/Weapons/Bounce are admitted selected-identity entry contracts; ROOT owns actual host callsites.',
      'Host vine, spring, pipe and death transitions remain explicit crossover adapters.'],
      bindings=[dict(path=str(f),sha256=sha(f))for f in [Path(__file__),ROOT/'tools/prepare_celeste_mario_controls.py',a.rom,a.rom.with_suffix('.dbg'),ROOT/'chr/characters/celeste-mario-assets.json',ROOT/'chr/characters/celeste-mario.chr']])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,core_bytes=proof['core_bytes'],art=len(art),rows=len(rows),interrupts=len(interrupts))))
if __name__=='__main__':main()
