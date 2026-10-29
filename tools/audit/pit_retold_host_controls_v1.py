"""Actual private Pit callers/OAM/CHR/allocator controls; CPU-only, no Mesen."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import pit_retold_layout_plan_v2 as V
import dragon_power_gameplay_controls_v1 as C
import dragon_power_flagpole_controls_v2 as T
import dragon_power_gameplay_render_v3 as D
from sunny_integrated_controls_v1 import *
from PIL import Image,ImageDraw
P=R/'build/kamikaze-mario-host-v4';O=R/'build/pit-retold-host-v1'

def pose(q,index,face=1,outline=0,variant=1):
 q.put(PlayerStatus=index//84,RgPose=index%84,PlayerFacingDir=face,PlayerOutlinesOff=outline,
  Player_Rel_XPos=96,Player_Rel_YPos=100,Player_X_Position=96,Player_Y_Position=100)
 q.m[0x5fe0]=variant

def bitmap(q,event):
 out={p:[[0]*96 for _ in range(80)]for p in[0,2,3]}
 o=bytes(q.m[0x200:0x300]);page=768+q.get('SmChrBank')
 assert page in range(808,813),page
 for j in reversed(range(event['before'],event['after'],4)):
  off=(j+event['rotation'])&255;sy,t,a,sx=[o[(off+i)&255]for i in range(4)]
  raw=q.b['raw'][1048592+page*1024+(t&254)*16:1048592+page*1024+(t&254)*16+32]
  assert len(raw)==32 and t<64,(t,page)
  for yy in range(16):
   for xx in range(8):
    x=sx-96+32+xx;y=sy+1-100+32+yy
    px=7-xx if a&64 else xx;py=15-yy if a&128 else yy
    val=(raw[(py//8)*16+py%8]>>(7-px)&1)|((raw[(py//8)*16+8+py%8]>>(7-px)&1)<<1)
    if val and 0<=x<96 and 0<=y<80:out[a&3][y][x]=val
 return out

def expected(index,face):
 grid=V.G.layers(V.target(V.G.POSES[index%84]))
 if face!=1:grid={p:[[row[79-x]if 0<=79-x<96 else 0 for x in range(96)]for row in rows]for p,rows in grid.items()}
 # Native NES scanout starts at OAM Y+1; the existing host records store
 # their canvas coordinate directly. Preserve that old one-line convention.
 return{p:[[0]*96]+rows[:-1]for p,rows in grid.items()}

def isr(q,name,kind):
 b=q.b;original=NesMPU.step;seen=set();events=[];minimum=255
 def step(c):
  nonlocal minimum
  minimum=min(minimum,c.sp);bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
  own=(bank==31 and 0xdde6<=c.pc<address(b,'GbPitRenderEnd'))or(bank==66 and 0xb600<=c.pc<address(b,'GbPitMenuEnd'))
  if own and(bank,c.pc)not in seen:
   seen.add((bank,c.pc))
   def state():
    return(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[:8]),bytes(q.m[z]for z in smc_at(b)),bytes(q.m[0x101+c.sp:0x200]),bytes(q.m[0x5c00:0x6000]),bytes(q.m[address(b,'CurrentCHRBank'):address(b,'CurrentCHRBank')+12]),bytes(q.m[address(b,'X5ChrMode'):address(b,'X5ChrMode')+15]),q.get('ReloadCHRBank'))
   before=state()
   if kind=='IRQ':assert not c.p&4;q.m[0x5204]=128;c.irq()
   else:c.nmi()
   for _ in range(50000):
    original(c);minimum=min(minimum,c.sp)
    if c.pc==before[0]and c.sp==before[5]:break
   else:raise AssertionError(('ISR timeout',name,kind,hex(c.pc)))
   assert state()==before,('actual interrupted context',name,kind,bank,hex(c.pc),[i for i,(v,z)in enumerate(zip(before,state()))if v!=z])
   events.append([bank,c.pc])
  original(c)
 NesMPU.step=step
 try:C.M.runtrace(q,name,p=0x30)
 finally:NesMPU.step=original
 return events,minimum

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 old,b=[scoped_load(x/'candidate.nes')for x in[P,O]]
 V.V.PATCH,_=V.V.A.ips();V.G.ROLE='PIT';V.G.COLORS=V.G.targets('PIT')
 proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={});ck=proof['checks']
 try:
  # Exact compiled direct references, real source bounds and real lifecycle.
  hits=[];ops={0xad,0xbd,0xb9,0x8d,0x9d,0x99,0xae,0xbe,0x8e,0xac,0xbc,0x8c,0xce,0xee,0xcd,0xdd,0xd9,0x0d,0x1d,0x19,0x2d,0x3d,0x39}
  for bank in range(128):
   raw=old['raw'][16+bank*8192:16+(bank+1)*8192]
   for i in range(8190):
    if raw[i]in ops and raw[i+1:i+3]==b'\xe0\x5f':hits.append([bank,i,raw[i:i+3].hex()])
  assert hits==[[62,20,'9de05f'],[78,21,'bde05f'],[78,52,'9de05f']],hits
  q=seed(b,6)
  for i in range(16):q.m[0x5fe0+i]=(i*11+1)&255
  prior=bytes(q.m[0x5fe0:0x5ff0]);run(q,'X5InventoryInit');assert bytes(q.m[0x5fe0:0x5ff0])==prior
  q=seed(b,18);q.put(PnInitialized=0,VvVariant=1);q.m[0x5fe0]=1;c,w,_=run(q,'PnEnsure')
  assert q.m[0x5fe0]==1 and max(z for z,v in w if 0x5f00<=z<0x5fe0)==0x5fdf
  q=seed(b,6);q.m[0x5fe0]=1;run(q,'X5ColdInit');assert q.m[0x5fe0]==0
  ck['variant_allocation']=dict(parent_direct_absolute_consumers=hits,source_X5Clear_zero16_and_save_restore16=True,actual_InventoryInit_roundtrip16_exact=True,actual_PnEnsure_max_5FDF=True,cold_reset_zero=True,not_a_new_gameplay_state_byte=True)
  rows=[]
  for index,face,flags in itertools.product(range(252),[1,2],[0x30,0x31,0x70,0x71]):
   pair=[]
   for v in[old,b]:
    q=seed(v,6);pose(q,index,face,variant=0);c,tr,mn=C.M.runtrace(q,'ExpandedPose',p=flags)
    pair.append((registers(c),C.M.fastapp(q),bytes(q.m[0x100:0x200]),tuple(q.m.banks),list(q.m.writes),c.processorCycles))
   assert pair[0][:4]==pair[1][:4],('original Pit full pose state',index,face,flags,pair[0][0],pair[1][0])
   assert pair[0][4]==pair[1][4],('original Pit ordered writes',index,face,flags)
   rows.append(pair[1][-1]-pair[0][-1])
  ck['normal_Pit_all252_full_pose']=dict(cases=len(rows),AXYP_SP_entirestack_allapplication_5SMC_banks_ordered_writes_exact=True,CPU_delta=[min(rows),max(rows)])
  pictures=[];rows=[];costs=[]
  for mode,index,face,outline in itertools.product(range(2),range(252),[1,2],range(2)):
   q=seed(b,6);pose(q,index,face,outline);q.put(CrossoverBehaviorVersion=mode,NmiDisable=255)
   baseline=seed(old,6);pose(baseline,index,face,outline);baseline.put(CrossoverBehaviorVersion=mode)
   co,_,_=C.M.runtrace(baseline,'ExpandedPose',p=0x71)
   c,tr,mn=C.M.runtrace(q,'ExpandedPose',p=0x71)
   assert registers(c)==registers(co),('alternate actual pose ABI',mode,index,face,outline,registers(c),registers(co))
   ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1);assert q.m.banks[2]==31
   c,events,mi,tr=D.draw(q)
   body=[e for e in events if e['C']==31 and e['ptr']==ptr]
   assert len(body)==1 and body[0]['accepted'],('real full DrawAll body',mode,index,face,outline,len(body))
   actual=bitmap(q,body[0]);want=expected(index,face)
   assert actual==want,('exact original-pattern classes through actual OAM',mode,index,face,outline)
   assert all(q.get('X5ChrMode',j)==0 for j in range(1,12))
   assert q.get('X5ChrMode')==0x83 and q.get('SmChrBank')in range(40,45)
   costs.append(c.processorCycles);rows.append([mode,index,face,outline,body[0]['header'],mi])
   if mode==0 and index in[0,3,4,5,14,21,22,23,24,25,26,78]and outline==0:pictures.append((V.G.POSES[index],face,actual))
  ck['alternate_all_poses_real_DrawAll_pixels']=dict(cases=len(rows),all_modes_tiers_faces_outline_options=True,every_opaque_paletteclass_HV_pixel_exact=True,body_window0_only=True,maximum_parts=max(r[4]//4 for r in rows),minimum_SP=min(r[5]for r in rows),DrawAll_CPU=[min(costs),max(costs)])
  # Menu navigation and native packet canaries, preserving all old returns.
  rows=[]
  for ch,variant,pressed in itertools.product([0,1,6,15,20,21,23],[0,1],[0,1,2,4,8]):
   pair=[]
   for v in[old,b]:
    q=seed(v,ch);q.m[0x5fe0]=variant;q.put(CrossoverMenuIndex=6,CrossoverMenuPressed=pressed,VRAM_Buffer1_Offset=0)
    c,tr,mn=C.M.runtrace(q,'GbPitMenuNavigate'if v is b else'NrMenuNavigate',a=91,x=77,y=55,p=0x71)
    pair.append((q,c))
   if ch==6 and pressed&4:
    assert pair[1][0].m[0x5fe0]==variant^1 and pair[1][1].a==6
   else:
    qa,ca=pair[0];qb,cb=pair[1];assert registers(ca)==registers(cb),('foreign navigation ABI',ch,variant,pressed)
   rows.append([ch,variant,pressed])
  for ch,variant in itertools.product([0,1,6,15,20,21,23],range(2)):
   pair=[]
   for v in[old,b]:
    q=seed(v,ch);q.m[0x5fe0]=variant;q.put(VRAM_Buffer1_Offset=11)
    for i in range(84):q.set('VRAM_Buffer1',0xa5,i)
    c,tr,mn=C.M.runtrace(q,'QueueSelectName',a=91,x=77,y=55,p=0x71);pair.append((q,c))
   qa,ca=pair[0];qb,cb=pair[1];assert registers(ca)==registers(cb),('name full ABI',ch,variant,registers(ca),registers(cb))
   aa=bytes(qa.m[address(old,'VRAM_Buffer1'):address(old,'VRAM_Buffer1')+84]);bb=bytes(qb.m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84])
   if ch==6 and variant:
    assert aa[:14]==bb[:14]and aa[30:]==bb[30:]and aa[14:30]!=bb[14:30]
   else:assert aa==bb,('foreign name packet',ch,variant)
  ck['menu_Select_name_ABI_canaries']=dict(navigation_cases=len(rows),name_cases=14,only16_actual_name_cells_changed=True)
  rows=[]
  for ch,mode,keys in itertools.product([0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23],range(2),[0,129]):
   pair=[]
   for v in[old,b]:
    q=C.setup(v,ch);q.m[0x5fe0]=1;q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys)
    c,tr,mn=C.M.runtrace(q,'GameLoop',p=0x71)
    pair.append((registers(c),C.M.fastapp(q),bytes(q.m[0x100:0x200]),tuple(q.m.banks),list(q.m.writes),c.processorCycles))
   assert pair[0]==pair[1],('foreign complete Main',ch,mode,keys)
   rows.append([ch,mode,keys])
  ck['foreign_complete_Main']=dict(cases=len(rows),all_registers_entire_stack_application_OAM_CHR_5SMC_banks_CPU_ordered_writes_exact=True)
  # IRQ/lagNMI during real helper and partial CHR publication, not only leaves.
  rows=[]
  for name,index,kind in itertools.product(['ExpandedPose','GbPitMenuNavigate','QueueSelectName'],[0,3,5,24],['IRQ','NMI']):
   q=C.setup(b,6);pose(q,index);q.put(CrossoverMenuIndex=6,CrossoverMenuPressed=4,NmiDisable=255)
   events,mn=isr(q,name,kind);assert events;rows.append([name,index,kind,len(events),mn])
  ck['actual_helper_IRQ_lagNMI']=dict(cases=sum(r[3]for r in rows),rows=rows,minimum_SP=min(r[4]for r in rows),live_registers_stack_5SMC_physical_shadow_C_A_banks_and_CHR_partial_epoch_exact=True)
  # One bounded source-art sheet, not native screenshots or a frame forest.
  colors={0:[None,(82,33,0),(248,120,88),(252,252,252)],2:[None,(216,40,0),(255,255,255),(252,152,56)],3:[None,(0,0,0),(0,0,0),(0,0,0)]}
  sheet=Image.new('RGB',(600,len(pictures)//2*110+24),(44,54,68));dr=ImageDraw.Draw(sheet)
  for n,(label,face,grid)in enumerate(pictures):
   im=Image.new('RGBA',(96,80))
   for p in grid:
    for y in range(80):
     for x in range(96):
      v=grid[p][y][x]
      if v:im.putpixel((x,y),colors[p][v]+(255,))
   at=((n%2)*300,(n//2)*110);sheet.paste(im.resize((144,120),Image.Resampling.NEAREST),at,im.resize((144,120),Image.Resampling.NEAREST))
   dr.text((at[0]+150,at[1]+36),label+' '+('R'if face==1 else'L'),fill='white')
  sheet.save(O/'source-pose-sheet.png')
  proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 files=[Path(__file__),Path(V.__file__),Path(V.V.__file__),Path(C.__file__),Path(C.M.__file__),Path(T.__file__),R/'tools/audit/dragon_power_gameplay_render_v1.py',Path(D.__file__),R/'tools/prepare_pit_retold_host_v1.py',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'candidate.nes',P/'candidate.dbg',R/'build/pit-retold-assets-v1/handoff.json']
 proof['bindings']={str(p.resolve()):sha(p)for p in files};a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']
if __name__=='__main__':main()
