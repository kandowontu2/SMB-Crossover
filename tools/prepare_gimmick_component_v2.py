"""Source-projected private Gimmick leaf. Never edits the installed/shared build."""
from pathlib import Path
import hashlib,json,re,sys,subprocess
import gimmick_source_audit_v1 as G
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
R=G.R;O=R/'build/gimmick-component-v2';S=R/'src'
CODE={30:[(0x8000,0x803f),(0x804d,0x80f6),(0x8132,0x82ef)],
      29:[(0x8023,0x8042),(0x8071,0x80e7),(0x8103,0x811f),(0x8124,0x8221),
          (0x82ab,0x82c4),(0x82f3,0x8332),(0x8332,0x8392),(0x83fc,0x8414),(0x8419,0x8469),(0x8d5c,0x8d85)],
      31:[(0xf670,0xf689),(0xf689,0xf6a5),(0xf6a5,0xf6cd),(0xf6cd,0xf6f3),(0xf6f3,0xf72f),
          (0xfcfd,0xfe1b)]}
DATA={30:[(0x83a1,0x83f5),(0x8608,0x860b)],29:[(0x828b,0x82ab),(0x8c23,0x8d5c)],31:[(0xfe1b,0xff13)]}
PATCH={
 (30,0x803f):(0x804a,'jsr GmInventoryJump\n .word GmN30_804A,GmN30_804D,GmN30_807F,GmN30_808B'),
 (30,0x804a):(0x804d,'jmp GmN30_8094'),
 (30,0x80f6):(0x8132,'ldy #0\n jmp GmN30_8132'),
 (30,0x82ec):(0x82ef,'jsr GmIntegrateCall\n rts'),
 (29,0x8042):(0x8071,'ldy #0\n jmp GmN29_8071'),
 (29,0x80e7):(0x8103,'jmp GmN29_8103'),
 (29,0x811f):(0x8124,'lda GmProperty+1\n bmi GmN29_80C6'),
 (29,0x8221):(0x82ab,'jsr GmSpawnEffect\n rts'),
 (29,0x82c4):(0x82f3,'ldy #0\n jmp GmN29_82F3'),
 (29,0x8392):(0x83fc,'jsr GmSpawnEffect\n rts'),
 (29,0x83fc):(0x840c,'jmp GmN29_840C'),
 (29,0x8414):(0x8419,'lda GmProperty+1\n bmi GmN29_8409'),
 (29,0x8409):(0x840c,'jmp GmN29_8332'),
 (31,0xf72c):(0xf72f,'rts'),(31,0xf72f):(0xf730,'rts')}
CALLS={0xf285:'GmQueueSound',0xf596:'GmIntegrateCall',0xfd6d:'GmScriptedCall',0xfcfd:'GmTransportCall'}
PAIR=[0x90,0x9a,0xa4,0xae,0xb8,0xc2,0xcc,0xd6,0x300,0x30a,0x314,0x31e,
      0x328,0x332,0x33c,0x35a,0x364,0x36e,0x378,0x382,0x38c,0x396,0x3a0,0x3c8]
PERSIST={0x2b:4,0x346:5,0x36:6,0x37:7,0x38:8,0x39:9}
ALIAS={0xf7:'SavedJoypadBits',0xf5:'GmFresh',0xed:'GmClock',0x19:'GmTickSlot',0x00:'R0',0x01:'R1',0x02:'R2',0x03:'R3',0x04:'R4',0x05:'R5',0x06:'R6',0x07:'R7',0x5b:'GmQueueSaveY'}
def instructions(bank):
 m=G.Original(bank);d=Disassembler(MPU(memory=m));seen={}
 for lo,hi in CODE[bank]:
  pc=lo
  while pc<hi:
   if (bank,pc)in PATCH:
    pc=PATCH[bank,pc][0];continue
   n,t=d.instruction_at(pc);op,mode=MPU.disassemble[m[pc]]
   assert op!='???',(bank,hex(pc));seen[pc]=(n,op,mode,m[pc+1]+256*m[pc+2],t);pc+=n
 return seen
