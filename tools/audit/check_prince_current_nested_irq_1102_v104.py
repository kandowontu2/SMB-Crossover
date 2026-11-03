"""Current GameLoop nested IRQ, with finite fixed-IRQ mapper independence."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_lag_nested_irq_1102_v92 as V
import check_prince_current_game_loop_isr_1102_v102 as C
O=V.O


def irq_closure():
 b,_=C.C.C.image();pc=V.address(b,'IrqScrollSplit');at=C.V.S.location(b,'IrqScrollSplit');raw=b['raw'];code=raw[at:at+68]
 assert(at-16)//8192==126 and int.from_bytes(raw[16+128*8192-2:16+128*8192],'little')==pc
 old=R/'build/sunny-growth-prelude-1102-v9/candidate.nes';before=old.read_bytes();assert hashlib.sha256(before).hexdigest()=='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'and before[at:at+68]==code
 offset=0;instructions=[]
 while offset<len(code):
  mn,mode=V.N.NesMPU.disassemble[code[offset]];size=1 if mode in ['imp','acc']else 2 if mode in ['imm','zpg','zpx','zpy','rel','inx','iny']else 3
  assert mode not in ['ind','inx','iny','rel']and mn not in ['JSR','JMP','BRK','???'],(offset,mn,mode)
  operand=int.from_bytes(code[offset+1:offset+size],'little')
  if mode in ['abs','abx','aby']:assert operand<0x800 or 0x2000<=operand<=0x2007 or operand in [0x5128,0x5204],(offset,mn,hex(operand))
  instructions.append(dict(CPU=pc+offset,mnemonic=mn,mode=mode,operand=operand));offset+=size
  if mn=='RTI':break
 assert offset==68 and instructions[-1]['mnemonic']=='RTI'
 return dict(fixed_PRG=126,CPU_half_open=[pc,pc+68],SHA256=hashlib.sha256(code).hexdigest(),instructions=instructions,no_indirect_or_branch_or_call=True,no_A_C_window_data_read_or_write=True,no_A_C_mapper_register_access=True,byte_identical_to_prior6690_mapping_context_test=True)


def main():
 closure=irq_closure();source=Path(V.__file__);text=source.read_text().replace('v92','v104')
 start=text.index('def environment():');end=text.index('\n\ndef main():',start);text=text[:start]+'def environment():return CURRENT.environment()'+text[end:]
 start=text.index(' e=environment();b,m,lab=V.loaded()');end=text.index(' actual=N.NesMPU;',start);text=text[:start]+' e=environment();lab,scenarios=CURRENT.scenarios(e)\n'+text[end:]
 assert 'key=(cut[0],cut[2],cut[3])'in text;text=text.replace('key=(cut[0],cut[2],cut[3])','key=cut[0]')
 assert "counts['lag_NMI_gather']==1846"in text;text=text.replace("counts['lag_NMI_gather']==1846","counts['lag_NMI_gather']==1833")
 env=dict(__file__=str(Path(__file__)),__name__='prince_current_nested_v104',CURRENT=C);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'post-return-nested-IRQ-CPU-v104.json';q=json.loads(path.read_text());assert q['minimum_nested_IRQ_SP']==125
 q.update(source_code_injected=False,qualified_cold=True,qualified_current_shared_cold=True,new_lifetimes_ungranted=False,memory_only_SHA256=C.C.C.image()[1]['expected_memory_only_SHA256'],finite_fixed_IRQ_closure=closure,nested_domain='All1833 actual currentFF GameLoop/gateway foreground cuts contribute every reached lag-NMI instruction and mapper context. Replay each lag instruction at its lowest actualSP across those contexts. Exact68B fixed native IRQ has no branches/calls/indirects, no A/C-window data reads and no A/C mapper register access; IRQ behavior is independent of those mappings. No lowerSP is omitted. Prior6690 explicit A/C contexts used the byte-identical IRQ.',scope='Actual current97 full cold/header image, actual GameLoop FF interval and native star/1up. IRQ is injected inside genuine lag audio only at I0, at each handler instruction lowest measuredSP. Full private/R0..7/SMC/maps/AXYP/SP and outer foreground state exact except tracked async native07DA. No ROM/menu/install/emulator claim.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,Path(C.__file__),O/'post-return-manifest-v97.json',O/'current-game-loop-ISR-CPU-v102.json',O/'post-return-nested-IRQ-CPU-v92.json',R/'src/reset.s']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
