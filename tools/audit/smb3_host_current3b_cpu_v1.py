"""Actual whole AudioUpdate and original same-input NSF source comparisons."""
from pathlib import Path
import argparse,hashlib,json,traceback
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import Memory,address
from verify_native_relocation import NesMPU
from smb3_original_music_closure_v3 import TraceBus,source_state

R=Path(__file__).resolve().parents[2];D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
RAW=(R/'reference/new-roster-audio/mario3/crossover-named.nsf').read_bytes();IMAGE=RAW[128:]
SOURCE_ROWS=json.loads((D/'smb3-native-core-v5/preparation.json').read_text())['emitted_original_instruction_rows']
CLOSURE=json.loads((D/'smb3-original-music-closure-v3/dynamic-closure.json').read_text())
FIELDS=sorted({i for key in ['RAM_reads','RAM_writes']for lo,hi in CLOSURE[key]for i in range(lo,hi+1)if not 0x100<=i<0x200})
ROLES={'normal':('AreaMusicQueue',1,9),'water':('AreaMusicQueue',2,11),'underground':('AreaMusicQueue',4,12),'castle':('AreaMusicQueue',8,23),'star':('AreaMusicQueue',16,14),'intro':('AreaMusicQueue',32,1),'bonus':('AreaMusicQueue',64,13),'die':('EventMusicQueue',1,43),'game_over':('EventMusicQueue',2,42),'win_castle':('EventMusicQueue',8,39),'win':('EventMusicQueue',32,38),'hurry':('EventMusicQueue',64,27)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):assert not p.exists();p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def native_address(b,at,live=False):
 if at in [0x6b,0x6c,0x6d,0x6e,0x71,0x72]:return address(b,'B3SourceZp'if live else'B3SourceZpImage')+[0x6b,0x6c,0x6d,0x6e,0x71,0x72].index(at)
 if 0x4d0<=at<=0x4ff:return address(b,'B3SourceImage')+at-0x4d0
 if 0x7f0<=at<=0x7fa:return address(b,'B3SourceTimers')+at-0x7f0
 return at
def projected(m,b,live=False):
 out=bytearray(9984)
 for at in FIELDS:
  i=at if at<256 else at-256 if at<2048 else at-0x5900;out[i]=list.__getitem__(m,native_address(b,at,live))
 return bytes(out)