def generate():
 assert not(O/'handoff.json').exists(),'frozen candidate'
 O.mkdir(exist_ok=True)
 seen={b:instructions(b)for b in CODE}
 used=set()
 for bank,code in seen.items():
  for pc,(n,op,mode,a,t)in code.items():
   if mode in ['zpg','zpx','zpy']:a&=255
   if mode in ['zpg','zpx','zpy','abs','abx','aby','inx','iny']and a<0x8000:used.add(a)
 # Only source fields actually touched by this projected closure are allocated.
 # Pair layout preserves native X/Y=0hero/1star indexed arithmetic.
 aliases=dict(ALIAS);at=12;fields=[]
 for base in PAIR:
  if base in used:
   for k in [0,1]:aliases[base+k]='GmRam%04X'%(base+k)
   fields.append((base,at,2));at+=2
  elif base+1 in used:
   aliases[base+1]='GmRam%04X'%(base+1);fields.append((base+1,at,1));at+=1
 for a in sorted(used):
  if a in aliases or a in PERSIST:continue
  aliases[a]='GmRam%04X'%a;fields.append((a,at,1));at+=1
 for a,off in PERSIST.items():aliases[a]='GmRam%04X'%a
 # Original history's four old frames; current native state is fifth record.
 layout={}
 for n,size in [('GmClock',1),('GmFresh',1),('GmPrevious',1),('GmTickSlot',1),
  ('GmCueCount',1),('GmCues',4),('GmHistory',20),('GmEffects',28),('GmScratch',12),('GmQueueSaveY',1),
  ('GmCalleeFlags',1),('GmCalleeA',1),('GmVisible',1)]:
  layout[n]=(at,size);at+=size
 assert at<=128,('Actual source closure exceeds approved128B RAM',at,fields)
 lines=['; Original-ROM source field projection. Exact raw26-exclusive overlay.','.ifndef __GIMMICK_STATE_V2','__GIMMICK_STATE_V2=1',
  'CHARACTER_GIMMICK=26','GM_FIRST_CHR=816','GmReady=$5c00','GmLife=$5c01','GmArea=$5c02','GmWorld=$5c03',
  'GmNextSpecial=$5c0a','GmPaletteAck=$5c0b']
 for a,off,n in fields:lines.append('%s=$%04x ; original%04X%s'%(aliases[a],0x5c00+off,a,' pair'if n==2 else''))
 for a,off,n in fields:
  if n==2:lines.append('%s=$%04x'%(aliases[a+1],0x5c00+off+1))
 for a,off in PERSIST.items():lines.append('%s=$%04x ; persistent original%04X'%(aliases[a],0x5c00+off,a))
 for n,(off,size)in layout.items():lines.append('%s=$%04x ;%dB'%(n,0x5c00+off,size))
 lines+=['GmProperty=GmScratch','GmSpawnIndex=GmScratch+2','GmArtPtr=GmScratch+3','GmPart=GmScratch+5',
  'GmOldY=GmScratch+6','GmOldX=GmScratch+8','GmTemp=GmScratch+10','GmTemp2=GmScratch+11','.endif']
 (S/'gimmick_state.inc').write_text('\n'.join(lines)+'\n')
 def target(bank,a):
  if a in CALLS:return CALLS[a]
  if (bank,a)in PATCH or a in seen[bank]or any(lo<=a<hi for lo,hi in DATA.get(bank,[])):
   return 'GmN%d_%04X'%(bank,a)
  raise AssertionError(('Unclosed native target',bank,hex(a)))
 out=['; Actual original instructions projected from ce2f8461. Generated, not guessed.']
 for bank in CODE:
  m=G.Original(bank)
  out+=['.pushseg','.segment "GIMMICK_CORE"'if bank!=31 else'.segment "GIMMICK_MOVE"']
  points=sorted(set(seen[bank])|{pc for bk,pc in PATCH if bk==bank})
  for pc in points:
   if bank==31 and pc==0xfcfd:out.append('.segment "GIMMICK_COLD"')
   out.append('GmN%d_%04X:'%(bank,pc))
   if (bank,pc)in PATCH:out.append(' '+PATCH[bank,pc][1]);continue
   n,op,mode,a,t=seen[bank][pc]
   if mode=='rel':
    dest=(pc+2+(m[pc+1]if m[pc+1]<128 else m[pc+1]-256))&65535
    text='j'+op[1:].lower()+' '+target(bank,dest)
   elif mode in ['abs','abx','aby','ind']:
    operand=target(bank,a)if a>=0x8000 else aliases[a]
    if a==0x7e00:operand='GmProperty+1'
    text=op.lower()+' '+('('+operand+')'if mode=='ind'else operand+(',x'if mode=='abx'else',y'if mode=='aby'else''))
   elif mode in ['zpg','zpx','zpy']:
    text=op.lower()+' '+aliases[a&255]+(',x'if mode=='zpx'else',y'if mode=='zpy'else'')
    if op in ['STY','STX']and mode!='zpg':
     assert mode=='zpx'and op=='STY'
     text='php\n pha\n tya\n sta '+aliases[a&255]+',x\n pla\n plp'
   elif mode in ['inx','iny']:
    text=op.lower()+' ('+aliases[a&255]+(',x)'if mode=='inx'else'),y')
   else:text=t.lower()
   out.append(' '+text+' ;%d:%04X %s'%(bank,pc,bytes(m[pc:pc+n]).hex()))
  for lo,hi in DATA.get(bank,[]):
   for p in range(lo,hi):out+=['GmN%d_%04X:'%(bank,p),' .byte $%02x'%G.PRG[bank*8192+(p&8191)]]
  out.append('.popseg')
 (S/'gimmick_native.inc').write_text('\n'.join(out)+'\n')
 (O/'projection.json').write_text(json.dumps(dict(used_source_RAM=sorted(used),RAM_bytes=at,fields=fields,layout=layout,aliases=aliases,
  source_instruction_count={str(b):len(v)for b,v in seen.items()},patched_boundaries=[dict(bank=b,pc=hex(p),next=hex(n),code=t)for(b,p),(n,t)in PATCH.items()]),indent=2)+'\n')
 print(json.dumps(dict(source_instructions=sum(len(v)for v in seen.values()),RAM=at)))
if __name__=='__main__':generate()
