"""Finite d232 pole/exit successor controls; actual CPU Main/NMI, no native/PPU timing."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import dragon_power_gameplay_controls_v1 as C
from sunny_integrated_controls_v1 import *
P=R/'build/dragon-power-platform-v1';O=R/'build/dragon-power-flagpole-v3'

def nmi(q,c):
 start=c.processorCycles;c.nmi()
 for _ in range(90000):
  c.step()
  if c.pc==0x5b00 and c.sp==253:return c.processorCycles-start
 raise AssertionError(('NMI timeout',hex(c.pc),q.m.banks))

def tick(q,keys,normal=True):
 q.put(SavedJoypadBits=keys)
 c,tr,mn=C.M.runtrace(q,'GameLoop')
 cycles=c.processorCycles
 if normal:ni=nmi(q,c)
 else:ni=0
 return c,tr,mn,cycles,ni

def resource(q):
 return {n:q.get(n)for n in['DpHP','DpPole','DpWaves','DpPower','DpHunger','DpReady','DpLife','NumberofLives','PlayerStatus','DpArea','DpWorld']}

def relocation_writes(old,new,wa,wb):
 """Keep all ordered writes; permit only authenticated code-address relocation."""
 assert len(wa)==len(wb)
 targets={(address(old,n),address(new,n)):n for n in old['syms']if n.startswith('Dp')and n in new['syms']and address(old,n)!=address(new,n)}
 lo=address(old,'FarcallJmpTarget_SMC')+1;rows=[]
 def code(bundle,pc):return bytes(bundle['raw'][16+86*8192+pc-0xa000:16+86*8192+pc-0xa000+3])
 for i,(a,z)in enumerate(zip(wa,wb)):
  if a==z:continue
  assert a[0]==z[0],('write address changed',i,a,z)
  at=a[0]
  if at in[lo,lo+1]:
   j=i if at==lo else i-1
   assert wa[j][0]==wb[j][0]==lo and wa[j+1][0]==wb[j+1][0]==lo+1
   pair=(wa[j][1]+256*wa[j+1][1],wb[j][1]+256*wb[j+1][1])
   assert pair in targets,('unexplained SMC target relocation',i,pair)
   rows.append([i,'genuine linked target',targets[pair],*pair]);continue
  assert 0x100<=at<0x200,('non-code-address ordered write changed',i,a,z)
  # Genuine6502 JSR pushes high then low. Validate the actual return's JSR
  # preimage and its real unchanged or genuinely relocated operand.
  j=i if i and wa[i-1][0]==wb[i-1][0]==at+1 else i+1
  assert wa[j-1][0]==wb[j-1][0]==wa[j][0]+1==wb[j][0]+1
  pa=wa[j][1]+256*wa[j-1][1]-2;pb=wb[j][1]+256*wb[j-1][1]-2
  ca,cb=code(old,pa),code(new,pb)
  assert len(ca)==len(cb)==3 and ca[0]==cb[0]==0x20,('not actual JSR return',i,pa,pb,ca,cb)
  ta,tb=int.from_bytes(ca[1:],'little'),int.from_bytes(cb[1:],'little')
  assert ta==tb or(ta,tb)in targets,('JSR target changed',i,ta,tb)
  matching=[n for n in old['syms']if n.startswith('Dp')and n in new['syms']and 0<=pa-address(old,n)<128 and pb-address(new,n)==pa-address(old,n)]
  assert matching,('return not same relative owned continuation',i,pa,pb)
  rows.append([i,'actual JSR saved return',matching[0],pa,pb])
 return rows

def earn(q,oneup=False):
 rows=[]
 for kind in([0,1,3]if oneup else[0,1]):
  C.actor(q,0,0x2e,96,176);q.set('Enemy_State',128,0);q.set('PowerUpType',kind,0)
  seen=set()
  for age in range(65):
   c,tr,mn,cy,ni=tick(q,0);seen.update(tr)
  assert q.get('Enemy_Flag',0)==0
  assert ((location(q.b,'EraseEnemyObject')-16)//8192,address(q.b,'EraseEnemyObject'))in seen
  rows.append(dict(type=kind,after=resource(q)))
 assert q.get('DpPole')==1 and q.get('DpWaves')==3 and q.get('DpPower')==2
 if oneup:assert q.get('NumberofLives')==3 and q.get('DpLife')==3
 return rows

def pole_arena(b,mode=0,earned=False):
 q=C.setup(b);q.put(CrossoverBehaviorVersion=mode,AreaPointer=37,WorldNumber=0,Hidden1UpFlag=1)
 pickups=earn(q,True)if earned else[]
 run(q,'GetAreaDataAddrs')
 for j in range(3):q.set('AreaObjectLength',255,j)
 cols=[]
 for _ in range(220):
  run(q,'AreaParserCore');cols.append([q.get('MetatileBuffer',y)for y in range(13)]);run(q,'IncrementColumnPos')
 assert cols[198][:10]==[0x24]+[0x25]*9 and cols[198][10]==0x61
 assert q.get('Enemy_ID',5)==0x30 and q.get('Enemy_ID',4)==0x31
 for x,col in enumerate(cols):
  for y,t in enumerate(col):q.m[address(b,'Block_Buffer_1')+((x//16)%2)*208+y*16+x%16]=t
 q.put(Player_PageLoc=12,Player_X_Position=64,Player_Y_Position=176,Player_Rel_XPos=96,
       ScreenLeft_PageLoc=11,ScreenLeft_X_Pos=224,ScreenRight_PageLoc=12,ScreenRight_X_Pos=223,Player_Pos_ForScroll=96)
 return q,pickups

def route(b,mode,earned=False,cap=1500):
 q,pickups=pole_arena(b,mode,earned);start=resource(q);prior=None;rows=[];seen=set();controlled=0;costs=[];nis=[];minsp=255
 for age in range(cap):
  c,tr,mn,cy,ni=tick(q,1|(128 if 2<=age%70<12 else 0));minsp=min(minsp,mn);seen.update(tr);costs.append(cy);nis.append(ni)
  key=tuple(q.get(n)for n in['OperMode_Task','GameEngineSubroutine','AreaType','AreaAddrsLOffset','LevelNumber'])
  if key!=prior:
   rows.append(dict(update=age,mode_task_engine_area_offset_level=key,x=q.get('Player_PageLoc')*256+q.get('Player_X_Position'),y=q.get('Player_Y_Position'),resources=resource(q)));prior=key
  if q.get('GameEngineSubroutine')==8:
   assert q.get('DpX')==(q.get('Player_X_Position')-q.get('ScreenLeft_X_Pos'))&255
   assert q.get('DpY')==(q.get('Player_Y_Position')+16)&255
  if q.get('LevelNumber')==1 and q.get('AreaType')==2 and q.get('GameEngineSubroutine')==8:controlled+=1
  if controlled>=25:break
 return q,dict(mode=mode,earned=earned,pickups=pickups,start=start,transitions=rows,updates=age+1,
   controlled_underground_updates=controlled,final=resource(q),Main_CPU=[min(costs),max(costs)],normal_NMI_CPU=[min(nis),max(nis)],min_SP=minsp,
   reached={n:((location(b,n)-16)//8192,address(b,n))in seen for n in['HandleClimbing','FlagpoleSlide','PlayerEndLevel','InitializeArea','EnterSidePipe']})

def irq_case(b,tile,kind):
 q=C.setup(b);q.put(NmiDisable=255);at=address(b,'Block_Buffer_1')+0x96;q.m[at]=tile
 original=NesMPU.step;seen=set();minimum=255
 start=address(b,'DpHostTileRead');end=address(b,'DpHostTileRead::Empty')+3
 def step(c):
  nonlocal minimum
  minimum=min(minimum,c.sp);bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
  key=(bank,c.pc)
  if bank==86 and start<=c.pc<end and key not in seen:
   seen.add(key)
   def snap():return(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[i]for i in smc_at(b)),bytes(q.m[:8]),bytes(q.m[0x101+c.sp:0x200]),bytes(q.m[0x5c00:0x6000]))
   before=snap()
   if kind=='IRQ':assert not c.p&4;q.m[0x5204]=128;c.irq()
   else:c.nmi()
   for _ in range(60000):
    original(c);minimum=min(minimum,c.sp)
    if c.pc==before[0]and c.sp==before[5]:break
   else:raise AssertionError(('ISR timeout',kind,key))
   assert snap()==before,('ISR live source/caller lease',kind,key)
  original(c)
 NesMPU.step=step
 try:run(q,'DpHostTileQuery',a=176,x=89,y=96,p=0x30)
 finally:NesMPU.step=original
 return len(seen),minimum

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 old,b=[scoped_load(p/'candidate.nes')for p in[P,O]];p=dict(passed=False,source_CPU_only=True,native_run=False,checks={});ck=p['checks']
 try:
  rows=[];code_writes=[];foreign_cost=[]
  flags=[f for f in range(256)if f&0x30==0x30]
  cases=[(t,f)for t in range(256)for f in[0x30,0x71]]+[(t,f)for t in[0,0x23,0x24,0x25,0x51,0xc0]for f in flags]
  for tile,fl in cases:
   pair=[]
   for v in[old,b]:
    q=C.setup(v);q.m[address(v,'Block_Buffer_1')+0x96]=tile
    c,_,_=run(q,'DpHostTileQuery',a=176,x=89,y=96,p=fl)
    pair.append((registers(c),bytes(q.m[:0x8000]),c.processorCycles))
   if tile in[0x24,0x25]:
    assert pair[0][0][0]==0x75 and pair[1][0][0]==0
    expected=pair[0][0][:];expected[0]=0;expected[3]=(expected[3]&~0x82)|2
    assert pair[1][0]==expected
    original=bytearray(pair[0][1]);original[address(old,'DpTileResult')]=0
    assert bytes(original)==pair[1][1]
   else:assert pair[0][:2]==pair[1][:2],('nonpole full query ABI/RAM',tile,fl)
   rows.append(pair[1][2]-pair[0][2])
  ck['actual_terrain_query']=dict(cases=len(cases),all256native_tiles=True,all64flags_selected_classes=True,only24_25_source_result_changes=True,full_AXYP_SP_32KB_RAM_including_stack_checked=True,CPU_delta=[min(rows),max(rows)])
  rows=[]
  for pose,face,attr in itertools.product(range(32),[0,64],[0,1,3,0x20,0x40,0x80,0xdf,0xff]):
   pair=[]
   for v in[old,b]:
    q=C.setup(v);run(q,'DpEnsure');q.put(DpPose=pose,DpAttribute=face,Player_SprAttrib=attr,Player_Rel_XPos=96,Player_Y_Position=100,CurrentOAMOffset=0,RgOamRotation=0)
    c,_,_=run(q,'DpDrawBody');pair.append((q,registers(c),bytes(q.m[0x200:0x300]),c.processorCycles))
   expected=bytearray(pair[0][2]);count=pair[0][0].get('CurrentOAMOffset')
   for i in range(2,count,4):expected[i]|=attr&32
   assert pair[1][2]==bytes(expected),('source body geometry/HV/P0/priority',pose,face,attr)
   assert pair[1][0].get('Player_SprAttrib')==attr and pair[0][0].get('Player_SprAttrib')==0
   assert pair[0][1]==pair[1][1],('whole draw return ABI',pose,face,attr,pair[0][1],pair[1][1])
   assert pair[0][0].get('CurrentOAMOffset')==pair[1][0].get('CurrentOAMOffset')
   rows.append(pair[1][3]-pair[0][3])
  ck['source_body_all32poses_both_HV_native_priority_only']=dict(cases=len(rows),all_OAM_bytes_compared=True,source_opaque_shapes_tiles_HV_P0_exact=True,native_attribute_preserved_in_full=True,only_priority20_projected=True,AXYP_SP_exact=True,CPU_delta=[min(rows),max(rows)])
  rows=[]
  for ch,mode,keys in itertools.product([i for i in range(29)if i!=24],range(2),[0,129]):
   pair=[]
   for v in[old,b]:
    q=C.setup(v,ch);q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys)
    c,tr,mn=C.M.runtrace(q,'GameLoop',p=0x71)
    pair.append((registers(c),C.M.fastapp(q),bytes(q.m[0x100:0x200]),tuple(q.m.banks),bytes(q.m[z]for z in smc_at(v)),list(q.m.writes),c.processorCycles))
   assert pair[0][:5]==pair[1][:5],('foreign complete Main final state',ch,mode,keys)
   detail=relocation_writes(old,b,pair[0][5],pair[1][5])
   code_writes.append(dict(char=ch,mode=mode,keys=keys,transient_code_addresses=detail))
   foreign_cost.append(pair[1][6]-pair[0][6])
   rows.append([ch,mode,keys])
  ck['foreign_complete_Main']=dict(cases=len(rows),whole_final_AXYP_SP_entire_stack_application_OAM_CHR_banks_5SMC_exact=True,ordered_game_state_and_hardware_writes_exact=True,transient_actual_code_address_relocations=code_writes,CPU_delta=[min(foreign_cost),max(foreign_cost)],v1_raw_ordered_write_rejection_retained=True)
  rows=[]
  for mode,earned in itertools.product(range(2),[False,True]):
   q,record=route(b,mode,earned);assert record['controlled_underground_updates']==25,record
   assert all(record['reached'].values()),record['reached']
   assert record['final']['NumberofLives']==record['start']['NumberofLives']
   if earned:
    for n in['DpHP','DpPole','DpWaves','DpPower']:
     assert record['final'][n]==record['start'][n],('same-life scene resource changed',mode,n,record)
   rows.append(record)
  ck['actual_Main_normal_NMI_flag_surface_underground']=dict(cases=rows,no_direct_flag_exit_or_result_calls=True,real_native220_parser_columns_and_flag_actors=True,typed_scene_origin_and_optional_mature_pickup_staging=True,no_resource_health_life_equipment_outcome_seeds=True,no_NES_PPU_or_native_timing_claim=True)
  # Preserve the two independent intermediate product negatives.
  negatives=[]
  for folder,cap,earned,kind in [('dragon-power-platform-v1',150,False,'solid pole blocks thin grab'),('dragon-power-flagpole-v1',1100,False,'renderer erases native pipe-transition attribute'),('dragon-power-flagpole-v2',800,True,'area reset erases genuinely earned equipment')]:
   q,r=route(scoped_load(R/'build'/folder/'candidate.nes'),0,earned,cap)
   if kind.startswith('solid'):assert not r['reached']['HandleClimbing']and q.get('GameEngineSubroutine')==8
   elif kind.startswith('renderer'):assert q.get('LevelNumber')==1 and q.get('AreaType')==1 and q.get('GameEngineSubroutine')==7
   else:assert r['start']['DpPole']==1 and q.get('DpPole')==0 and q.get('NumberofLives')==r['start']['NumberofLives']
   negatives.append(dict(cause=kind,ROM=sha(R/'build'/folder/'candidate.nes'),observation=r))
  ck['retained_intermediate_product_negatives']=negatives
  rows=[]
  for tile,kind in itertools.product([0x24,0x25,0x51,0xc0],['IRQ','NMI']):rows.append([tile,kind,*irq_case(b,tile,kind)])
  ck['real_terrain_ISR_seams']=dict(rows=rows,reached=sum(r[2]for r in rows),min_SP=min(r[3]for r in rows),live_register_flags_stack_native_scratch_ExRAM_5SMC_banks_exact=True,NMI_is_actual_lag_branch=True)
  p['passed']=True
 except Exception as e:p.update(failure=repr(e),traceback=traceback.format_exc())
 files=[Path(__file__),Path(C.__file__),Path(C.M.__file__),R/'tools/audit/sunny_integrated_controls_v1.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'tools/audit/verify_native_relocation.py']
 for folder in[P,O,R/'build/dragon-power-flagpole-v1',R/'build/dragon-power-flagpole-v2']:
  files.extend(folder/n for n in['candidate.nes','candidate.dbg','candidate.lbl','build-proof.json'])
 p['bindings']={str(x.resolve()):sha(x)for x in files};a.output.write_text(json.dumps(p,indent=2)+'\n')
 print(json.dumps(dict(passed=p['passed'],failure=p.get('failure'),checks=list(ck),sha256=sha(a.output))))
 assert p['passed']

if __name__=='__main__':main()
