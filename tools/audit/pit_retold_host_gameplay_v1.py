"""Supplement real Pit menu/lives/Main+NMI and world ownership, no native."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import pit_retold_host_controls_v1 as H
from sunny_integrated_controls_v1 import *
P=H.P;O=H.O

def gameplay_main(q):
 # HpPrepareNativePointers snapshots SmPosePtr for native object0; the real
 # DrawMetasprite consumer must then select that exact immutable C31 record.
 # These four pointer bytes are graphics metadata, not unproved dead RAM.
 b=q.b;original=NesMPU.step;pending=None;seen=[]
 def step(c):
  nonlocal pending
  bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
  if c.pc==address(b,'HpNativePointerBegin')and bank==4 and c.y==0:
   native=q.get('HpNativeDrawLo')+256*q.get('HpNativeDrawHi')
   assert native==q.get('SmPosePtr')+256*q.get('SmPosePtr',1),('actual native body snapshot',hex(native))
   pending=native
  if c.pc==address(b,'MetaspriteRenderLoop')and bank==4 and pending is not None:
   ptr=q.get('R0')+256*q.get('R1')
   assert ptr==pending and q.m.banks[2]==31,('native real pointer consumer',hex(ptr),hex(pending),q.m.banks)
   seen.append(ptr);pending=None
  original(c)
 NesMPU.step=step
 try:out=H.C.M.runtrace(q,'GameLoop',p=0x71)
 finally:NesMPU.step=original
 assert pending is None
 return(*out,seen)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 old,b=[scoped_load(x/'candidate.nes')for x in[P,O]]
 proof=dict(passed=False,native_run=False,source_CPU_only=True,checks={});ck=proof['checks']
 try:
  rows=[]
  for mode,status,keys in itertools.product(range(2),range(3),[0,4,65,129]):
   pair=[]
   for v in[old,b]:
    q=H.C.setup(v,6);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=status,SavedJoypadBits=keys)
    q.m[0x5fe0]=0;c,tr,mn=H.C.M.runtrace(q,'GameLoop',p=0x71)
    pair.append((registers(c),H.C.M.fastapp(q),bytes(q.m[0x100:0x200]),tuple(q.m.banks),list(q.m.writes),c.processorCycles,mn))
   assert pair[0][:5]==pair[1][:5],('normal Pit whole Main',mode,status,keys)
   rows.append([mode,status,keys,pair[1][-2]-pair[0][-2],pair[1][-1]])
  ck['normal_Pit_complete_Main']=dict(cases=len(rows),rows=rows,all_live_and_entire_stack_application_OAM_CHR_5SMC_ordered_writes_exact=True)
  # Existing menu's genuine Select edge, existing queued palette/name/cursor,
  # and actual preview consumer; release each complete packet through normal NMI.
  q=H.C.setup(b,6);q.put(CrossoverMenuState=2,CrossoverMenuIndex=6,CrossoverMenuButtons=0,SavedJoypad2Bits=0)
  q.m[0x5fe0]=0;rows=[]
  for held,wanted in[(4,1),(0,1),(4,0),(0,0),(4,1)]:
   q.put(SavedJoypad1Bits=held);c,tr,mn=H.C.M.runtrace(q,'CrossoverMenuInput')
   assert q.m[0x5fe0]==wanted and q.get('SelectedCharacter')==6 and q.get('CrossoverMenuIndex')==6
   assert q.get('VRAM_Buffer1_Offset')<=84
   if held:
    assert q.get('SmChrBank')==(40 if wanted else 213)
    assert q.get('X5ChrMode')==(0x83 if wanted else 0)
   rows.append([held,wanted,q.get('SmChrBank'),q.get('X5ChrMode'),q.get('VRAM_Buffer1_Offset'),mn])
   # The outer Main owns this release; direct-component CPU arena marks the
   # same completed-publication boundary, never a native/PPU assertion.
   q.put(NmiDisable=0);H.T.nmi(q,c);q.put(NmiDisable=255)
  ck['actual_menu_Select_release_preview']=dict(rows=rows,real_CrossoverMenuInput_and_normalNMI=True,original0_to_GB1_to_original0=True,no_buffer_growth_without_consumer=True)
  rows=[]
  for variant,mode,status in itertools.product(range(2),range(2),range(3)):
   q=H.C.setup(b,6);q.m[0x5fe0]=variant;q.put(CrossoverBehaviorVersion=mode,PlayerStatus=status)
   c,tr,mn=H.C.M.runtrace(q,'DrawPlayer_Intermediate')
   assert q.get('SmChrBank')==(40 if variant else 213)
   assert q.get('ObjectMetasprite')==address(b,'METASPRITE_SAMUS_BODY')
   assert q.get('SmPosePtr')+256*q.get('SmPosePtr',1)==address(b,'XgPIT0_STANDRight')
   rows.append([variant,mode,status,mn,c.processorCycles])
  ck['genuine_lives_portrait_caller']=dict(rows=rows,all_modes_tiers_and_variants=True)
  visual=set(range(0x200,0x300))
  for n,size in[('SmChrBank',1),('PlayerChrBank',1),('CurrentCHRBank',1),('X5ChrMode',1),('X5WideChrActive',1),('ReloadCHRBank',1),('SmPosePtr',2),('R0',2),('HpNativeDrawLo',1),('HpNativeDrawHi',1)]:visual.update(range(address(b,n),address(b,n)+size))
  # No broad application mask: every non-graphics byte must remain identical.
  compare=[i for i in list(range(0x100))+list(range(0x200,0x2000))+list(range(0x5c00,0x8000))if i not in visual]
  rows=[];deadstack=[];pointer_rows=[]
  for mode in range(2):
   qa,qb=[H.C.setup(v,6)for v in[old,b]]
   for q in[qa,qb]:q.put(CrossoverBehaviorVersion=mode,PlayerStatus=2);q.m[0x5fe0]=1
   latches=[[None]*12,[None]*12]
   for age in range(96):
    keys=(1 if age<40 else 0)|(128 if 4<=age<12 else 0)|(64 if 48<=age<54 or 70<=age<74 else 0)|(4 if 56<=age<64 else 0)
    pair=[]
    for q in[qa,qb]:
     q.put(SavedJoypadBits=keys,NmiDisable=255)
     c,tr,mn,body=gameplay_main(q)
     pair.append((c,tr,mn,c.processorCycles,body))
    ca,cb=pair[0][0],pair[1][0]
    assert registers(ca)==registers(cb)and qa.m.banks==qb.m.banks,('owned full Main registers/banks',mode,age,registers(ca),registers(cb))
    dif=[(i,qa.m[i],qb.m[i])for i in compare if qa.m[i]!=qb.m[i]]
    assert not dif,('nonvisual Main state changed',mode,age,dif[:16])
    if any(qa.get(n)!=qb.get(n)for n in['R0','R1','HpNativeDrawLo','HpNativeDrawHi']):
     for q in[qa,qb]:
      native=q.get('HpNativeDrawLo')+256*q.get('HpNativeDrawHi')
      assert native==q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
     # Later native work may overwrite R0 alone (e.g. bank126:86FF/870F).
     # Only a byte that actually differs must retain its corresponding exact
     # body-pointer byte; the unchanged byte is still compared normally.
     for n,pointer in[('R0','HpNativeDrawLo'),('R1','HpNativeDrawHi')]:
      if qa.get(n)!=qb.get(n):
       assert all(q.get(n)==q.get(pointer)for q in[qa,qb]),('retained final pointer byte',mode,age,n)
    assert len(pair[0][-1])==len(pair[1][-1])
    pointer_rows.append([mode,age,pair[0][-1],pair[1][-1]])
    assert bytes(qa.m[0x1fe:0x200])==bytes(qb.m[0x1fe:0x200])
    changed=[i for i in range(0x100,0x1fe)if qa.m[i]!=qb.m[i]]
    if changed:deadstack.append([mode,age,min(changed),max(changed),len(changed)])
    nis=[];witness=[]
    for which,(q,c)in enumerate([(qa,ca),(qb,cb)]):
     q.m.writes=[];nis.append(H.T.nmi(q,c));witness.append([(a,v)for a,v in q.m.writes if 0x5121<=a<=0x512b])
     upper=q.m[0x5130]&3
     for at,value in q.m.writes:
      if at==0x5130:upper=value&3
      elif 0x5120<=at<=0x512b:latches[which][at-0x5120]=upper*256+value
    # A cache hit can omit redundant writes. Compare actual10-bit MMC5
    # latches, including each write's real5130 upper bits, never just lows.
    assert None not in latches[0]+latches[1]
    assert latches[0][1:]==latches[1][1:],('native world/effect effective CHR changed',mode,age,latches)
    assert latches[1][0]==768+qb.get('SmChrBank'),('body physical CHR publication',mode,age,latches[1])
    assert not [(i,qa.m[i],qb.m[i])for i in compare if qa.m[i]!=qb.m[i]],('nonvisual normalNMI state changed',mode,age)
    rows.append([mode,age,keys,pair[0][3],pair[1][3],pair[1][3]-pair[0][3],*nis,qb.get('SmChrBank'),qb.get('ReloadCHRBank')])
  ck['actual_Main_normalNMI_gameplay_preservation']=dict(updates=len(rows),rows=rows,all_nonvisual_application_bytes_registers_banks_exact=True,normalNMI_native_world_effect10bit_latches_exact=True,actual_5130_order_per_write_accounted=True,declared_graphics_addresses=sorted(visual-set(range(0x200,0x300))),consumed_return_stack_differences=deadstack,live_return_bytes_1FE_1FF_exact=True,stack_note='Alternate pushes its P/Y to preserve full caller ABI; consumed cells below returned SP are recorded rather than claimed whole-stack-equal. IRQ controls separately prove all live interrupted frames exact.',first_oracle_negative='Exact ordered publish-write presence was too strong: true cache hit omits redundant writes; first failure retained. Final hardware10bit latches and all other shadow fields must still match.')
  ck['native_body_pointer_metadata']=dict(rows=pointer_rows,actual_DrawMetasprite_to_renderer_consumers=sum(len(r[3])for r in pointer_rows),source='HpPrepareNativePointers stores actual SmPosePtr at HpNativeDrawLo[0]/Hi[0]; DrawMetasprite native Y0 selects it. Each final R0/R1 byte that differs independently equals its corresponding consumed body-pointer byte; later native R0-only work remains equal. Other six native actor pointer slots remain in exact application comparison.',negative='controls-gameplay.json preserved the overstrict art-pointer equality failure; controls-gameplay-final.json preserved the overly strong whole-final-pointer oracle (native later work overwrites R0 alone at bank126:86FF/870F). No gameplay or source change made.')
  rows=[]
  for mode,scene,star in itertools.product(range(2),range(4),[0,32]):
   pair=[]
   for v in[old,b]:
    q=H.C.setup(v,6);q.m[0x5fe0]=1;q.put(CrossoverBehaviorVersion=mode,AreaType=scene,StarInvincibleTimer=star)
    c,tr,mn=H.C.M.runtrace(q,'GetPlayerColors');pair.append((registers(c),H.C.M.fastapp(q),tuple(q.m.banks),list(q.m.writes),c.processorCycles))
   assert pair[0]==pair[1],('palette/backdrop changed',mode,scene,star)
   rows.append([mode,scene,star])
  ck['actual_palette_backdrop_callers']=dict(cases=len(rows),rows=rows,all_native_palette_commands_and_ABI_CPU_exact=True)
  proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 files=[Path(__file__),Path(H.__file__),R/'tools/prepare_pit_retold_host_v1.py',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'candidate.nes',P/'candidate.dbg']
 proof['bindings']={str(p.resolve()):sha(p)for p in files};a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']
if __name__=='__main__':main()
