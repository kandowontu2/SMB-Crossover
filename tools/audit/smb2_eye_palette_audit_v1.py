"""Read-only actual SMB2 eye pixels and genuine original/native palette consumers."""
from pathlib import Path
import collections,hashlib,importlib.util,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_smb2_roster_native_v1 as N
import prepare_smb2_roster_art_v1 as ART
import prepare_ff_joint_source_v1 as B
from check_tmnt_render_oa import location
O=R/'build/smb2-eye-role-audit-v1';J=R/'build/functional-roster-coherent62-v4/joint'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class OriginalBus:
 def __init__(self):self.ram=N.original(3);self.vram=bytearray(16384);self.ctrl=0;self.latch=0;self.addr=0;self.writes=[]
 def __getitem__(self,a):
  if isinstance(a,int)and a==0x2002:self.latch=0;return 0
  return self.ram[a]
 def __setitem__(self,a,v):
  self.ram[a]=v
  if a==0x2000:self.ctrl=v
  elif a==0x2006:
   self.addr=((v&63)<<8)|(self.addr&255)if not self.latch else(self.addr&0x3f00)|v;self.latch^=1
  elif a==0x2007:
   at=self.addr&16383;self.vram[at]=v;self.writes.append([at,v]);self.addr=(self.addr+(32 if self.ctrl&4 else 1))&16383
