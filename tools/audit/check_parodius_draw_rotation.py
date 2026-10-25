"""Execute old/new linked draw code and compare rotation, OAM and return ABI.

Exhaustive byte clocks/valid record lengths test the actual offset instructions.
Whole-emitter cases cover clipping, signed offsets, capacity and rotated OAM.
These are CPU arenas; they do not certify campaign or hardware visibility.
"""
from pathlib import Path
import argparse,gzip,hashlib,itertools,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
from verify_native_relocation import NesMPU
from check_roll_renderer import Memory


def load(path):
 raw=path.read_bytes();p=path.with_suffix('.dbg');debug=p.read_text()if p.exists()else gzip.decompress(p.with_suffix('.dbg.gz').read_bytes()).decode()
 fields=lambda line:dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',line.split('\t',1)[1]))
 scopes=[fields(l)for l in debug.splitlines()if l.startswith('scope\t')]
 scope=next(r['id']for r in scopes if r.get('name')=='"PnDraw"')
 segments=[{k:(v.strip('"')if k=='name'else int(v,0))for k,v in fields(l).items()if k in('id','name','start','size','ooffs')}for l in debug.splitlines()if l.startswith('seg\t')and'ooffs='in l]
 labels={m[2]:int(m[1],16)for l in path.with_suffix('.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',l))}
 for line in debug.splitlines():
  if line.startswith('sym\t'):
   f=fields(line)
   if f.get('scope')==scope and f.get('name')in('"Draw"','"Modulo"','"Start"'):labels['Inner'+f['name'].strip('"')]=int(f['val'],0)
 def seg(n):return next(r for r in segments if r['name']==n)
 def bank(n):return(seg(n)['ooffs']-16)//8192
 base=bytearray(65536)
 for s in segments:
  if s['name']=='SMCCODE':base[s['start']:s['start']+s['size']]=raw[s['ooffs']:s['ooffs']+s['size']]
 bus=Memory(raw,base,{0x8000:bank('LOWCODE'),0xa000:bank('VIC_WORLD'),0xc000:bank('VIC_GFX'),0xe000:bank('FIXED')})
 cpu=NesMPU(memory=bus)
 return dict(raw=raw,labels=labels,segments=segments,bank=bank,base=base,bus=bus,cpu=cpu)


def offset(m,length,clock,new):
 c,b,l=m['cpu'],m['bus'],m['labels'];b.data[l['OutlineBytesLeft']]=length;b.data[l['VvClock']]=clock
 c.pc=l['PnDrawRotationOffset']if new else l['InnerModulo']-5
 if not new:assert b.data[c.pc:c.pc+5]==bytes([0xad,l['VvClock']&255,l['VvClock']>>8,10,10])
 stop=l['PnDrawRotationReady']if new else l['InnerStart']
 c.a=length;c.x=173;c.y=0;c.p=0x6d;c.processorCycles=0
 for _ in range(2000):
  if c.pc==stop:break
  c.step()
 else:raise AssertionError('Bounded rotation instructions')
 return c.a,c.p&0x41,c.processorCycles


