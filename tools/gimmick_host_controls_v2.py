"""Actual compiled Gimmick rendering/host APIs; compact finite source controls."""
from pathlib import Path
import hashlib,json,itertools,sys
import gimmick_kernel_controls_v2 as K
G=K.G;R=G.R;O=K.O;B=K.B
from check_tmnt_render_oa import Memory,address
from verify_native_relocation import NesMPU
A=lambda n:address(B,n)
def setv(m,**kw):
 for n,v in kw.items():m[A(n)]=v
def mem(bank=24):
 m=Memory(B);m.page(1,bank);m.page(2,73)
 setv(m,SelectedCharacter=26,CurrentBank=bank|128,CurrentBankC=201)
 return m
def call(m,name,a=0,x=0,y=0,p=0x31):return K.run(m,A(name),a=a,x=x,y=y,p=p)
def raw_record(group,frame):
 ptr=A('Gm'+group+'Table')+2*frame;m=mem();return m[ptr]+256*m[ptr+1]
def adapt_attr(a):return a^3 if a&3==1 else a
def oam(m,count,start=32):return bytes(m[0x200+start:0x200+start+4*count])
def renderer_controls():
 audit=json.loads((R/'build/gimmick-source-audit-v1.json').read_text());rows=[]
 for group,bank,key,table in [('Hero',30,'hero_frames',0x843d),('Star',29,'star_frames',0x8523)]:
  for row,face,mask in itertools.product(audit[key],[0,1],[0,0x20,0x80,1]):
   src=G.Original(bank)
   for at,v in {0:table&255,1:table>>8,0x300:row['frame'],0x30a:face,0x9a:0,0xae:0,0xa4:6,0xb8:6,0xef:32,0x3c8:mask}.items():src[at]=v
   c,_=G.run(src,0xf468)
   expected=bytearray(src[0x220:0x220+4*len(row['parts'])])
   for i in range(2,len(expected),4):expected[i]=adapt_attr(expected[i])
   m=mem();ptr=raw_record(group,row['frame'])
   setv(m,R0=ptr&255,R1=ptr>>8,R3=mask|(0x40 if face else 0),R4=96,R5=0,R6=96,GmTemp2=face,CurrentOAMOffset=32)
   d=call(m,'GmEmitRecord')
   assert m[A('CurrentOAMOffset')]==32+len(expected),(group,row['frame'],face,'part count')
   assert oam(m,len(row['parts']))==expected,(group,row['frame'],face,mask,'literal original OAM',oam(m,len(row['parts'])).hex(),expected.hex())
   rows.append([group,row['frame'],face,mask,len(row['parts']),c.processorCycles,d.processorCycles])
 # Genuine compiled emitter at host edges, rotation and capacity, compared to
 # an explicit source-format geometry projection (not an original PPU claim).
 for sx,sy,face,start,rot in itertools.product([-16,0,4,248,256],[0,16,191,224,239],[0,1],[32,244,248,252],[0,128]):
  row=audit['hero_frames'][8];ptr=raw_record('Hero',8);m=mem();setv(m,R0=ptr&255,R1=ptr>>8,R3=face*64,R4=sx&255,R5=(sx>>8)&255,R6=sy,GmTemp2=face,CurrentOAMOffset=start,GuestOamRotationActive=bool(rot),RgOamRotation=rot)
  expected=[];off=start
  for dy,tile,attr,dx in row['parts']:
   yy=(sy+dy)&255;xx=(0xfa-dx)&255 if face else dx;xx=sx+(xx if xx<128 else xx-256)
   if yy>=240:continue
   if off+4>255:break
   if 0<=xx<256:expected.append(((off+rot)&255,bytes([yy,tile,adapt_attr(attr^(face*64)),xx])));off+=4
  call(m,'GmEmitRecord');assert m[A('CurrentOAMOffset')]==off,('edge capacity',sx,sy,face,start,rot)
  for at,blob in expected:assert bytes(m[0x200+at:0x204+at])==blob,('edge OAM',sx,sy,face,start,rot)
 return dict(source_original_cases=len(rows),host_edge_cases=6*5*2*4*2,source_OAM_cycles=rows,
  scope='All22 hero/66 star original records, both facings/four masks; literal ordered original OAM with only source1->native2 palette mapping. Host240-row clipping/rotation/capacity is separately projected. Source CHR bytes packed unchanged; this does not emulate PPU fetches or prove shared CHR/mixer ownership.')
