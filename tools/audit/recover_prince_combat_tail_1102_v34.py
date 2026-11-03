"""Recover actual omitted battle control closure before choosing a native proxy.

All original branch sides are retained, including player and defender paths.
This is a closure measurement, not an allocation or native combat claim.
"""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import recover_prince_core_1101_v1 as B
import prepare_prince_cold_worker_1102_v19 as A
P,O=B.P,B.O


def main():
 old=json.loads((O/'contact-recovery.json').read_text())['instructions'];c=P.machine();d=B.Disassembler(c)
 roots={'PpCombatControls':(7,0xf090),'PpOriginalStrike':(4,0xacd6),'PpOriginalIncoming':(4,0xacfa)}
 bound={(7,0xd010):'PpMap5',(7,0xd8fc):'PpMap4',(7,0xe0e1):'PpMap6',(7,0xf2d3):'PpMapA',(7,0xd6ce):'PpNativeSfx',(6,0xaa13):'PpNativeRawSfx',(7,0xd487):'PpWorldLandingAlign'}
 def key(bank,pc):return(7 if pc>=0xc000 else (6 if pc==0xaa13 else (5 if 0x8000<=pc<0xa000 else 4)),pc)
 def tag(k):return f'{k[0]}:{k[1]:04X}'
 pending=list(roots.values());ins={};external=set();indirect=[];static=[];parents={}
 def push(k,parent):parents.setdefault(k,parent);pending.append(k)
 while pending:
  k=bank,pc=pending.pop()
  if k in ins:continue
  if k in bound or tag(k)in old:external.add(k);continue
  c.memory.switch(bank);n,text=d.instruction_at(pc);mn,mode=c.disassemble[c.memory[pc]]
  if mn=='???':
   path=[k]
   while path[-1]in parents and len(path)<20:path.append(parents[path[-1]])
   raise AssertionError(('Unclosed original battle instruction',k,text,path))
  v=int.from_bytes(bytes(c.memory[pc+1:pc+n]),'little');ins[k]=dict(n=n,mn=mn,mode=mode,value=v,display=text,raw=bytes(c.memory[pc:pc+n]).hex())
  if mn not in ['JSR','JMP']and mode in ['abs','abx','aby','zpg','zpx','zpy']and v>=0x800:
   static.append(dict(instruction=tag(k),bank=bank,address=v,mode=mode,display=text))
  if mn in ['RTS','RTI']:continue
  if mode=='rel':push(key(bank,pc+n),k);push(key(bank,(pc+2+(v if v<128 else v-256))&65535),k)
  elif mn=='JMP':
   if mode=='ind':indirect.append(dict(instruction=tag(k),pointer=v))
   else:push(key(bank,v),k)
  elif mn=='JSR':push(key(bank,v),k);push(key(bank,pc+n),k)
  else:push(key(bank,pc+n),k)
 listing=[]
 for k,v in sorted(ins.items()):listing.append(f'{tag(k)} {v["raw"]:6} {v["display"]}\n')
 (O/'combat-tail-original-v34.txt').write_text(''.join(listing))
 labels=P.T.labels(O/'contact-core.lbl');de={};names={}
 for k in sorted(external):
  symbol=bound.get(k,f'PpN_{k[0]}_{k[1]:04X}');names[k]=symbol
  if symbol=='PpNativeSfx':at=0x5100
  elif symbol=='PpNativeRawSfx':at=0x5110
  elif symbol=='PpWorldLandingAlign':at=0x5120
  else:at=labels['PpMap'if symbol=='PpMapA'else symbol]
  de[symbol]=at
 def name(k):return f'PpBattle_{k[0]}_{k[1]:04X}'
 def target(bank,pc):
  k=key(bank,pc)
  return name(k)if k in ins else names[k]
 asm=['.setcpu "6502"\n.macpack longbranch\n.segment "BATTLE"\n']
 for label,k in roots.items():asm.append(f'.export {label}\n{label}={name(k)}\n')
 original=['.setcpu "6502"\n.segment "ORIGINAL"\n'];expected=bytearray();branches=[]
 for k,v in sorted(ins.items()):
  bank,pc=k;mn,mode,a=v['mn'],v['mode'],v['value'];asm.append(f'.export {name(k)}\n{name(k)}: ; original{tag(k)} {v["raw"]} {v["display"]}\n')
  if mode=='rel':operand=target(bank,(pc+2+(a if a<128 else a-256))&65535);branches.append((name(k),mn,operand));mn=B.BR[mn]
  elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
   if mn in ['JSR','JMP']:operand=target(bank,a)
   else:assert a<2048;operand=f'${0xc000+a:04x}'
   operand+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
  elif mode=='imm':operand=f'#${a:02x}'
  elif mode=='acc':operand='a'
  else:assert mode=='imp';operand=''
  asm.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
  if k==(4,0xb8e7):
   # Original B8D5's not-found path deliberately discards its caller's
   # return address, exposing that address's high byte in A/N/Z. There is
   # exactly one recovered caller,7:E982, whose original return is E984.
   # Relocation must retain that observable original byte, not weaken ABI.
   callers=[at for at,row in ins.items()if row['mn']=='JSR'and key(at[0],row['value'])==(4,0xb8d5)]
   assert callers==[(7,0xe982)],callers
   asm.append(' lda #$e9 ; Original popped return high of7:E982, not relocated address\n')
  text=v['display'].lower()
  if mode in ['abs','abx','aby']and a<256:text=text.replace('$','a:$',1)
  original.append(f'.org ${pc:04x}\n {text}\n');expected.extend(bytes.fromhex(v['raw']))
 pre=''.join(f'{n}=${a:04x}\n'for n,a in de.items());text=pre+''.join(asm);short=set()
 for _ in range(10):
  blob,compiled=A.assemble('combat-tail-v34',text,'MEMORY{M:start=$4000,size=$1000,file=%O;}SEGMENTS{BATTLE:load=M,type=ro;}');changed=False
  for label,mn,dest in branches:
   if label in short:continue
   at=compiled.get(dest,de.get(dest));assert at is not None,dest
   if -128<=at-compiled[label]-2<=127:
    oldline=' '+B.BR[mn]+' '+dest+'\n';new=' '+mn.lower()+' '+dest+'\n';needle=label+':';begin=text.index(needle);end=text.index('\n',text.index('\n',begin)+1)+1;fragment=text[begin:end]
    assert oldline in fragment,(label,fragment,oldline);text=text[:begin]+fragment.replace(oldline,new)+text[end:];short.add(label);changed=True
  if not changed:break
 else:raise AssertionError('Battle local branch relaxation bound')
 exact,_=A.assemble('combat-original-v34',''.join(original),'MEMORY{M:start=0,size=$1000,file=%O;}SEGMENTS{ORIGINAL:load=M,type=ro;}');assert exact==expected
 q=dict(measured=True,closed=not indirect,source_CPU_only=True,native_emulator=False,ROM_written=False,original_instruction_boundaries=len(ins),original_instruction_bytes=sum(v['n']for v in ins.values()),original_PC_assembly_exact=True,original_instruction_SHA256=hashlib.sha256(expected).hexdigest(),unplaced_component_bytes=len(blob),synthetic_CPU_only_link_half_open=[0x4000,0x4000+len(blob)],branches_relaxed=len(short),external_compiled_bindings=de,reused_original_or_environment_entries=[dict(bank=k[0],PC=k[1],name=bound.get(k,f'PpN_{k[0]}_{k[1]:04X}'))for k in sorted(external)],indirect_sites_needing_finite_targets=indirect,static_data_sites_needing_relocation=static,source_roots={n:list(k)for n,k in roots.items()},instructions={tag(k):v for k,v in sorted(ins.items())},scope='Actual original whole battle control tail and strike/incoming branches. Reuses previously qualified motion/contact instructions. Original guard reaction branches are included, never discarded as a presumed native no-op. Original-PC assembly exact; source audio/world fixture ports remain explicit. Original-ROM instruction differentials and live proxy/placement are still required.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(P.__file__),O/'contact-recovery.json',O/'contact-continuation-negative-v33.json',O/'combat-tail-v34.bin',O/'combat-original-v34.bin']})
 (O/'combat-tail-recovery-v34.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','instructions']}))


if __name__=='__main__':main()
