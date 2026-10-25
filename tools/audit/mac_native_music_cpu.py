"""Compare linked Mac native music to original calls, then exercise dispatch.

This is a CPU/source proof, not an emulator audio, NMI or lag qualification.
Golden files come from the independently executed original NSF source probe.
"""
from pathlib import Path
import argparse,gzip,hashlib,itertools,json
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified,execute,result
from verify_native_relocation import NesMPU

class MusicMemory(Memory):
 def __init__(self,b):
  super().__init__(b);self.events=[];self.pc=None;self.lowwrites=[]
  self.image=address(b,'GuestNativeApu')
 def __setitem__(self,at,v):
  if isinstance(at,int)and hasattr(self,'image'):
   if self.image<=at<self.image+16:self.events.append((0x4000+at-self.image,v))
   if 0x4000<=at<=0x4017:self.events.append((at,v))
   if at<0x8000:self.lowwrites.append((self.pc,at,v))
  super().__setitem__(at,v)

class Run:
 def __init__(self,b):
  self.b=b;self.m=MusicMemory(b);self.c=NesMPU(memory=self.m);self.depth=255
 def set(self,name,value,index=0):self.m[address(self.b,name)+index]=value&255
 def get(self,name,index=0):return self.m[address(self.b,name)+index]
 def call(self,name,a=0,x=0,y=0,p=0x24):
  pc=address(self.b,name)if isinstance(name,str)else name
  if pc>=0xa000 and pc<0xc000:
   self.m.page(1,123);self.set('CurrentBank',251)
  self.c.pc=pc;self.c.a=a;self.c.x=x;self.c.y=y;self.c.p=p;self.c.sp=253
  self.m[510]=255;self.m[511]=126;self.m.events=[];self.m.lowwrites=[];self.m.writes=[]
  start=self.c.processorCycles;self.depth=255
  for _ in range(100000):
   if self.c.pc==0x7f00:break
   self.depth=min(self.depth,self.c.sp);self.m.pc=self.c.pc;self.c.step()
  else:raise AssertionError(('Timeout',name,hex(self.c.pc),self.m.banks))
  self.m.pc=None;assert self.c.sp==255
  return self.c.processorCycles-start

def canonical_zp(z):
 z=list(z);pointer=z[8]+256*z[9]
 if 0xa000<=pointer<0xc000:
  pointer-=8192;z[8]=pointer&255;z[9]=pointer>>8
 return z

def driver(b,gold,calls,out):
 rows=[]
 for song in [1,2,4,6,7,9,20,22,23]:
  expected=json.loads(gzip.decompress((gold/f'song-{song:02d}.json.gz').read_bytes()))
  r=Run(b);direct='LmNativeDirectZp'in b['syms'];r.m[0xf0:0x100]=[(71+19*i)&255 for i in range(16)]if direct else[0]*16
  if direct:r.m[248]=r.m[249]=0
  foreground=list(r.m[240:256]);ram=address(b,'LmNativeRam');r.m[ram:ram+288]=[0]*288
  allowed=set(range(256,512))|set(range(ram,ram+48))|set(range(address(b,'LmNativeZp'),address(b,'LmNativeZp')+16))|{248,249,0x4015,0x4017}
  for name in ['GuestNativeApu','GuestNativeDirty']:allowed.update(range(address(b,name),address(b,name)+16))
  allowed.update(address(b,name)for name in ['GuestNativeEnable','GuestCombinedEnable'])
  costs=[];n=0;digest=hashlib.sha256();peaksp=255
  for tick,want in enumerate(expected[:calls+1]):
   cycles=r.call('LmNativeSourceInit'if tick==0 else'LmNativeMusicPlay',a=song-1 if tick==0 else 0)
   z=list(r.m[240:256])
   if direct:
    z=list(r.m[address(b,'LmNativeZp'):address(b,'LmNativeZp')+16]);z[8]=r.m[248];z[9]=r.m[249]
    for i in range(16):
     if i not in [8,9]:assert r.m[240+i]==foreground[i],('Source wrote non-owned live ZP',song,tick,hex(240+i),r.m.lowwrites)
    assert all(at in allowed for pc,at,v in r.m.lowwrites),('First source write outside owned audio/stack/pointer state',song,tick,next((v for v in r.m.lowwrites if v[1]not in allowed),None))
   got=dict(writes=list(map(list,r.m.events)),active=z[6],ram=list(r.m[ram:ram+48]),zp=canonical_zp(z))
   assert got=={k:want[k]for k in got},('First divergent native call',song,tick,got,want)
   costs.append(cycles);n+=len(r.m.events);peaksp=min(peaksp,r.depth)
   digest.update(json.dumps(got,separators=(',',':')).encode())
  src=[v['cycles']for v in expected[1:calls+1]]
  active=[costs[i]for i in range(1,len(costs))if expected[i]['active']or expected[i-1]['active']]
  row=dict(song=song,source_calls_compared=len(costs),ordered_APU_writes=n,linked_mean_cycles=sum(costs[1:])/max(1,len(costs)-1),linked_peak_cycles=max(costs[1:]),source_mean_cycles=sum(src)/len(src),source_peak_cycles=max(src),linked_active_mean_cycles=sum(active)/len(active),init_cycles=costs[0],minimum_SP=peaksp,logical_trace_sha256=digest.hexdigest())
  print('DRIVER',json.dumps(row),flush=True);rows.append(row)
  (out/'driver-progress.json').write_text(json.dumps(rows,indent=2))
 return rows

