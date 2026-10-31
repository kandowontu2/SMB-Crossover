"""Real a126 IRQ/NMI vectors interrupt the new imported-scratch Thomas source.

Only the isolated code/state arena is fixture-preloaded; the host ROM and its
vectors, mapper/audio/protocol instructions are unchanged and never intercepted.
"""
from pathlib import Path
import copy,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import thomas_original_cpu_1031_v1 as T
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from arthur_cache_host_controls_v1 import OverlayMemory
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import address
P=R/'build/thomas-host-scratch-1031-v1';J=R/'build/contra-force-world-roles-1031-v2/joint'
O=R/'build/thomas-actual-host-vectors-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

class HostMemory(OverlayMemory):
 def observe(self,syms):
  self.pc=-1;self.logical=bytearray(self.ram[2][:16]);self.working=bytearray(16);self.source_map={};self.inverse={}
  for prefix in ['Th_','ThHealth_','ThGeom_','ThCold_','ThController_','ThTimers_','ThFrameReset_','ThData_']:
   self.inverse.update({v:int(n[len(prefix):],16)for n,v in syms.items()if n.startswith(prefix)})
  self.source_map=dict(self.inverse);self.commit=syms['ThomasC2Return']+4;self.borrow=syms['ThomasC2Borrow'];self.source_writes=[]
 def __setitem__(self,key,v):
  if isinstance(key,int) and hasattr(self,'source_map'):
   if 0xc000<=key<0xc010 and self.rawtags[2]==2:
    self.logical[key-0xc000]=self.working[key-0xc000]if self.pc==self.commit else v&255
   if 3<=key<11 and self.rawtags[1]==3 and self.pc in self.source_map:
    i=key-3;native=self.source_map[self.pc];self.working[i]=v&255
    if native in [0xa842,0xa915,0xa923]:
     pointer=self[key-1]|((v&255)<<8);assert pointer in self.inverse,(hex(native),hex(pointer))
     self.working[i-1:i+1]=self.inverse[pointer].to_bytes(2,'little')
    elif native in [0x84fc,0x8505,0x850d]:self.working[i]=(v-0xc0)&255
   if self.rawtags[1]==3 and self.pc in self.source_map and key<256:
    assert 3<=key<11,('source escaped actualR0..R7',hex(self.pc),hex(key))
    self.source_writes.append((self.pc,key,v&255))
  super().__setitem__(key,v)

class CPU(NesMPU):
 def step(self):
  m=self.memory;m.pc=self.pc
  if m.rawtags[1]==3 and self.pc==m.borrow:m.working[:]=m.logical
  return super().step()

def main():
 assert not O.exists();O.mkdir(parents=True)
 proof=dict(passed=False,native=False,host_ROM_unchanged=True,arena_preloaded=True)
 try:
  stage=json.loads((P/'source-stage.json').read_text());assert sha(J/'candidate.nes')==stage['host_sha256']
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  b=H.C.qualified(J/'candidate.nes');s=T.labels(P/'component.lbl');image=(P/'component.bin').read_bytes()
  def make(lag=255,pause=0,audio=0):
   m=L.make(b,SelectedCharacter=10,FmAlts=64,GamePauseStatus=pause,NmiDisable=lag,GuestAudioCharacter=audio,FamilyMainCommit=1)
   m.__class__=HostMemory;m.ram[3][:]=image;m.ram[2][:]=bytes(8192)
   m.raw_page(1,3);m.raw_page(2,2);H.put(m,CurrentBank=3,CurrentBankC=2)
   for i in range(11):m[i]=(i*23+41)&255
   m.observe(s);m.writes.clear();m.ram_writes.clear();return m
  def run(m,name,a=0,x=1,y=0,p=0x30,hook=None):
   c=CPU(memory=m,pc=s[name]);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,0xa9;c.stPushWord(0x5aff);pcs=[];low=c.sp
   for step in range(40000):
    if c.pc==0x5b00:break
    if hook:hook(m,c,step)
    pcs.append(c.pc);low=min(low,c.sp);c.step()
   else:raise AssertionError(('bounded Thomas',name,hex(c.pc)))
   assert(c.a,c.x,c.y,c.p,c.sp)==(a,x,y,p,0xa9),(name,'actual callerAXYP')
   return pcs,low
  def state(m):return bytes(m.ram[2]),bytes(m.ram[3]),bytes(m[3:11]),m.rawtags[:],H.get(m,'CurrentBank'),H.get(m,'CurrentBankC'),bytes(m[0x15a:0x17b])
  def fork(m):
   z=L.fork(m);z.__class__=HostMemory;return z
  rows=[];minimum=255
  for operation in ['cold','frame']:
   origin=make()
   if operation=='frame':run(origin,'ThomasC2ColdInit')
   entry='ThomasC2ColdInit'if operation=='cold'else'ThomasC2AcceptedFrame';args=dict(a=0 if operation=='cold'else 72,y=1)
   baseline=fork(origin);pcs,_=run(baseline,entry,**args)
   # First and last instructions, every scope instruction, actual pointer
   # publication sites, plus a bounded spread of actual original actor PCs.
   first={}
   for i,pc in enumerate(pcs):first.setdefault(pc,i)
   cuts=set([0,len(pcs)-2]);unique=list(first.values());cuts.update(unique[::max(1,len(unique)//28)])
   for pc,i in first.items():
    if s['ThomasC2Borrow']<=pc<s['ThomasC2Return']+20 or origin.source_map.get(pc)in[0xa842,0xa915,0xa923,0x84fc,0x8505,0x850d]:cuts.add(i)
   for lag,pause,kind in itertools.product([0,255],[0,1],['NMI','IRQ']):
    for cut in sorted(cuts):
     m=fork(origin);H.put(m,NmiDisable=lag,GamePauseStatus=pause)
     snapshots=[]
     def hook(mem,c,step):
      if step==cut:snapshots.append(V.interrupt(mem,c,kind))
     _,low=run(m,entry,hook=hook,**args);minimum=min(minimum,low)
     assert len(snapshots)==1
     assert state(m)==state(baseline),(operation,lag,pause,kind,cut,'resumed owner differs')
     rows.append(dict(operation=operation,lag=lag,pause=pause,cut=cut,PC=f'{pcs[cut]:04X}',**snapshots[0]))
  proof.update(passed=True,actual_vectors=len(rows),minimum_foreground_SP=minimum,
   actual_scratch=list(range(3,11)),source_never_touches_native_NmiR0_R1_R2=True,
   real_outer_NMI_IRQ_vectors=True,real_audio_mapper_protocol_not_intercepted=True,
   caller_AXYP_SP=True,SMC33_stack_maps_R0_through_R7_exact=True,rows=rows,
   limits=['Explicit isolated RAM3/C2 preload, not a cold loader or installed hook','No native raster/cadence or playable readiness claim'])
 except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc())
 proof['bindings']={str(p):sha(p)for p in [Path(__file__),Path(L.__file__),Path(H.__file__),Path(V.__file__),R/'tools/audit/verify_native_relocation.py',P/'source-stage.json',P/'component.bin',P/'component.lbl',J/'candidate.nes',J/'candidate.dbg']}
 dump(O/'controls.json',proof);print(json.dumps({k:v for k,v in proof.items()if k not in['rows','bindings','traceback']}));assert proof['passed'],proof.get('error')
if __name__=='__main__':main()
