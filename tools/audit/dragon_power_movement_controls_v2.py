"""Finite real linked movement consumers; source CPU only, no native admission."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from sunny_integrated_controls_v1 import *
from nr_router_compact_controls_v1 import fastapp
O=R/'build/dragon-power-movement-v1';OLD=R/'build/nr-router-compact-v1.nes'
def setup(b,ch=24):
 q=seed(b,ch);q.put(Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,
 Player_Rel_XPos=96,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,
 ScreenRight_PageLoc=0,Player_Pos_ForScroll=96,PlayerFacingDir=1,Player_MovingDir=1,Player_State=0,PlayerSize=0,
 GameTimerDisplay=4,PlayerStatus=0,GameEngineSubroutine=8,PlayerEntranceCtrl=2,NmiDisable=255)
 # Actual two-column-map buffers: flat native floor at screenY208.
 for base in ['Block_Buffer_1','Block_Buffer_2']:
  for x in range(16):q.m[address(b,base)+0xb0+x]=0x61
 return q
def flags(c):return c.p&0xcf
def snap(q,c):return(registers(c),fastapp(q),tuple(q.m.banks),bytes(q.m[i]for i in smc_at(q.b)))
def runtrace(q,name,a=0,x=0,y=0,p=0x30):
 b=q.b;pc=address(b,name);bank=(location(b,name)-16)//8192;win=(pc-0x8000)//8192;q.m.page(win,bank)
 if win in[1,2]:q.set('CurrentBank'if win==1 else'CurrentBankC',bank|128)
 q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,253;c.stPushWord(0x5aff);trace=[];mn=253
 for _ in range(300000):
  if c.pc==0x5b00:return c,trace,mn
  mn=min(mn,c.sp);at=c.pc;physical=q.m.banks[(at-0x8000)//8192]if at>=0x8000 else-1
  trace.append((physical,at));assert q.m[at]!=0,('BRK',name,hex(at),physical);c.step()
 raise AssertionError(('timeout',name,hex(c.pc),q.m.banks))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 old,new=[scoped_load(p)for p in[OLD,O/'candidate.nes']];proof=dict(passed=False,native_run=False,source_CPU_only=True,checks={});ck=proof['checks']
 try:
  rows=[]
  for ch,mode,keys in itertools.product([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,26,27,28],range(2),[0,1,129]):
   pair=[]
   for b in[old,new]:
    q=setup(b,ch);q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3)
    c,tr,mn=runtrace(q,'GameLoop',p=0x71);pair.append((snap(q,c),[(i,v)for i,v in q.m.writes if i not in smc_at(b)and not 0x100<=i<0x200 and not 0x5114<=i<=0x5117],c.processorCycles,mn))
   assert pair[0][:2]==pair[1][:2],('foreign complete Main',ch,mode,keys,pair[0][0][0],pair[1][0][0]);rows.append([ch,mode,keys,pair[1][2]-pair[0][2],pair[1][3]])
  ck['foreign_complete_Main']=dict(cases=len(rows),AXYP_SP_allapplication_OAM_CHR_final5SMC_banks_and_remaining_ordered_writes_exact=True,CPU_delta=[min(z[-2]for z in rows),max(z[-2]for z in rows)],min_SP=min(z[-1]for z in rows),rows=rows)
  # Actual source movement and camera commit through COMPLETE Main, including
  # no-DrawAll catch-up. No host actor weapon/HP/audio/menu qualification.
  rows=[]
  for mode,facing,skip in itertools.product(range(2),[1,2],[0,1]):
   q=setup(new);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=facing,ShouldSkipDrawSprites=skip)
   cycles=[]
   for age in range(96):
    keys=(1 if facing==1 else 2)|(128 if 8<=age<16 or 50<=age<58 else 0)
    q.put(SavedJoypadBits=keys,NmiDisable=255,VRAM_Buffer1_Offset=0)
    c,tr,mn=runtrace(q,'GameLoop',p=0x30);cycles.append(c.processorCycles)
    assert tr.count((86,address(new,'DpSourceFrame')))==1,('one source frame',age)
    assert (126,address(new,'PlayerBGCollision'))not in tr,('second native solid resolver',age)
    assert q.get('DpX')==(q.get('Player_X_Position')-q.get('ScreenLeft_X_Pos'))&255,('late camera sourceX',age)
    assert q.get('DpY')==(q.get('Player_Y_Position')+16)&255,('late native sourceY',age)
    assert q.get('CurrentBank')&127==q.m.banks[1]and q.get('CurrentBankC')&127==q.m.banks[2]
   rows.append([mode,facing,skip,min(cycles),max(cycles),q.get('DpClock'),q.get('Player_X_Position'),q.get('Player_PageLoc')])
  ck['owned_complete_Main']=dict(updates=96*len(rows),one_real_source_frame_per_update=True,no_second_native_solid_resolver=True,post_camera_nativecarry_coordinates_exact=True,rows=rows)
  # Existing pending record carries true world coordinates across camera moves;
  # real busy native block slots preserve command and actual admission ACKs once.
  rows=[]
  for tile in[0x51,0x55,0x58,0xc0,0xc1]:
   q=setup(new);run(q,'DpEnsure');q.put(DpProbeX=160,DpProbePage=0,DpProbeY=0x50)
   run(q,'DpHostCommitBlock',a=128,x=0,p=0x71)
   assert [q.m[address(new,'DpContacts')+i]for i in[7,9,11]]==[0x85,160,0]
   at=address(new,'Block_Buffer_1')+0x50+10;q.m[at]=tile
   q.put(ScreenLeft_X_Pos=17);q.set('Block_State',0x11,0);q.set('Block_State',0x11,1)
   before=bytes(q.m[at:at+1]);run(q,'DpHostBlocks');assert q.m[address(new,'DpContacts')+7]==0x85 and bytes(q.m[at:at+1])==before,('busy lost record',tile)
   q.set('Block_State',0,0);q.set('Block_RepFlag',0,0);before=[q.get(n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','PlayerSize','CrouchingFlag','Player_Y_Speed','MmBlockAttack']]
   c,tr,mn=runtrace(q,'DpHostBlocks');assert q.m[address(new,'DpContacts')+7]==0 and q.m[at]==0x23,('native consume/ACK',tile,hex(q.m[at]))
   assert before==[q.get(n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','PlayerSize','CrouchingFlag','Player_Y_Speed','MmBlockAttack']],('native block player restore',tile)
   assert (126,address(new,'PlayerHeadCollision'))in tr
   rows.append([tile,c.processorCycles,mn,q.get('Block_Metatile',0)])
  ck['real_native_block_busy_retry_ACK']=dict(cases=len(rows),rows=rows)
  proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',R/'build/dragon_power_movement_host_v1.inc',OLD,OLD.with_suffix('.dbg')]}
 a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']
if __name__=='__main__':main()
