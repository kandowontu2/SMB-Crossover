"""Real linked 4cbd native transaction/caller controls; never launches Mesen."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
import rogue_dawn_host_services_controls_v1 as prior
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/rogue-dawn-host-transactions-v2'
P=R/'build/roster-shared-rcr-adopted-v8.nes'
B=O/'candidate.nes'

def make(b):
 m=prior.arena(b,{})
 for n,v in [('NmiDisable',255),('AreaType',1),('CrossoverBehaviorVersion',1),('PlayerStatus',0),('PlayerSize',1),('ScreenLeft_PageLoc',0),('ScreenRight_PageLoc',1),('Up_Down_Buttons',0),('Player_X_Position',120),('Player_Y_Position',176),('Player_PageLoc',0)]:m[address(b,n)]=v
 m[0x5c01],m[0x5c02],m[0x5c0c],m[0x5c0d],m[0x5c0e]=15,4,0,192,128
 return m

def run(m,name,**kw):
 pc=address(m.bundle,name)
 # These are actual CPU entry contracts, not a claim that a low-bank helper
 # remaps its caller's bank9 local continuation by itself.
 bank=9 if name=='CrossoverBlockSize'else(location(m.bundle,name)-16)//8192 if 0xa000<=pc<0xc000 else m.banks[1]
 m.page(1,bank);m[address(m.bundle,'CurrentBank')]=bank|128
 return prior.invoke(m,pc,sp=0xe0,**kw)
def tile(m,wx,y,v):
 p,x=divmod(wx,256);a=address(m.bundle,'Block_Buffer_2'if p&1 else'Block_Buffer_1')+(y&240)-32+(x>>4);m[a]=v;return a
def get(m,n,i=0):return m[address(m.bundle,n)+i]

def main():
 global O,B
 if '--artifact' in sys.argv:
  O=Path(sys.argv[sys.argv.index('--artifact')+1]).resolve();B=O/'candidate.nes'
 b=scoped_load(B);parent=scoped_load(P);count={};cost={};low=255
 owned=set(range(0x5c00,0x5c80))|set(range(0x5fb0,0x5fb8))
 # No new service/overlay access before exact owner. The existing native
 # foreign platform path is compared separately, not falsely called a no-op.
 n=0
 for char,var,name in itertools.product([0,1,2,3,4,20,21,23,255],[0,1,2],['RdHostDispatch','RdTxHead','RdTxAfterMovement']):
  if(char,var)==(2,1):continue
  m=make(b);m[address(b,'SelectedCharacter')]=char;m[0x5fee]=var
  c,l,t=run(m,name,a=0x5a,x=3,y=7,p=0x71)
  assert not m.reads&owned and not any(a in owned for a,v in m.writes),(char,var,name)
  assert not c.p&1;n+=1
 count['foreign_no_overlay_reads_or_writes']=n
 # Actual immutable bridge identifies7 Health/8 Low. Preserve v1 negative,
 # then prove source B11C clears Hit only forHealth, notLowHealth.
 sounds=[]
 for service,name in [(7,'RdHostHealthSound'),(8,'RdHostLowHealthSound')]:
  m=make(b);m[0x5c0a]=0xa5;m[0x5c79]=service
  c,l,t=run(m,name,a=0,x=3,y=7)
  assert m[0x5c0a]==(0 if service==7 else 0xa5)
  assert (m.banks[1],m.banks[2])==(95,94)
  sounds.append(dict(service=service,callback=name,hit=m[0x5c0a],CPU=c.processorCycles,minimum_SP=l))
 count['actual_bridge_sound_endpoints']=sounds
 # Real SetupPowerUp -> NrPrepare -> exact-owner constructor hook, including
 # Star/Life. It cannot descend the old Samus inventory chain or grant early.
 prep=[]
 for slot,typ in itertools.product(range(6),range(4)):
  m=make(b);m[address(b,'Enemy_ID')+slot]=0x2e;m[address(b,'PowerUpType')+slot]=typ
  before=bytes(m[0x5fb0:0x5fb6]);c,l,t=run(m,'NrPrepare',a=0x59,x=slot,y=7,p=0x71)
  assert bytes(m[0x5fb0:0x5fb6])==before
  assert get(m,'InvPickup',slot)==([0xd8,0xd9,0xfc,0xfc][typ])
  assert (c.a,c.x,c.y,c.p&207)==(0x59,slot,7,0x71&207)
  assert not any(pc==address(b,'InventoryPreparePickup')for pc,bank in t)
  prep.append(dict(slot=slot,type=typ,CPU=c.processorCycles,minimum_SP=l))
 count['actual_NrPrepare_typed_construction_no_grant']=prep
 # Full real CrossoverBlockSize legal foreign modes/PlayerStatus/SmBall and
 # block-attack values. New Rogue fences before ANY old SmBall access.
 n=0
 for char,mode,status,ball,attack,iy in itertools.product(range(24),[0,1],range(3),[0,1],[0,1],[0,1]):
  one=[]
  for bundle in [parent,b]:
   m=make(bundle)
   for name,v in [('SelectedCharacter',char),('CrossoverBehaviorVersion',mode),('PlayerStatus',status),('SmBall',ball),('MmBlockAttack',attack)]:m[address(bundle,name)]=v
   m[0x5fee]=0
   c,l,t=run(m,'CrossoverBlockSize',a=0x5a,x=4,y=iy,p=0x71)
   one.append((c.a,c.x,c.y,c.p,c.sp))
  assert one[0]==one[1],(char,mode,status,ball,attack,iy,one);n+=1
 for mode,status,ball in itertools.product([0,1],range(3),[0,1,255]):
  m=make(b);m[address(b,'CrossoverBehaviorVersion')]=mode;m[address(b,'PlayerStatus')]=status;m[address(b,'SmBall')]=ball
  c,l,t=run(m,'CrossoverBlockSize',y=0)
  assert c.y==1 and address(b,'SmBall')not in m.reads
 count['complete_native_block_size_foreign_cells']=n
 count['Rogue_no_legacy_ball_reads']=18
 # Native head/questions/bricks keep authoritative row/column and no source
 # separation warp. Cell-bottom gate negatives cover all15noncrossing phases.
 rows=[]
 for page,x,metatile in itertools.product([0,1],[4,128,252],[0x51,0x52,0x5f,0x60]):
  m=make(b);m[0x5c0c]=page;m[0x5c0e]=x;m[0x5c0d]=191
  pos=page*256+x-4
  if pos<0:continue
  a=tile(m,pos,175,metatile);before=bytes(m[0x5c00:0x5c30]);zp=bytes(m[3:11]);temps=bytes(m[z]for z in [0x5c31,0x5c32,0x5c33,0x5c35,0x5c36,0x5c37])
  c,l,t=run(m,'RdTxHead');low=min(low,l)
  assert m[a]==0x23 and get(m,'BlockBounceTimer')==16,(page,x,metatile,hex(m[a]),get(m,'BlockBounceTimer'))
  assert bytes(m[0x5c00:0x5c30])==before and bytes(m[3:11])==zp
  assert bytes(m[z]for z in [0x5c31,0x5c32,0x5c33,0x5c35,0x5c36,0x5c37])==temps
  assert any(pc==address(b,'NativeRarePlayerHeadCollisionCore')and bank==9 for pc,bank in t)
  rows.append(dict(page=page,x=x,tile=metatile,CPU=c.processorCycles,minimum_SP=l))
 for phase in range(15):
  m=make(b);m[0x5c0d]=176+phase;tile(m,124,160+phase,0x51)
  c,l,t=run(m,'RdTxHead');assert get(m,'BlockBounceTimer')==0
  assert not any(pc==address(b,'PlayerHeadCollision')for pc,bank in t)
 count['real_native_head_transactions']=rows;count['noncrossing_ceiling_side_rejections']=15
 # One native coin even when all nine samples touch adjacent coins. Resource
 # changes come from GiveOneCoin and actual point/VRAM owners, not seeded outcomes.
 coins=[]
 for page,x,y,typ in itertools.product([0,1],[8,128,248],[160,192],[0xc2,0xc3]):
  m=make(b);m[0x5c0c],m[0x5c0e],m[0x5c0d]=page,x,y
  a=tile(m,page*256+x-4,y-15,typ);zp=bytes(m[3:11]);c,l,t=run(m,'RdTxAfterMovement');low=min(low,l)
  assert m[a]==0 and get(m,'CoinTallyFor1Ups')==1 and bytes(m[3:11])==zp
  assert any(pc==address(b,'HandleCoinMetatile')for pc,bank in t)
  coins.append(c.processorCycles)
 count['real_native_coin_transactions']=len(coins);cost['coin_CPU']=[min(coins),max(coins)]
 # Down-pipe is a real native paired10/11+Down transaction; no fake source
 # Door/Elevator flags or scene seeds. Wrong pair/button never enters pipe.
 n=0
 for down,left,right in itertools.product([0,4],[0,0x10],[0,0x11]):
  m=make(b);m[0x5c0e]=128;m[0x5c29]=down;m[address(b,'Up_Down_Buttons')]=down
  tile(m,124,208,left);tile(m,132,208,right)
  c,l,t=run(m,'RdTxAfterMovement');low=min(low,l)
  yes=(down,left,right)==(4,0x10,0x11)
  assert get(m,'GameEngineSubroutine')==(3 if yes else 8)
  if yes:assert get(m,'ChangeAreaTimer')==0x30 and get(m,'Player_SprAttrib')==0x20
  assert m[0x5c00]not in [5,9];n+=1
 count['native_pipe_pair_button_controls']=n
 # Genuine existing HPlat/S_Plat/VPlat callers execute their real math and
 # private gate. All foreign outputs remain fullAXYP/SP and applicationRAM
 # equivalent except foreground fiveSMC final target/dead stack.
 n=0;platform=[]
 for char,var,pc,x,ordinate,delta in itertools.product([0,2,4,21],[0,1],['PositionPlayerOnHPlat','PositionPlayerOnVPlat','PositionPlayerOnS_Plat'],[0,4],[64,176],[0,1,255]):
  if pc=='PositionPlayerOnS_Plat'and delta!=0:continue
  outputs=[]
  for bundle in [parent,b]:
   m=make(bundle);m[address(bundle,'SelectedCharacter')]=char;m[0x5fee]=var
   m[address(bundle,'Enemy_Y_Position')+x]=ordinate;m[address(bundle,'Enemy_Y_HighPos')+x]=1;m[address(bundle,'R0')]=delta
   m[address(bundle,'Enemy_ID')+x]=0x28
   c,l,t=run(m,pc,a=2 if pc=='PositionPlayerOnS_Plat'else ordinate,x=x,p=0x71)
   outputs.append((m,c,l))
  m,c,l=outputs[1];low=min(low,l)
  if(char,var)==(2,1):
   assert get(m,'Player_Y_Position')==(ordinate-32)&255
   assert m[0x5c0d]==(ordinate-16)&255 and m[0x5c08]==m[0x5c14]==0 and m[0x5c2d]==1
   assert m[0x5c0e]==(get(m,'Player_X_Position')+8)&255
   platform.append(c.processorCycles)
  else:
   old,oc,ol=outputs[0]
   assert (oc.a,oc.x,oc.y,oc.p,oc.sp)==(c.a,c.x,c.y,c.p,c.sp),(char,var,pc,x,ordinate,delta,(oc.a,oc.x,oc.y,oc.p),(c.a,c.x,c.y,c.p))
   for name in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','Player_Y_MoveForce','Platform_X_Scroll']:
    assert get(m,name)==get(old,name),(name,char,var,pc)
  n+=1
 count['full_native_platform_caller_controls']=n;cost['owned_platform_CPU']=[min(platform),max(platform)]
 cost['head_CPU']=[min(z['CPU']for z in rows),max(z['CPU']for z in rows)]
 # Complete original action owner -> fixed C94 bridge -> real native block
 # constructor, with initialized actual driver and real NMI/IRQ returns. No
 # stand-in service/return PCs. The admitted entrySP224 is explicit.
 seams=[]
 for name,bank in [('RdTxHead',95),('NativeRarePlayerHeadCollisionCore',9),('SetupPowerUp',9),('NrPrepare',124),('RdNrPrepare',124),('RdTxPrepareActor',95),('RdHsPrepareActor',95)]:
  for kind in ['IRQ','lagNMI']:
   m=make(b);m[0x5c0d]=191;tile(m,124,175,0x60)
   m[0x5c00]=2;m[0x5c08]=0xfd;m[0x5c14]=0x1a;m[0x5c29]=128;m[0x5c03]=12
   m.page(1,124);m[address(b,'CurrentBank')]=252
   c,l,tr=prior.invoke(m,address(b,'RdControlStep'),sp=224,seam=(address(b,name),bank,kind));low=min(low,l)
   assert any(pc==address(b,'NativeRarePlayerHeadCollisionCore')and a==9 for pc,a in tr)
   assert any(pc==address(b,'RdTxPrepareActor')and a==95 for pc,a in tr)
   seams.append(dict(entry=name,bank=bank,kind=kind,minimum_SP=l,real_source_control_and_native_constructor=True))
 count['complete_action_native_head_ISR_seams']=seams
 # Four continuous source action campaigns using real imported/exported world
 # positions and actual after-Main transactions. Authored CPU terrain is not a
 # claimed native run or source Metroid room. No health/gear acquisition claim.
 actions=[]
 for gear,pads in [(0,[0]*3+[129]*10+[1]*65+[0]*8),(4,[2]*12+[130]*10+[2]*55),(17,[4,0,128]+[0]*45+[8,0]+[0]*35),(8,[129]*14+[1]*60)]:
  m=make(b);m[0x5fb0]=gear;m[0x5fb4]=0x99;m[0x5fb5]=9
  m[address(b,'Player_X_Position')]=96
  for pg,xx in itertools.product(range(2),range(16)):tile(m,pg*256+16*xx,208,0x54)
  run(m,'RdHsEnterScene');seen=set();total=0;lowest=255
  for pad in pads:
   m[address(b,'SavedJoypadBits')]=pad;m[address(b,'Up_Down_Buttons')]=pad&12
   for target in ['RdHsImportPosition','RdHsClockBefore','RdControlStep','RdHsExportPosition','RdTxAfterMovement','RdHsClockAfter']:
    c,l,tr=run(m,target);total+=c.processorCycles;lowest=min(lowest,l);low=min(low,l)
   seen.add(m[0x5c00])
  assert get(m,'Player_Y_HighPos')==1 and m[0x5c0d]+m[0x5c01]<208
  actions.append(dict(gear=gear,updates=len(pads),actions=sorted(seen),final_host_position=[get(m,'Player_PageLoc')*256+get(m,'Player_X_Position'),get(m,'Player_Y_Position')],CPU=total,minimum_SP=lowest))
 count['continuous_real_source_action_transactions']=actions
 proof=dict(passed=True,source_only=True,native_run=False,ROM_sha256=ref.digest(B.read_bytes()),counts=count,positive_CPU=cost,minimum_SP=low,entry_SP=224,actor_damage_freeze_unadmitted=True,shared_admission_menu_items_audio_open=True,bindings=[ref.binding(p)for p in [Path(__file__),B,B.with_suffix('.dbg'),O/'build.json',R/'src/rogue_dawn_host_transactions.s']])
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,minimum_SP=low,counts={k:v if isinstance(v,int)else len(v)for k,v in count.items()},costs=cost)))
if __name__=='__main__':main()
