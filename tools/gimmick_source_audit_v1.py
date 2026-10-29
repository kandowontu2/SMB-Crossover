"""Bounded original-ROM Gimmick audit; no port, native runner or ROM output."""
from pathlib import Path
import collections,hashlib,json,re,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools/audit'))
from verify_native_relocation import NesMPU
from py65.disassembler import Disassembler
ROM=Path('C:/NES/Gimmick! (Japan).nes')
REF=R.parent/'gimmick/readable-disassembly'
OUT=R/'build/gimmick-source-audit-v1.json'
EXPECTED='ce2f84618dfe3d5581fcdf11a10190b717853af3be0bea7988cd27cd1498c092'
sha=lambda b:hashlib.sha256(b).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(Path(p).read_bytes()))
raw=ROM.read_bytes();PRG=raw[16:16+262144];CHR=raw[16+262144:]

class Original(list):
 def __init__(self,bank=30):
  super().__init__([0]*65536);self.writes=[];self.bank=bank
  self[0x8000:0xa000]=PRG[bank*8192:(bank+1)*8192]
  self[0xe000:]=PRG[31*8192:32*8192]
 def __setitem__(self,p,v):
  if isinstance(p,int):
   assert p<0x8000,('unexpected original mapper/ROM write',hex(p),v)
   self.writes.append((p,v))
  super().__setitem__(p,v)

def run(m,start,stop=0x5b00,x=0,y=0,a=0,limit=10000):
 c=NesMPU(memory=m,pc=start);c.a,c.x,c.y,c.p,c.sp=a,x,y,0x30,0xfd;c.stPushWord(0x5aff)
 m.writes=[];seen=[]
 for i in range(limit):
  if c.pc==stop:return c,seen
  seen.append(c.pc);assert m[c.pc]!=0,('unexpected BRK',hex(c.pc))
  c.step()
 raise AssertionError(('bounded original fragment',hex(start),hex(c.pc)))

def hero():
 m=Original();m[0x90]=1;m[0xb8]=5;m[0xae]=128;m[0xa4]=6;m[0x2b]=m[0x346]=3
 m[0x33c]=0x30;m[0x328]=0x60;m[0x314]=0xe0
 return m

def input_kernel(m,held,fresh=None):
 m[0xf5]=held&~m[0xf7]if fresh is None else fresh;m[0xf7]=held
 c,tr=run(m,0x8000,0x82ec);m[0xed]=(m[0xed]+1)&255
 return c,tr

def motion(m,ground=False):
 # Execute the original selected flat-ground friction or free-flight path,
 # including gravity and both signed16bit integrations, STOP before terrain.
 return run(m,0xf689 if ground else 0xf6f3,0xf72f,x=0)

def controls():
 rows=[]
 for ground in[False,True]:
  for name,mask in [('right',1),('left',2),('both',3)]:
   m=hero();v=[]
   for _ in range(32):
    m[0x9a]=0;m[0xa4]=6  # typed stable Y for isolated horizontal-path check.
    input_kernel(m,mask);motion(m,ground);v.append(m[0xcc])
   m[0x9a]=0;m[0xa4]=6
   before=m[0xcc];input_kernel(m,0);motion(m,ground)
   rows.append(dict(kind='terrain-selected X control',ground_friction_path=ground,input=name,velocity_sequence=v,release_before=before,release_after=m[0xcc],units_per_pixel=16))
 jumps=[]
 for hold in[1,4,12,32]:
  m=hero();origin=m[0x9a]+256*m[0xa4];ys=[];vel=[]
  for tick in range(30):
   m[0x36e]=128 if tick==0 else 0
   input_kernel(m,128 if tick<hold else 0);motion(m,False)
   ys.append(m[0x9a]+256*m[0xa4]);vel.append(m[0xc2])
  jumps.append(dict(hold_updates=hold,height_pixels=(origin-min(ys))/16,apex_update=ys.index(min(ys)),Yspeed=vel[:24],scope='Source pre-terrain control then actual free-flight gravity/integration; no landing/contact/camera model.'))
 assert jumps[-1]['height_pixels']>jumps[0]['height_pixels']
 charge=[]
 for ticks in[1,32,33,42,60]:
  for face in[0,1]:
   m=hero();m[0x30a]=face;m[0xcc]=16
   seq=[]
   for _ in range(ticks):input_kernel(m,64);seq.append(m[0x91])
   input_kernel(m,0)
   charge.append(dict(held=ticks,facing=face,status_sequence=seq,release_status=m[0x91],kind=m[0x351],starVX=m[0xcd],starVY=m[0xc3],heroVX=m[0xcc],heroVY=m[0xc2],starX=m[0xaf]+256*m[0xb9],starY=m[0x9b]+256*m[0xa5]))
 assert all(c['release_status']==0 for c in charge if c['held']<33)
 assert all(c['release_status']==1 for c in charge if c['held']>=33)
 bounce=[]
 for wall,floor in[(False,False),(True,False),(False,True),(True,True)]:
  m=Original(29);m[0x91]=1;m[0xb9]=5;m[0xa5]=6;m[0x351]=0
  m[0xcd]=m[0x3a1]=40;m[0xc3]=m[0x397]=48
  m[0x379]=128 if wall else 0;m[0x36f]=128 if floor else 0
  c,tr=run(m,0x8023,0x815c)
  bounce.append(dict(wall=wall,floor=floor,outputVX=m[0xcd],outputVY=m[0xc3],flags=m[0xd7],cycles=c.processorCycles,original_instructions=len(tr)))
 assert bounce[1]['outputVX']==216 and bounce[2]['outputVY']==216
 idle=Original(29);idle[0x91]=1;idle[0xb9]=5;idle[0xa5]=6;ids=[]
 for _ in range(8):
  c,tr=run(idle,0x8023,0x815c if idle[0x38d]<7 else 0x5b00)
  ids.append([idle[0x91],idle[0x38d]])
 assert idle[0x91]==0xd0
 return dict(horizontal=rows,variable_jump=jumps,charge_and_inherited_throw=charge,bounce_preterrain=bounce,eight_rest_updates=ids,
  limits='Actual original instructions and real QueueSound calls, no rewritten physics. Typed RAM/input/contact flags and split original terrain-path entry; these are bounded kernel controls, not complete original Main or native PPU/mapper/IRQ/terrain gameplay, not a port differential. No external service is replaced by a success stub.')

