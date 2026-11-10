"""Private actual host cache CPU/mapper/PPU model. No native cadence claim."""
from pathlib import Path
import argparse,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import arthur_actual_host_controls_v1 as A
import arthur_draw_cache_controls_v1 as D
import arthur_draw_cache_plan_v1 as P
import link_pit_rygar_sophia_audit_cpu as ArenaModule
from check_tmnt_render_oa import Memory,address,location
O=R/'build/arthur-host-cache-v1';OLD=R/'build/arthur-host-integration-v2'

class OverlayMemory(Memory):
 def __init__(self,b):
  self.rawtags=[254,215,216,255];self.ram=[bytearray(8192)for _ in range(4)];self.ram_writes=[]
  self.chr_latches=[0]*12;self.upper=0;self.lastset=0;self.ppu_addr=0;self.toggle=0;self.buffer=0;self.ppuctrl=0;self.vram=bytearray(16384);self.ppu_reads=0;self.ppu_log=[];self.corrupt_at=None
  self.protection=[2,1];self.blocked=[]
  super().__init__(b)
 def page(self,win,bank):self.raw_page(win,bank|128)
 def raw_page(self,win,raw):
  self.rawtags[win]=raw;self.banks[win]=raw&127
  if raw&128:
   bank=raw&127;list.__setitem__(self,slice(0x8000+win*8192,0xa000+win*8192),self.bundle['raw'][16+bank*8192:16+(bank+1)*8192])
 def __getitem__(self,i):
  if isinstance(i,slice):return[self[k]for k in range(*i.indices(65536))]
  if i>=0x8000:
   raw=self.rawtags[(i-0x8000)//8192]
   if not raw&128:
    v=self.ram[raw&3][i&8191]
    return v^1 if self.corrupt_at==(raw&3,i&8191)else v
  if i==0x2002:self.toggle=0;return 0
  if i==0x2007:
   self.ppu_reads+=1;value=self.buffer;at=self.ppu_addr
   if at<8192:
    slot=at//1024;slot=(8+slot%4)if self.lastset else slot
    physical=self.chr_latches[slot];pos=1048592+1024*physical+(at&1023)
    actual=self.bundle['raw'][pos]
   else:actual=self.vram[at]
   self.buffer=actual;self.ppu_addr=(at+(32 if self.ppuctrl&4 else 1))&16383
   return actual if at>=0x3f00 else value
  return list.__getitem__(self,i)
 def __setitem__(self,i,v):
  if isinstance(i,slice):
   for k,z in zip(range(*i.indices(65536)),v):self[k]=z
   return
  v&=255
  if i>=0x8000:
   raw=self.rawtags[(i-0x8000)//8192];assert not raw&128,('write to actual ROM',hex(i),raw,v)
   self.writes.append((i,v));self.ram_writes.append((raw&3,i&8191,v))
   if self.protection==[2,1]:self.ram[raw&3][i&8191]=v
   else:self.blocked.append((raw&3,i&8191,v))
   return
  self.writes.append((i,v));list.__setitem__(self,i,v)
  if 0x5114<=i<=0x5117:self.raw_page(i-0x5114,v)
  elif i in[0x5102,0x5103]:self.protection[i-0x5102]=v&3
  elif i==0x5130:self.upper=v&3
  elif 0x5120<=i<=0x512b:self.chr_latches[i-0x5120]=v+256*self.upper;self.lastset=int(i>=0x5128)
  elif i==0x2000:self.ppuctrl=v
  elif i==0x2006:
   self.ppu_log.append((i,v));self.ppu_addr=((self.ppu_addr&0x3f00)|v)if self.toggle else(v&63)<<8;self.toggle^=1
  elif i==0x2005:self.ppu_log.append((i,v));self.toggle^=1
  elif i==0x2007:
   self.ppu_log.append((i,v));self.vram[self.ppu_addr]=v;self.ppu_addr=(self.ppu_addr+(32 if self.ppuctrl&4 else 1))&16383

ArenaModule.Memory=OverlayMemory
def ready(b):
 q=A.setup(b);q.put(OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,NmiDisable=255)
 c,tr,mn=A.owned(q,'ArCacheEnsure');assert c.p&1,('cache load failed',c.a,c.p,q.get('ArDrawPtr'),q.get('ArDrawPtr',1))
 return q,c,tr,mn

def load_controls(b):
 q,c,tr,mn=ready(b);m=q.m;old=A.scoped_load(OLD/'candidate.nes');expected=D.expected_cache(old)
 code=b['raw'][location(b,'ArCacheEmit'):location(b,'ArCacheExecEnd')]
 sig=bytes.fromhex(json.loads((O/'cache-final-link-proof.json').read_text())['signature'])
 assert bytes(m.ram[2][:6130])==expected,('actual forced-blank cache mismatch',next((i for i,(x,y)in enumerate(zip(m.ram[2],expected))if x!=y),None))
 assert bytes(m.ram[2][0x1800:0x1800+len(code)])==code
 assert bytes(m.ram[2][0x1fe0:0x1ff0])==sig
 assert m.ram_writes[0]==(2,0x1fe0,0)and m.ram_writes[-1]==(2,0x1fe0,167),('shared cookie invalidated first, published last')
 assert all(z[0]==2 for z in m.ram_writes)
 assert not any(a in[0x5102,0x5103,0x5113]for a,v in m.writes)
 assert q.get('ArHostReady')==167 and q.get('ArHostOldPage')==0
 A.exact_maps(q);assert m.rawtags[1]==q.get('CurrentBank')and m.rawtags[2]==q.get('CurrentBankC')
 assert m.ppuctrl==160 and m.toggle==0 and m.ppu_log[-2:]==[(0x2005,0),(0x2005,0)]
 reads=m.ppu_reads;before=bytes(m.ram[2]);cw,_,_=A.owned(q,'ArCacheEnsure');assert cw.p&1 and reads==m.ppu_reads and bytes(m.ram[2])==before
 # Every identity/fingerprint byte must prevent stale/foreign warm reuse.
 poisoned=[]
 for i in range(16):
  m.ram[2][0x1fe0+i]^=1;q.put(DisableScreenFlag=0,Mirror_PPUMASK=30);rw=len(m.ram_writes);nr=m.ppu_reads
  bad,_,_=A.owned(q,'ArCacheEnsure');assert not bad.p&1 and len(m.ram_writes)==rw and nr==m.ppu_reads
  m.ram[2][0x1fe0+i]^=1;poisoned.append(i)
 # Own retirement leaves Quick's already-published identity intact.
 m.ram[2][0x1fe1]=9;A.owned(q,'ArCacheRetire');assert m.ram[2][0x1fe0]==167
 m.ram[2][0x1fe1]=32;A.owned(q,'ArCacheRetire');assert m.ram[2][0x1fe0]==0
 failures=[]
 for name,values in [('active',dict(DisableScreenFlag=0)),('mask',dict(Mirror_PPUMASK=30)),('NMI',dict(NmiDisable=0)),('title',dict(OperMode=0))]:
  z=A.setup(b)
  base=dict(OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255);base.update(values);z.put(**base)
  out,_,_=A.owned(z,'ArCacheEnsure');assert not out.p&1 and not z.m.ram_writes and z.m.ppu_reads==0;failures.append(name)
 for name,locked,corruption in [('protection',True,None),('readback',False,(2,0x1bc))]:
  z=A.setup(b);z.put(OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255);z.m.protection=[0,0]if locked else[2,1];z.m.corrupt_at=corruption
  out,_,_=A.owned(z,'ArCacheEnsure');assert not out.p&1 and z.m.ram[2][0x1fe0]!=167 and z.get('ArHostReady')==0;assert z.m.protection==([0,0]if locked else[2,1]);failures.append(name)
 return dict(actual_loader_cycles=c.processorCycles,actual_warm_check_cycles=cw.processorCycles,minimum_SP=mn,buffered_reads=reads,cache_bytes=6130,code_bytes=len(code),cookie_all16bytes_guarded=poisoned,negative_cases=failures,validity_first_clear_last_publish=True,shared_RAM0_protection_unchanged=True)

def render_controls(b):
 old=A.scoped_load(OLD/'candidate.nes');keys=[k for k in range(74)if P.expand(old,0,k)is not None];q,_,_,_=ready(b)
 rows=[]
 cases=[(m,k,104,200,0,0,0)for m in range(3)for k in keys]
 edges=[(0,0,0,0,0),(0,16,0,240,4),(255,239,0,248,252),(255,208,-1,4,4),(0,208,1,0,0),(7,1,0,252,0),(248,200,0,244,252),(104,200,0,255,4)]
 cases +=[(m,k,*edge)for m in range(3)for k in[0,1,16,32,53,54,58,63,73]for edge in edges]
 cases +=[(m,k,104,200,0,p,r)for m in range(3)for k in keys for p,r in[(208,4),(208,252)]]
 for mode,key,x,y,high,prefix,rotation in cases:
  pose=key if key<54 else P.byte(old,'ArPalShotPose',key-54);slot=0 if key<54 else 1
  pair=[]
  for v,z in[(old,A.setup(old)),(b,q)]:
   z.put(ArHostOldPage=mode,OperMode=1,GameEngineSubroutine=8,CurrentOAMOffset=prefix,GuestOamRotationActive=int(rotation!=0),RgOamRotation=rotation)
   for i in range(4):z.set('ArR_04F0',128 if i==slot else 0,i)
   for n,value in [('ArR_0522',pose),('ArR_05AF',x),('ArR_0583',(1+high)&255),('ArR_0599',y),('ArR_056D',0)]:z.set(n,value,slot)
   z.put(ArR_0064=0,ArR_0065=1);z.m[512:768]=[248,0,0,0]*64
   writes=len(getattr(z.m,'ram_writes',[]));cpu,tr,mn=A.owned(z,'ArHostDraw')
   assert writes==len(getattr(z.m,'ram_writes',[])),('no runtime cache/code writes',mode,key)
   pair.append((bytes(z.m[512:768]),z.get('CurrentOAMOffset'),z.get('SmChrBank'),cpu.processorCycles,mn))
  assert pair[0][:2]==pair[1][:2],('actual complete Draw ordered OAM/cursor',mode,key,x,y,high,prefix,rotation)
  if slot==0:assert pair[0][2]==pair[1][2]
  rows.append([mode,key,x,y,high,prefix,rotation,pair[0][3],pair[1][3],pair[1][4]])
 return dict(actual_complete_Draw_cases=len(rows),rows=rows,new_cycles=[min(z[8]for z in rows),max(z[8]for z in rows)],scope='Actual complete mapper/slot/common/body publisher wrappers, all201source views plus clipping/priority/capacity/rotation. Ordered OAM exact and unchanged source CHR/palette establishes same pixels, conditional on later native publisher commits; no video cadence claim.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--only',default='loader,render');a=ap.parse_args();assert not a.output.exists()
 b=A.scoped_load(O/'candidate.nes');d=dict(passed=False,native_run=False,checks={})
 try:
  for name in a.only.split(','):d['checks'][name]=(load_controls if name=='loader'else render_controls)(b)
  d['passed']=True
 except Exception as e:d.update(failure=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):A.sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'cache-final-link-proof.json']}
 a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(passed=d['passed'],checks=list(d['checks']),failure=d.get('failure'))));assert d['passed']
if __name__=='__main__':main()