def graphics_controls():
 rows=[]
 for pose,ground,hurt in itertools.product([0,8,21],[0,128],range(128)):
  src=G.Original(30)
  for at,v in {0x300:pose,0x36e:ground,0x38c:hurt}.items():src[at]=v
  c=K.run(src,0x83f5,0x8429)
  m=mem(75);setv(m,GmRam0300=pose,GmRam036E=ground,GmRam038C=hurt)
  # Real mapper/farcall/X5 publisher path; no renderer or bank helper stub.
  before=(m[A('CurrentBank')],m[A('CurrentBankC')],m.banks[:]);scratch=[m[A('R'+str(i))]for i in range(8)]
  d=call(m,'GmGraphics',a=91,x=17,y=43,p=0xf1)
  assert (d.a,d.x,d.y,d.p,d.sp)==(91,17,43,0xf1,0xfd),('graphics caller',pose,ground,hurt,(d.a,d.x,d.y,d.p,d.sp))
  assert m[A('GmRam0300')]==src[0x300] and m[A('GmRam0382')]==src[0x382] and m[A('GmRam038C')]==src[0x38c],('source late timer',pose,ground,hurt)
  assert bool(m[A('GmVisible')])==(c.pc==0x8429),('source blink',pose,ground,hurt)
  assert (m[A('CurrentBank')],m[A('CurrentBankC')],m.banks)==before,('graphics bank restore',pose,ground,hurt)
  assert [m[A('R'+str(i))]for i in range(8)]==scratch
  rows.append(d.processorCycles)
 return dict(cases=len(rows),cycles=[min(rows),max(rows)],scope='Actual original30:83F5 to render boundary vs compiled late-Main callback, every legal protection0..127, source airborne/ground and pose21 exception; genuine X5/farcall and outer AXYP/SP/banks/R0..7.')
def lifecycle_controls():
 rows=[]
 for capacity,hp,kind in itertools.product([2,3,4],[0,1,2],[0,1]):
  m=mem(75);call(m,'GmNewGame');assert m[A('GmRam002B')]==m[A('GmRam0346')]==2
  setv(m,GmRam002B=capacity,GmRam0346=hp)
  c=call(m,'GmPickup',a=kind)
  assert c.p&1
  if kind==0:assert m[A('GmRam002B')]==m[A('GmRam0346')]==min(capacity+1,4)
  else:assert m[A('GmRam0036')]==2 and m[A('GmRam0039')]==1 and m[A('GmNextSpecial')]==2
  rows.append(c.processorCycles)
 m=mem(75);call(m,'GmNewGame')
 for k in [2,3,2]:
  c=call(m,'GmPickup',a=1);assert c.p&1 and m[A('GmRam0036')+m[A('GmRam0039')]-1]==k
 old=bytes(m[0x5c00:0x5c0c]);c=call(m,'GmPickup',a=1);assert not c.p&1 and old==bytes(m[0x5c00:0x5c0c])
 return dict(cases=len(rows)+4,scope='Typed capacity/HP arenas and actual normalized collector API only, genuine original4-code inventory semantics. No physical native acquisition or arbitrary outcome seeds in native.')
