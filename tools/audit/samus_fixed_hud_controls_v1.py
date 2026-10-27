"""Finite assembled fixed-page HUD, complete callers, publication and IRQ checks."""
from pathlib import Path
import hashlib,itertools,json,re,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location,Memory
from samus_hud_icon_controls_v1 import setup,run,execute,pixel
from verify_native_relocation import NesMPU
R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P='samus_fixed_hud';EXPECTED='9d1a333ee6141424e13ff1c8c0876452e59dc812bc1a310fbe6276727b4610d9'

def state(q):
 return [q.get(n)for n in ['SsChrActive','SsChrPhysical','CurrentOAMOffset']],q.m.banks[:]
def model(b,scenario,parity):
 q=setup(b);q.invoke('X5ColdInit');q.invoke('PlayerGfxHandler');q.put(FrameCounter=parity,AvDrawFirst=19)
 if scenario in ['long','wave']:
  for n,v in [('SmShotType',2 if scenario=='long'else 3),('SmShotDir',0),('SmShotX',100),('SmShotPage',1),('SmShotY',120)]:q.set(n,v,0)
 elif scenario=='ice':
  q.put(AvDrawFirst=8)
  for n,v in [('RgShotType',46),('RgShotDir',1),('RgShotX',160),('RgShotPage',1),('RgShotY',120),('RgShotYHigh',1)]:q.set(n,v,9)
 elif scenario=='refill':
  q.put(AvDrawFirst=18)
  for n,v in [('InvDropKind',2),('AvDropItem',2),('InvDropX',200),('InvDropPage',1),('InvDropY',160)]:q.set(n,v,3)
 return q