def adapter(b,gold):
 rows=[]
 # One representative role per distinct source track. The complete original
 # song ending and the adapter's explicit whole-song replay are both tested.
 roles=[('area',2,1),('area',4,2),('event',3,4),('event',2,6),('event',0,7),('event',1,9),('area',0,20),('area',1,22),('area',3,23)]
 for role,bit,song in roles:
  golden=json.loads(gzip.decompress((gold/f'song-{song:02d}.json.gz').read_bytes()))
  for behavior in [0,1]:
   r=Run(b);r.set('SelectedCharacter',15);r.set('OperMode',1);r.set('CrossoverBehaviorVersion',behavior);r.set('AreaMusicQueue'if role=='area'else'EventMusicQueue',1<<bit);r.m.page(2,38)
   r.m[240:256]=[(97+17*i)&255 for i in range(16)];saved=bytes(r.m[240:256]);ram=address(b,'LmNativeRam');zp=address(b,'LmNativeZp');r.call('VgAudioDispatch');cursor=1;loops=0;calls=1;stores=0;minimum=r.depth
   assert list(r.m[ram:ram+48])==golden[0]['ram']and canonical_zp(r.m[zp:zp+16])==golden[0]['zp']
   for frame in range(4500):
    ended=r.get('LmNativeZp',2)==r.get('LmNativeZp',6)==0
    before=(bytes(r.m[ram:ram+48]),bytes(r.m[zp:zp+16]))
    r.call('VgAudioDispatch',a=frame&255,x=(frame*3)&255,y=(frame*7)&255);calls+=1;minimum=min(minimum,r.depth)
    assert bytes(r.m[240:256])==saved,('Borrowed CPU ZP leaked',song,behavior,frame)
    if ended and role=='event':
     assert r.get('XgAudioEvent')==2 and r.m.events==[(0x4015,0)] and before==(bytes(r.m[ram:ram+48]),bytes(r.m[zp:zp+16]))
     break
    if ended:
     want=golden[0];cursor=1;loops+=1
     assert r.m.events==[(0x4000+i,0)for i in reversed(range(16))]+[(0x4015,15)]
    else:
     want=golden[cursor];cursor+=1
     assert list(map(list,r.m.events))==want['writes'],('Actual dispatch first wrong APU write',song,behavior,frame,r.m.events,want['writes'])
    assert list(r.m[ram:ram+48])==want['ram']and canonical_zp(r.m[zp:zp+16])==want['zp'],('Actual dispatch source state diverged',song,behavior,frame)
    stores+=len(want['writes'])
   rows.append(dict(song=song,behavior=behavior,linked_dispatch_calls=calls,source_APU_stores_compared=stores,whole_tune_restarts=loops,minimum_SP=minimum))
 return rows

