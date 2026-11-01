"""Check exact successor changes and instruction-level movement write domains."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from verify_native_relocation import NesMPU
from py65.disassembler import Disassembler
O=R/'build/shinobi-chr-closure-1101-v1'
P=R/'build/kirby-approach-owner-1101-v3'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    old=(R/'build/kirby-owner-main-1101-v2/candidate.nes').read_bytes()
    new=(P/'candidate.nes').read_bytes()
    proof=json.loads((P/'owner-link.json').read_text())
    assert sha(old)==proof['base_ROM_sha256'] and sha(new)==proof['ROM_sha256']
    spans=proof['source_intervals'];allowed=set()
    for s in spans:allowed.update(range(s['start'],s['start']+s['bytes']))
    changes={i for i,(a,b) in enumerate(zip(old,new)) if a!=b}
    assert len(old)==len(new) and changes<=allowed and len(changes)==1432
    def decode(raw,span):
        start=span['start'];size=span['bytes'];pc=0xa000+(start-16)%8192
        c=NesMPU();c.memory[pc:pc+size]=raw[start:start+size]
        d=Disassembler(c);end=pc+size;writes=set();calls=set();count=0
        while pc<end:
            op,mode=c.disassemble[c.memory[pc]]
            n,text=d.instruction_at(pc)
            assert pc+n<=end and op not in ['BRK','???'],(hex(pc),text)
            operand=bytes(c.memory[pc+1:pc+n]).hex()
            if op in ['STA','STX','STY','INC','DEC','ASL','LSR','ROL','ROR'] and mode!='acc':
                writes.add((op,mode,operand))
            if op=='JSR':
                target=c.memory[pc+1]+256*c.memory[pc+2]
                if not 0xa000+(start-16)%8192<=target<end:calls.add(target)
            count+=1;pc+=n
        return dict(instructions=count,writes=sorted(writes),external_calls=sorted(calls))
    before=decode(old,spans[0]);after=decode(new,spans[0])
    added=set(map(tuple,after['writes']))-set(map(tuple,before['writes']))
    added_calls=set(after['external_calls'])-set(before['external_calls'])
    pull=spans[1]['start']
    assert old[pull:pull+14]==bytes.fromhex('ad0c5cf0034c37a22055a24c37a2')
    assert new[pull:pull+14]==bytes.fromhex('2055a24c37a2eaeaeaeaeaeaeaea')
    injury=spans[2]['start']
    assert old[injury-1:injury+2]==bytes.fromhex('20e6a5')
    assert new[injury-1:injury+2]==bytes.fromhex('20b0a5')
    # The relocated NegateX leaf must retain its exact body through RTS.
    def leaf(raw,target):
        base=16+((injury-16)//8192)*8192
        c=NesMPU();c.memory[0xa000:0xc000]=raw[base:base+8192]
        d=Disassembler(c);pc=target
        for _ in range(64):
            n,_=d.instruction_at(pc);pc+=n
            if c.memory[pc-n]==0x60:return bytes(c.memory[target:pc])
        raise AssertionError('NegateX leaf did not terminate')
    assert leaf(old,0xa5e6)==leaf(new,0xa5b0)
    result=dict(passed=not added and not added_calls,ROM_sha256=sha(new),
        changed_bytes=len(changes),all_other_bytes_exact=True,
        movement_before=before,movement_after=after,
        added_write_operands=sorted(added),added_external_calls=sorted(added_calls),
        pull_uses_existing_call_and_jump=True,injury_relocated_leaf_exact=True,
        scope='Linear assembled Movement instruction audit, exact existing Pull targets and relocated Injury leaf, full-image change containment. No new write operands or external Movement calls; no global allocation claim.')
    (O/'current-writer-preservation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if not k.startswith('movement_')}))
    assert result['passed']

if __name__=='__main__':main()
