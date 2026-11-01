"""Real native geometry/effects for Tank; explicit preloaded C2 CPU fixture."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_host_1101_v2 import P,O,PIN,REF,TERRAIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN
 assembly=json.loads((O/'host-assembly.json').read_text())
 for p in [REF,TERRAIN]:assert sha(p.read_bytes())==assembly['source_bindings'][str(p.relative_to(R))]
 labels={q[2][1:]:int(q[1],16)for line in(O/'host.lbl').read_text().splitlines()if len(q:=line.split())==3}
 code=(O/'host.bin').read_bytes();measured={};seed=M.fresh(b)
 S=0x880;BUDGET=0x88a;HEAD=0x88b
 def fresh(**values):
  m=M.fork(seed);m.ram[2][0x1600:0x1600+len(code)]=code
  M.put(m,SelectedCharacter=0,MarioVariant=7,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,PlayerStatus=2,PlayerSize=0,Player_State=0,Player_CollisionBits=3,Player_Y_Position=96,Player_Y_HighPos=1,Player_X_Position=96,Player_PageLoc=0,PlayerFacingDir=1,Player_MovingDir=1,AreaType=1,ObjectOffset=0,NmiDisable=255,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,Player_Y_Speed=0xfd)
  M.put(m,**values)
  return m
 def call(m,name,*,a=85,x=0,y=3,p=0x31):
  if name not in labels:return M.invoke(m,name,a=a,x=x,y=y,p=p)
  target=labels[name];m[address(b,'SafecallA_SMC')+1]=a;m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
  c=NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=2;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff);low=c.sp
  for _ in range(300000):
   if c.pc==0x5b00:break
   assert m[c.pc]!=0,(name,hex(c.pc),m.rawtags);c.step();low=min(low,c.sp)
  else:raise AssertionError((name,'bounded',hex(c.pc)))
  assert c.sp==224 and m.rawtags[1]==M.get(m,'CurrentBank')and m.rawtags[2]==M.get(m,'CurrentBankC')
  q=measured.setdefault(name,dict(calls=0,max_cycles=0,minimum_SP=224));q['calls']+=1;q['max_cycles']=max(q['max_cycles'],c.processorCycles);q['minimum_SP']=min(q['minimum_SP'],low)
  return dict(A=c.a,X=c.x,Y=c.y,P=c.p,CPU=c.processorCycles,minimum_SP=low)
 def probe(m,y=3,head=False):
  call(m,'BlockBufferColli_Head'if head else'BlockBufferColli_Side',y=y)
  return M.get(m,'R6')+256*M.get(m,'R7')+M.get(m,'R2')
 def player(m):return tuple(M.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','Player_X_Speed','PlayerSize','CrouchingFlag'])
 protected=set(json.loads((R/'build/mario-tank-source-1101-v1/rules-CPU-controls.json').read_text())['protected_metatiles'])
 tile=0;m=fresh()
 for v,p in itertools.product(range(256),[0x30,0xf1]):
  c=call(m,'MtTerrainTileChecks',a=v,p=p);assert c['A']==v and bool(c['P']&1)==(v in protected);tile+=1
 # Native queries supply the complete world cell, including page carry.
 # Side destruction must not collect a coin above that cell or release items.
 side=0
 for page,px,adder,cell in itertools.product([0,1],[0,8,240,248,255],[3,4,5,6],[0x51,0xc1,0x61]):
  m=fresh(Player_PageLoc=page,Player_X_Position=px);at=probe(m,adder);row=M.get(m,'R2');world=M.get(m,'R5');xp=page+int(world<px)
  m[at]=cell;m[at-16]=0xc2;m[address(b,'R3')]=cell
  prior=player(m);z=bytes(m[address(b,'R0'):address(b,'R0')+8]);y=adder
  c=call(m,'MtTerrainDestroyCell',a=cell,y=y)
  assert c['P']&1 and c['A']==0 and m[at]==0 and m[at-16]==0xc2
  assert player(m)==prior and bytes(m[address(b,'R0'):address(b,'R0')+8])==z and c['Y']==y
  assert m.ram[2][BUDGET]==1 and M.get(m,'NoiseSoundQueue')==1 and M.get(m,'VRAM_Buffer_AddrCtrl')==6
  assert M.get(m,'Block_State')==0x12 and M.get(m,'Block_Metatile')==0 and M.get(m,'Block_RepFlag')==0
  assert M.get(m,'Block_X_Position')==world&0xf0 and M.get(m,'Block_PageLoc')==xp and M.get(m,'Block_Y_Position')==(row+32)&255
  assert M.get(m,'Block_Y_HighPos')==1 and M.get(m,'Block_Y_HighPos',2)==1
  assert M.get(m,'Block_X_Speed')==240 and M.get(m,'Block_Y_Speed')==250 and M.get(m,'Block_Y_Speed',2)==252
  assert not M.get(m,'Enemy_Flag',5) and M.get(m,'PlayerScoreDisplay',5)==5
  # A second distinct cell remains intact and awards no repeated score.
  m[at+1]=0x51;m[address(b,'R6')]=(M.get(m,'R6')+1)&255
  score=bytes(m[address(b,'PlayerScoreDisplay'):address(b,'PlayerScoreDisplay')+6]);c=call(m,'MtTerrainDestroyCell',a=0x51,y=y)
  assert c['A']==0 and c['P']&1 and m[at+1]==0x51 and score==bytes(m[address(b,'PlayerScoreDisplay'):address(b,'PlayerScoreDisplay')+6]);side+=1
 gates=0
 for mode in ['small','big','scripted','queue','slots','protected']:
  m=fresh();at=probe(m);cell=0xc1 if mode!='protected'else 0x6d;m[at]=cell;m[address(b,'R3')]=cell
  if mode in ['small','big']:M.put(m,PlayerStatus=0 if mode=='small'else 1)
  if mode=='scripted':M.put(m,GameEngineSubroutine=7)
  if mode=='queue':M.put(m,VRAM_Buffer_AddrCtrl=6)
  if mode=='slots':
   for slot in [0,1]:m[address(b,'Block_State')+slot]=0x11
  prior=player(m);c=call(m,'MtTerrainDestroyCell',a=cell)
  assert not c['P']&1 and c['A']==cell and m[at]==cell and not m.ram[2][BUDGET]and player(m)==prior;gates+=1
 head=0
 for area,px,py,coin in itertools.product([0,1],[96,248],[80,83,84,87],[False,True]):
  m=fresh(AreaType=area,Player_X_Position=px,Player_Y_Position=py);at=probe(m,0,True);row=M.get(m,'R2');world=M.get(m,'R5');xp=int(world<px)
  m[at]=0xc1
  if coin:m[at-16]=0xc2
  prior=player(m);c=call(m,'MtTerrainHeadProbe',a=0x42,y=0)
  assert c['A']==0 and m[at]==0 and m.ram[2][BUDGET]==1 and player(m)==prior
  assert M.get(m,'Block_X_Position')==world&0xf0 and M.get(m,'Block_PageLoc')==xp and M.get(m,'Block_Y_Position')==(row+32)&255
  assert M.get(m,'Block_RepFlag')==1 and M.get(m,'BlockBounceTimer')==16 and not M.get(m,'Enemy_Flag',5)
  if coin:assert m[at-16]==0 and M.get(m,'CoinTallyFor1Ups')==1
  head+=1
 # Protected terrain/coins retain donor native interactions; it cannot be
 # silently fed through the ordinary question/item dispatch when queue busy.
 protected_head=0
 for cell in [0x26,0x6d,0x67,0x68,0xc5,0x1c,0x1f,0x6b,0x6c,0xc2,0xc3]:
  m=fresh(Player_Y_Position=83);at=probe(m,0,True);m[at]=cell
  c=call(m,'MtTerrainHeadProbe',y=0);assert m[at]==cell and not m.ram[2][BUDGET]
  if cell in [0xc2,0xc3]:assert c['A']==cell
  else:assert c['A']==0 and M.get(m,'Player_Y_Speed')==1 and M.get(m,'Square1SoundQueue')==(0 if cell==0x26 else 2)
  protected_head+=1
 # Full foreign outputs and native memory are compared against the exact old
 # dispatch, not only an invented prediction of A or geometry.
 foreign=0
 def result(m,c):
  skip=set(range(0x100,0x200))|set(range(0x2000,0x5c00))|{address(b,n)for n in ['CurrentBank','CurrentBankC','safecall_a']}
  return tuple(c[n]for n in ['A','X','Y','P']),bytes(v for i,v in enumerate(m[:0x8000])if i not in skip),[bytes(q)for q in m.ram]
 for selected,variant,p,kind in itertools.product(range(16),range(7),[0x30,0x71],['head','side']):
  # Native-only ready contexts here. Other actors require their authentic
  # cache constructions, which are a later owning-ROM qualification gate.
  if selected not in [0,1,2,3,5,6,7,8,9,10]or(selected==0 and variant==7):continue
  left=fresh(SelectedCharacter=selected,MarioVariant=variant,PlayerStatus=0);right=M.fork(left)
  probe(left,3);probe(right,3)
  x=call(left,'MtTerrainHeadProbe'if kind=='head'else'MtTerrainSideProbe',y=3,p=p)
  y=call(right,'MaaHead'if kind=='head'else'MmNativeSideShortcut',y=3,p=p)
  assert result(left,x)==result(right,y),(selected,variant,p,kind,result(left,x)[0],result(right,y)[0]);foreign+=1
 q=dict(passed=True,base_ROM_sha256=PIN,component_bytes=len(code),terrain_bytes=labels['MtTerrainEnd']-labels['MtTerrainStart'],preloaded_RAM2_fixture=True,actual_A2_farcall_transport=True,owning_link=False,native_run=False,installed=False,code_lease_granted=False,RAM_lease_granted=False,
  authentic256cell_classification_cases=tile,native_world_cell_side_effect_cases=side,one_cell_budget_cases=side,inactive_pressure_protected_cases=gates,native_head_effect_cases=head,native_head_protected_coin_cases=protected_head,foreign_complete_native_output_cases=foreign,measured=measured,
  scope='Actual frozen native queries, RemoveCoin_Axe/DestroyBlockMetatile, CheckTopOfBlock, SpawnBrickChunks, AddToScore and sound owners. Actual FarCallCommon rawbank2 maps the preloaded worker atA2B600 and restores the old A-window; context is A2A880..A88B. C-window ROM is retained. Preloading is a CPU fixture, not an authenticated loader, global gate, Main/ISR qualification or menu admission. No player geometry proxy.',
  adaptations=['Host has two debris slots rather than donor four. Existing GuestClaimBlockSlot protects bouncing question/item slots and may recycle earlier harmless debris.','Busy native VRAM selector defers mutation. Upward Tank is held instead of allowing ordinary head item release; side retains normal collision until resource available.','Twelve conditional bytes are proposed only for this fixture; complete ownership/header/scene retirement and loaded code resources remain ungranted.'],bindings={str(TERRAIN.relative_to(R)):sha(TERRAIN.read_bytes()),str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes()),'host.bin':sha(code)})
 (O/'terrain-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k.endswith('cases')or k in ['passed','component_bytes','terrain_bytes','measured']}))

if __name__=='__main__':main()