def history_controls():
 rows=[]
 for frame,face,mask in itertools.product([0,14,15,20,21,65],[0,1],[0,0x80,1]):
  src=G.Original(29)
  # Four old entries plus actual current entry. Source8469 captures current
  # then draws even0/2/4, shifts all6 arrays, restores current at index4.
  for i in range(4):
   for at,v in [(0x420+i,0),(0x425+i,6),(0x42a+i,0),(0x42f+i,6),(0x434+i,frame),(0x439+i,1)]:src[at]=v
  for at,v in {0x9b:0,0xa5:6,0xaf:0,0xb9:6,0x301:frame,0x91:1,0x30b:face,0x3c9:mask,0xef:32}.items():src[at]=v
  c=K.run(src,0x8469,0x84fd)
  count=(src[0xef]-32)//4;expected=bytearray(src[0x220:0x220+count*4])
  for i in range(2,len(expected),4):expected[i]=adapt_attr(expected[i])
  m=mem();setv(m,GmRam009B=0,GmRam00A5=6,GmRam00AF=0,GmRam00B9=6,GmRam0301=frame,GmRam0091=1,GmRam030B=face,GmRam03C9=mask,CurrentOAMOffset=32)
  for i in range(4):m[A('GmHistory')+i*5:A('GmHistory')+i*5+5]=[96,0,96,0,frame|128]
  d=call(m,'GmDraw',a=0xa7,x=0x35,y=0x93,p=0x79)
  assert oam(m,count)==expected,('actual history OAM',frame,face,mask,oam(m,count).hex(),expected.hex())
  assert m[A('CurrentOAMOffset')]==32+4*count
  assert (d.a,d.x,d.y,d.p,d.sp)==(0xa7,0x35,0x93,0x79,0xfd)
  assert list(m[A('GmHistory'):A('GmHistory')+20])==[96,0,96,0,frame|128]*4
  rows.append([frame,face,mask,count,c.processorCycles,d.processorCycles])
 return dict(cases=len(rows),costs=rows,scope='Actual original29:8469..84FD trail order, current attribute/facing reuse and four old frames vs complete compiled draw callback; no particles/body admitted in these isolated history arenas.')
def portrait_controls():
 audit=json.loads((R/'build/gimmick-source-audit-v1.json').read_text());rows=[]
 for face,oldc in itertools.product([0,1],[42,73,88]):
  m=mem(75);m.page(2,oldc);setv(m,CurrentBankC=oldc|128,R4=96,R5=0,R6=96,CurrentOAMOffset=32)
  old=[m[A(n)+d]for n,d in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
  c=call(m,'GmPortrait',a=face)
  expected=bytearray.fromhex(next(z['OAM']for z in audit['original_renderer_cases']if z['bank']==30 and z['frame']==0 and z['facing']==face))
  # Frozen audit uses source positions100.0 (0x640/16), current portrait96.0.
  for i in range(0,len(expected),4):expected[i]=(expected[i]-4)&255;expected[i+3]=(expected[i+3]-4)&255;expected[i+2]=adapt_attr(expected[i+2])
  assert oam(m,len(expected)//4)==expected,('real portrait original parts',face,oldc,oam(m,len(expected)//4).hex(),expected.hex())
  assert m.banks[2]==oldc and m[A('CurrentBankC')]==oldc|128
  assert [m[A(n)+d]for n,d in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]==old
  assert m[A('CurrentCHRBank')]==48 and m[A('CurrentCHRBank')+1]==50
  assert m[A('X5ChrMode')]==m[A('X5ChrMode')+1]==0x83
  rows.append([face,oldc,c.processorCycles])
 return dict(cases=len(rows),rows=rows,scope='Whole cold portrait API and genuine X5 publisher, source pose0 both facings, three real incoming C mappings, all5SMC/C restored; no native menu publication/display claim.')
def main():
 assert not(O/'handoff.json').exists()
 try:
  proof=dict(status='COMPILED_HOST_PARTIAL_PASS',leaf=G.bind(O/'leaf.bin'),candidate=G.bind(O/'candidate.nes'),renderer=renderer_controls(),graphics=graphics_controls(),lifecycle=lifecycle_controls(),history=history_controls(),portrait=portrait_controls(),limits='Isolated source model on genuine full private link. Shared terrain/fullMain/normalNMI/publication/native still unqualified.')
  (O/'host-controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k not in ['renderer','leaf']}))
 except Exception as e:
  p=O/'host-first-failure.json'
  if not p.exists():p.write_text(json.dumps(dict(status='FALSE',error=repr(e),leaf=G.bind(O/'leaf.bin')),indent=2)+'\n')
  raise
if __name__=='__main__':main()