def main():
 old=scoped_load(B/'proto_palette_ack.nes');new=scoped_load(B/(P+'.nes'));held=scoped_load(B/'samus_projectile_hud.nes')
 assert sha(B/(P+'.nes'))==EXPECTED
 # Actual emitted tuples and their complete42-pixel indexed shape/color agree
 # with authenticated original missile art, relocated into fixed page20 only.
 q=setup(new);c,w,e=run(q);hud=[(a,v)for a,v,i in w if i==20]
 parts=[tuple(q.m[512+i:516+i])for i in (0,4)]
 assert parts==[(20,79,194,195),(20,77,194,187)]
 pixels={};auth={}
 for ps,page,tiles in [(pixels,20,[79,77]),(auth,215,[61,59])]:
  for (y,_,attr,x),tile in zip(parts,tiles):
   for dy in range(16):
    for dx in range(8):
     v=pixel(new['raw'],page,tile,attr,dx,dy)
     if v:ps[x+dx,y+1+dy]=v
 assert pixels==auth and len(pixels)==42
 assert [min(x for x,y in pixels),min(y for x,y in pixels),max(x for x,y in pixels),max(y for x,y in pixels)]==[187,21,197,28]
 rows=[]
 for (char,item,mixed),offset,rot in itertools.product([(2,2,False),(2,2,True),(2,0,False),(2,1,False),(2,3,False),(2,7,False),(3,2,False),(9,1,False)],[0,220,236,244,248],[False,True]):
  qs=[];results=[];costs=[]
  for b in [old,held,new]:
   z=setup(b,char,item,offset,rot,mixed)
   for i in range(64):z.m[512+4*i]=248;z.m[514+4*i]=0
   cpu,ev,entries=run(z);regs=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp]
   hs=[(a,v)for a,v,i in ev if i==20]
   ys=[z.m[a]for a,v in hs if(a-512)%4==0]
   z.put(SmFreezeRenderState=1);z.set('AvFrozen',180,0);finish,_=z.invoke('SamusFreezeRenderFinish')
   costs.append([cpu.processorCycles,finish.processorCycles,cpu.processorCycles+finish.processorCycles])
   results.append(dict(regs=regs,events=ev,HUD_stores=len(hs),HUD_visible=sum(y<239 for y in ys),leases=state(z)[0],entries=entries));qs.append(z)
  foreign=not(char==2 and item==2)
  if foreign:
   assert results[0]['regs']==results[2]['regs']and results[0]['events']==results[2]['events']
   assert qs[0].m[:0x1c0]==qs[2].m[:0x1c0]and qs[0].m[0x200:0x8000]==qs[2].m[0x200:0x8000]
  rows.append(dict(char=char,item=item,mixed=mixed,offset=offset,synthetic_rotation=rot,cycles_parent_4e5c_fixed=costs,HUD_stores=[r['HUD_stores']for r in results],visible_parts=[r['HUD_visible']for r in results],delta_parent=costs[2][2]-costs[0][2],delta_4e5c=costs[2][2]-costs[1][2],foreign_fullcaller_exact=foreign,partial_AXYP_SP_equal=results[0]['regs']==results[2]['regs']))
 # Complete outer caller includes native OAMClear tail and freeze rewrites.
 outer=[]
 for char,item,mixed,freeze in [(2,2,False,0),(2,2,False,1),(2,2,True,0),(2,2,True,1),(2,1,False,0),(2,7,False,0),(3,2,False,0),(9,1,False,0)]:
  values=[]
  for b in [old,held,new]:
   z=setup(b,char,item,0,False,mixed);z.put(SmFreezeRenderState=freeze)
   if freeze:z.set('AvFrozen',180,0)
   cpu,_=z.invoke('SamusFreezeDrawAll');values.append(dict(cycles=cpu.processorCycles,AXYP_SP=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp],banks=z.m.banks[:],source256=list(z.m[512:768])))
  assert values[0]['AXYP_SP']==values[2]['AXYP_SP']and values[0]['banks']==values[2]['banks']
  if not(char==2 and item==2):assert values[0]['source256']==values[2]['source256']
  outer.append(dict(char=char,item=item,mixed=mixed,freeze=freeze,cycles=[v['cycles']for v in values],delta_parent=values[2]['cycles']-values[0]['cycles'],delta_4e5c=values[2]['cycles']-values[1]['cycles'],complete_return_AXYP_SP_banks_exact=True))
 # Real SamusDrawShots includes parity-dependent RemainingDraw and beam order.
 # Fixed HUD never consumes SsChr arbitration, including native beam and
 # source drop/ice families that previously rejected its icon.
 owner=[]
 for scenario,parity in itertools.product(['idle','long','wave','ice','refill'],[0,1]):
  z=model(new,scenario,parity);z.invoke('SamusDrawShots');o=z.m[512:768]
  slots=[i//4 for i in range(0,256,4)if tuple(o[i:i+4])in parts]
  assert len(slots)==2,(scenario,parity,slots)
  assert z.get('CurrentCHRBank',5)==24 and z.m[0x5125]==20 and z.m[0x5130]==0
  owner.append(dict(scenario=scenario,FrameCounter=parity,HUD_slots=slots,special_physical=z.get('SsChrPhysical'),window5_physical=z.m[0x5125],body_window0=z.m[0x5120]))
 # Both full caller forms use the genuine fixed alias Dxxx in C61 while the
 # renderer farcall maps A4. No source data gets overwritten by A remapping.
 z=setup(new);orig=NesMPU.step;seen=[]
 def step(cpu):
  if cpu.pc==address(new,'MetaspriteRenderLoop')and z.m.banks[1]==4:
   ptr=z.get('R0')+256*z.get('R1')
   # The subsequent body draw legitimately retains AvDrawIndex20. Bind the
   # unique intended record pointer, never a stale producer-index scope.
   if ptr==address(new,'SamusFixedHudRecord')+8192:seen.append(dict(pointer=ptr,Cbank=z.m.banks[2],Abank=z.m.banks[1],SP=cpu.sp,bytes=list(z.m[ptr:ptr+9])))
  orig(cpu)
 NesMPU.step=step
 try:z.invoke('SamusFreezeDrawAll')
 finally:NesMPU.step=orig
 assert len(seen)==1 and all(v['Cbank']==61 and v['Abank']==4 and v['bytes']==[8,77,194,252,251,79,194,252,3]for v in seen)
 # Actual IRQ vector at every reached new helper instruction, including the
 # legitimate shadow-before-$5116 bank transition; all5SMC/live stack retained.
 z=setup(new);z.m.page(1,61);z.set('CurrentBank',189);image=list(z.m);banks=z.m.banks[:]
 def fresh():
  m=Memory(new);list.__setitem__(m,slice(None),image);m.banks=banks[:];return m
 m=fresh();cpu,trace=execute(new,m,'RemainingDraw',record=True)
 keys=sorted({(pc,k)for pc,k in trace if k==61 and address(new,'SamusFixedMissileHud')<=pc<address(new,'SamusFixedHudRecord')})
 def flat(m):return bytes(m[:0x1c0]+m[0x200:0x800]+m[0x6000:0x8000])
 def bus(m):return[w for i,w in enumerate(m.writes)if i not in m.irq_write_indices and not 256<=w[0]<512]
 expected=(cpu.a,cpu.x,cpu.y,cpu.p&207,cpu.sp,flat(m),m.banks,bus(m))
 for key in keys:
  m=fresh();cpu,_=execute(new,m,'RemainingDraw',inject=key)
  assert(cpu.a,cpu.x,cpu.y,cpu.p&207,cpu.sp,flat(m),m.banks,bus(m))==expected,key
 # Mapping instructions unchanged for every window5 choice; fixed aliases
 # only default logical24=>20. Foreign direct/wide pages retain their choice.
 publication=[]
 for logical,direct,upper in [(24,0,0),(21,0,0),(80,0,0),(20,128,0),(13,129,1),(5,130,2)]:
  vals=[]
  for b in [old,new]:
   z=setup(b);z.invoke('X5ColdInit');z.set('CurrentCHRBank',logical,5);z.set('X5ChrMode',direct,5);z.put(X5WideChrActive=int(bool(direct)));z.invoke('X5PublishChr');vals.append([z.m[0x5125],z.m[0x5130],z.get('CurrentCHRBank',5)])
  assert vals[0]==vals[1];publication.append(dict(logical=logical,mode=direct,result=vals[1]))
 text=(R/'src/metasprite.s').read_text();mouse=text[text.index('.if ::MOUSE_DISPLAY_CURSOR'):text.index('.endif',text.index('.if ::MOUSE_DISPLAY_CURSOR'))]
 pairs=[int(t,16)//2 for t in re.findall(r'MetaspriteBox "MOUSE", "[A-Z]+", \$(\w+), \$(\w+)',mouse)for t in t]
 assert pairs==[0,1,2,3,4,5]and'MOUSE_VRAM_OFFSET = SPRITE_BANK_5'in mouse
 assert address(new,'MOUSE_DISPLAY_CURSOR')==0
 mapping=new['raw'][location(new,'ChrPhysicalMap'):location(new,'ChrPhysicalMap')+256]
 assert [i for i,v in enumerate(mapping)if v==20]==[24]
 sources=['src/metasprite.s','src/mmc5.s','src/mmc5_expanded.s','src/samus_weapons.s','src/chr_map_mmc5.inc','src/guest_publish_chr.inc']
 proof=dict(passed=True,source_only=True,native_run=False,ROM_sha256=EXPECTED,parent_sha256=sha(B/'proto_palette_ack.nes'),RemainingDraw_and_frame_scan_cases=len(rows),rows=rows,complete_outer_cases=outer,actual_SamusDrawShots_family_cases=owner,fixed_record_C_alias=seen,actual_IRQ_instruction_boundaries=keys,IRQ_scope='Actual compiled vector. FullAXYP/SP, applicationRAM0000..01BF/0200..07FF/6000..7FFF, banks and ordered nonIRQ/nonstack writes; dead upper64stack and IRQ-owned PPU registers excluded.',window5_publication_cases=publication,mouse=dict(current_compiled_option=0,static_three_records_pairs=pairs,physical20_logical_aliases=[24],all_original_pairs0_to5_exact=True),source_pixels=dict(opaque42=True,indexed_palette_shape_exact=True,bounds=[187,21,197,28]),limits='SOURCE ONLY. Fixed HUD changes special-family admission and part count intentionally; mixed world/shot output may improve or change. Near-full OAM may admit new parts and add work. Foreign admittedHUD +15cycles; no selectedHUD +0. Hardware8sprite visibility, native cadence/epochs, high jumping body overlap and fullNMI timing require ROOT native review. Current mouse option disabled; optional mouse proof is its exact static three-record source, not a mouse-enabled native run.',bindings={str(p):sha(p)for p in [Path(__file__),B/(P+'.nes'),B/(P+'.dbg'),B/(P+'_build.json'),R/'tools/audit/samus_hud_icon_controls_v1.py',R/'tools/audit/samus_hud_icon_candidate_v1.py']+[R/n for n in sources]})
 out=B/(P+'_controls.json');assert not out.exists();out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(passed=True,proof_sha256=sha(out),cases=len(rows),IRQ=len(keys),outer=outer)))
if __name__=='__main__':main()
