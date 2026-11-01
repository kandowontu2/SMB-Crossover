"""Actual owning Main, original friction, rear controls and IRQ/NMI closure."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_kirby_approach_owner_1101_v3 as P
import check_kirby_owner_main_1101_v2 as K
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
O=P.O;sha=P.sha

def value(m,n,i=0):return m[address(m.bundle,n)+i]

def case(seed,mode,kind,face,gap,moving=True,npcspeed=0):
    m=C.fork(seed);K.scene(m,face);K.actor(m,kind,112+(gap if face==1 else-gap))
    H.put(m,CrossoverBehaviorVersion=mode)
    if npcspeed:
      H.put(m,Enemy_X_Speed=npcspeed if face==2 else(-npcspeed)&255,Enemy_MovingDir=1 if face==2 else 2)
    minimum=255;trace=[];samples=[]
    for frame in range(50 if npcspeed else 12):
      keys=64+((1 if face==1 else 2)if moving else 0);K.keys(m,keys);origin=C.fork(m)
      c,low,o=K.main_step(m,keys);minimum=min(minimum,low)
      trace.append(dict(frame=frame,health=H.get(m,'KbHealth'),mouth=H.get(m,'KbMouth'),action=H.get(m,'KbAction'),age=H.get(m,'KbActionAge'),playerX=value(m,'Player_X_Position')+256*value(m,'Player_PageLoc'),enemyX=value(m,'Enemy_X_Position')+256*value(m,'Enemy_PageLoc'),VX=value(m,'MmVX',1)+256*value(m,'MmVX',2),facing=value(m,'PlayerFacingDir'),injury=o.counts['KbInjuryStart'],capture=o.counts['KbWeapons::Suction']))
      if frame==0:samples.append((origin,C.fork(m),(c.a,c.x,c.y,c.p,c.sp),o,f'firstB-mode{mode}-kind{kind}-face{face}-gap{gap}'))
      C.consume(m)
      if H.get(m,'KbMouth')or H.get(m,'KbHealth')<6:break
    return dict(mode=mode,enemy=kind,facing=face,gap=gap,B_direction=moving,npcspeed=npcspeed,health=H.get(m,'KbHealth'),mouth=H.get(m,'KbMouth'),updates=frame+1,minimum_Main_SP=minimum,trace=trace),samples

def original_friction(new):
    rom=P.DONOR.read_bytes();code=rom[16+0x21*8192:16+0x22*8192];seed=C.fresh(new);pairs=0
    for v in [0,1,13,14,15,32,64,128,255,256,257,336,512,588,65535,65523,65522,65521,65280,65024,64948]:
      m=bytearray(65536);m[0x8000:0xa000]=code;m[0x5bb]=v&255;m[0x5bc]=v>>8
      c=NesMPU(memory=m,pc=0x8597);c.a=0;c.y=10;c.sp=224;c.stPushWord(0x7ffe)
      for _ in range(100):
        if c.pc==0x7fff:break
        c.step()
      else:raise AssertionError('Original drag bound')
      port=C.fork(seed);H.put(port,MmVX=v&255) # actual live component is +1/+2
      port[address(new,'MmVX')+1]=v&255;port[address(new,'MmVX')+2]=v>>8
      H.put(port,KbFloat=0,MmUnderwater=0,KbAction=1)
      C.invoke(port,'KbMovement::Friction')
      got=port[address(new,'MmVX')+1]+256*port[address(new,'MmVX')+2]
      want=m[0x5bb]+256*m[0x5bc];assert got==want,('Original friction',v,got,want);pairs+=1
    return dict(passed=True,actual_original_8597_signed_velocity_pairs=pairs,ground_drag=14,instant_stop=False,scope='Actual donor8597 A0 Y10 against existing linked friction on signed Q8.8 velocities, including zero/crossing/sign cases. Original input/state/terrain wrapper is not transplanted.')

def main():
    q=dict(passed=False,source_CPU=True,native_emulator=False,installed=False,ROM_sha256=sha(O/'candidate.nes'))
    try:
      owner=json.loads((O/'owner-link.json').read_text());assert owner['passed']and owner['ROM_sha256']==q['ROM_sha256']
      for p,h in owner['bindings'].items():assert sha(p)==h,p
      old=qualified(P.J/'candidate.nes');new=qualified(O/'candidate.nes');a,astart=K.cold(old);b,bstart=K.cold(new)
      results=[];samples=[]
      for mode,kind,face,gap in itertools.product([0,1],[0,6],[1,2],[2,4]):
        before,_=case(a,mode,kind,face,gap);after,rows=case(b,mode,kind,face,gap)
        assert before['health']==5 and after['health']==6 and after['mouth']==kind+1,(before,after)
        assert after['updates']==1,after
        results.append(dict(old=before,new=after));samples.extend(rows)
      controls=[]
      for mode,kind,face,gap,moving in itertools.product([0,1],[0,6],[1,2],[-8,8],[False,True]):
        after,rows=case(b,mode,kind,face,gap,moving)
        if gap<0:assert after['health']==5 and after['mouth']==0,after
        else:assert after['health']==6 and after['mouth']==kind+1,after
        controls.append(after)
      walks=[]
      for mode,kind,face in itertools.product([0,1],[0,6],[1,2]):
        row,_=case(b,mode,kind,face,40,True,8)
        assert row['health']==6 and row['mouth']==kind+1,row;walks.append(row)
      # Earn real run velocity first; inhale then applies drag, retaining facing.
      runs=[]
      for face in [1,2]:
        m=C.fork(b);K.scene(m,face)
        for _ in range(10):K.main_step(m,1 if face==1 else 2);C.consume(m)
        before=value(m,'MmVX',1)+256*value(m,'MmVX',2);values=[];helper=[]
        for frame in range(4):
          keys=64+(1 if face==1 else 2);K.keys(m,keys);origin=C.fork(m);o=K.Observe(new)
          points={address(new,n):n for n in['KbInhaleFriction','KbMovement::KbInhaleFriction::Ordinary']}
          hits=[]
          def observe(mem,c,i):
            o(mem,c,i)
            if c.pc in points and mem.rawtags[1]==200:hits.append((i,c.sp,c.pc,points[c.pc]))
          c,low=K.call(m,'GameLoop',observe);got=value(m,'MmVX',1)+256*value(m,'MmVX',2)
          signed=lambda v:v if v<32768 else v-65536
          want=max(0,abs(signed(before))-14)*(1 if signed(before)>=0 else-1)
          assert signed(got)==want and H.get(m,'PlayerFacingDir')==face and H.get(m,'KbDash')==0 and H.get(m,'KbDashWindow')==0,(before,got,want,face)
          values.append(dict(before=signed(before),after=signed(got),facing=face));before=got
          if frame==0:
            samples.append((origin,C.fork(m),(c.a,c.x,c.y,c.p,c.sp),o,f'earned-run-inhale-face{face}'))
            for step,sp,pc,name in hits:
              selector=SimpleNamespace(low=(sp,step,pc,200),events=[])
              samples.append((origin,C.fork(m),(c.a,c.x,c.y,c.p,c.sp),selector,'explicit-new-helper-'+name))
          C.consume(m)
        runs.append(dict(face=face,source_velocity=values))
      earned=[]
      for family,face,target in itertools.product([2,3],[1,2],[6,0]):
        row,saved=K.earned_copy(b,family,face,target);earned.append(row)
        samples.extend((aa,bb,cc,dd,f'copy{family}-face{face}-target{target}')for aa,bb,cc,dd,_ in saved)
      q.update(original_friction=original_friction(new),actual_Select_Start_parser=dict(old=astart,new=bstart),fixed_forward_cases=results,front_rear_controls=controls,naturally_moving_enemy_approaches=walks,earned_run_inhale=runs,earned_shells=earned)
      q['interrupts']=K.interrupts(samples);assert q['interrupts']['passed'],q['interrupts']
      q.update(passed=True,caller='Unchanged actual Start JSR IdleLoop / PHA JSR Main / parent PLA, entrySP250; c864 native anchor retained as historical same-byte caller evidence.',scope='Actual full cartridge Main after real menu/parser, immediate capture, native defeated/score/SFX paths and all33SMC/livepage1 IRQ/NMI resumption. Easy/Hard and real native NPC movement data; no ability/HP/shot/outcome seeds. Not native emulator or full-stage proof.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    refs=[Path(__file__),R/'tools/audit/check_kirby_owner_main_1101_v2.py',R/'tools/audit/prepare_kirby_approach_owner_1101_v3.py',O/'candidate.nes',O/'candidate.dbg',O/'owner-link.json',O/'donor-inhale-witness.json',P.J/'candidate.nes',P.J/'candidate.dbg',P.J/'Main-CPU.json']
    q['bindings']={str(p.resolve()):sha(p)for p in refs};(O/'Main-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
    shown={k:v for k,v in q.items()if k not in['bindings','traceback','fixed_forward_cases','front_rear_controls','naturally_moving_enemy_approaches','earned_shells']}
    if'interrupts'in shown:shown['interrupts']={k:v for k,v in shown['interrupts'].items()if k!='rows'}
    print(json.dumps(shown));assert q['passed'],q.get('error')

if __name__=='__main__':main()