def dispatch(old,new):
 # Legacy branches alter flags in a resident gate but the complete decoder
 # outcome must remain identical, including every non-stack RAM byte/APU write.
 total=0
 for char,area,event,pause,var in itertools.product([6,7,9,10,11,12,13,14,16,17,18,19,20],[0,1,2,4,8,16,32,64,128],[0,4,64],[0,1],[0,1]):
  seed={'SelectedCharacter':char,'OperMode':1,'AreaMusicQueue':area,'EventMusicQueue':event,'GamePauseStatus':pause,'VvVariant':var,'KbVariant':var,'RlVariant':var,'CurrentBank':215}
  c,m=execute(old,'VgAudioDispatch',seed);d,n=execute(new,'VgAudioDispatch',seed)
  assert result(c,m)==result(d,n),('Legacy changed',char,area,event,pause,var)
  total+=1
 rows=[]
 areas=[20,22,1,23,2,1,23];events=[7,9,6,4,9,6,23]
 for kind,table in [('area',areas),('event',events)]:
  for i,song in enumerate(table):
   r=Run(new);r.set('SelectedCharacter',15);r.set('OperMode',1);r.set('AreaMusicQueue'if kind=='area'else'EventMusicQueue',1<<i)
   r.m[240:256]=list(range(91,107));before=list(r.m[240:256]);r.m.page(2,38)
   cost=r.call('VgAudioDispatch')
   assert r.get('XgAudioCharacter')==252 and r.get('RgAudioSong')==song
   assert r.get('LmNativeZp',2)!=0 and r.get('LmNativeZp',6)==0 and list(r.m[240:256])==before
   assert r.m.banks[1]==123 and all(r.get(n)==0 for n in ['AreaMusicQueue','EventMusicQueue','Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'])
   assert r.get('XgAudioEvent')==(0 if kind=='area'else 4 if i==6 else 1)
   first=dict(ram=list(r.m[address(new,'LmNativeRam'):address(new,'LmNativeRam')+48]),zp=canonical_zp(r.m[address(new,'LmNativeZp'):address(new,'LmNativeZp')+16]))
   r.set('GamePauseStatus',1);r.call('VgAudioDispatch');assert first==dict(ram=list(r.m[address(new,'LmNativeRam'):address(new,'LmNativeRam')+48]),zp=canonical_zp(r.m[address(new,'LmNativeZp'):address(new,'LmNativeZp')+16]))and r.get('GuestNativeEnable')==0
   r.set('GamePauseStatus',0);playcost=r.call('VgAudioDispatch');assert r.get('GuestNativeEnable')==15 and list(r.m[240:256])==before
   rows.append(dict(kind=kind,bit=i,song=song,init_cycles=cost,first_play_cycles=playcost))
 # Initial no-queue state, event precedence, persistent silence, pause, and
 # full tune completion/repeat are exercised through the real linked gate.
 r=Run(new);r.set('SelectedCharacter',15);r.set('OperMode',1);r.m.page(2,38);r.call('VgAudioDispatch');assert r.get('RgAudioSong')==20
 r.set('AreaMusicQueue',1);r.set('EventMusicQueue',8);r.call('VgAudioDispatch');assert r.get('RgAudioSong')==4 and r.get('XgAudioEvent')==1
 for i in range(580):r.call('VgAudioDispatch')
 assert r.get('XgAudioEvent')==2 and r.get('GuestNativeEnable')==0
 r.set('AreaMusicQueue',4);r.call('VgAudioDispatch');assert r.get('RgAudioSong')==1 and r.get('XgAudioEvent')==0
 starts=r.get('XgAudioSong')
 for i in range(4040):r.call('VgAudioDispatch')
 assert r.get('XgAudioSong')==(starts+1)&255 and r.get('LmNativeZp',6)!=0 and r.get('XgAudioEvent')==0
 state=bytes(r.m[address(new,'LmNativeRam'):address(new,'LmNativeRam')+288]);r.set('AreaMusicQueue',128);r.call('VgAudioDispatch')
 assert r.get('RgAudioSilenced')==1 and r.get('GuestNativeEnable')==0
 for i in range(5):r.call('VgAudioDispatch');assert bytes(r.m[address(new,'LmNativeRam'):address(new,'LmNativeRam')+288])==state
 r.set('AreaMusicQueue',2);r.call('VgAudioDispatch');assert r.get('RgAudioSilenced')==0 and r.get('RgAudioSong')==22
 startup=[]
 for mode,paused,area,event in itertools.product([0,1],[0,1],[0,1,4],[0,8]):
  r=Run(new);r.set('SelectedCharacter',15);r.set('OperMode',mode);r.set('GamePauseStatus',paused);r.set('AreaMusicQueue',area);r.set('EventMusicQueue',event);r.m.page(2,38)
  hist=address(new,'LmNativeRam');r.m[hist:hist+288]=[(31*i+17)&255 for i in range(288)]
  before=bytes(r.m[hist:hist+288]);r.call('VgAudioDispatch')
  if mode==0:
   assert r.get('XgAudioCharacter')!=252 and bytes(r.m[hist:hist+288])==before
   want=20
  else:want=4 if event else 1 if area==4 else 20
  if paused or mode==0:
   assert r.get('GuestNativeEnable')==0 and bytes(r.m[hist:hist+288])==before
   r.set('OperMode',1);r.set('GamePauseStatus',0);r.call('VgAudioDispatch')
  assert r.get('RgAudioSong')==want and r.get('LmNativeZp',2)!=0
  r.call('VgAudioDispatch');assert r.get('LmNativeZp',6)!=0
  startup.append(dict(initial_mode=mode,paused=paused,area=area,event=event,resumed_song=want))
 # Bounded dispatcher-only costs. Mixer/NMI/draw work are expressly excluded.
 # Both variants execute 601 calls for the same character and area request.
 perf=[]
 for i in range(7):
  one=[]
  for bundle in [old,new]:
   r=Run(bundle);r.set('SelectedCharacter',15);r.set('OperMode',1);r.set('AreaMusicQueue',1<<i);r.m.page(2,38)
   costs=[];minimum=255
   for tick in range(601):
    costs.append(r.call('VgAudioDispatch'));minimum=min(minimum,r.depth)
    # Each live mixer consumes these marks before the next music update.
    r.m[address(bundle,'GuestNativeDirty'):address(bundle,'GuestNativeDirty')+16]=[0]*16
   one.append(dict(init_cycles=costs[0],updates=600,mean_cycles=sum(costs[1:])/600,peak_cycles=max(costs[1:]),minimum_SP=minimum))
  perf.append(dict(area_bit=i,old_Pit_fallback=one[0],new_PunchOut_music=one[1]))
 return dict(non_Mac_exact_dispatch_cases=total,Mac_maps_and_pause_resume=rows,whole_tune_repeat=True,finite_event_stop=True,persistent_silence=True,event_over_area_priority=True,cold_title_and_paused_queue_controls=startup,dispatcher_only_costs=perf)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--gold',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--calls',type=int,default=18000);p.add_argument('--dispatch-only',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old,new=load(a.baseline),load(a.rom);qb,qa=qualified(a.baseline),qualified(a.rom);assert all(qa.get(n)==v for n,v in qb.items()),'An old named symbol moved'
 diff={b:[i for i in range(8192)if old['raw'][16+b*8192+i]!=new['raw'][16+b*8192+i]]for b in range(128)};diff={b:v for b,v in diff.items()if v};assert set(diff)=={38,123,126},diff.keys()
 assert old['raw'][16+1048576:]==new['raw'][16+1048576:],'CHR changed'
 vg=location(old,'VgAudioDispatch');assert diff[38]==[vg-16-38*8192+21,vg-16-38*8192+22]
 gate=address(new,'LmNativeMusicGate');assert all(gate<=0x8000+i<gate+18 for i in diff[126])
 assert old['raw'][16+127*8192:16+128*8192]==new['raw'][16+127*8192:16+128*8192],'Fixed/DPCM bank changed'
 proof=dict(passed=False,accepted=False,baseline_sha256=hashlib.sha256(old['raw']).hexdigest(),candidate_sha256=hashlib.sha256(new['raw']).hexdigest(),source_NSF_sha256='9a7a3ae5f16b745f74296478ec208b5b87ad5ec2773a14b243f7e631a2dd8d68',old_qualified_symbols=len(qb),old_PC_RAM_CHR_preserved=True,changed_PRG_banks={k:len(v)for k,v in diff.items()},adapter_bytes=address(new,'LmNativeAdapterEnd')-address(new,'LmNativeMusicUpdate'),tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='CPU units; exact original music writes/state and actual linked dispatch. No native waveform, NMI/PPU, or gameplay lag claim.')
 if not a.dispatch_only:
  proof['source_music_comparison']=driver(new,a.gold,a.calls,a.output)
  proof['actual_adapter_source_comparison']=adapter(new,a.gold)
 proof['dispatch']=dispatch(old,new);proof['passed']=True;(a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
