"""Private DK Jr source phase/contact/terrain extension; no host allocation."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import dkjr_original_cpu_1102_v1 as D
from py65.disassembler import Disassembler
O=R/'build/dkjr-native-source-1102-v2'
CHECKPOINT=R/'docs/qa/checkpoints/2026-11-02/dkjr-source-core-v1'
RANGES=[(0xcd91,0xcde4),(0xd2fc,0xd405),(0xe893,0xe98b)]
EXTRA_EXPORTS={'Frame':0xcd91,'PlayerContact':0xd2fc,'VineProbe':0xe893,'HandProbe':0xe897,'WallProbe':0xe89b,'SupportProbe':0xe89f,'PlatformProbe':0xe8a3}
sha=lambda data:hashlib.sha256(data).hexdigest()


def original_geometry(mem):
 lists={};tables={}
 for start,name in[(0xc440,'support'),(0xc448,'vines'),(0xc450,'walls')]:
  rows=[]
  for stage in range(4):
   ptr=mem[start+2*stage]+256*mem[start+2*stage+1];rows.append(ptr);count=0
   if ptr<0x800:continue # Stage2 owns its original mutable geometry in RAM.
   while mem[ptr+count]!=255:count+=4;assert count<=252,(name,stage,hex(ptr))
   lists[ptr]=bytes(mem[ptr:ptr+count+1])
  tables[name]=rows
 return lists,tables


def main():
 O.mkdir(exist_ok=True);manifest=json.loads((CHECKPOINT/'manifest.json').read_text());archive=(CHECKPOINT/'inputs.zip').read_bytes();assert sha(archive)==manifest['archive_SHA256']
 with zipfile.ZipFile(CHECKPOINT/'inputs.zip')as z:
  source=z.read('generated/component.s').decode();old=json.loads(z.read('generated/component-layout.json'))
 assert sha(source.encode())==next(x['SHA256']for x in manifest['members']if x['path']=='generated/component.s')
 source=source.replace('\r\n','\n')
 source=source.replace('DkjrComponentEnd:\n.export DkjrComponentEnd','')
 compiled=set(int(x,16)for x in re.findall(r'^D_([0-9a-f]{4}):',source,re.M));mem=D.Bus();dis=Disassembler(D.T.NesMPU(memory=mem,pc=0));ins={}
 for lo,hi in RANGES:
  pc=lo
  while pc<hi:
   n,s=dis.instruction_at(pc);assert pc+n<=hi;ins[pc]=(n,s.lower());pc+=n
 for target in[0xe893,0xe897,0xe89b,0xe89f]:
  source=source.replace('DImport_%04x'%target,'D_%04x'%target)
  source=source.replace('D_%04x: jmp D_%04x ; closed local trap until typed host binding'%(target,target),'')
 imports=set()
 for pc,(n,s)in ins.items():
  source+='\nD_%04x: ; original $%04X: %s\n'%(pc,pc,s)
  op=s.split()[0]
  if op in['jsr','jmp']:
   target=int(s.split('$')[1],16);known=target in ins or target in compiled;imports.add(target)if not known else None
   source+=' '+op+' '+('D_'if known else'DImport_')+'%04x\n'%target;continue
  if op in['bcc','bcs','beq','bne','bmi','bpl','bvc','bvs']:
   target=int(s.split('$')[1],16);assert target in ins or target in compiled,(hex(pc),s)
   source+=' j'+op[1:]+' D_%04x\n'%target;continue
  def remap(m):
   a=int(m[1],16)
   if a<0x800:return '$%04x'%(a+0xc000)
   if 0xc2cd<=a<0xc3cf:return 'DData_%04x'%a
   if 0xc440<=a<0xc458:return '$%04x'%(0xc8c0+a-0xc440)
   raise AssertionError((hex(pc),s,hex(a)))
  if '#'not in s:s=re.sub(r'\$([0-9a-f]+)',remap,s)
  source+=' '+s+'\n'
 for name,pc in EXTRA_EXPORTS.items():source+='\n.export Dkjr'+name+'\nDkjr'+name+'=D_%04x\n'%pc
 existing_imports=set(int(x,16)for x in re.findall(r'^DImport_([0-9a-f]{4}):',source,re.M))
 for pc in sorted(imports-existing_imports):source+='\n.export DImport_%04x\nDImport_%04x: jmp DImport_%04x ; explicit independent donor/native phase import\n'%(pc,pc,pc)
 for pc in range(0xc3cd,0xc3cf):source+='DData_%04x: .byte $%02x\n'%(pc,mem[pc])
 lists,tables=original_geometry(mem)
 for pc,data in sorted(lists.items()):source+='DGeometry_%04x:\n .byte '%pc+','.join('$%02x'%v for v in data)+'\n'
 source+='''
.export DkjrUseOriginalGeometry,DkjrUseNativeGeometry
; Measurement-only host context C800..C8D8. Neither this context nor the
; writable private actor image is an allocated native host range.
DkjrUseOriginalGeometry:
 ldx #23
:
 lda DkjrOriginalGeometryPointers,x
 sta $c8c0,x
 dex
 bpl :-
 rts
DkjrUseNativeGeometry:
 ; Three typed source-format lists, each at most15inclusive rectangles and
 ; FF sentinel, occupy C800/40/80. Validate every record before publishing.
 ldy #0
Validate:
 lda $c800,y
 cmp #$ff
 beq ValidList
 cmp $c802,y
 bcc :+
 bne Reject
:
 lda $c801,y
 cmp $c803,y
 bcc :+
 bne Reject
:
 iny
 iny
 iny
 iny
 tya
 and #$3f
 cmp #60
 bcc Validate
 lda $c800,y
 cmp #$ff
 bne Reject
ValidList:
 tya
 and #$c0
 clc
 adc #$40
 tay
 cpy #$c0
 bne Validate
 ldx #6
Publish:
 lda #0
 sta $c8c0,x
 lda #$40
 sta $c8c8,x
 lda #$80
 sta $c8d0,x
 lda #$c8
 sta $c8c1,x
 sta $c8c9,x
 sta $c8d1,x
 dex
 dex
 bpl Publish
 sec
 rts
Reject:
 clc
 rts
DkjrOriginalGeometryPointers:
'''
 for name in['support','vines','walls']:source+=' .word '+','.join('$%04x'%(x+0xc000)if x<0x800 else'DGeometry_%04x'%x for x in tables[name])+'\n'
 source+='DkjrComponentEnd:\n.export DkjrComponentEnd\n'
 (O/'component.s').write_text(source);(O/'component.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in[[cc/'ca65.exe',O/'component.s','-g','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'component.bin','-Ln',O/'component.lbl']]:
  p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
 lab={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'component.lbl').read_text(),re.M)};blob=(O/'component.bin').read_bytes();assert len(blob)<=8160
 imports={n.split('_')[1].upper():pc for n,pc in lab.items()if n.startswith('DImport_')}
 q=dict(passed=True,ROM_written=False,host_allocation=False,donor_SHA256=D.SHA,inherited_checkpoint_SHA256=sha(archive),component_bytes=len(blob),original_core_bytes=4853,added_original_instruction_bytes=sum(b-a for a,b in RANGES),original_instruction_bytes=3117+sum(b-a for a,b in RANGES),geometry_list_bytes=sum(map(len,lists.values())),geometry_list_count=len(lists),context_measurement_half_open=[0xc800,0xc8d8],original_private_state_bytes=2048,code_measurement_half_open=[0xa000,0xa000+len(blob)],header_reserved_code_spare=8160-len(blob),exports={n:pc for n,pc in lab.items()if n.startswith('Dkjr')},imports=imports,original_geometry={name:rows for name,rows in tables.items()},geometry_list_lengths={str(pc):len(data)for pc,data in lists.items()},code_SHA256=sha(blob),scope='Original phase/contact/terrain source extension and typed source-format list binding only. Native BlockBuffer/vine producer, fruit/enemy/UI imports, mapper/header/IRQ/menu/resources are not implemented or granted.')
 (O/'layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