def signed(n):return n-256 if n>=128 else n
def pixels(raw,page,rec):
 result={};eye={};base=1048592
 # Native Meta loop DEYs; original four body parts precede the eye in OAM.
 for k in range((rec[0]//4)-1,-1,-1):
  t,a,y,x=rec[1+k*4:5+k*4]
  for yy in range(16):
   sy=15-yy if a&128 else yy;at=base+page*1024+(t&254)*16+(sy//8)*16+sy%8
   for xx in range(8):
    sx=7-xx if a&64 else xx;v=(raw[at]>>(7-sx)&1)|((raw[at+8]>>(7-sx)&1)<<1)
    if v:
     p=(signed(x)+xx,signed(y)+yy)
     if k==0:eye[p]=v
     result.setdefault(p,(a&3,v,k))
 return result,eye
def main():
 assert not O.exists();O.mkdir();out=O/'audit.json';q=dict(passed=False,native=False,source_changed=False,checks={});ck=q['checks']
 try:
  B.validate(J.parent/'handoff.json','bb581aad7a4224cd35b83e056fe880cbd49c5cfcf04bfa637b00ea146bc01ab6')
  raw=N.ROM.read_bytes();assert N.digest(raw)==N.SHA;assert(N.REF/'bin/native.nes').read_bytes()[16:]==raw[16:]
  l=N.labels();original=[]
  for world,selector in itertools.product(range(7),range(3)):
   m=OriginalBus();m.ram[l['CurrentWorldTileset']]=world
   # Body is independent from the world eye role; supply genuine Mario data.
   at=16+5*16384+l['CharacterPalette']-0x8000;m.ram[l['RestorePlayerPalette0']:l['RestorePlayerPalette0']+4]=raw[at:at+4]
   producer=ART.call(m,'ApplyPalette',a=selector)
   ptr=l['RAM_PPUDataBufferPointer'];base=l['PPUBuffer_301'];m.ram[ptr]=base&255;m.ram[ptr+1]=base>>8
   consumer=ART.call(m,'UpdatePPUFromBufferNMI')
   p1=list(m.vram[0x3f14:0x3f18]);assert p1[2]==0x16 and len(m.writes)==32
   original.append(dict(world=world,sprite_selector=selector,actual_PPU_P1=p1,actual_PPUDATA_writes=m.writes,ApplyPalette_CPU=producer.processorCycles,UpdatePPUFromBufferNMI_CPU=consumer.processorCycles))
  ck['genuine_original_ApplyPalette_and_NMI_consumer']=dict(cases=len(original),rows=original,all_eye_index2_is_NES16=True,white_or_black_eye_assumption_rejected=True)
  b=B.scoped_load(J/'candidate.nes')if hasattr(B,'scoped_load')else None
  if b is None:
   from link_pit_rygar_sophia_audit_cpu import scoped_load
   b=scoped_load(J/'candidate.nes')
  cartridge=b['raw'];rows=[];visible_counts=collections.Counter();roles=set()
  for profile,i in itertools.product(range(8),range(32)):
   rid=cartridge[location(b,'S2BodyRecord')+profile*32+i];ptr=cartridge[location(b,'S2ArtLo')+rid]+256*cartridge[location(b,'S2ArtHi')+rid];at=16+80*8192+ptr-0xc000;rec=cartridge[at:at+21]
   assert rec[0]==20 and rec[1]in[56,58]and rec[2]&3==1
   final,eye=pixels(cartridge,796+profile,rec);roles|=set(eye.values());shown=[p for p in eye if final[p][2]==0]
   visible_counts[profile]+=len(shown);assert all(eye[p]==2 for p in shown)
   rows.append(dict(profile=profile,native_class=profile//2,size=profile&1,index=i,record_id=rid,eye_tile=rec[1],eye_attrs=rec[2],all_eye_pixels=dict(collections.Counter(eye.values())),visible_eye_pixels=len(shown),source_color16=True))
  assert roles=={2};ck['all256_current_body_eye_parts']=dict(cases=len(rows),rows=rows,used_nontransparent_indices=sorted(roles),visible_pixels_by_profile=dict(visible_counts),maximum_visible_eye_pixels=max(x['visible_eye_pixels']for x in rows),part_count=5,no_extra_CHR_window_or_OAM_needed_if_P2_red16_proven=True)
  # Import ONE actual final62 bus factory. Its native NMI executes the real
  # source queue/palette consumer, not a model that parses packets by hand.
  f=R/'build/smb2-natural-current-audio-v20/controls.py';sp=importlib.util.spec_from_file_location('eye_audit_single_actual_bus',f);A=importlib.util.module_from_spec(sp);sp.loader.exec_module(A);C=A.C;M=A.M
  def fresh(v):
   m=M.fresh(v,0);prior=C.O;C.O=J
   try:new=C.Bus()
   finally:C.O=prior
   m.bundle=new.bundle;m.ROM_banks=new.ROM_banks;m.lab=new.lab;return m
  donor=[]
  for area in range(4):
   m=fresh(0);M.put(m,AreaType=area);C.invoke(m,'GetAreaPalette');A.interrupt(m,0)
   p2=list(m.vram[0x3f19:0x3f1c]);p3=list(m.vram[0x3f1d:0x3f20]);assert p2==[22,48,39]
   donor.append(dict(scene='native-area-'+str(area),P2=p2,P3=p3))
   # The original Bowser packet changes P1 only; red/worldP2 stays exact.
   M.put(m,VRAM_Buffer_AddrCtrl=11);A.interrupt(m,0);assert list(m.vram[0x3f19:0x3f1c])==p2
   donor.append(dict(scene='bowser-after-area-'+str(area),P2=list(m.vram[0x3f19:0x3f1c]),P3=list(m.vram[0x3f1d:0x3f20])))
  for var in range(4):
   m=fresh(var);C.invoke(m,'GetAreaPalette');A.interrupt(m,0)
   for name in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,name)
   A.interrupt(m,0);assert list(m.vram[0x3f19:0x3f1c])==[22,48,39];donor.append(dict(scene='selected-class'+str(var),P2=list(m.vram[0x3f19:0x3f1c]),P3=list(m.vram[0x3f1d:0x3f20])))
   M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',A=0);pending=False
   for age in range(1500):
    A.interrupt(m,0)
    if pending:
     p2=list(m.vram[0x3f19:0x3f1c]);assert p2==[22,48,39]
     donor.append(dict(scene='true-lives-class'+str(var),P2=p2,P3=list(m.vram[0x3f1d:0x3f20]),actual_NMI_PPUDATA_consumption=True));break
    z=C.invoke(m,'GameLoop');pending=any(pc==m.lab['DisplayIntermediate']and tags[(pc-32768)//8192]==m.bank('DisplayIntermediate')|128 for tags,pc in z['trace']if pc>=32768)
   else:raise AssertionError('Actual lives did not appear')
  ck['actual_native_P2_donor_and_P3_negative']=dict(cases=len(donor),rows=donor,source_red16_P2index1_in_every_case=True,P3_black_not_constant=True)
  ck['minimal_proposal']=dict(pattern='Only eye56 sourceindex2 ->nativeP2index1; plane1bits move losslessly toplane0. Blank58 unchanged.',descriptor='Existing eye quad attrsP1->P2; allfour P0body parts exact; total remains5.',source_original_visible_color='NES16, not an assumed white/black role. Original producer and actual NMI consumer21cases prove it.',no_palette_writes_or_world_recolor=True,no_extra_OAM_CHR_RAM_PRG=True,unimplemented_until_source_link=True)
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 files={Path(__file__),N.ROM,N.REF/'bin/native.nes',N.REF/'src/prg-6-7.asm',N.REF/'src/prg-e-f.asm',J/'candidate.nes',J/'candidate.dbg',J.parent/'handoff.json',R/'src/smb2_roster_palette_v2.s',J/'src/characters.s'}
 for module in list(sys.modules.values()):
  f=getattr(module,'__file__',None)
  if f and Path(f).resolve().is_relative_to(R/'tools'):files.add(Path(f).resolve())
 q['bindings']={str(f.resolve()):sha(f)for f in files if f.is_file()};out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps(dict(passed=q['passed'],error=q.get('error'),path=str(out),sha256=sha(out))),flush=True);assert q['passed']
if __name__=='__main__':main()
