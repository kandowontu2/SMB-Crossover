"""Actual original-driver/compiled host callback comparison; no common NMI hook."""
from pathlib import Path
import collections,hashlib,itertools,json
import smb2_roster_audio_controls_v1 as A
import smb2_roster_audio_leases_v1 as L
import prepare_smb2_roster_audio_host_v8 as B
R,O,bind=B.R,B.O,B.bind
AREA=[1,4,4,8,32,4,16,128]
EVENT=[8,16,4,2,16,32,0,128]
PAIRED=[]

class Pair:
 def __init__(self,b):
  self.b=b;self.ref=A.Campaign(b);self.actual=A.Campaign(b);self.m=self.actual.new;self.cache=[0]*8;self.rows=[]
  for m in[self.ref.new,self.m]:
   for n,v in dict(SelectedCharacter=25,GuestAudioCharacter=25,OperMode=1,AreaType=1).items():m[A.address(b,n)]=v
   m[0x5115]=m[A.address(b,'CurrentBank')]
   m[0x5116]=m[A.address(b,'CurrentBankC')]
  L.invoke(self.m,b,'S2HostAcquireNmi')
 def put(self,**values):
  for n,v in values.items():
   for m in[self.ref.new,self.m]:m[A.address(self.b,n)]=v
 def tick(self,area=0,event=0,effect=None,flags=0x30,collect=False):
  b=self.b;m=self.m;r=self.ref.new;at=lambda n:A.address(b,n);get=lambda n:m[at(n)]
  self.put(AreaMusicQueue=area,EventMusicQueue=event)
  if effect:
   for i,v in effect.items():m[at({1:'S2DpcmRequest',2:'S2Sfx1',4:'S2Sfx2'}[i])]=v;self.ref.queue(i,v)
  if not m[0x5fb6]&1:
   if not self.cache[7]or[self.cache[0],self.cache[1]]!=[get('S2World'),get('S2Area')]:
    self.cache[3]=[4,1,4,8][get('AreaType')&3];self.ref.queue(0,self.cache[3])
   self.cache[0:3]=[get('S2World'),get('S2Area'),get('S2Life')]
   self.cache[4:6]=[get('OperMode_Task'),get('GameEngineSubroutine')]
   star=int(get('StarInvincibleTimer')!=0)
   if star and(not self.cache[6]or get('S2World')!=r[at('S2HostWorld')]or get('S2Area')!=r[at('S2HostScene')]):self.ref.queue(0,16)
   elif not star and self.cache[6]:self.ref.queue(0,self.cache[3])
   self.cache[6:8]=[star,1]
  if area and not event:     # actual native MusicHandler admits event FIRST.
   i=(area&-area).bit_length()-1
   if i==7:self.ref.queue(3,128);self.ref.queue(0,0)
   else:
    self.ref.queue(0,AREA[i])
    if i<6:self.cache[3]=AREA[i]
  if event:
   v=EVENT[(event&-event).bit_length()-1]
   if v:self.ref.queue(3,v)
  self.ref.pause(0x41 if get('GamePauseStatus')&1 else 0)
  old,direct=self.ref.tick(flags=flags,sp=0xc0)
  list.__setitem__(m,slice(0xbb,0xc7),bytes(r[0xbb:0xc7]))
  initial=L.snapshot(m);beforeclock=get('S2Clock');smc=bytes(m[0x15a:0x17b]);maps=m.banks.copy()
  c=A.call(m,at('S2HostNmiTick'),a=0x55,x=3,y=7,p=flags,sp=0xc0)
  assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(0x55,3,7,flags&0xcf,0xc0),'host full AXYP/SP'
  assert get('S2Clock')==(beforeclock+1)&255,'exactly one genuine compiled source clock'
  assert m.events==r.events and m.fetches==r.fetches,('literal ordered source APU/full fetch',area,event,m.events,r.events)
  assert bytes(m[at('S2AudioState'):at('S2AudioState')+52])==bytes(r[at('S2AudioState'):at('S2AudioState')+52]),'all52 source RAM'
  assert bytes(m[at('S2AudioZpState'):at('S2AudioZpState')+12])==bytes(r[at('S2AudioZpState'):at('S2AudioZpState')+12]),'all12 source ZP/pointer'
  assert bytes(m[at('S2HostWorld'):at('S2HostWorld')+8])==bytes(self.cache),('context',self.cache,bytes(m[at('S2HostWorld'):at('S2HostWorld')+8]).hex())
  assert bytes(m[0x15a:0x17b])==smc and m.banks[:3]==maps[:3]and m.banks[3]==r.banks[3],'all33SMC/A/C restored; genuine source-selected E lease'
  assert m[0x4011]==0x49 and bytes(m[0xbb:0xc7])==bytes(r[0xbb:0xc7])
  # Account only intentional extra publication/cache outputs, then compare
  # ALL zero page and non-stack application RAM to the direct source oracle.
  for n in['S2Clock','GuestNativeEnable','AreaMusicQueue','EventMusicQueue']:
   r[at(n)]=m[at(n)]
  for i,v in enumerate(self.cache):r[at('S2HostWorld')+i]=v
  assert L.live(m)==L.live(r),'complete non-stack RAM/maps versus source oracle'
  forbidden=set(range(at('RgAudioZp'),at('RgAudioCpuZp')))
  assert not forbidden.intersection(m.reads),'never borrow live RgAudioZp'
  row=dict(original=old.processorCycles,direct=direct.processorCycles,host=c.processorCycles,added=c.processorCycles-direct.processorCycles,min_SP=c.minimum_SP,area=area,event=event)
  self.rows.append(row)
  PAIRED.append(row)
  return initial,c

