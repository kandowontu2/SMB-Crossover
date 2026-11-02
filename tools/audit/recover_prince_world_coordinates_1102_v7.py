"""Private measured successor: original room coordinate call closure.

No ROM/menu/owner writes. The two executable state slots are a proposal inside
the already exclusive Prince state window, pending the measured lifetime grant.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import recover_prince_core_1101_v1 as B
from private_build_outputs_v1 import validate
P,O=B.P,B.O
ROOTS={'PpWorldContext':0xd4a2,'PpWorldFeetContext':0xd499,
 'PpWorldAheadContext':0xf649,'PpWorldOffsetContext':0xf655,
 'PpWorldOffsetX':0xfa60,'PpWorldAddX':0xf870,'PpWorldColumn':0xd12c,
 'PpWorldSupportContext':0xd4b5,'PpWorldRow':0xd147,
 'PpWorldRowAdjusted':0xd164}
OWN={'PpRawQuery':0xc078,'PpBaseColumn':0xc07a}


def main():
 lab=P.T.labels(O/'contact-core.lbl');core=json.loads((O/'contact-recovery.json').read_text())
 pending=[(7,pc)for pc in ROOTS.values()];ins={};c=P.machine();d=B.Disassembler(c)
 key=lambda bank,pc:(7 if pc>=0xc000 else 2,pc)
 external={(7,0xd141):'PpWorldSelect2',(7,0xe0e1):'PpWorldSelect6',
  (7,0xf2d3):'PpWorldPrivateMap',(7,0xfa6c):'PpWorldSourceSubtract'}
 while pending:
  bank,pc=k=pending.pop()
  if k in ins or k in external:continue
  c.memory.switch(bank);n,t=d.instruction_at(pc);mn,mode=c.disassemble[c.memory[pc]]
  assert mn!='???';v=int.from_bytes(bytes(c.memory[pc+1:pc+n]),'little')
  ins[k]=dict(n=n,mn=mn,mode=mode,value=v,display=t,raw=bytes(c.memory[pc:pc+n]).hex())
  if mn in ['RTS','RTI']:continue
  if mode=='rel':pending.extend([key(bank,pc+n),key(bank,(pc+2+(v if v<128 else v-256))&65535)])
  elif mn in ['JMP','JSR']:
   assert mode=='abs';pending.append(key(bank,v))
   if mn=='JSR':pending.append(key(bank,pc+n))
  else:pending.append(key(bank,pc+n))
 name=lambda k:f'PpW_{k[0]}_{k[1]:04X}'
 def target(bank,pc):
  k=key(bank,pc)
  return external[k]if k in external else name(k)
 head=['.setcpu "6502"\n.macpack longbranch\n']
 head.extend(f'{n}=${a:04x}\n.export {n}\n'for n,a in OWN.items())
 head.append(f'PpWorldSourceSubtract=${lab["PpN_7_FA6C"]:04x}\n')
 for n,pc in ROOTS.items():head.append(f'.export {n}\n{n}={name((7,pc))}\n')
 body=[];original=['.setcpu "6502"\n.segment "ORIGINAL"\n'];expected=bytearray()
 # A single temporary measurement segment first; fixed slots are chosen only
 # after actual instruction sizes and legal split boundaries have been read.
 body.append('.segment "WORLD"\n')
 for (bank,pc),v in sorted(ins.items()):
  if (bank,pc)==(7,0xd172):body.append('.segment "WORLD2"\n')
  mn,mode,a=v['mn'],v['mode'],v['value'];body.append(f'.export {name((bank,pc))}\n{name((bank,pc))}: ; original{bank}:{pc:04X} {v["raw"]} {v["display"]}\n')
  if (bank,pc)==(2,0xa8b1):
   body.append(' php\n lda $c017\n sta PpRawQuery\n lda $c018\n sta PpRawQuery+1\n lda #0\n sta $c082\n plp\n')
  if (bank,pc)==(7,0xd132):
   body.append(' php\n lda $c4b1\n sta PpBaseColumn\n plp\n')
  if mode=='rel':operand=target(bank,(pc+2+(a if a<128 else a-256))&65535);mn=B.BR[mn]
  elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
   if mn in ['JSR','JMP']:operand=target(bank,a)
   else:assert a<2048,(bank,pc,a);operand=f'${0xc000+a:04x}'+dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
  elif mode=='imm':operand=f'#${a:02x}'
  elif mode=='acc':operand='a'
  else:assert mode=='imp';operand=''
  body.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
  t=v['display'].lower()
  if mode in ['abs','abx','aby']and a<256:t=t.replace('$','a:$',1)
  original.append(f'.org ${pc:04x}\n {t}\n');expected.extend(bytes.fromhex(v['raw']))
 body.append('''.export PpWorldCoordinateEnd
PpWorldSelect2:lda #2
 rts
PpWorldSelect6:lda #6
PpWorldPrivateMap:
 sty $c041
 tay
 sta $c6d1
 ldy $c041
 rts
PpWorldCoordinateEnd:
''')
 asm=O/'world-coordinates-v7.s';asm.write_text(''.join(head+body))
 (O/'world-coordinates-v7.cfg').write_text('MEMORY{M:start=$c100,size=$600,file=%O;N:start=$c735,size=$600,file=%O;}SEGMENTS{WORLD:load=M,type=ro;WORLD2:load=N,type=ro;}')
 (O/'world-coordinate-original-v7.s').write_text(''.join(original))
 (O/'world-coordinate-original-v7.cfg').write_text('MEMORY{M:start=0,size=$800,file=%O;}SEGMENTS{ORIGINAL:load=M,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 for prefix in ['world-coordinates-v7','world-coordinate-original-v7']:
  for cmd in [[cc/'ca65.exe','-g',O/(prefix+'.s'),'-o',O/(prefix+'.o')],[cc/'ld65.exe','-C',O/(prefix+'.cfg'),O/(prefix+'.o'),'-o',O/(prefix+'.bin'),'-Ln',O/(prefix+'.lbl')]]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 assert(O/'world-coordinate-original-v7.bin').read_bytes()==expected
 blob=(O/'world-coordinates-v7.bin').read_bytes();labels=P.T.labels(O/'world-coordinates-v7.lbl')
 # Monotonic local branch compaction, independent of original branch widths.
 import re
 text=asm.read_text();rounds=[]
 for _ in range(12):
  changed=[0]
  def short(m):
   n,mn,t=m.groups()
   if -128<=labels[t]-labels[n]-2<=127:
    changed[0]+=1;return m.group().replace(' '+mn+' ',' '+dict(jeq='beq',jne='bne',jmi='bmi',jpl='bpl',jcs='bcs',jcc='bcc',jvs='bvs',jvc='bvc')[mn]+' ')
   return m.group()
  text=re.sub(r'(PpW_\d_[0-9A-F]+):[^\n]*\n (jeq|jne|jmi|jpl|jcs|jcc|jvs|jvc) (PpW_\d_[0-9A-F]+)\n',short,text)
  rounds.append(changed[0]);asm.write_text(text)
  for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'world-coordinates-v7.o'],[cc/'ld65.exe','-C',O/'world-coordinates-v7.cfg',O/'world-coordinates-v7.o','-o',O/'world-coordinates-v7.bin','-Ln',O/'world-coordinates-v7.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
  labels=P.T.labels(O/'world-coordinates-v7.lbl')
  if not changed[0]:break
 (O/'world-coordinates-v7.cfg').write_text('MEMORY{M:start=$c100,size=$100,file=%O,fill=yes;N:start=$c235,size=$12b,file=%O;}SEGMENTS{WORLD:load=M,type=ro;WORLD2:load=N,type=ro;}')
 cmd=list(map(str,[cc/'ld65.exe','-C',O/'world-coordinates-v7.cfg',O/'world-coordinates-v7.o','-o',O/'world-coordinates-v7.bin','-Ln',O/'world-coordinates-v7.lbl']))
 validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 labels=P.T.labels(O/'world-coordinates-v7.lbl');blob=(O/'world-coordinates-v7.bin').read_bytes()
 q=dict(measured=True,qualified=False,private_proposal_only=True,source_bytes=len(expected),source_boundaries=len(ins),original_PC_bytes_exact=True,original_SHA256=hashlib.sha256(expected).hexdigest(),compiled_bytes=len(blob),proposed_state_code_half_open=[[0xc100,0xc200],[0xc235,labels['PpWorldCoordinateEnd']]],state_code_source_file_offsets=[0,256],branch_relaxation=rounds,source_roots=ROOTS,private_fields=OWN,external_source_subtract=lab['PpN_7_FA6C'],instrumentation='Capture the complete post-alternate-form query before destructive32px division, then the original clamped column before row addition; preserve original flags and subsequent A overwrite.',instructions={f'{k[0]}:{k[1]:04X}':v for k,v in sorted(ins.items())},bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'contact-core.bin',asm,O/'world-coordinates-v7.bin']})
 (O/'world-coordinate-recovery-v7.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['instructions','bindings']}))


if __name__=='__main__':main()
