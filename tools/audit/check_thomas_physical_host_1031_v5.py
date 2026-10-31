"""Actual linked cold loader and original42pose native OAM; no RAM preload."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
P=R/'build/thomas-physical-host-1031-v9';O=R/'build/thomas-physical-controls-1031-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False,no_RAM_preload=True,shared_hooks_unchanged=True)
 try:
  stage=json.loads((P/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  b=H.C.qualified(P/'candidate.nes');cookie=(P/'source/cookie.bin').read_bytes()
  expected=[bytearray((P/f'{n}.bin').read_bytes())for n in ['state','kernel']]
  for v in expected:v[0x1fe0:0x1ff0]=cookie
  def make(**kw):return L.make(b,SelectedCharacter=10,FmAlts=64,CurrentPlayer=0,Player_Rel_XPos=120,Player_Rel_YPos=160,**kw)
  def call(m,name,slot=None,**kw):return L.call(m,name,slot=slot,**kw)
  def row(m,slot,**kw):return call(m,'ThServiceVeneers',slot=slot,**kw)
  def completed_nmi(m):
   H.put(m,NmiDisable=0);c=NesMPU(memory=m,pc=0x5b00);c.sp=224;c.p=0x30;return V.interrupt(m,c,'NMI')
  loaders=[];seed=None
  for p,ctrl in itertools.product([L.flags(0),L.flags(63)],[128,160,164]):
   m=make(Mirror_PPUCTRL=ctrl);m.ppuctrl=ctrl;H.invoke(m,'X5PublishChr');latches=m.chr_latches[:]
   context=bytes(m[0x5c00:0x8000]);zero=bytes(m[3:11]);ram01=[bytes(v)for v in m.ram[:2]];m.writes.clear();m.ram_writes.clear()
   c,low=call(m,'ThLoad',a=0x59,x=7,y=0x83,p=p)
   assert(c.a,c.x,c.y,c.sp)==(0x59,7,0x83,224)and c.p==((p&0x7d)|1),('load ABI',c.a,c.x,c.y,c.p,c.sp,p)
   assert [bytes(v)for v in m.ram[2:]]==list(map(bytes,expected)),('true sparse loader payload',[(i,bytes(m.ram[i])==bytes(expected[i-2]))for i in[2,3]])
   assert m.ram_writes[:2]==[(3,0x1fe0,0),(2,0x1fe0,0)]and m.ram_writes[-1]==(2,0x1fe0,167)
   assert [bytes(v)for v in m.ram[:2]]==ram01 and bytes(m[0x5c00:0x8000])==context and bytes(m[3:11])==zero
   assert m.chr_latches==latches and m.upper==0 and m.ppuctrl==ctrl and m.toggle==0
   assert m.ppu_log[-2:]==[(0x2005,73),(0x2005,32)]
   assert not any(a in[0x5102,0x5103,0x5113]for a,v in m.writes)
   reads=m.ppu_reads;writes=len(m.ram_writes);warm,_=call(m,'ThLoad',a=0x59,x=7,y=0x83,p=p)
   assert warm.p&1 and reads==m.ppu_reads and writes==len(m.ram_writes)
   loaders.append(dict(p=p,ctrl=ctrl,coldCPU=c.processorCycles,warmCPU=warm.processorCycles,PPUreads=reads,minimumSP=low))
   if seed is None:seed=L.fork(m)
  print('Thomas actual sparse copy/verify/cookies/warm contexts PASS',flush=True)
  rejects=[]
  for name,kw in [('Ryu',dict(FmAlts=0)),('Shinobi',dict(FmAlts=4)),('illegalboth',dict(FmAlts=68)),('foreign',dict(SelectedCharacter=0)),('title',dict(OperMode=0)),('notbusy',dict(FamilyMainCommit=0)),('active',dict(DisableScreenFlag=0)),('mask',dict(Mirror_PPUMASK=30)),('normalNMI',dict(NmiDisable=0))]:
   m=make();H.put(m,**kw);before=[bytes(v)for v in m.ram];m.ram_writes.clear();c,_=call(m,'ThLoad')
   assert not c.p&1 and [bytes(v)for v in m.ram]==before and not m.ram_writes and m.ppu_reads==0,name
   rejects.append(name)
  poisons=0
  for bank,i in itertools.product([2,3],range(16)):
   m=L.fork(seed);m.ram[bank][0x1fe0+i]^=1
   for f in range(64):
    z=L.fork(m);c,_=call(z,'ThCheckCode',a=0x59,x=7,y=0x83,p=L.flags(f))
    assert(c.a,c.x,c.y,c.sp)==(0x59,7,0x83,224)and c.p==(L.flags(f)&0x7c)and not z.ram_writes
    poisons+=1
  for bank in [2,3]:
   for family in [9,22,31,32,33,10]:
    m=L.fork(seed);m.ram[bank][0x1fe1]=family;other=5-bank;m.ram[other][0x1fe0]=0
    before=bytes(m.ram[bank]);call(m,'ThRetire');expected_validity=0 if family==10 else 167
    assert m.ram[bank][0x1fe0]==expected_validity and bytes(m.ram[bank][0x1fe0+1:])==before[0x1fe0+1:]
  print('Thomas owner rejection/allcookie-byte allflags/retirement PASS',flush=True)
  # Initialize through the real resident36row and first accepted movement.
  m=L.fork(seed);H.put(m,FrameCounter=1,GameEngineSubroutine=8,SavedJoypadBits=0)
  c,_=row(m,0);assert m.rawtags[2]==2 and m.ram[2][0x800]==167 and m.ram[2][0x845]==167
  c,_=call(m,'ThCheck');assert c.p&1
  epoch=[]
  for field in ['CurrentPlayer','NumberofLives','WorldNumber','AreaAddrsLOffset']:
   z=L.fork(m);H.put(z,**{field:(H.get(z,field)+1)&255});c,_=call(z,'ThCheck');assert not c.p&1;epoch.append(field)
  # Actual cold preview works with poisoned uninitialized RAM; original standing
  # descriptor is immutable ROM and sourcevalidity remains completely untouched.
  cold=[]
  for yy,xx,p in itertools.product([88,160],[96,116],[L.flags(0),L.flags(63)]):
   z=make(Player_Y_Position=yy,Player_X_Position=xx);old=[bytes(v)for v in z.ram];H.put(z,CurrentOAMOffset=0)
   c,_=row(z,17,p=p)
   assert(c.a,c.x,c.y,c.p,c.sp)==(85,7,91,p&0x7d,224)
   assert all(z[512+i]<240 for i in range(0,24,4)),'Cold native body hidden'
   assert H.get(z,'CurrentOAMOffset')==24 and [bytes(v)for v in z.ram]==old and not z.ram_writes
   completed_nmi(z)
   assert z.chr_latches[0]==stage['body_first_page'];cold.append([yy,xx,p])
  # All source42commands render through actualnative kernel and published CHR.
  source=json.loads((R/'build/thomas-original-component-v5/assets/poses.json').read_text())
  indices=(R/'build/thomas-original-component-v5/assets/thomas-source-indices.bin').read_bytes()
  renders=[]
  for i,pose in enumerate(source['poses']):
   z=L.fork(m);z.ram[2][address(b,'ThPoseCommand')&8191]=pose['command'];H.put(z,CurrentOAMOffset=0)
   row(z,26);row(z,2);completed_nmi(z);count=H.get(z,'CurrentOAMOffset');oam=bytes(z[512:512+count]);assert count==pose['parts']*4
   pixels={}
   for at in range(0,count,4):
    y,tile,attr,x=oam[at:at+4];assert attr&3==0
    physical=z.chr_latches[(tile&254)//64];offset=1048592+physical*1024+((tile&254)%64)*16
    for dy in range(16):
     rowbits=(dy//8)*16+(dy&7);lo=b['raw'][offset+rowbits];hi=b['raw'][offset+rowbits+8]
     for dx in range(8):
      v=((lo>>(7-dx))&1)|(((hi>>(7-dx))&1)<<1)
      if v:pixels.setdefault((x+dx,y+1+dy),v)
   expected_pixels={}
   source_at=indices[i*3840:(i+1)*3840]
   for y in range(80):
    for x in range(48):
     v=source_at[y*48+x]
     if v:expected_pixels[(120-16-H.get(z,'ScreenLeft_X_Pos')+x,160-48+y)]=v
   assert list(z.vram[0x3f11:0x3f14])==[39,48,15],'Actual completed original P0 palette'
   assert pixels==expected_pixels,('native42pose pixel/anchor mismatch',pose['command'],list(pixels.items())[:3],list(expected_pixels.items())[:3])
   renders.append(dict(command=pose['command'],parts=count//4,pixels=len(pixels)))
  print('Thomas ROM-only cold +42 genuine native OAM/CHR pixel cases PASS',flush=True)
  q.update(passed=True,actual_farcall_NZ_contract='Genuine FarCallCommon final LDA of returnedA sets N/Z; direct helper fullflags requires separate target-entry proof, not prefarcall inputP identity.',loaders=loaders,rejects=rejects,allflag_cookie_poison_pairs=poisons,epoch_rejects=epoch,cold_preview_cases=len(cold),actual_completed_normalNMI_publications=len(cold)+len(renders),native42pose_cases=len(renders),renders=renders,
   limits=['Private owned payload only; currentmenu/main routing unchanged and Thomasstillpending','Selected authenticatedRAMcallbacks intentionallyreturnC2; sharedcallerABIclosure remains reviewwork','Native screenshot/rasterdeadline nottested'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in [Path(__file__),Path(L.__file__),Path(H.__file__),Path(V.__file__),P/'source-stage.json',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',P/'kernel.bin',P/'state.bin',P/'source/cookie.bin']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','renders','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
