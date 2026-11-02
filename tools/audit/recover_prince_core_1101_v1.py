"""Recover original Prince animation-driven motion into explicit private state.

The two original audio consumers remain declared environment boundaries; the
CPU fixture executes their actual donor instructions. No host grant/unlock.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as P
from py65.disassembler import Disassembler
from private_build_outputs_v1 import validate
O=R/'build/prince-actor-1101-v1'
BR={'BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BCS':'jcs','BCC':'jcc','BVS':'jvs','BVC':'jvc'}
START=(7,0xf158);END=(7,0xf1a2)
CONTROL_END=(7,0xf090)
CALLBACKS={(6,0xaa19):'PpNativeMusic',(7,0xd6ce):'PpNativeSfx',
 (7,0xd4a2):'PpWorldContext',(7,0xd499):'PpWorldFeetContext',
 (7,0xce63):'PpWorldTile',(7,0xce66):'PpWorldTileY',
 (7,0xdb18):'PpWorldGateState',(7,0xf649):'PpWorldAheadContext',
 (7,0xd147):'PpWorldRow',(7,0xf655):'PpWorldOffsetContext',
 (7,0xfa60):'PpWorldOffsetX',(7,0xf870):'PpWorldAddX',
 (7,0xd12c):'PpWorldColumn',(7,0xc8d4):'PpWorldAlign',
 (7,0xd4b5):'PpWorldSupportContext',(7,0xf882):'PpNativeFallDamage',
 (2,0xbb4f):'PpNativeEndScene',(7,0xcaab):'PpWorldGateHeight',
 (7,0xd9b5):'PpWorldGateSupport',(7,0xde0b):'PpWorldRoomAbove'}
MAPPERS={(7,0xd010):5,(7,0xe0e1):6,(7,0xcb00):2}


def key(bank,a):
 # This recovered fixed-bank interpreter runs with bank5. Its sole low-window
 # bank6 target is the original music consumer after JSR E0E1 at F1D6.
 return(7 if a>=0xc000 else (6 if a==0xaa19 else (2 if a==0xbb4f else (5 if bank==7 else bank))),a)


def recover():
 c=P.machine();d=Disassembler(c);raw=P.donor();bank5=raw[16+5*16384:16+6*16384]
 word=lambda a:bank5[a-0x8000]|bank5[a-0x7fff]<<8
 vectors={i:key(5,word(0x842b+2*i)) for i in range(1,16)}
 entries={'PpAdvanceActor':START,'PpSetAction':(5,0x8730),'PpFall':(5,0x8133),'PpDecodeInput':(5,0x839f),'PpControls':(7,0xeff2)}
 pending=list(entries.values())+list(vectors.values());ins={};external=set();parents={k:None for k in pending}
 def push(target,origin):parents.setdefault(target,origin);pending.append(target)
 while pending:
  bank,pc=pending.pop();k=(bank,pc)
  if k in [END,CONTROL_END]or k in ins:continue
  if k in CALLBACKS or k in MAPPERS:external.add(k);continue
  c.memory.switch(bank);n,text=d.instruction_at(pc);mn,mode=c.disassemble[c.memory[pc]]
  if mn=='???':
   chain=[];q=k
   while q is not None and len(chain)<30:chain.append(q);q=parents.get(q)
   raise AssertionError((k,text,chain))
  value=int.from_bytes(bytes(c.memory[pc+1:pc+n]),'little')
  ins[k]=dict(n=n,mn=mn,mode=mode,value=value,display=text,bytes=bytes(c.memory[pc:pc+n]).hex())
  if mn in ['RTS','RTI']:continue
  if mode=='rel':push(key(bank,pc+n),k);push(key(bank,(pc+2+(value if value<128 else value-256))&65535),k)
  elif mn=='JMP':
   if mode=='ind':assert value==0x23,(k,value)
   else:push(key(bank,value),k)
  elif mn=='JSR':push(key(bank,pc+n),k);push(key(bank,value),k)
  else:push(key(bank,pc+n),k)
 assert external<=set(CALLBACKS)|set(MAPPERS),external
 def name(k):return f'PpN_{k[0]}_{k[1]:04X}'
 def code(bank,a):
  k=key(bank,a)
  if k==END:return 'PpFrameComplete'
  if k==CONTROL_END:return 'PpControlComplete'
  if k in CALLBACKS:return CALLBACKS[k]
  if k in MAPPERS:return f'PpMap{MAPPERS[k]}'
  assert k in ins,('Unclosed code',k)
  return name(k)
 def data(a):
  if a<0x800:return f'PpState+${a:03x}'
  if a==0x95f2 or a==0x95f3:return f'PpActionTable+{a-0x95f2}'
  if a in [0x842b,0x842c]:return f'PpCommandTable+{a-0x842b}'
  chain=[];q=(bank,pc)
  while q is not None and len(chain)<16:chain.append(f'{q[0]}:{q[1]:04X}');q=parents.get(q)
  raise AssertionError(('Unclosed static data',hex(a),bank,hex(pc),v['display'],chain))
 out=['; Authenticated original Prince of Persia NES instructions.\n.setcpu "6502"\n.macpack longbranch\nPpState=$c000\n.export PpState\n.segment "CORE"\n']
 for i,(k,n)in enumerate(CALLBACKS.items()):out.append(f'{n}=${0x5200+16*i:04x}\n.export {n}\n')
 for n,k in entries.items():out.append(f'.export {n}\n{n}={name(k)}\n')
 for (bank,pc),v in sorted(ins.items()):
  mn,mode,a=v['mn'],v['mode'],v['value'];out.append(f'.export {name((bank,pc))}\n{name((bank,pc))}: ; native bank{bank} ${pc:04X} {v["bytes"]}: {v["display"]}\n')
  if mn=='LDA'and mode=='iny':assert a==0x21;out.append(' jsr PpReadSequence\n');continue
  if mode=='rel':operand=code(bank,(pc+2+(a if a<128 else a-256))&65535);mn=BR[mn]
  elif mode=='ind':operand=f'({data(a)})'
  elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
   operand=code(bank,a)if mn in ['JSR','JMP'] else data(a)
   operand+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
  elif mode=='imm':operand=f'#${a:02x}'
  elif mode=='acc':operand='a'
  else:assert mode=='imp',(bank,pc,mn,mode);operand=''
  out.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
  if (bank,pc+v['n'])in [END,CONTROL_END]:out.append(' jmp '+code(bank,pc+v['n'])+'\n')
 out.append('''
.export PpFrameComplete,PpCoreEnd
PpFrameComplete:rts
PpControlComplete:rts
; Preserve original script-pointer values in private state. Only the ROM read
; address moves. PHP/PLP retain original C/V/I/D before the actual LDA result.
PpReadSequence:
 php
 lda PpState+$21
 sec
 sbc #<$96ae
 sta PpRead+1
 lda PpState+$22
 sbc #>$96ae
 clc
 adc #>PpScripts
 sta PpRead+2
 plp
PpRead:lda $ffff,y
 rts
PpMap5:lda #5
 jmp PpMap
PpMap2:lda #2
 jmp PpMap
PpMap6:lda #6
PpMap:
 sty PpState+$41
 tay
 sta PpState+$6d1
 ldy PpState+$41
 rts
PpCoreEnd:
.segment "SCRIPTS"
.export PpScripts,PpScriptsEnd
PpScripts:
''')
 scripts=bank5[0x16ae:0x1d93]
 for a in range(0,len(scripts),16):out.append(' .byte '+','.join(f'${v:02x}'for v in scripts[a:a+16])+'\n')
 out.append('PpScriptsEnd:\n.segment "TABLES"\n.export PpActionTable,PpCommandTable\nPpActionTable:\n')
 for a in range(0x95f2,0x96ae,2):out.append(f' .word ${word(a):04x}\n')
 out.append('PpCommandTable:\n .word 0\n')
 for i in range(1,16):out.append(' .word '+code(*vectors[i])+'\n')
 out.append('.export PpTablesEnd\nPpTablesEnd:\n')
 (O/'prince-core.s').write_text(''.join(out))
 (O/'prince-core.cfg').write_text('MEMORY{M:start=$a000,size=$2000,file=%O;}SEGMENTS{CORE:load=M,type=ro;SCRIPTS:load=M,type=ro,start=$b000;TABLES:load=M,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',O/'prince-core.s','-o',O/'prince-core.o'],[cc/'ld65.exe','-C',O/'prince-core.cfg',O/'prince-core.o','-o',O/'prince-core.bin','-Ln',O/'prince-core.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 # Assemble every recovered original instruction at its genuine PC, then
 # compare the packed fragments against original physical ROM bytes. ORG
 # changes the assembler PC without retaining a whole source/ROM bank copy.
 original=['.setcpu "6502"\n.segment "ORIGINAL"\n']
 expected=bytearray()
 for (bank,pc),v in sorted(ins.items()):
  text=v['display'].lower()
  if v['mode']in ['abs','abx','aby']and v['value']<256:text=text.replace('$','a:$',1)
  original.append(f'.org ${pc:04x}\n {text}\n');expected.extend(bytes.fromhex(v['bytes']))
 (O/'original-core.s').write_text(''.join(original));(O/'original-core.cfg').write_text('MEMORY{M:start=0,size=$1000,file=%O;}SEGMENTS{ORIGINAL:load=M,type=ro;}')
 for cmd in [[cc/'ca65.exe',O/'original-core.s','-o',O/'original-core.o'],[cc/'ld65.exe','-C',O/'original-core.cfg',O/'original-core.o','-o',O/'original-core.bin']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 assert (O/'original-core.bin').read_bytes()==expected,'Original-PC assembly must reproduce every actual donor instruction byte'
 labels=P.T.labels(O/'prince-core.lbl')
 q=dict(recovered=True,source_CPU_only=True,donor_sha256=P.SHA,source_instruction_bytes=sum(v['n']for v in ins.values()),source_instruction_boundaries=len(ins),original_PC_assembly_byte_exact=True,original_instruction_SHA256=hashlib.sha256(expected).hexdigest(),component_code_bytes=labels['PpCoreEnd']-0xa000,script_bytes=len(scripts),table_bytes=labels['PpTablesEnd']-labels['PpActionTable'],compact_code_image_bytes=(O/'prince-core.bin').stat().st_size,compact_code_image_half_open=['A000',f'{labels["PpTablesEnd"]:04X}'],state_bytes=2048,original_actions=94,original_commands=15,source_entries={n:[k[0],hex(k[1])]for n,k in entries.items()},source_end_before_projection=[7,'F1A2'],source_end_before_combat_selector=[7,'F090'],dynamic_command_targets={str(i):[k[0],hex(k[1])]for i,k in vectors.items()},declared_original_environment_boundaries={n:[k[0],hex(k[1])]for k,n in CALLBACKS.items()},mapper_adaptation='Original banking shadow/Y-scratch effects retained in private state; no host mapper writes. Script ROM reads move via owned SMC and retain original pointer values.',instructions={f'{k[0]}:{k[1]:04X}':v for k,v in sorted(ins.items())},scope='Original single-actor animation/motion/fall/input and basic control choice; original world/health/audio environment boundaries explicit. Ends before native render projection and combat selector. No host allocations, menu or native playability claim.')
 (O/'core-recovery.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='instructions'}))
 return q,labels


if __name__=='__main__':recover()