def emitter(m,length,clock,origin,cursor,parts=None):
 c,b,l=m['cpu'],m['bus'],m['labels'];b.data[:0x8000]=m['base'][:0x8000]
 def w(n,v):b.data[l[n]]=v&255
 a=m['bank']('VIC_WORLD');cb=m['bank']('VIC_GFX')
 for n,v in(('CurrentBank',a|128),('CurrentBankC',cb|128),('CurrentOAMOffset',cursor),('GuestOamRotationActive',clock&1),('RgOamRotation',(clock*4)&252),('VvClock',clock),('R3',0),('R4',origin[0]),('R5',origin[0]>>8),('R6',origin[1]),('R7',1),('SmPosePtr',0),('R0',0)):
  w(n,v)
 b.data[l['SmPosePtr']+1]=0x61;b.data[0x6100]=(8,24,64,128)[(length//4+clock)%4]
 b.data[l['R1']]=0x60;b.data[0x6000]=length
 if parts is None:parts=[[(i*2)&254,(i%4)|((i&1)*64),((i*7)%33-16)&255,((i*11)%49-24)&255]for i in range(length//4)]
 assert len(parts)*4==length
 for i,part in enumerate(parts):b.data[0x6001+i*4:0x6005+i*4]=bytes(part)
 start=l['Sprite_Y_Position']
 for i in range(256):b.data[start+i]=(i*73+29)&255
 sp=0xd9;stop=0x5b00;b.data[0x101+sp]=(stop-1)&255;b.data[0x102+sp]=(stop-1)>>8
 buffer=l['OutlinePoseBuffer'];initial_buffer=bytes(b.data[buffer:buffer+125]);source=bytes(b.data[0x6000:0x6100])
 fast=False;clipped=False
 b.writes=[];c.a=173;c.x=73;c.y=19;c.p=0x6d;c.sp=sp;c.pc=l.get('PnDrawRecord',l['InnerDraw']);c.processorCycles=0
 for n in range(30000):
  if c.pc==stop:break
  if c.pc==l.get('PnFastDrawRecord')and b.banks[0xa000]==m['bank']('ROLL_CORE'):fast=True
  if c.pc==l.get('PnFastDrawClippedRecord')and b.banks[0xa000]==m['bank']('ROLL_CORE'):fast=True;clipped=True
  c.step()
 else:raise AssertionError(('Bounded full emitter',length,clock,origin,cursor,hex(c.pc)))
 assert c.sp==sp+2 and b.banks[0xa000]==a and b.banks[0xc000]==cb
 assert bytes(b.data[0x6000:0x6100])==source,'Source record must remain read-only'
 return dict(regs=[c.a,c.x,c.y,c.p&0xcf,c.sp],oam=bytes(b.data[start:start+256]),offset=b.data[l['CurrentOAMOffset']],
  writes=[z for z in b.writes if start<=z[0]<start+256],buffer=bytes(b.data[buffer:buffer+125]),initial_buffer=initial_buffer,
  buffer_writes=[z for z in b.writes if buffer<=z[0]<buffer+125],pointer=b.data[l['R0']]+256*b.data[l['R1']],
  r3=b.data[l['R3']],r7=b.data[l['R7']],fast=fast,clipped=clipped,cycles=c.processorCycles)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 old,new=load(a.before),load(a.after);deltas={};checks=0
 for length in range(4,256,4):
  values=[]
  for clock in range(256):
   x,y=offset(old,length,clock,False),offset(new,length,clock,True)
   assert x[:2]==y[:2]and y[0]==((clock*4)&255)%length,(length,clock,x,y)
   values.append(y[2]-x[2]);checks+=1
  deltas[str(length)]=dict(min=min(values),mean=sum(values)/len(values),max=max(values))
 full=0;fast=0;clipped=0;fast_deltas=[]
 origins=((4,24),(32,48),(96,120),(247,232),(32,96),(223,175),(31,96),(224,175),(32,95),(223,176),(-16,120),(256,120),(0,0),(255,255))
 def compare(length,clock,origin,cursor,parts=None):
  nonlocal fast,clipped,full
  x,y=emitter(old,length,clock,origin,cursor,parts),emitter(new,length,clock,origin,cursor,parts)
  for key in('regs','oam','offset','writes','r3','r7'):assert x[key]==y[key],(length,clock,origin,cursor,key,x[key],y[key])
  if y['fast']:
   # PnDraw's callers consume OAM, flags and cursor. Their next actor lookup
   # reloads R0/R1, and no caller reads OutlinePoseBuffer after this return.
   # The optimization deliberately avoids copying into that dead scratch.
   assert y['pointer']==0x6000 and y['buffer']==y['initial_buffer']and not y['buffer_writes']
   if not y['clipped']:assert 32<=origin[0]<224 and 96<=origin[1]<176
   else:clipped+=1
   fast+=1;fast_deltas.append(y['cycles']-x['cycles'])
  else:
   for key in('buffer','pointer'):assert x[key]==y[key],(length,clock,origin,cursor,key)
  full+=1
 for args in itertools.product(range(0,256,4),(0,1,2,31,63,64,127,255),origins,(0,160,220,252)):compare(*args)
 manifest_path=ROOT/'reference/parodius-nes/art/packed/manifest.json';manifest=json.loads(manifest_path.read_text());records=0
 signed=lambda v:v if v<128 else v-256
 for pool in manifest['pools']:
  for parts in pool['records'].values():
   assert all(-24<=signed(x)<=24 and -64<=signed(y)<=64 and not(a&0x3c)for t,a,y,x in parts),'All actual generated records must obey the interior admission contract'
   records+=1
   for clock,origin,cursor in itertools.product((1,63),((32,96),(223,175),(4,24),(247,232),(-16,120),(256,120)),(0,160)):
    compare(len(parts)*4,clock,origin,cursor,parts)
 assert fast>100,'The direct path must actually execute, including its guard boundaries'
 report=dict(passed=True,before_sha256=hashlib.sha256(old['raw']).hexdigest(),after_sha256=hashlib.sha256(new['raw']).hexdigest(),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),actual_pooled_records=records,pooled_art_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),offset_cases=checks,full_emitter_cases=full,fast_emitter_cases=fast,clipped_fast_emitter_cases=clipped,fast_cycle_delta=dict(min=min(fast_deltas),mean=sum(fast_deltas)/len(fast_deltas),max=max(fast_deltas)),rotation_cycle_deltas=deltas,allowed_dead_scratch_difference='Fast path leaves R0/R1 at the read-only input record and does not write OutlinePoseBuffer. All actual OAM bytes/store order, registers/flags, cursor, bank and stack are compared.',scope=__doc__)
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in('rotation_cycle_deltas','scope')}))


if __name__=='__main__':main()
