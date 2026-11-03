"""Unplaced original player hurt/death component, exact ROM instruction oracle.

The synthetic $4000 link address is a CPU fixture, never a hardware allocation.
Native contact admission, palette and game-over ingress remain separate work.
"""
from collections import Counter
from pathlib import Path
import hashlib,itertools,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import recover_prince_core_1101_v1 as B
from private_build_outputs_v1 import validate
P,O=B.P,B.O


def main():
 old=json.loads((O/'contact-recovery.json').read_text())['instructions']
 labels=P.T.labels(O/'contact-core.lbl')
 labels.update(P.T.labels(O/'host-services-v18.lbl'))
 roots={'PpPlayerCombatHurt':(7,0xe95a),'PpPlayerDeathReaction':(4,0xad19)}
 # Each omitted edge is impossible for the explicitly owned player Y=0.
 selected={(7,0xe962):0xe967,(7,0xe97b):0xe999,(4,0xad1b):0xad33}
 bound={(7,0xd010):('PpMap5',labels['PpMap5']),
        (7,0xd8fc):('PpMap4',labels['PpMap4']),
        (7,0xd6ce):('PpNativeQuietSfx',labels['PpNativeQuietSfx']),
        (7,0xd487):('PpOriginalAlignmentBoundary',0x5100)}
 def key(bank,pc):
  return (7 if pc>=0xc000 else (4 if pc==0xad19 else (5 if bank==7 else bank)),pc)
 def tag(k):return f'{k[0]}:{k[1]:04X}'
 def name(k):return f'PpReaction_{k[0]}_{k[1]:04X}'
 c=P.machine();d=B.Disassembler(c);pending=list(roots.values());ins={}
 while pending:
  k=bank,pc=pending.pop()
  if k in ins or k in bound or tag(k)in old:continue
  c.memory.switch(bank);n,text=d.instruction_at(pc);mn,mode=c.disassemble[c.memory[pc]]
  assert mn!='???';value=int.from_bytes(bytes(c.memory[pc+1:pc+n]),'little')
  ins[k]=dict(n=n,mn=mn,mode=mode,value=value,display=text,raw=bytes(c.memory[pc:pc+n]).hex())
  if k in selected:pending.append(key(bank,selected[k]));continue
  if mn in ['RTS','RTI']:continue
  if mode=='rel':pending.extend([key(bank,pc+n),key(bank,(pc+2+(value if value<128 else value-256))&65535)])
  elif mn=='JMP':assert mode!='ind';pending.append(key(bank,value))
  elif mn=='JSR':pending.extend([key(bank,value),key(bank,pc+n)])
  else:pending.append(key(bank,pc+n))
 external={}
 def target(bank,pc):
  k=key(bank,pc)
  if k in ins:return name(k)
  if k in bound:symbol,at=bound[k]
  else:
   assert tag(k)in old,('Unclosed original target',k)
   symbol=f'PpN_{k[0]}_{k[1]:04X}';at=labels[symbol]
  external[symbol]=at;return symbol
 source=['.setcpu "6502"\n.macpack longbranch\n.segment "REACTION"\n']
 for label,k in roots.items():source.append(f'.export {label}\n{label}:\n ldy #0\n jmp {name(k)}\n')
 original=['.setcpu "6502"\n.segment "ORIGINAL"\n'];expected=bytearray()
 for k,v in sorted(ins.items()):
  bank,pc=k;mn,mode,a=v['mn'],v['mode'],v['value']
  source.append(f'{name(k)}: ; original {tag(k)} {v["raw"]} {v["display"]}\n')
  if k in selected:mn,operand='jmp',target(bank,selected[k])
  elif mode=='rel':operand=target(bank,(pc+2+(a if a<128 else a-256))&65535);mn=B.BR[mn]
  elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
   if mn in ['JSR','JMP']:operand=target(bank,a)
   else:assert a<2048;operand=f'${0xc000+a:04x}'
   operand+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
  elif mode=='imm':operand=f'#${a:02x}'
  elif mode=='acc':operand='a'
  else:assert mode=='imp';operand=''
  source.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
  t=v['display'].lower()
  if mode in ['abs','abx','aby']and a<256:t=t.replace('$','a:$',1)
  original.append(f'.org ${pc:04x}\n {t}\n');expected.extend(bytes.fromhex(v['raw']))
 pre=''.join(f'{n}=${a:04x}\n'for n,a in external.items())
 (O/'player-reaction-v31.s').write_text(pre+''.join(source))
 (O/'player-reaction-v31.cfg').write_text('MEMORY{M:start=$4000,size=$1000,file=%O;}SEGMENTS{REACTION:load=M,type=ro;}')
 (O/'reaction-original-v31.s').write_text(''.join(original))
 (O/'reaction-original-v31.cfg').write_text('MEMORY{M:start=0,size=$1000,file=%O;}SEGMENTS{ORIGINAL:load=M,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 for prefix in ['player-reaction-v31','reaction-original-v31']:
  for cmd in [[cc/'ca65.exe',O/(prefix+'.s'),'-o',O/(prefix+'.o')],[cc/'ld65.exe','-C',O/(prefix+'.cfg'),O/(prefix+'.o'),'-o',O/(prefix+'.bin'),'-Ln',O/(prefix+'.lbl')]]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 assert(O/'reaction-original-v31.bin').read_bytes()==expected
 blob=(O/'player-reaction-v31.bin').read_bytes();lab=P.T.labels(O/'player-reaction-v31.lbl')
 seed=(O/'state-899.bin').read_bytes();runtime=(O/'public-runtime-v24.bin').read_bytes();metadata=(O/'public-metadata-v24.bin').read_bytes();state=(O/'host-state-code-v12.bin').read_bytes()
 # Exact granted source-dead executable spans and native geometry/packet have
 # no donor counterpart. The oracle still compares every remaining source
 # application byte, including HP/action/script/death flags and source shadow.
 dead=[(0x78,0xb0),(0xb0,0xf8),(0x100,0x200),(0x200,0x352),(0x362,0x3ff),(0x40b,0x491),(0x4ff,0x606),(0x780,0x800)]
 ignored={0,1,6,0x41}|{i for lo,hi in dead for i in range(lo,hi)}
 # Hardware stack, not the relocated source's code, owns all nested returns.
 ignored.update(range(0x100,0x200))
 cases=Counter();actions=Counter();cost=[];worldcalls=0;sourcewrites=set();quiet_events=Counter()
 for hp,sword,action,face,ycoord,flags in itertools.product(range(7),[0,1,2],[0,4,74,85],[0,255],[48,128,255],[0x20,0x61]):
  ram=bytearray(seed);ram[0x6cf]=hp;ram[0x6ee]=sword;ram[0x616]=action;ram[0x615]=face;ram[0x611]=ycoord
  donor=P.machine();donor.memory.switch(4);list.__setitem__(donor.memory,slice(0,2048),ram)
  out=P.call(donor,0xe95a,a=83,x=71,y=0,p=flags,limit=20000)
  sourcewrites.update(a for a,v in donor.memory.writes if a<2048 and not 0x100<=a<0x200)
  m=[0]*65536;m[0xa000:0xa000+len(runtime)]=runtime;m[0xc000:0xc800]=ram
  for lo,hi in [(0xb0,0xf8),(0x100,0x200),(0x235,0x352),(0x362,0x3ff),(0x40b,0x491),(0x4ff,0x606)]:
   m[0xc000+lo:0xc000+hi]=state[lo-0xb0:hi-0xb0]
  m[0xc800:0xc800+len(metadata)]=metadata;m[0x4000:0x4000+len(blob)]=blob
  z=P.T.NesMPU(memory=m,pc=lab['PpPlayerCombatHurt']);z.a,z.x,z.y,z.p=83,71,109,flags;z.sp=253;z.stPushWord(0x5ffe)
  for _ in range(20000):
   if z.pc==0x5fff:break
   if z.pc==0x5100:
    # Explicit source-world environment boundary: execute the actual donor
    # D487 instructions against the current source state. No native terrain
    # or outcome is asserted by this component-only differential.
    env=P.machine();env.memory.switch(m[0xc6d1]);list.__setitem__(env.memory,slice(0,2048),m[0xc000:0xc800])
    got=P.call(env,0xd487,a=z.a,x=z.x,y=z.y,p=z.p,limit=20000)
    for i in range(2048):
     if i not in ignored:m[0xc000+i]=env.memory[i]
    z.a,z.x,z.y,z.p=got[:4];z.pc=(z.stPopWord()+1)&65535;worldcalls+=1;continue
   assert m[z.pc]!=0,('Reaction BRK',hex(z.pc),hp,sword,action);z.step()
  else:raise AssertionError('Compiled player reaction instruction bound')
  differences=[(hex(i),donor.memory[i],m[0xc000+i])for i in range(2048)if i not in ignored and donor.memory[i]!=m[0xc000+i]]
  assert not differences,('Original player reaction application state',hp,sword,action,face,ycoord,flags,differences[:12])
  assert out[:3]==(z.a,z.x,z.y)and out[3]&0xef==z.p&0xef and out[4]==z.sp,('Reaction AXYP/SP',out,(z.a,z.x,z.y,z.p,z.sp))
  assert not any(m[:256])and not any(m[0x200:0x800])
  cases['lethal'if hp<=1 else'surviving']+=1;actions[str(m[0xc616])]+=1;cost.append(z.processorCycles);quiet_events[(m[0xc0ad],m[0xc0ae])]+=1
 q=dict(passed=True,source_CPU_only=True,native_emulator=False,host_ROM_created=False,hardware_placement_granted=False,donor_SHA256=P.SHA,original_instruction_bytes=len(expected),original_instruction_boundaries=len(ins),original_PC_assembly_exact=True,original_instruction_SHA256=hashlib.sha256(expected).hexdigest(),component_bytes=len(blob),synthetic_CPU_only_link_half_open=[0x4000,0x4000+len(blob)],source_entry_Y_contract='Owned wrapper LDY0; no guard/enemy entry is claimed.',specialized_branch_edges=[dict(original=tag(k),original_bytes=ins[k]['raw'],taken_target=f'{v:04X}',invariant='Y=0; E95A saves/restores Y across Sfx, Map5 and8710 preserve it.')for k,v in selected.items()],reused_original_entries=external,differential_cases=dict(cases),resulting_source_actions=dict(actions),original_alignment_environment_calls=worldcalls,quiet_event_examples={f'{a:02X}/{x:02X}':n for(a,x),n in quiet_events.items()},component_CPU_including_reused_core_and_quiet_events=[min(cost),max(cost)],source_application_RAM_AXYP_SP_exact=True,host_ZP_preserved=True,original_reaction_written_source_bytes=sorted(sourcewrites),excluded_source_dead_spans=dead,explicit_world_boundary='Actual original D487 executed with current source state, copy only source-live state. Native geometry is not claimed by this differential.',resource_gap='Unplaced component; current approved basic image has3 physical bytes,14 metadata bytes and28 resident bytes spare. No new storage or executable audio-state grant is assumed.',scope='Original player E95A hurt/death reaction and4:AD19 player specialization. Authentic HP0/1 selects85, HP2..6 selects74; source sound event FF/0C recorded quietly. Does not establish native contact admission, invulnerability, native game-over, palette or combat defeat.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(P.__file__),O/'contact-core.bin',O/'public-runtime-v24.bin',O/'public-metadata-v24.bin',O/'host-state-code-v12.bin',O/'player-reaction-v31.bin',R/'docs/qa/allocations/prince-shared-successor-1102-v30.json']})
 (O/'player-reaction-CPU-v31.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','original_reaction_written_source_bytes']}))


if __name__=='__main__':main()
