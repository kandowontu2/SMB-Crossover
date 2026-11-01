"""Private current-ROM menu→Start→parser/Main proof, no native emulator."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN,labels
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 base=scoped_load(P/'candidate.nes');assert sha(base['raw'])==PIN;receipt=json.loads((O/'candidate-patches.json').read_text());raw=(O/'candidate.nes').read_bytes();assert sha(raw)==receipt['private_candidate_sha256'];b=dict(base,raw=raw)
 new=labels(O/'visible.lbl');gate=labels(O/'graft.lbl');entries={}
 for n in ['MtHostMovement','MtHostContact','MtHostInjury','MtHostBeginPowerup','MtHostGrowthUpdate','MtTerrainHeadProbe','MtTerrainSideProbe','MtTerrainDestroyCell','MtArtPostV5']:entries[new[n],2]=n
 for n,bank in [('MtFreshV5',78),('MtColdLoadV4',31),('MtDrawAllV5',86),('MtReservationV5',66)]:entries[gate[n],128|bank]=n
 seen={};minimum=224;samples=[]
 def call(m,name,**regs):
  nonlocal minimum
  pc=address(b,name);m[address(b,'SafecallA_SMC')+1]=regs.get('a',85);m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
  c=NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=128|((location(b,name)-16)//8192);c.x=regs.get('x',0);c.y=regs.get('y',0);c.p=regs.get('p',0x31);c.sp=224;c.stPushWord(0x5aff);low=224;counts={}
  for _ in range(700000):
   if c.pc==0x5b00:break
   key=(c.pc,m.rawtags[(c.pc-0x8000)//8192])if c.pc>=0x8000 else None;n=entries.get(key)
   if n:counts[n]=counts.get(n,0)+1;seen[n]=seen.get(n,0)+1
   assert m[c.pc]!=0,('ActualMain BRK',name,hex(c.pc),m.rawtags);c.step();low=min(low,c.sp)
  else:raise AssertionError((name,'ActualMain bounded',hex(c.pc)))
  minimum=min(minimum,low);assert c.sp==224 and m.rawtags[2]==M.get(m,'CurrentBankC')
  return dict(A=c.a,X=c.x,Y=c.y,P=c.p,CPU=c.processorCycles,minimum_SP=low,counts=counts)
 m=M.fresh(b);M.put(m,CrossoverMenuIndex=0);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection');variants=[]
 for i in range(8):
  variants.append(M.get(m,'MarioVariant'))
  if M.get(m,'MarioVariant')==7:break
  M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);call(m,'CrossoverMenuInput')
 assert variants==[0,1,5,6,2,3,4,7],variants
 name=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+M.get(m,'VRAM_Buffer1_Offset')]);tank=bytes(36 if c==32 else c-55 for c in b' MARIO THE TANK ');assert tank in name,(name.hex(),tank.hex())
 M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0);start=call(m,'CrossoverMenuInput');assert M.get(m,'CrossoverMenuState')==0
 call(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P']);call(m,'PauseRoutine',a=0)
 for setup in range(600):
  if M.get(m,'OperMode_Task')==3 and M.get(m,'GameEngineSubroutine')==8:break
  M.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255);call(m,'GameLoop');M.consume(m)
 else:raise AssertionError('Native parser/entrance bounded')
 assert bytes(m.ram[2][0x1fe0:0x1ff0])==(O/'cookie.bin').read_bytes(),('Cold constructor not published',seen,bytes(m.ram[2][0x1fe0:0x1ff0]).hex(),{n:M.get(m,n)for n in['OperMode','DisableScreenFlag','Mirror_PPUMASK','FamilyMainCommit','MarioVariant']})
 assert m.ram[2][0x1600:0x1e00]==(O/'code501.bin').read_bytes()+(O/'art-code502.bin').read_bytes()
 frames=0
 for powered in [False,True]:
  if powered:M.put(m,PlayerStatus=2,PlayerSize=0)
  for age in range(30):
   keys=(1 if age<20 else 0)|(128 if 4<=age<8 else 0)|(64 if age==18 else 0)
   M.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
   c=call(m,'GameLoop');assert M.get(m,'MarioVariant')==7 and M.get(m,'SelectedCharacter')==0
   assert c['counts'].get('MtHostMovement')==1 and c['counts'].get('MtArtPostV5')==1,(powered,age,c)
   M.consume(m);frames+=1
  samples.append(dict(powered=powered,worldX=M.get(m,'Player_X_Position')+256*M.get(m,'Player_PageLoc'),playerY=M.get(m,'Player_Y_Position'),status=M.get(m,'PlayerStatus'),OAM=bytes(m[address(b,'Sprite_Data'):address(b,'Sprite_Data')+24]).hex()))
 q=dict(passed=True,current_ROM_sha256=sha(raw),base_ROM_sha256=PIN,menu_native_select_cycle=variants,proper_native_Tank_name=True,real_Start=True,actual_parser_entrance_updates=setup,cold_header_and_full_image_loaded=True,Main_updates=frames,minimum_actual_call_SP=minimum,owned_entry_counts=seen,samples=samples,owning_full_relink=False,Main_ISR_seams=False,native_Mesen=False,installed=False,resources_pending=True,bindings={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes())})
 (O/'candidate-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