def frames(bank,table,count,hero_bank=False):
 m=Original(bank);rows=[]
 for f in range(count):
  ptr=m[table+2*f]+256*m[table+2*f+1];assert 0x8000<=ptr<0xa000,(bank,f,hex(ptr))
  parts=[];i=0
  while m[ptr+i]:
   assert i<128,(bank,f,hex(ptr),'record terminator')
   parts.append(list(m[ptr+i:ptr+i+4]));i+=4
  rows.append(dict(frame=f,table=hex(table),record=hex(ptr),bytes=i+1,parts=parts,CHR_page=(PRG[30*8192+0x5ce+f]if hero_bank else 8)))
 return rows

def renderer(rows,bank):
 checks=[]
 for row in rows:
  for face in[0,1]:
   m=Original(bank);m[0x00]=int(row['table'],16)&255;m[1]=int(row['table'],16)>>8
   m[0x300]=row['frame'];m[0x30a]=face;m[0x9a]=m[0xae]=0x40;m[0xa4]=m[0xb8]=6;m[0xef]=32
   c,tr=run(m,0xf468)
   count=(m[0xef]-32)//4
   assert count==len(row['parts']),(bank,row['frame'],face,count,len(row['parts']))
   checks.append(dict(bank=bank,frame=row['frame'],facing=face,parts=count,cycles=c.processorCycles,OAM=bytes(m[0x220:0x220+count*4]).hex()))
 return checks

def main():
 assert not OUT.exists()and sha(raw)==EXPECTED
 reference=(REF/'readable-built.nes').read_bytes();assert reference[16:]==raw[16:]
 hero_rows=frames(30,0x843d,22,True);star_rows=frames(29,0x8523,66)
 control=controls();render=renderer(hero_rows,30)+renderer(star_rows,29)
 # Record source bytes/addresses and decoded direct callers without new dumps.
 ranges=[('hero input/charge/throw/animation',30,0x8000,0x83a1),('hero original records and CHR selectors',30,0x83a1,0x860b),('star dispatch/motion/art',29,0x8006,0x8d85),('original terrain/ramps',31,0xf596,0xff13),('native support overlap',31,0xff13,0xff91),('native sprite renderer',31,0xf468,0xf596)]
 sections=[]
 for name,bank,start,end in ranges:
  off=16+bank*8192+(start&8191);blob=raw[off:off+end-start]
  sections.append(dict(name=name,physical8Kbank=bank,CPU=[hex(start),hex(end-1)],bytes=len(blob),file_offset=hex(off),sha256=sha(blob)))
 m=Original();d=Disassembler(NesMPU(memory=m));p=0xe9c6;nmi=[]
 for _ in range(100):
  n,text=d.instruction_at(p);nmi.append([hex(p),text]);p+=n
  if text=='RTI':break
 proof=dict(status='READ_ONLY_AUTHENTIC_SOURCE_MAP_AND_BOUNDED_ORIGINAL_KERNEL_CONTROLS',native=False,port_implemented=False,ROM=bind(ROM),local_source=bind(REF/'README.txt'),
  primary_repository='https://github.com/LucianoTheWindowsFan/gimmick',local_pinned_commit='eb896859858879526943bdc7c3edab2871a636e2',
  authority=dict(local_build=bind(REF/'readable-built.nes'),PRG_CHR_payload_exact=True,only_header_differences=[i for i,(x,y)in enumerate(zip(raw,reference))if x!=y],payload_sha256=sha(raw[16:])),
  actual_Main_order='Fixed31:E368 selects30 viaF051/JSR8000 hero;E370 selects29/JSR8006 star;E378 selects16/JSR8003 objects. LaterE545 selects29/JSR8003 star render;E566 selects30/JSR83F5 hero render. Preserve that gameplay order; aliases in 16KB source files must be converted to actual8KB mapping.',
  routines=sections,controls=control,hero_frames=hero_rows,star_frames=star_rows,original_renderer_cases=render,NMI_instructions=nmi,
  identity='Requested proposed raw26/menu25. Current canonical f56a and own6305 source contains no Gimmick constant/module/menu entry. Root must explicitly admit it; this audit does not reserve the slot or storage.',
  bindings=[bind(p)for p in[Path(__file__),REF/'GIMMICK-JPN14.asm',REF/'GIMMICK-JPN15.asm',REF/'GIMMICK-JPN8.asm',REF/'RenderMetasprite.asm',REF/'object_symbols.asm',REF/'SPRITE_FORMAT.txt',REF/'verification.json',R/'docs/new-roster-request-2026-10-28.txt']])
 OUT.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(status=proof['status'],proof=bind(OUT),hero_frames=len(hero_rows),star_frames=len(star_rows),renderer_cases=len(render),jump=control['variable_jump'],bounce=control['bounce_preterrain'])))
if __name__=='__main__':main()
