"""Actual queued palette, first DMA and independent retirement contracts."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_hogan_palette_groups_controls_v2 as G
import ff_current_ready_cold_controls_v2 as C
from check_tmnt_render_oa import address
from ff_wram_host_isr_v4 import clone
from wwf_first_hogan_owner_isr_v1 import interrupt
from arthur_cache_host_controls_v1 import OverlayMemory
class PaletteMirrorMemory(OverlayMemory):
 def __setitem__(self,i,v):
  at=self.ppu_addr if i==0x2007 else None
  super().__setitem__(i,v)
  if at is not None and at>=0x3f00:
   lo=at&31
   if lo in [16,20,24,28]:lo-=16
   for a in range(0x3f00,0x4000):
    other=a&31
    if other in [16,20,24,28]:other-=16
    if other==lo:self.vram[a]=v&63
H=G.H;T=G.T;J=R/'build/wwf-hogan-natural-source-v15/joint';O=R/'build/wwf-hogan-palette-closure-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def own(b):
 G.J=J;m=G.own(b);m.__class__=PaletteMirrorMemory
 H.put(m,AreaType=1,BackgroundColorCtrl=0,SmFreezePaletteControl=2,SmFreezeRenderState=0,RgOamUsed=0,RgOamFirst=0,RgOamRotation=0,GuestOamRotationActive=0,SpriteShuffleOffset=0,FrameCounter=0)
 for n in ['ObjectMetasprite','SprObject_SprAttrib']:
  for i in range(24):m[address(b,n)+i]=0
 meta=address(b,'METASPRITE_KOOPA_WALKING_1');m[address(b,'ObjectMetasprite')+1]=meta
 for n,v in dict(Enemy_Flag=1,Enemy_ID=0,Enemy_X_Position=184,Enemy_PageLoc=0,Enemy_Y_Position=176,Enemy_Y_HighPos=1,Enemy_MovingDir=1,Enemy_SprAttrib=1).items():m[address(b,n)]=v
 H.put(m,VRAM_Buffer1_Offset=0);m[address(b,'VRAM_Buffer1')]=0
 return m

def draw(m,hook=None):
 if not H.get(m,'FamilyMainCommit')&1:H.invoke(m,'PauseRoutine',a=255)
 H.put(m,CurrentOAMOffset=0);m[512:768]=[248,0,0,0]*64
 H.invoke(m,'PlayerGfxHandler');G.shared(m,hook=hook)

def queue(m,raw):
 at=address(m.bundle,'VRAM_Buffer1');m[at:at+len(raw)]=raw
 H.put(m,VRAM_Buffer1_Offset=len(raw)-1)

def flush(m):
 H.invoke(m,'PauseRoutine',a=0)
 return C.A.consume(m)

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,checks={},vectors=[])
 try:
  b=T.qualified(J/'candidate.nes');base=own(b)
  m,_=clone(base,G.NesMPU(memory=base));phases=[]
  H.invoke(m,'WfColors')
  for age in range(4):
   draw(m);choice=m.ram[2][address(b,'WfP1Choice')-0xc000]
   attrs=bytes(m[address(b,'SprObject_SprAttrib'):address(b,'SprObject_SprAttrib')+24])
   assert attrs[1]==1 and all(m[514+i]&24==0 for i in range(0,256,4))
   r=flush(m);want=[22,5,15]if choice else[26,48,39]
   assert r['P1']==want,(age,choice,r)
   assert list(m.vram[0x3f11:0x3f14])==[40,39,23]
   assert m.vram[0x3f00]==m.vram[0x3f10]==34
   phases.append(dict(age=age,choice=choice,PPU=r,parts=sum(m[512+i]<240 for i in range(0,256,4))))
  assert[r['choice']for r in phases]==[1,0,1,0]
  q['checks']['actual_normal_NMI_whole_groups']=dict(passed=True,phases=phases)
  # Full queue: retain all complete unrelated native bytes, hide only the
  # two competing whole groups, don't advance turn; retry after real NMI.
  m,_=clone(base,G.NesMPU(memory=base));raw=[0x20,0,74]+[0x24]*74+[0];queue(m,raw)
  turn=m.ram[2][address(b,'WfP1Turn')-0xc000];draw(m)
  assert list(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+78])==raw
  assert m.ram[2][address(b,'WfP1Turn')-0xc000]==turn
  assert m.ram[2][address(b,'WfP1Choice')-0xc000]==2
  assert all(m[512+i]>=240 for i in range(0,48,4))
  flush(m);draw(m);r=flush(m);assert r['P1']==[22,5,15]
  q['checks']['full_queue_bounded_retry']=dict(passed=True,bytes=78,PPU=r)
  # Repeated real publications with vertical/repeat and a literal whose
  # *data* resembles an own command. Only true complete command headers
  # may be changed by retirement; the unrelated data must remain exact.
  m,_=clone(base,G.NesMPU(memory=base));prefix=[0x20,0,6,63,21,3,22,5,15,0x20,0x40,0x43,0x24,0x20,0x80,0x82,0x25,0x26]
  queue(m,prefix+[0])
  for age in range(4):draw(m)
  count=H.get(m,'VRAM_Buffer1_Offset');before=list(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+count+1]);seen=[]
  def pending(mem,cpu,step):
   if cpu.pc==address(b,'WfP1NativeRestore'):seen.append(['entry',H.get(mem,'SmFreezePalettePending')])
  H.invoke(m,'WfP1Retire',hook=pending)
  after=list(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+count+1])
  assert after[:len(prefix)]==prefix
  for at in range(len(prefix),count,6):assert after[at:at+6]==[63,21,3,26,48,39]
  assert H.get(m,'SmFreezePalettePending')==192
  r=flush(m);assert r['P1']==[26,48,39]
  q['checks']['all_owned_queued_commands_retire']=dict(passed=True,old=before,new=after,PPU=r,pending=seen)
  # Corrupt-cookie paths may never run/read selected code. The pure ROM
  # retirement parser still cancels queued own colours and restores native.
  rejects=0
  for at in range(16):
   m,_=clone(base,G.NesMPU(memory=base));draw(m);m.ram[2][0x1fe0+at]^=1;image=bytes(m.ram[2]);executed=[]
   def no_guest(mem,cpu,step):
    if 0xc000<=cpu.pc<0xe000 and mem.rawtags[2]==2:executed.append(cpu.pc)
   H.invoke(m,'WfP1LateDispatch',hook=no_guest)
   assert not executed and bytes(m.ram[2])==image
   assert flush(m)['P1']==[26,48,39];rejects+=1
  q['checks']['poison_before_first_guest']=dict(passed=True,all_cookie_bytes=rejects)
  # Actual menu retirement is before Selected publication, and before a
  # later foreign cache can take the lease. A foreign C2 cookie/packet is
  # never cleared by a subsequent stale WWF retirement call.
  m,_=clone(base,G.NesMPU(memory=base));draw(m);H.put(m,CrossoverMenuIndex=30,FmGroups=0)
  publication=[];old_selected=H.get(m,'SelectedCharacter')
  def publish(mem,cpu,step):
   nonlocal old_selected
   now=H.get(mem,'SelectedCharacter')
   if now!=old_selected:
    publication.append([old_selected,now,mem.ram[2][0x1fe0],mem.ram[3][0x1fe0],H.get(mem,'SmFreezePalettePending')]);old_selected=now
  H.invoke(m,'MenuResolveCharacter',hook=publish)
  assert publication and publication[0][:4]==[29,31,0,0],publication
  assert flush(m)['P1']==[26,48,39]
  # This simulates a subsequent fully distinct lease identity only, not a
  # claimed CF loader proof. Rejection must be data-independent and exact.
  m.ram[2][0x1fe0:0x1ff0]=bytes([167,31])+bytes(range(14));H.put(m,SmFreezePalettePending=128)
  packet=address(b,'SmFreezePalettePacket');m[packet:packet+7]=[63,21,3,16,48,54,0]
  image=bytes(m.ram[2]);states=bytes(m[packet:packet+7]);H.invoke(m,'WfP1Retire')
  assert bytes(m.ram[2])==image and bytes(m[packet:packet+7])==states and H.get(m,'SmFreezePalettePending')==128
  q['checks']['actual_selected_publication_and_foreign_lease']=dict(passed=True,publication=publication)
  # Real vector cuts at epoch consume, packet construction/copy, queue
  # retirement and final native publication; actual foreground owns lag.
  m,_=clone(base,G.NesMPU(memory=base));shots=[];seen=set()
  names=['WfP1Early','WfP1LateCore','WfP1MakePacket','WfP1PublishPacket','WfP1Retire','WfP1NativeRestore','WfP1CancelQueuedOwn','FwMuxNativeSelect','WfRuntimeReturnOriginal']
  points={address(b,n):n for n in names}
  def capture(mem,cpu,step):
   key=(cpu.pc,mem.rawtags[1],mem.rawtags[2]);name=points.get(cpu.pc)
   if name and name not in seen:seen.add(name);shots.append((name,*clone(mem,cpu)))
  H.put(m,NmiDisable=255);draw(m,capture);H.invoke(m,'WfP1Retire',hook=capture)
  for name,s,c in shots:
   for kind in ['NMI','IRQ']:
    if kind=='IRQ'and c.p&4:continue
    z,d=clone(s,c);low=interrupt(z,d,kind);H.finish(z,d)
    assert H.get(z,'CurrentBankC')==z.rawtags[2]
    q['vectors'].append(dict(entry=name,kind=kind,SP=c.sp,minimum_SP=low))
  assert q['vectors']
  q.update(passed=True,candidate=sha(J/'candidate.nes'),minimum_ISR_SP=min(r['minimum_SP']for r in q['vectors']))
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(G.__file__),Path(C.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json',R/'build/wwf-hogan-retirement-probe-v1/controls.json']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in['passed','candidate','minimum_ISR_SP','error']}))
if __name__=='__main__':main()
