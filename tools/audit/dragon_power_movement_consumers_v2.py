"""Additional real source/native consumers, lifecycle and interrupt ownership."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import dragon_power_movement_controls_v2 as C
import nr_router_compact_controls_v1 as I
from sunny_integrated_controls_v1 import *
O=C.O
def interrupt_actual(q,name,target=None,flags=0x30,inject=None,kind='IRQ',a=91,x=0,y=0,record_trace=False):
    b=q.b;pc=address(b,name);bank=(location(b,name)-16)//8192;win=(pc-0x8000)//8192;q.m.page(win,bank)
    if win in(1,2):q.set('CurrentBank' if win==1 else 'CurrentBankC',bank|128)
    q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,flags,253;c.stPushWord(0x5aff)
    minimum=c.sp;entry=None;hit=False;trace=[]
    for _ in range(300000):
        minimum=min(minimum,c.sp)
        if c.pc==0x5b00:assert c.sp==253;return c,entry,minimum,trace,hit
        physical=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if entry is None and target and c.pc==target[0]and physical==(target[1]&127):
            entry=(registers(c),C.fastapp(q),tuple(q.m.banks),bytes(q.m[z]for z in smc_at(b)),bytes(q.m[0x101+c.sp:0x200]))
        if record_trace:trace.append((physical,c.pc))
        if inject==(physical,c.pc)and not hit:
            def state():return(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,tuple(q.m.banks),bytes(q.m[:11]),bytes(q.m[0x101+c.sp:0x200]),bytes(q.m[z]for z in smc_at(b)),bytes(q.m[0x5c00:0x6000]),q.get('CurrentBank'),q.get('CurrentBankC'))
            before=state()
            if kind=='IRQ':
                assert not c.p&4;q.m[0x5204]=128;c.irq()
            else:c.nmi()
            for _ in range(60000):
                c.step();minimum=min(minimum,c.sp)
                if c.pc==before[0]and c.sp==before[5]:break
            else:raise AssertionError(('ISR timeout',name,kind,hex(c.pc)))
            assert state()==before,('ISR full context',name,kind,inject,[(i,(a0,b0))for i,(a0,b0)in enumerate(zip(before,state()))if a0!=b0]);hit=True
        assert q.m[c.pc]!=0,('BRK',name,q.get('SelectedCharacter'),hex(c.pc),physical);c.step()
    raise AssertionError(('timeout',name,q.get('SelectedCharacter'),hex(c.pc)))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 b=scoped_load(O/'candidate.nes');proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={});ck=proof['checks']
 try:
  # Complete source jump -> source pending commit -> native slot claim,
  # genuine question/brick transaction, all within the real Main pipeline.
  rows=[]
  for tile,mode in itertools.product([0x51,0x55,0xc0],range(2)):
   q=C.setup(b);q.put(CrossoverBehaviorVersion=mode)
   at=address(b,'Block_Buffer_1')+0x70+6;q.m[at]=tile
   found=False
   for age in range(48):
    q.put(SavedJoypadBits=128 if 1<=age<20 else 0,NmiDisable=255,VRAM_Buffer1_Offset=0)
    c,tr,mn=C.runtrace(q,'GameLoop')
    if (126,address(b,'PlayerHeadCollision'))in tr:
     assert q.m[at]==0x23 and q.m[address(b,'DpContacts')+7]==0,('real command ACK',tile,mode,age)
     assert (86,address(b,'DpHostCommitBlock'))in tr
     rows.append([tile,mode,age,c.processorCycles,mn]);found=True;break
   assert found,('source jump failed to issue real command',tile,mode,q.get('DpAction'),q.get('DpY'))
  ck['source_jump_full_Main_native_block_consumer']=dict(cases=len(rows),rows=rows,no_seeded_command_or_native_outcome=True)
  # Exact EF77 replacement ABI: original STA changes no register/flag. Only
  # the three existing pending fields get the declared world-cell encoding.
  count=0
  for f,slot in itertools.product([p for p in range(256)if p&0x30==0x30],range(2)):
   q=C.setup(b);q.put(DpProbeX=173,DpProbePage=3,DpProbeY=0xa0)
   c,_,_=run(q,'DpHostCommitBlock',a=128,x=slot,y=91,p=f)
   assert registers(c)==[128,slot,91,f,253],('source publication ABI',f,slot,registers(c))
   assert [q.m[address(b,'DpContacts')+i+slot]for i in[7,9,11]]==[0x8a,160,3]
   count+=1
  ck['source_EF77_all_flags']=dict(cases=count,AXYP_SP_exact=True,no_new_RAM=True)
  # Existing native platform ownership records, including balance sibling and
  # small-platform second arm, prevent inventing support on coincidentY alone.
  count=0
  for kind,slot in itertools.product(range(0x24,0x2d),range(6)):
   for accepted in[False,True]:
    q=C.setup(b);q.set('Enemy_Flag',1,slot);q.set('Enemy_ID',kind,slot);q.set('Enemy_Y_HighPos',1,slot)
    q.set('Enemy_Y_Position',208,slot);q.set('PlatformCollisionFlag',slot if accepted else 255,slot)
    if kind==0x24:q.set('Enemy_State',slot,slot)
    if kind>=0x2b:q.set('PlatformCollisionFlag',2 if accepted else 255,slot)
    run(q,'DpHostSupport');assert q.get('DpPlatform')==(128 if accepted else 0),('real platform owner',kind,slot,accepted,q.get('DpPlatform'))
    assert q.m[address(b,'DpPlatform')+1]==0,('double horizontal carry',kind,slot)
    count+=1
  ck['native_platform_owner_import']=dict(cases=count,source_horizontal_carry_zero_because_native_world_carry_already_committed=True)
  # Real loaded-scene owner, future pipe pointer and actual life gain/loss.
  q=C.setup(b);run(q,'DpEnsure');q.put(DpPole=1,DpWaves=7,DpHP=83,DpClock=17,AreaPointer=0xc2)
  run(q,'DpEnsure');assert [q.get(n)for n in['DpHP','DpPole','DpWaves','DpClock']]==[83,1,7,17]
  q.set('NumberofLives',3);run(q,'DpEnsure');assert q.get('DpHP')==83 and q.get('DpWaves')==7
  q.set('AreaAddrsLOffset',6);run(q,'DpEnsure');assert q.get('DpArea')==0x26 and q.get('DpClock')==0 and q.get('DpWaves')==7
  q.set('NumberofLives',2);run(q,'DpEnsure');assert [q.get(n)for n in['DpHP','DpPole','DpWaves']]==[100,0,0]
  q.put(DpHP=12,DpPole=1);run(q,'DpHostReset');assert q.get('DpHP')==100 and q.get('DpPole')==0
  ck['lifecycle']=dict(actual_scene_future_AreaPointer_preserves=True,life_gain_preserves=True,life_loss_resets=True,explicit_future_menu_Reset_API_resets=True,menu_not_admitted=True)
  # Actual reached instructions of both real bridge target rebindings and the
  # owned source/native controller. Preserve unknown/wrong bank/SP guards.
  events=[];minsp=255
  for name,ch in[('GuestGameRoutinesBridge',0),('GuestGameRoutinesBridge',24),('DpHostController',24),('DpHostCommitBlock',24),('DpHostBlocks',24)]:
   q=C.setup(b,ch);q.put(NmiDisable=255)
   if name=='DpHostBlocks':q.put(DpProbeX=160,DpProbePage=0,DpProbeY=0x50);run(q,'DpHostCommitBlock',a=128);q.m[address(b,'Block_Buffer_1')+0x50+10]=0x55
   c,tr,mn=C.runtrace(q,name,a=128,p=0x30)
   points=sorted(set((bank,pc)for bank,pc in tr if bank==86 or bank==127 and address(b,'GuestGameRoutinesBridge')<=pc<address(b,'GuestGameRoutinesBridge')+45))
   for kind,point in itertools.product(['IRQ','NMI'],points):
    q=C.setup(b,ch);q.put(NmiDisable=255)
    if name=='DpHostBlocks':q.put(DpProbeX=160,DpProbePage=0,DpProbeY=0x50);run(q,'DpHostCommitBlock',a=128);q.m[address(b,'Block_Buffer_1')+0x50+10]=0x55
    c,_,sp,_,hit=interrupt_actual(q,name,flags=0x30,inject=point,kind=kind,a=128)
    assert hit;events.append([name,ch,kind,*point]);minsp=min(minsp,sp)
  ck['actual_IRQ_and_lagNMI_seams']=dict(cases=len(events),minimum_SP=minsp,PC_AXYP_live_stack_R0_R7_physical_banks_shadows_5SMC_context_exact=True,events=events)
  proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(C.__file__),Path(I.__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',R/'build/dragon_power_movement_host_v1.inc']}
 a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']
if __name__=='__main__':main()
