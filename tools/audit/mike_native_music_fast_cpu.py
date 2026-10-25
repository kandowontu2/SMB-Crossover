"""Qualify source-equivalent fast StarTropics path against original calls.

CPU-only source, foreground ownership and full outer-call checks. No native
cadence or waveform claim. Caller flags and stack are compared explicitly.
"""
from pathlib import Path
import argparse,gzip,hashlib,itertools,json
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified,execute,result
from verify_native_relocation import NesMPU
from mike_native_music_probe import ZP
from mike_parodius_music_probe import TRACKS,EXPECTED

class MusicMemory(Memory):
 def __init__(self,b):
  super().__init__(b);self.events=[];self.pc=None;self.lowwrites=[];self.image=address(b,'GuestNativeApu')
 def __setitem__(self,at,v):
  if isinstance(at,int)and hasattr(self,'image'):
   if self.image<=at<self.image+16:self.events.append((0x4000+at-self.image,v))
   if 0x4000<=at<=0x4017:self.events.append((at,v))
   if at<0x8000:self.lowwrites.append((self.pc,at,v))
  super().__setitem__(at,v)
class Run:
 def __init__(self,b):self.b=b;self.m=MusicMemory(b);self.c=NesMPU(memory=self.m);self.depth=255
 def set(self,name,value,index=0):self.m[address(self.b,name)+index]=value&255
 def get(self,name,index=0):return self.m[address(self.b,name)+index]
 def call(self,name,a=0,x=0,y=0,p=0x24):
  pc=address(self.b,name)if isinstance(name,str)else name
  if 0xa000<=pc<0xc000:self.m.page(1,115);self.set('CurrentBank',243)
  self.c.pc=pc;self.c.a=a;self.c.x=x;self.c.y=y;self.c.p=p;self.c.sp=253;self.m[510]=255;self.m[511]=126;self.m.events=[];self.m.lowwrites=[];self.m.writes=[]
  start=self.c.processorCycles;self.depth=255
  for _ in range(200000):
   if self.c.pc==0x7f00:break
   self.depth=min(self.depth,self.c.sp);self.m.pc=self.c.pc;self.c.step()
  else:raise AssertionError(('Timeout',name,hex(self.c.pc),self.m.banks))
  self.m.pc=None;assert self.c.sp==255
  return self.c.processorCycles-start

def translated(b,want,components):
 state=want['zp']+want['ram'];out=[]
 for value,origin in zip(state,want['origins']):
  if origin in components:
   part,target=components[origin];v=address(b,f'StNativeP{target:04X}');value=v&255 if part=='<'else v>>8
  out.append(value)
 return dict(zp=out[:16],ram=out[16:])
def state(r,direct):
 z=[r.get('StNativeZp',i)for i in range(16)]
 if direct:
  for at in [0xac,0xad,0xf0,0xf1]:z[ZP.index(at)]=r.m[at]
 return dict(zp=z,ram=[r.get('StNativeRam',i)for i in range(160)])
