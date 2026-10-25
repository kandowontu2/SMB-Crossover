"""Execute both linked renderers and compare actual OAM writes and return ABI.

These are isolated CPU cases, not controller or scene-visibility evidence.
Body/projectile records come from the candidate's linked art. Interior and
edge origins, capacity rejection and rotated OAM are exercised independently.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,re,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
from verify_native_relocation import NesMPU


class Memory:
 def __init__(self,raw,memory,banks):
  self.raw=raw;self.data=bytearray(memory);self.banks={};self.writes=[]
  for window,bank in banks.items():self.map(window,bank)
 def map(self,window,value):
  bank=value&127;start=16+bank*8192
  self.data[window:window+8192]=self.raw[start:start+8192];self.banks[window]=bank
 def __getitem__(self,a):return self.data[a&2047 if a<8192 else a]
 def __setitem__(self,a,v):
  a=a&2047 if a<8192 else a
  if a in(0x5114,0x5115,0x5116,0x5117):self.map(0x8000+(a-0x5114)*8192,v)
  else:
   assert a<0x2000 or 0x5c00<=a<0x8000,('Unexpected write',a,v)
   self.data[a]=v
  self.writes.append((a,v))


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 rom=args.rom.resolve();raw=rom.read_bytes()
 labels={m[2]:int(m[1],16)for line in rom.with_suffix('.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
 segments=[]
 for line in rom.with_suffix('.dbg').read_text().splitlines():
  if line.startswith('seg\t'):
   fields=dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',line.split('\t',1)[1]))
   if 'ooffs'in fields:segments.append({k:(v.strip('"')if k=='name'else int(v,0))for k,v in fields.items()if k in('name','start','size','ooffs')})
 def segment(name):return next(s for s in segments if s['name']==name)
 def bank(name):return(segment(name)['ooffs']-16)//8192
 meta=json.loads((ROOT/'reference/roll-mobile/art.json').read_text());records=[]
 for key,parts in meta['records'].items():
  f,o,d=key.split('-');records.append((f'RlP{f}O{o}D{d}',parts,True))
 for facing,items in((1,meta['shot_records']),(2,meta['shot_left_records'])):
  for n,parts in enumerate(items):records.append((f'RlShot{n}'+('Left'if facing==2 else''),parts,False))
 art=segment('ROLL_ART')
 for name,parts,_ in records:
  offset=art['ooffs']+labels[name]-art['start'];expected=bytes([len(parts)*4]+[v for part in parts for v in part])
  assert raw[offset:offset+len(expected)]==expected,('Linked art differs',name)
 base=bytearray(65536)
 for s in segments:
  if s['name']=='SMCCODE':base[s['start']:s['start']+s['size']]=raw[s['ooffs']:s['ooffs']+s['size']]
 def execute(name,parts,body,origin,cursor,rotation,rotation_on,fast):
  memory=bytearray(base);a_bank=bank('ROLL_CORE'if fast else'METASPRITE')
  for n,v in(('CurrentBank',a_bank|128),('CurrentBankC',bank('ROLL_ART')|128),('CurrentOAMOffset',cursor),('RgOamRotation',rotation),('GuestOamRotationActive',rotation_on),('R3',0),('R4',origin[0]),('R5',0),('R6',origin[1]),('R7',1)):
   memory[labels[n]]=v
  for i in range(256):memory[labels['Sprite_Y_Position']+i]=(i*73+29)&255
  pointer=labels[name]
  if not body:
   pointer=labels['OutlinePoseBuffer'];payload=bytes([len(parts)*4]+[v for part in parts for v in part]);memory[pointer:pointer+len(payload)]=payload
  memory[labels['R0']]=pointer&255;memory[labels['R1']]=pointer>>8
  sp=0xd9;stop=0x5b00;memory[0x101+sp]=(stop-1)&255;memory[0x102+sp]=(stop-1)>>8
  bus=Memory(raw,memory,{0x8000:bank('LOWCODE'),0xa000:a_bank,0xc000:bank('ROLL_ART'),0xe000:bank('FIXED')})
  cpu=NesMPU(memory=bus);cpu.pc=labels[('RlFastBodyRender'if body else'RlFastShotRender')if fast else'MetaspriteRenderLoop'];cpu.sp=sp;cpu.a=173;cpu.x=73;cpu.y=19;cpu.p=0x6d
  for steps in range(10000):
   if cpu.pc==stop:break
   cpu.step()
  else:raise AssertionError(('Unbounded renderer',name,hex(cpu.pc)))
  assert cpu.sp==sp+2 and bus.banks[0xa000]==a_bank and bus.banks[0xc000]==bank('ROLL_ART'),'Bank/stack restoration'
  begin=labels['Sprite_Y_Position']
  return dict(regs=[cpu.a,cpu.x,cpu.y,cpu.p&0xcf,cpu.sp],oam=bytes(bus.data[begin:begin+256]),offset=bus.data[labels['CurrentOAMOffset']],writes=[z for z in bus.writes if begin<=z[0]<begin+256],cycles=cpu.processorCycles,bank_switches=sum(a==0x5115 for a,v in bus.writes))
 checks=0;deltas=[];return_nz=0
 origins=[(96,176),(32,48),(207,191),(4,224)]
 for(name,parts,body),origin,cursor,rotation,rotation_on in itertools.product(records,origins,(0,160,252),(0,128,252),(0,1)):
  old,new=[execute(name,parts,body,origin,cursor,rotation,rotation_on,fast)for fast in(False,True)]
  for field in('oam','offset','writes'):assert old[field]==new[field],(name,origin,cursor,rotation,rotation_on,field)
  # Native farcall's final LDA restores A and sets its N/Z. These are dead in
  # both callers: DrawMetasprite reads C then LDA Atr; RlDraw reads LDX RlSlot.
  # Account for that specific producer, rather than masking an unexplained
  # status difference. All other flags, A/X/Y and SP must remain identical.
  assert old['regs'][:3]+old['regs'][4:]==new['regs'][:3]+new['regs'][4:]
  if old['regs'][3]!=new['regs'][3]:
   assert new['bank_switches']==2 and(old['regs'][3]^new['regs'][3])&~0x82==0
   assert new['regs'][3]&0x82==((new['regs'][0]&0x80)|(2 if new['regs'][0]==0 else 0))
   return_nz+=1
  checks+=1;deltas.append(new['cycles']-old['cycles'])
 report=dict(passed=True,rom_sha256=hashlib.sha256(raw).hexdigest(),checks=checks,records=len(records),cycle_delta_min=min(deltas),cycle_delta_max=max(deltas),identified_farcall_return_nz_cases=return_nz,scope=__doc__)
 out=args.output.resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