class HostMemory(Memory):
 def __init__(self,b):
  self.in_source=False;self.pc=0;self.logical=[];self.sourcewrites=[];self.maps_written=[];self.samplechecks=0;self.hwdmc=False;self.source_apu=[0]*24;self.hw=[0]*24
  self.b=b;super().__init__(b)
  self.source_pcs={address(b,f"B3Source{r['source_PC']:04X}")for r in SOURCE_ROWS}
  self.source_write_pcs={address(b,f"B3Source{r['source_PC']:04X}")for r in SOURCE_ROWS if r['source_instruction'].split()[0]in ['STA','STX','STY','INC','DEC','ROR','LSR','ASL','ROL']}
  self.inverse={native_address(b,at,True):at for at in FIELDS}
  self.image_starts={int(s['val'],0)for n,s in b['syms'].items()if n.startswith('B3Image')and'::'not in n}
 def __getitem__(self,at):
  if at==0x4015:return(self.hw[21]&15)|(16 if self.hwdmc else 0)
  return super().__getitem__(at)
 def __setitem__(self,at,v):
  if isinstance(at,int):
   if self.in_source:
    if self.pc in self.source_write_pcs and at in self.inverse:self.sourcewrites.append((self.inverse[at],v))
    if self.pc in self.image_starts:
     reg=at-address(self.b,'GuestNativeApu');assert 0<=reg<16,(self.pc,at,reg);self.logical.append((0x4000+reg,v));self.source_apu[reg]=v
    elif at==address(self.b,'B3Source4012'):
     self.logical.append((0x4012,v));self.source_apu[18]=v
    elif at==address(self.b,'B3Source4015'):
     self.logical.append((0x4015,v));self.source_apu[21]=v
    elif 0x4010<=at<=0x4017 and at not in [0x4012,0x4015]:
     self.logical.append((at,v));self.source_apu[at-0x4000]=v
    if self.pc in self.source_pcs and address(self.b,'B3VirtualMaps')<=at<address(self.b,'B3VirtualMaps')+8:self.maps_written.append((0x5ff8+at-address(self.b,'B3VirtualMaps'),v))
   if 0x4000<=at<=0x4017:
    self.hw[at-0x4000]=v
    if at==0x4015:
     self.hwdmc=bool(v&16)
     if v&16:
      maps=list.__getitem__(self,slice(address(self.b,'B3VirtualMaps'),address(self.b,'B3VirtualMaps')+8));source=0xc000+self.source_apu[18]*64;physical=0xc000+self.hw[18]*64;length=self.hw[19]*16+1
      expected=bytes(IMAGE[maps[(((source+i)&65535)-0x8000)//4096]*4096+((source+i)&4095)]for i in range(length));actual=bytes(list.__getitem__(self,(physical+i)&65535)for i in range(length));assert actual==expected,('DMC wrong fetched payload',hex(self.pc),self.banks[3],source,physical,length);self.samplechecks+=1
  super().__setitem__(at,v)

class Fixture:
 def __init__(self,b,mode,variant):
  self.b=b;self.q=Arena(b,17);self.q.m=HostMemory(b);self.m=self.q.m;self.q.put(SelectedCharacter=17,CrossoverBehaviorVersion=mode,M3Variant=variant,PlayerStatus=1,OperMode=1,GameEngineSubroutine=8,XgAudioCharacter=255,GuestAudioCharacter=255,GamePauseStatus=0);self.original=None;self.pending=None;self.sourcecalls=[];self.minsp=255
 def original_call(self,entry,c):
  if entry=='init':self.original=TraceBus(RAW)
  m=self.original;assert m is not None;m.events=[];m.mapper=[];m.nonstack_writes=[]
  ref=NesMPU(memory=m);ref.pc=0x9000 if entry=='init'else 0xa000;ref.a,ref.x,ref.y,ref.p=c.a,c.x,c.y,c.p;ref.sp=(c.sp+2)&255;ref.stPushWord(0x7eff)
  for _ in range(10000):
   if ref.pc==0x7f00:break
   m.pc=ref.pc;m.pc_physical=m.physical(ref.pc);ref.step()
  else:raise AssertionError('Original timeout')
  return dict(AXYP_SP=[ref.a,ref.x,ref.y,ref.p&207,ref.sp],APU=m.events[:],RAM=m.nonstack_writes[:],maps=m.mapper[:],state=source_state(m),cycles=ref.processorCycles)
 def invoke(self,queue=None,flags=0x20):
  if queue:self.q.set(queue[0],queue[1])
  for i in range(6):self.m[address(self.b,'B3SourceZp')+i]=(i*43+len(self.sourcecalls)*7+19)&255
  zp=self.m[address(self.b,'B3SourceZp'):address(self.b,'B3SourceZp')+6];oldshadow=self.q.get('CurrentBank');c=NesMPU(memory=self.m);c.pc=address(self.b,'AudioUpdate');c.sp=253;c.a=c.x=c.y=0;c.p=flags;c.stPushWord(0x5aff);self.m.writes=[];started=c.processorCycles
  for _ in range(100000):
   if self.pending and c.pc==self.pending['return_PC']:
    want=self.pending['want'];assert[c.a,c.x,c.y,c.p&207,c.sp]==want['AXYP_SP'],('Source AXYP_SP',self.pending['kind'],[c.a,c.x,c.y,c.p&207,c.sp],want['AXYP_SP'])
    assert self.m.logical==want['APU'],('Ordered source APU',self.m.logical,want['APU'])
    assert self.m.sourcewrites==want['RAM'],('Ordered source RAM',self.m.sourcewrites,want['RAM'])
    assert self.m.maps_written==want['maps'],('Source virtual mapper',self.m.maps_written,want['maps'])
    assert projected(self.m,self.b,True)==want['state'],('Full projected source RAM',self.pending['kind'])
    self.sourcecalls.append(dict(kind=self.pending['kind'],source_cycles=c.processorCycles-self.pending['start'],original_cycles=want['cycles'],APU_stores=len(want['APU'])));self.pending=None;self.m.in_source=False
   if c.pc==0x5b00:break
   if c.pc in [address(self.b,'B3Source9000'),address(self.b,'B3SourceA000')]:
    assert self.pending is None;kind='init'if c.pc==address(self.b,'B3Source9000')else'play';self.m.logical=[];self.m.sourcewrites=[];self.m.maps_written=[];self.m.in_source=True;want=self.original_call(kind,c);ret=self.m[0x100+((c.sp+1)&255)]|self.m[0x100+((c.sp+2)&255)]<<8;self.pending=dict(return_PC=(ret+1)&65535,want=want,start=c.processorCycles,kind=kind)
   self.m.pc=c.pc;self.minsp=min(self.minsp,c.sp);c.step()
  else:raise AssertionError(('Host timeout',hex(c.pc),self.m.banks))
  assert self.pending is None and c.sp==253
  assert self.m[address(self.b,'B3SourceZp'):address(self.b,'B3SourceZp')+6]==zp,('Foreground ZP changed',zp,self.m[address(self.b,'B3SourceZp'):address(self.b,'B3SourceZp')+6])
  assert self.q.get('CurrentBank')==oldshadow and self.m.banks[1]==(oldshadow&127),('Foreground A/shadow restoration',oldshadow,self.m.banks)
  assert projected(self.m,self.b)==source_state(self.original),('Post-restore source image')
  return c.processorCycles-started

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--roles',default='normal');p.add_argument('--ticks',type=int,default=64);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True);b=scoped_load(a.packet/'candidate.nes');rows=[]
 try:
  for role in a.roles.split(','):
   name,bit,track=ROLES[role];f=Fixture(b,0,0);cost=[f.invoke((name,bit))]
   for tick in range(a.ticks):cost.append(f.invoke())
   assert f.q.get('XgAudioCharacter')==250 and f.q.get('RgAudioSong')==track and len(f.sourcecalls)==a.ticks+1
   row=dict(role=role,track=track,calls=len(cost),source_calls=len(f.sourcecalls),ordered_source_APU_stores=sum(x['APU_stores']for x in f.sourcecalls),source_sample_payload_checks=f.m.samplechecks,whole_AudioUpdate_cold=cost[0],whole_AudioUpdate_play_mean=sum(cost[1:])/len(cost[1:]),whole_AudioUpdate_play_peak=max(cost[1:]),minimum_SP=f.minsp,source_input_I=0,source_entry_return_AXYP_SP_exact_to_original_same_input=True);rows.append(row);print(json.dumps(row),flush=True)
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(a.packet/'candidate.nes'),roles=rows,caller_source_RAM_state_ordered_RAM_APU_maps_registers_and_sample_payloads_exact=True,six_live_foreground_ZP_bytes_restored_each_call=True,CurrentBank_shadow_preserved_and_hardwareA_restored=True,checker_sha256=sha(__file__),limits='Representative wholeAudio CPU fixture with modeled DMC status, no actual DMA/PPU/IRQ/waveform or transition/foreign qualification yet. Original source runs with ACTUAL native entry AXYP/SP (I0), not a mask of old I1 goldens.'))
 except Exception as e:
  put(a.output/'failure.json',dict(passed=False,roles=rows,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