def driver(b,gold,calls,out):
 q=json.loads((gold/'coverage.json').read_text());components={}
 for lo,hi,at,target in q['pointer_components']:components[lo]=('<',target);components[hi]=('>',target)
 rows=[]
 for song in TRACKS:
  r=Run(b);r.m[:256]=[(71+19*i)&255 for i in range(256)]
  for at in [0xac,0xad,0xf0,0xf1]:r.m[at]=0
  foreground=bytes(r.m[:256]);ram=address(b,'StNativeRam');r.m[ram:ram+288]=[0]*288
  allowed=set(range(256,512))|set(range(ram,ram+160))|set(range(address(b,'StNativeZp'),address(b,'StNativeZp')+16))|{0xac,0xad,0xf0,0xf1,0x4015}
  for name in ['GuestNativeApu','GuestNativeDirty']:allowed.update(range(address(b,name),address(b,name)+16))
  allowed.update(address(b,name)for name in ['GuestNativeEnable','GuestCombinedEnable'])
  costs=[];stores=0;digest=hashlib.sha256();minimum=255
  with gzip.open(gold/f'song-{song:02d}.jsonl.gz','rt')as stream:
   for tick,line in enumerate(stream):
    if tick>calls:break
    want=json.loads(line);cycles=r.call('StNativeSourceInit'if tick==0 else'StNativeMusicPlay',a=song-1 if tick==0 else 0)
    got=state(r,True);expected=translated(b,want,components)
    assert got==expected,('Source state first divergence',song,tick,[(k,i,x,y)for k in got for i,(x,y)in enumerate(zip(got[k],expected[k]))if x!=y][:12])
    assert list(map(list,r.m.events))==want['writes'],('Source ordered APU first divergence',song,tick,r.m.events,want['writes'])
    assert all(at in allowed for pc,at,v in r.m.lowwrites),('First unowned source write',song,tick,next(v for v in r.m.lowwrites if v[1]not in allowed))
    assert all(r.m[i]==foreground[i]for i in range(256)if i not in [0xac,0xad,0xf0,0xf1]),('Foreground ZP changed',song,tick)
    costs.append(cycles);stores+=len(r.m.events);minimum=min(minimum,r.depth);digest.update(json.dumps(got,separators=(',',':')).encode())
  row=dict(song=song,calls=len(costs),ordered_APU_stores=stores,mean_play_cycles=sum(costs[1:])/(len(costs)-1),peak_play_cycles=max(costs[1:]),init_cycles=costs[0],minimum_SP=minimum,state_sha256=digest.hexdigest());rows.append(row);print('DRIVER',row,flush=True);(out/'driver-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
 return rows

def non_mike(old,new,quick):
 rows=[];pvalues=sorted({0x20|c|(z<<1)|(v<<6)|(n<<7)for c,z,v,n in itertools.product([0,1],repeat=4)}|{0xee,0xff})
 chars=[v for v in range(20)if v!=16]
 for name in ['ExpandedAudioUpdate','AudioUpdate']:
  entry_chars=chars if name=='AudioUpdate'else[v for v in chars if v>=6]
  count=0;costdiff=set()
  for char,var,flags,phase in itertools.product(entry_chars,[0,1],pvalues,range(2 if quick else 6)):
   areas=[1,0,4,128,0,64];events=[0,4,0,0,64,8]
   seed={'SelectedCharacter':char,'OperMode':1,'AreaMusicQueue':areas[phase],'EventMusicQueue':events[phase],'GamePauseStatus':int(phase==4),'VvVariant':var,'KbVariant':var,'RlVariant':var,'CurrentBank':215,'CurrentBankC':166}
   c,m=execute(old,name,seed,flags=flags);d,n=execute(new,name,seed,flags=flags)
   assert result(c,m)==result(d,n),('Non-Mike full outer ABI divergence',name,char,var,hex(flags),phase,[(i,m[i],n[i])for i in range(0x8000)if m[i]!=n[i]and not 0x100<=i<0x200][:16],(c.a,c.x,c.y,c.p,c.sp),(d.a,d.x,d.y,d.p,d.sp))
   costdiff.add(d.processorCycles-c.processorCycles);count+=1
  row=dict(entry=name,cases=count,caller_flags=pvalues,legal_characters=entry_chars,valid_Kirby_variants=[0,1],cycle_deltas=sorted(costdiff));rows.append(row);print('NONMIKE',row,flush=True)
 return rows

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--gold',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--calls',type=int,default=18000);p.add_argument('--quick',action='store_true');p.add_argument('--driver-only',action='store_true');p.add_argument('--dispatch-only',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old,new=load(a.baseline),load(a.rom);qb,qa=qualified(a.baseline),qualified(a.rom);changed={str(k):[v,qa.get(k)]for k,v in qb.items()if qa.get(k)!=v};assert set(changed)=={str(('KbAudioFamily','Kirby'))},changed
 assert qa[('KbAudioFamily',)]==qb[('KbAudioFamily',)]and qa[('KbAudioFamily','Done')]==qb[('KbAudioFamily','Done')]
 diff={i:[j for j in range(8192)if old['raw'][16+i*8192+j]!=new['raw'][16+i*8192+j]]for i in range(128)};diff={k:v for k,v in diff.items()if v};assert set(diff)=={38,115,126},diff.keys()
 assert max(diff[38])<location(old,'KbAudioFamily')-16-38*8192+35 and min(diff[38])>=location(old,'KbAudioFamily')-16-38*8192
 assert min(diff[115])>=512
 decoded=address(old,'ExpandedAudioDecoded');assert set(diff[126])==set(range(decoded-32768,decoded-32768+3)),diff[126]
 assert old['raw'][16+127*8192:]==new['raw'][16+127*8192:],'Fixed/CHR changed'
 report=dict(passed=False,accepted=False,baseline_sha256=hashlib.sha256(old['raw']).hexdigest(),candidate_sha256=hashlib.sha256(new['raw']).hexdigest(),changed_old_qualified_symbols=changed,retained_old_qualified_symbols=len(qb)-len(changed),changed_PRG_bytes={k:len(v)for k,v in diff.items()},packed_native_bytes=address(new,'StNativeEnd')-address(new,'StNativeBankStart'),source_sha256=EXPECTED,native_emulator_launched=False,tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 if not a.dispatch_only:report['golden_driver']=driver(new,a.gold,a.calls,a.output)
 if not a.driver_only:report['non_Mike_full_outer']=non_mike(old,new,a.quick)
 report['passed']=True;(a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
