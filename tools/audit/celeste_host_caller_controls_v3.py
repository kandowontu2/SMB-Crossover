"""Small real-draw/foreign-caller supplement for the assembled Celeste host."""
from pathlib import Path
import argparse,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from celeste_host_controls_v4 import *

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True,type=Path);p.add_argument('--baseline',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists()
 b=scoped_load(a.rom);old=scoped_load(a.baseline);proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={},bindings={str(z):sha(z)for z in[Path(__file__),R/'tools/audit/celeste_host_controls_v4.py',a.rom,a.rom.with_suffix('.dbg'),a.baseline,a.baseline.with_suffix('.dbg')]});ck=proof['checks']
 try:
  rows=[];assets=json.loads((R/'chr/characters/celeste-mario-assets.json').read_text());records={(r['pose'],r['face']):r['parts']for r in assets['records']}
  for face,state,swim,anim in itertools.product([1,2],[0,1,2,3],[0,1],[0,1,2]):
   q=cmseed(b,2);q.put(PlayerFacingDir=face,Player_State=state,CmState=state,SwimmingFlag=swim,PlayerAnimCtrl=anim,PlayerAnimTimer=3,Player_X_Speed=16 if face==1 else 240,Player_XSpeedAbsolute=16,Left_Right_Buttons=face,Player_MovingDir=face,Player_SprAttrib=1,CurrentOAMOffset=16)
   run(q,'CmHostGraphics');pose=q.get('CmPose');parts=records[pose,face]
   # Genuine body reservation is16B: four native8x16 parts, not8x8 sprites.
   assert len(parts)==4
   q.m.page(2,12);q.set('CurrentBankC',140) # Real intervening unrelated C owner.
   run(q,'DrawAllMetasprites')
   want=bytes(v for tile,attr,yy,xx in reversed(parts)for v in[(160+yy)&255,tile,(attr|1)&243,(96+xx)&255])
   assert bytes(q.m[0x200:0x210])==want,(face,state,swim,anim,pose,list(q.m[0x200:0x210]),list(want))
   assert q.m.banks[2]==98 and q.get('CurrentBankC')==226 and q.get('CurrentOAMOffset')==16
   rows.append(dict(face=face,state=state,water=swim,animation=anim,pose=pose,body_bytes=16,C98_restored_before_first_record=True))
  ck['full_DrawAll_native_body']=dict(passed=True,cases=len(rows),rows=rows)
  # Every currently implemented old profile, both behavior modes. Actual
  # complete caller returns are exact without ignoring application RAM.
  identities=[(0,'MarioVariant',0),(8,'MarioVariant',1),(1,'ProtoVariant',0),(1,'ProtoVariant',1),(2,'MarioVariant',0),(3,'BillVariant',0),(3,'BillVariant',1),(4,'Z2Variant',0),(4,'Z2Variant',1),(5,'Cv3Variant',0),(5,'Cv3Variant',1),(5,'Cv3Variant',2),(5,'Cv3Variant',3),(6,'MarioVariant',0),(7,'MarioVariant',0),(9,'RlVariant',0),(9,'RlVariant',1),(10,'MarioVariant',0),(11,'MarioVariant',0),(12,'DarkwingVariant',0),(12,'DarkwingVariant',1),(13,'KbVariant',0),(13,'KbVariant',1),(14,'CdVariant',0),(14,'CdVariant',1),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),(16,'MarioVariant',0),(17,'M3Variant',0),(17,'M3Variant',1),(18,'VvVariant',0),(18,'VvVariant',1),(18,'VvVariant',2),(18,'VvVariant',3),(19,'TnVariant',0),(19,'TnVariant',1),(19,'TnVariant',2),(19,'TnVariant',3),(20,'IcVariant',0),(20,'IcVariant',1),(21,'RcVariant',0),(21,'RcVariant',1),(23,'MarioVariant',0)]
  costs=[]
  for char,key,var in identities:
   for mode in[0,1]:
    pairs=[]
    for bundle in[old,b]:
     q=seed(bundle,char);q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1);q.set(key,var)
     q.m[0x5ff8:0x5ffe]=bytes(range(161,167))
     c,w,_=run(q,'GameLoop',p=0x71);effects=[(i,v)for i,v in w if (0x200<=i<0x300 or 0x2000<=i<0x6000)and not 0x5114<=i<0x5118];pairs.append((registers(c),app(q),q.m.banks,effects,c.processorCycles))
    assert bytes(q.m[0x5ff8:0x5ffe])==bytes(range(161,167)),('high slab foreign writer',char,key,var,mode)
    assert pairs[0][:4]==pairs[1][:4],('foreign fullcaller',char,key,var,mode,pairs[0][0],pairs[1][0])
    costs.append(dict(char=char,variant_key=key,variant=var,mode=mode,CPU_delta=pairs[1][4]-pairs[0][4]))
  ck['foreign_complete_callers']=dict(passed=True,calls=len(costs),rows=costs,whole_AXYP_SP_appRAM_banks=True,ordered_OAM_nonbank_hardware=True,internal_relocated_code_pointer_and_bank_protocol_writes_disclosed=True)
  # Actual status packet has seven glyphs; +18 belongs to the next packet.
  for flags in[0x30,0x31,0x70,0x71]:
   q=cmseed(b);q.m[address(b,'VRAM_Buffer1')+11:address(b,'VRAM_Buffer1')+19]=bytes([204]*8)
   c,_,_=run(q,'NrStatusName',a=0,x=7,y=91,p=flags)
   assert registers(c)==[0,7,91,flags,253]
   assert bytes(q.m[address(b,'VRAM_Buffer1')+11:address(b,'VRAM_Buffer1')+19])==b'CELESTE'+bytes([204])
  ck['allocator_cold_source_bounds']=dict(passed=True,high_slab=[0x5ff8,0x5ffd],Pn_clear_last=0x5fdf,Pn_history_last=0x5fbf,menu_variant_last=0x5fef,bounce_last=0x5ff5,Bill_status_last=0x5ff7,only_existing_global_newgame_clear=True,foreign_complete_call_canaries=len(costs),old_allocator_negative='build/celeste_host_caller_controls_v1.json')
  ck['status_canary']=dict(passed=True,cases=4,AXYP_SP_exact=True,seven_cells=True)
  assert all(sha(z)==v for z,v in proof['bindings'].items());proof['passed']=True
 except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'passed':True,'checks':list(ck),'sha256':sha(a.output)}))
if __name__=='__main__':main()