def main():
 build=json.loads((O/'build-proof.json').read_text());b=A.scoped_load(O/'candidate.nes');assert bind(O/'candidate.nes')==build['candidate']
 rows=[];q=Pair(b)
 try:
  q.tick(area=128)
  q=Pair(b);q.tick();q.put(StarInvincibleTimer=10);q.tick();q.put(S2Area=33);q.tick()
 except AssertionError as e:
  path=O/'first-control-negative.json'
  if not path.exists():path.write_text(json.dumps(dict(candidate=build['candidate'],error=str(e),tool=bind(__file__),classification='unqualified draft control failure; retained, not passing evidence'),indent=2)+'\n')
  raise
 for family in ['area','event']:
  for value in range(256):
   q=Pair(b);q.tick(**{family:value});rows+=q.rows
 q=Pair(b);q.tick(area=1)
 try:q.tick(area=128,event=64)
 except AssertionError as e:
  path=O/'event-priority-draft-negative.json'
  if not path.exists():path.write_text(json.dumps(dict(candidate=build['candidate'],error=str(e),tool=bind(__file__),classification='native event-priority defect in unqualified draft adapter; retained'),indent=2)+'\n')
  raise
 for area,event in itertools.product([1,2,4,8,16,32,64,128,255],repeat=2):
  q=Pair(b);q.tick(area=area,event=event)
 # Exact original song/DPCM/effect coexistence, source pause and context-busy,
 # life gain, actual new scene, Star entrance/exit. No skipped source tick.
 q=Pair(b);q.tick(area=1)
 for i in range(144):
  q.put(GamePauseStatus=int(24<=i<48),StarInvincibleTimer=40 if 60<=i<90 else 0)
  if i==72:q.put(S2Area=33)
  if i==96:q.put(S2Life=3)
  q.m[0x5fb6]=q.ref.new[0x5fb6]=1 if 100<=i<108 else 0
  q.tick(effect={1:1<<(i%8),2:8,4:1}if i%16==0 else None,flags=[0x30,0x39,0x70,0xff][i%4])
 rows+=q.rows
 # Foreign raw / uncommitted owner / SoundTest / title callbacks do not touch
 # private state, queues, source clocks, hardware or any live application RAM.
 blank=L.snapshot(Pair(b).m);foreign=0
 for raw in range(256):
  if raw==25:continue
  for api in ['S2HostNmiTick','S2HostAcquireNmi']:
   m=L.restore(b,blank);m[A.address(b,'SelectedCharacter')]=raw;pre=L.live(m);m.reads=[]
   L.invoke(m,b,api,a=0x41,x=7,y=91,p=0x79,sp=0xc0);assert L.live(m)==pre
   assert not set(range(A.address(b,'RgAudioRam'),A.address(b,'RgAudioRam')+77)).intersection(m.reads)
   foreign+=1
 for field,v in [('GuestAudioCharacter',9),('RgAudioCharacter',9),('CrossoverMenuState',8),('OperMode',0)]:
  m=L.restore(b,blank);m[A.address(b,field)]=v;pre=L.live(m);L.invoke(m,b,'S2HostNmiTick',p=0x79);assert L.live(m)==pre
 # Old-owner retire and status endpoints intentionally admit owner25 after
 # raw identity changes; actual busy/complete status is modeled input only.
 lifecycle=[]
 for request in [1,2,4,8,16,32,64,128]:
  q=Pair(b);q.m[0x5fb6]=q.ref.new[0x5fb6]=1
  q.tick(effect={1:request});m=q.m;active=m[A.address(b,'S2AudioActiveBank')];assert active in[119,120],(request,m.events)
  m[A.address(b,'SelectedCharacter')]=0
  for busy in [True,False]:
   snap=L.snapshot(m);z=L.restore(b,snap)
   if not busy:list.__setitem__(z,0x4015,z[0x4015]&15)
   for p in [0x30,0x79,0xff]:
    w=L.restore(b,L.snapshot(z));c=A.call(w,A.address(b,'S2HostDmcStatus'),a=15,x=37,y=91,p=p,sp=0xc0)
    assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(31 if busy else 15,37,91,p&0xcf,0xc0)
    assert w.banks[3]==(active if busy else 127)and not w.events and w[0x4011]==0x49
  L.invoke(m,b,'S2HostRetireNmi',a=0x91,x=37,y=91,p=0x79,sp=0xc0)
  assert m.banks[3]==127 and m[A.address(b,'RgAudioCharacter')]==255 and m.events==[(0x4015,15)]and m[0x4011]==0x49
  lifecycle.append(dict(request=request,active_E=active,busy_completion_retire=True))
 # Reached IRQ seams in the actual adapter/clock/borrow/original native body.
 q=Pair(b);initial,_=q.tick(effect={1:128,2:8,4:1});sites=sorted(set(q.m.execs));irqs=[]
 names=['S2HostNmiTick','S2HostContext','S2HostCues','S2AudioBorrow','S2AudioNativeEntry','S2AudioRelease']
 for name in names:
  site=(A.address(b,name),74);assert site in sites,(name,'genuine seam not reached')
  m=L.restore(b,initial);m[0x5204]=128
  c=A.call(m,A.address(b,'S2HostNmiTick'),a=0x55,x=3,y=7,p=0x30,sp=0xc0,inject=site)
  assert m.events==q.m.events and m.fetches==q.m.fetches
  irqs.append(dict(entry=name,physical_bank=74,PC=hex(site[0]),min_SP=c.minimum_SP,cycles=c.processorCycles))
 # All flag bytes including decimal: direct APIs preserve the complete public
 # flags contract; no forced carry/return mask conceals scratch differences.
 flags=[]
 for p in range(256):
  q=Pair(b);_,c=q.tick(flags=p);flags.append(c.minimum_SP)
 # Genuine incoming farcall, all actual same-final E aliases and interrupted
 # arbitrary A/C mappings. Only real outer caller transport is changed.
 far=[]
 for request in [0,1,8]:
  q=Pair(b);q.m[0x5fb6]=q.ref.new[0x5fb6]=1
  if request:q.tick(effect={1:request})
  initial,_=q.tick();want=L.snapshot(q.m)
  for ba,bc in [(4,4),(62,80),(99,93),(118,117)]:
   m=L.restore(b,initial);m.page(1,ba);m.page(2,bc)
   for n,v in [('CurrentBank',ba|128),('CurrentBankC',bc|128),('SafecallA_SMC',None)]:
    if v is not None:m[A.address(b,n)]=v
   target=A.address(b,'S2HostNmiTick')
   for n,v in [('SafecallA_SMC',0x55),('FarcallJmpTarget_SMC',target&255)]:m[A.address(b,n)+1]=v
   m[A.address(b,'FarcallJmpTarget_SMC')+2]=target>>8
   c=A.call(m,A.address(b,'FarCallCommon'),a=202,x=3,y=7,p=0x30,sp=0xc0,inject=(A.address(b,'S2AudioBorrow'),74))
   assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(0x55,3,7,0,0xc0),'genuine farcall recomputes NZ from returned A'
   assert m.banks[:3]==[126,ba,bc]and m.banks[3]==want[1][3]
   expected=bytearray(want[0])
   for n,v in [('CurrentBank',ba|128),('CurrentBankC',bc|128),('S2AudioSavedC',bc|128)]:expected[A.address(b,n)]=v
   expected[0x5115]=ba|128;expected[0x5116]=bc|128
   for n,v in [('SafecallA_SMC',0x55),('FarcallJmpTarget_SMC',target&255),('NextBank_SMC',202),('SafereturnA_SMC',0x55)]:expected[A.address(b,n)+1]=v
   expected[A.address(b,'FarcallJmpTarget_SMC')+2]=target>>8
   for i in range(0x8000):
    if 0x100<=i<0x200:continue
    assert m[i]==expected[i]or i in[0x2005,0x2006,0x5128],('farcall fullRAM',ba,bc,hex(i),m[i],expected[i])
   assert bytes(m[0x15a:0x17b])==bytes(expected[0x15a:0x17b])and bytes(m[0x100:0x15a])==bytes(expected[0x100:0x15a])
   assert m.events==q.m.events and m.fetches==q.m.fetches and c.minimum_SP>=0x7b
   far.append(dict(A=ba,C=bc,E=m.banks[3],cycles=c.processorCycles,min_SP=c.minimum_SP))
 # Busy foreign acquisition is a real decline, with explicit owner readback.
 m=L.restore(b,blank);m[A.address(b,'RgAudioCharacter')]=9;list.__setitem__(m,0x4015,31)
 pre=L.live(m);L.invoke(m,b,'S2HostAcquireNmi');assert L.live(m)==pre
 for owner in range(256):
  if owner==25:continue
  for api in ['S2HostDmcStatus','S2HostRetireNmi']:
   m=L.restore(b,blank);m[A.address(b,'RgAudioCharacter')]=owner;pre=L.live(m);m.reads=[]
   L.invoke(m,b,api,a=0x91,x=37,y=91,p=0x79,sp=0xc0);assert L.live(m)==pre
   assert not set(range(A.address(b,'RgAudioRam'),A.address(b,'RgAudioRam')+77)).intersection(m.reads)
 rows=PAIRED
 endpoints={n:dict(PC=hex(A.address(b,n)),bank=74,bytes=int(b['syms'][n]['size'],0))for n in ['S2HostAcquireNmi','S2HostNmiTick','S2HostRetireNmi','S2HostDmcStatus']}
 proof=dict(passed=True,native=False,source_CPU_only=True,candidate=build['candidate'],tool=bind(__file__),endpoints=endpoints,adapter_bytes=A.address(b,'S2HostAudioEnd')-A.address(b,'S2HostAudioBegin'),spare=0xc000-A.address(b,'S2HostAudioEnd'),paired_calls=len(rows),costs=dict(original=[min(x['original']for x in rows),max(x['original']for x in rows)],direct=[min(x['direct']for x in rows),max(x['direct']for x in rows)],host=[min(x['host']for x in rows),max(x['host']for x in rows)],added=[min(x['added']for x in rows),max(x['added']for x in rows)],min_SP=min([x['min_SP']for x in rows]+flags)),foreign_calls=foreign,old_foreign_status_retire_calls=510,foreign_DMC_busy_acquire_declines=True,lifecycle=lifecycle,actual_IRQ=irqs,genuine_farcall_IRQ=far,all_byte_native_music_priority=True,all_flag_bytes=256,common_NMI_hook_installed=False,mixer_installed=False,limits='Actual original-driver differential/image/store/fetch and actual source clock endpoint; no real NMI scheduler/analogAPU/DMC-steal/PPU/cadence/native/audio-listening acceptance. Common owner acquisition, pause/world mixer and owned DMC-status route must be composed before use.')
 (O/'host-controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(proof))
if __name__=='__main__':main()
