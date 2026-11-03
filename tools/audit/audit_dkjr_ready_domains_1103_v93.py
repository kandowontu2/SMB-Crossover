"""Compiled reachable Ready accesses and possible indexed/SMC aliases."""
import collections
import json
import re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N

R,O=A.R,A.O


def main():
    q=json.loads((O/'native-entrance-v89-layout.json').read_text());source=(O/'native-entrance-v89.s').read_text()
    hidden=sorted(set(re.findall(r'^(DIndirect_[0-9a-f]{4}):',source,re.M)))
    cfg=(O/'native-entrance-v89.cfg').read_text().replace('native-entrance-','native-ready-domains-').replace('-v89.bin','-v93.bin')
    linked,L=A.assemble('native-ready-domains-v93',source+'\n.export '+','.join(hidden)+'\n',cfg)
    assert linked==(O/'native-entrance-v89.bin').read_bytes()
    mem={}
    for file,at in [('native-entrance-v89.bin',0xa000),('native-entrance-pause-v89.bin',0xd540),('native-entrance-main-v89.bin',0xd65e),('native-entrance-ports-v89.bin',0xd6a7)]:
        mem.update({at+i:v for i,v in enumerate((O/file).read_bytes())})
    sizes={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}
    roots=[L['DkServices']+3*i for i in range(38)]+[L[n]for n in ['DkjrNativeFruitSet','DkjrNativeFruitReset','DkjrNativeFruitProject','DkjrNativeFruitRemove']]
    reached=set();todo=list(roots);opaque=set();decoded={}
    while todo:
        pc=todo.pop()
        if pc in reached:continue
        if pc not in mem:opaque.add(pc);continue
        reached.add(pc);name,mode=N.NesMPU.disassemble[mem[pc]];assert name not in ['???','BRK'],(pc,name)
        size=sizes[mode];operand=mem.get(pc+1,0)+(mem.get(pc+2,0)*256 if size==3 else 0)
        decoded[pc]=(name,mode,size,operand);nextpc=pc+size
        if name=='JSR':todo.extend([operand,nextpc])
        elif name=='JMP':assert mode=='abs';todo.append(operand)
        elif mode=='rel':todo.extend([nextpc,nextpc+operand-(256 if operand&128 else 0)])
        elif name not in ['RTS','RTI']:todo.append(nextpc)
    direct=[];possible=[];dynamic=[]
    hidden_pc={L[n]:n for n in hidden}
    for pc,(name,mode,size,operand)in sorted(decoded.items()):
        if pc in hidden_pc:dynamic.append(dict(PC=pc,label=hidden_pc[pc],operation=name));continue
        if mode=='abs'and operand==0xc8fe:direct.append(dict(PC=pc,operation=name,mode=mode,address=operand))
        if mode in ['abx','aby']and operand<=0xc8fe<=operand+255:possible.append(dict(PC=pc,operation=name,mode=mode,base=operand))
    assert len(dynamic)==23
    prior=json.loads((O/'native-packet-domains-v58.json').read_text())
    assert {z['name']for z in prior['complete_original_indirect_sites']}==set(hidden)
    # Only an actual direct INC may introduce2. Cold clearing is separately
    # performed by the genuine forced-blank common worker with headers invalid.
    writers=[z for z in direct if z['operation']in ['STA','STX','STY','INC','DEC','ASL','LSR','ROL','ROR']]
    assert collections.Counter(z['operation']for z in writers)=={'STA':2,'INC':1},writers
    out=dict(passed=True,qualification_complete=False,ROM_written=False,native_owner_admitted=False,
        compiled_reachable_instructions=len(reached),declared_public_and_world_roots=len(roots),
        ready_direct_accesses=direct,ready_writers=writers,possible_indexed_ready_aliases=possible,
        inherited_original_SMC_indirect_sites=dynamic,inherited_indirect_domains=prior['indirect_domains'],
        opaque_native_targets=sorted(opaque),
        scope='All compiled38 public vectors/fourtyped world roots; every direct Ready access and possible absolute-indexed alias identified. Original23translated indirect sites retain frozen58 domains. This census is not yet the completed new indexed/producer/async lifetime proof or native admission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),O/'native-entrance-v89.s',O/'native-entrance-v89-layout.json',O/'native-ready-domains-v93.bin',O/'native-ready-domains-v93.lbl',O/'native-packet-domains-v58.json']})
    (O/'native-ready-domains-v93-census.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','compiled_reachable_instructions','ready_direct_accesses','ready_writers','possible_indexed_ready_aliases','opaque_native_targets']}))


if __name__=='__main__':main()
