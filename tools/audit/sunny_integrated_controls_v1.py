"""Finite actual-CPU Sunny shared integration checks; no native/PPU timing claim."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def seed(b,char):
 q=Arena(b,char);q.put(OperMode_Task=3,AreaType=1,AreaAddrsLOffset=5,AreaPointer=0x25,WorldNumber=0,NumberofLives=2,PlayerSize=0,PlayerStatus=1,Player_State=0,Player_Rel_XPos=96,Player_Rel_YPos=160,Player_MovingDir=1,Player_X_Speed=0,CurrentOAMOffset=0,TimerControl=0,GameEngineSubroutine=8,NmiDisable=255,DisableScreenFlag=1)
 if char==23:q.put(SunnyReady=0x53,SunnyLife=2,SunnyArea=0x25,SunnyWorld=0,SunnyForm=1,SunnyPalette=255)
 return q

def run(q,name,a=0,x=0,y=0,p=0x30,irq=False):
 b=q.b;s=b['syms'][name];g=b['segs'][s['seg']];pc=address(b,name);bank=(int(g['ooffs'],0)-16)//8192;win=(pc-0x8000)//8192
 q.m.page(win,bank)
 if win in(1,2):q.set('CurrentBank' if win==1 else 'CurrentBankC',bank|128)
 q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,253;c.stPushWord(0x5aff);seen=set();injected=0;steps=0
 while c.pc!=0x5b00:
  steps+=1;assert steps<300000,(name,'timeout',hex(c.pc),q.m.banks)
  at=c.pc;physical=q.m.banks[(at-0x8000)//8192] if at>=0x8000 else -1
  if irq and physical in[81,94,124,126,127] and not c.p&4 and (at,physical) not in seen:
   seen.add((at,physical));before=(c.pc,c.a,c.x,c.y,c.p,c.sp,bytes(q.m[:8]),q.get('CurrentBank'),q.get('CurrentBankC'));banks=q.m.banks[:];smc=bytes(q.m[z] for z in smc_at(b));q.m[0x5204]=128;c.irq()
   for _ in range(30000):
    if c.pc==before[0] and c.sp==before[5]:break
    c.step()
   else:raise AssertionError(('IRQ timeout',name,hex(c.pc)))
   assert (c.pc,c.a,c.x,c.y,c.p,c.sp,bytes(q.m[:8]),q.get('CurrentBank'),q.get('CurrentBankC'))==before,(name,'IRQ context',hex(at))
   assert q.m.banks==banks and bytes(q.m[z]for z in smc_at(b))==smc,(name,'IRQ bank/SMC',hex(at))
   injected+=1
  c.step()
 assert c.sp==253,(name,c.sp)
 return c,list(q.m.writes),injected

def smc_at(b):
 return [address(b,n)+i for n in ['NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC'] for i in ([1,2] if n=='FarcallJmpTarget_SMC' else [1])]
def registers(c):return[c.a,c.x,c.y,c.p,c.sp]
def app(q,skip=()):
 exclude=set(range(0x100,0x200))|set(range(0x2000,0x6000))|set(skip)
 # Active ExRAM is application RAM, not hardware: keep every byte.
 exclude-=set(range(0x5c00,0x5fff))
 for g in q.b['segs'].values():
  if g.get('name')=='"SMCCODE"':exclude.update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
 if 'safecall_a' in q.b['syms']:exclude.add(address(q.b,'safecall_a'))
 return bytes(v for i,v in enumerate(q.m[:0x8000]) if i not in exclude)
def cleanwrites(q,w):
 skip=set(range(0x100,0x200))|set(range(0x5114,0x5118))|set(smc_at(q.b))
 return[(i,v)for i,v in w if i not in skip]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={},bindings={str(z):sha(z)for z in[Path(__file__),a.rom,a.rom.with_suffix('.dbg'),a.baseline,a.baseline.with_suffix('.dbg'),R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py']})
 b=scoped_load(a.rom);old=scoped_load(a.baseline);checks=proof['checks']
 try:
  # The full RosterGraphicsBank caller normalizes X; compare full live return.
  cycles=[];n=0
  for char,variant,flags in itertools.product([3,4,5],range(3),[0x30,0x31,0x70,0x71,0x34,0xf3]):
   pair=[]
   for bundle in[old,b]:
    q=seed(bundle,char);q.set('Cv3Variant',variant);c,w,_=run(q,'RosterGraphicsBank',a=83,x=177,y=91,p=flags);pair.append((registers(c),app(q),q.m.banks,c.processorCycles))
   assert pair[0][:3]==pair[1][:3],('resident caller',char,variant,flags,pair[0][0],pair[1][0]);cycles.append(pair[1][3]-pair[0][3]);n+=1
  checks['resident_full_caller']=dict(passed=True,cases=n,cycles_delta=[min(cycles),max(cycles)])
  # Actual whole resident graphics selector, every old legal raw identity.
  cycles=[];n=0
  for char,variant in itertools.product(range(6,22),range(3)):
   pair=[]
   for bundle in[old,b]:
    q=seed(bundle,char)
    for nm in['Cv3Variant','MacVariant','ProtoVariant','ParodiusVariant','ChipVariant']:
     if nm in bundle['syms']:q.set(nm,variant)
    c,w,_=run(q,'CrossoverGraphicsBank',a=29,x=81,y=7,p=0x71);pair.append((registers(c),app(q),q.m.banks,c.processorCycles))
   assert pair[0][:3]==pair[1][:3],('whole graphics',char,variant,pair[0][0],pair[1][0]);cycles.append(pair[1][3]-pair[0][3]);n+=1
  q=seed(b,23);c,w,_=run(q,'CrossoverGraphicsBank',a=29,x=81,y=7,p=0x71);assert q.m.banks[2]==94 and q.get('CurrentBankC')==222
  checks['expanded_full_selector']=dict(passed=True,foreign_cases=n,foreign_cycles_delta=[min(cycles),max(cycles)],Sunny_C=94)
  # Sunny no-table body/terrain admission; box Y is the live native row.
  for yy in range(256):
   q=seed(b,23);c,_,_=run(q,'NrBox',a=23,x=93,y=yy,p=0x71);assert c.y==yy and c.x==93
   q=seed(b,23);c,_,_=run(q,'NrAdder',a=23,x=93,y=yy,p=0x71);assert not c.p&1 and c.y==yy and c.x==93
  checks['native_box_adder']=dict(passed=True,all_Y_cases=512)
  # Genuine loaded-scene persistence, including future bonus-pipe AreaPointer.
  q=seed(b,23);q.put(SunnyForm=2,PlayerStatus=2,AreaPointer=0xc2);q.m[0x5c00:0x5c80]=bytes(range(128));run(q,'SunnyEnsure');assert q.get('SunnyForm')==2 and bytes(q.m[0x5c00:0x5c80])==bytes(range(128))
  q.set('AreaAddrsLOffset',6);run(q,'SunnyEnsure');assert q.get('SunnyArea')==0x26 and q.get('PlayerStatus')==2
  q.set('NumberofLives',1);run(q,'SunnyEnsure');assert q.get('SunnyForm')==0 and q.get('PlayerStatus')==0 and q.get('PlayerSize')==1
  q=seed(b,23);q.set('SunnyForm',2);run(q,'NrFreshGameInit');assert bytes(q.m[0x5fb8:0x5fc0])==bytes(8)
  checks['lifecycle']=dict(passed=True,future_pipe_preserves=True,real_scene_preserves_form=True,life_loss_and_fresh_clear=True)
  # Actual pickup + real source freeze caller, all Easy/Hard initial forms.
  n=0
  for mode,form,kind in itertools.product([0,1],range(3),[0,1]):
   q=seed(b,23);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=form,PlayerSize=int(form==0),SunnyForm=form,ObjectOffset=5);q.set('PowerUpType',kind,5);q.set('Enemy_Flag',1,5);q.set('Enemy_ID',0x2e,5)
   run(q,'NrPickup',x=5);want=form if form==2 else min(2,form+1) if mode==0 else max(form,kind+1)
   for age in range(60):run(q,'PlayerChangeSize')
   assert [q.get(z) for z in ['PlayerStatus','SunnyForm','GuestPowerupActive','PlayerSize']]==[want,want,0,int(want==0)],('pickup',mode,form,kind,want,[q.get(z)for z in['PlayerStatus','SunnyForm','GuestPowerupActive','PlayerSize']]);n+=1
  for kind in[2,3]:
   q=seed(b,23);q.set('PowerUpType',kind,5);q.set('Enemy_Flag',1,5);run(q,'NrPickup',x=5)
   assert q.get('StarInvincibleTimer')==0x23 if kind==2 else q.get('FloateyNum_Control',5)==11
  q=seed(b,23);q.put(PlayerStatus=2,SunnyForm=2);run(q,'NrInjury');
  for _ in range(60):run(q,'PlayerChangeSize')
  assert q.get('PlayerStatus')==0 and q.get('SunnyForm')==0
  checks['actual_pickup_injury_pipeline']=dict(passed=True,Easy_Hard_form_cases=n,freeze_updates_per_case=60,native_star_life_cases=2,injury_source_freeze=True)
  # Native Mario audio is literally the same SoundEngine stream for Sunny.
  n=0;deltas=[];completion={}
  for event in[0,1,2,4,8,16,32,64]:
   pair=[seed(b,23) for _ in[0,23]]
   pair[0].set('SelectedCharacter',0)
   for q in pair:q.put(AreaMusicQueue=1,EventMusicQueue=event)
   for tick in range(900):
    if tick in[9,40,70]:
     for q in pair:q.put(Square1SoundQueue=1 if tick==9 else 2,Square2SoundQueue=16 if tick==40 else 0,NoiseSoundQueue=2 if tick==70 else 0)
    out=[]
    for q in pair:
     c,w,_=run(q,'AudioUpdate');out.append((registers(c),app(q,skip=[address(b,'SelectedCharacter')]),w,q.m.banks,c.processorCycles))
    assert out[0][:4]==out[1][:4],('native audio',event,tick,out[0][0],out[1][0])
    deltas.append(out[1][4]-out[0][4]);n+=1
    if event and tick>0 and pair[1].get('EventMusicBuffer')==0 and event not in completion:completion[event]=tick
  checks['native_audio']=dict(passed=True,paired_updates=n,ordered_all_writes_exact=True,native_event_buffer_clear_ticks=completion,Sunny_vs_Mario_cycle_delta=[min(deltas),max(deltas)])
  # Foreign audio same source calls/APU/state; routing cost measured separately.
  n=0;deltas=[]
  for char in[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]:
   pair=[seed(bundle,char)for bundle in[old,b]]
   for q in pair:q.put(AreaMusicQueue=1,EventMusicQueue=0,GamePauseStatus=1)
   for tick in range(3):
    out=[]
    for q in pair:
     c,w,_=run(q,'AudioUpdate');out.append((registers(c),app(q),cleanwrites(q,w),q.m.banks,c.processorCycles))
    assert out[0][:4]==out[1][:4],('foreign audio',char,tick,out[0][0],out[1][0]);deltas.append(out[1][4]-out[0][4]);n+=1
  checks['foreign_audio']=dict(passed=True,paired_updates=n,cycle_delta=[min(deltas),max(deltas)])
  # Existing extra foreground routes must retain full foreign live output.
  n=0;costs={}
  for name in['PlayerChangeSize','PlayerFireFlower','ProcFireball_Bubble']:
   ds=[]
   for char in range(23):
    if char==22:continue
    pair=[]
    for bundle in[old,b]:
     q=seed(bundle,char);q.put(TimerControl=1,GamePauseStatus=0,GuestPowerupActive=0);c,w,_=run(q,name,a=79,x=2,y=93,p=0x71);pair.append((registers(c),app(q),cleanwrites(q,w),q.m.banks,c.processorCycles))
    assert pair[0][:4]==pair[1][:4],('foreign caller',name,char,pair[0][0],pair[1][0]);ds.append(pair[1][4]-pair[0][4]);n+=1
   costs[name]=[min(ds),max(ds)]
  checks['foreign_foreground_callers']=dict(passed=True,cases=n,cycles_delta=costs)
  # Actual Sunny selector/graphics/draw with native source records in C94.
  n=0
  for form,face,state,water,crouch in itertools.product(range(3),[1,2],range(4),[0,1],[0,1]):
   q=seed(b,23);q.put(PlayerStatus=form,SunnyForm=form,PlayerSize=int(form==0),PlayerFacingDir=face,Player_State=state,SwimmingFlag=water,CrouchingFlag=crouch,PlayerAnimCtrl=1,SunnyClock=21,Player_Y_Speed=255 if state==1 else 1,Player_SprAttrib=0x23)
   run(q,'NrGraphics');assert q.m.banks[2]==94 and q.get('ObjectMetasprite')==address(b,'METASPRITE_SAMUS_BODY')
   ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1);at=16+94*8192+ptr-0xc000;count=b['raw'][at];assert count%4==0 and 0<count<=20
   run(q,'NrDraw');assert q.m.banks[2]==94;n+=1
  checks['graphics_draw']=dict(passed=True,cases=n,actual_C94_record_bounds=True)
  irqs=0
  for name in['NrGraphics','NrDraw','NrNativePowerupDispatch','NrObjectWeaponTail','AudioUpdate','CrossoverGraphicsBank']:
   q=seed(b,23);q.put(PlayerStatus=2,SunnyForm=2,AreaMusicQueue=1);c,w,nn=run(q,name,p=0x30,irq=True);irqs+=nn
  checks['actual_IRQ_boundaries']=dict(passed=True,injections=irqs,registers_flags_stack_R0_R7_banks_fiveSMC_exact=True)
  assert all(sha(z)==digest for z,digest in proof['bindings'].items());proof['passed']=True
 except Exception as e:
  proof.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:a.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(passed=proof['passed'],receipt=str(a.output),sha256=sha(a.output),checks=list(checks))))
if __name__=='__main__':main()
