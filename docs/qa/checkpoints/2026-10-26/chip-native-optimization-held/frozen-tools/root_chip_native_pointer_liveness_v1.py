"""Conservative pointer liveness over the original player's call/abort graph."""
from collections import deque
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler


def pointer_liveness(mem, seen, dispatch_tables, dispatch_calls):
    cpu=MPU(memory=mem);dis=Disassembler(cpu)
    # The actual four dispatcher calls consume their own inline-table JSR
    # return, set the original numeric C1/C2, and tail-enter802C. Ordinary
    # The real command8541 discards one caller's return. Ordinary data-stack
    # operations are not control edges. Actual physical stack balance and
    # numeric branch feasibility are separate original-trace CPU controls.
    states={};pending=deque();reads={};writers={1:set(),2:set()};exits=set()

    def merge(pc,stack,low,high,dispatch=None):
        assert pc in seen,('Unknown instruction',hex(pc))
        assert len(stack)<40,('Unbounded source stack',hex(pc),stack)
        key=(pc,stack,dispatch);old=states.get(key,(frozenset(),frozenset()))
        new=(old[0]|frozenset(low),old[1]|frozenset(high))
        if key not in states or new != old:
            states[key]=new;pending.append(key)

    for pc in [0x8000,0xaf99]:merge(pc,(),[None],[None])
    while pending:
        pc,stack,dispatch=pending.popleft();low,high=states[pc,stack,dispatch]
        op,mode=cpu.disassemble[mem[pc]];size,_=dis.instruction_at(pc)
        v=mem[pc+1];word=v+256*mem[pc+2]
        if mode=='zpg' and v in [0xc1,0xc2] and op in ['STA','STX','STY','ASL','LSR','ROL','ROR','INC','DEC']:
            writers[v-0xc0].add(pc)
            if v==0xc1:low=frozenset([pc])
            else:high=frozenset([pc])
        if mode=='iny' and v==0xc1:
            a,b=reads.get(pc,(set(),set()));a.update(low);b.update(high);reads[pc]=(a,b)
        if op=='JSR':
            if word==0x8023:
                assert pc in dispatch_calls
                merge(0x802c,stack,[pc],[pc],pc)
            else:merge(word,stack+(pc+size,),low,high,dispatch)
        elif op=='JMP':
            if mode=='ind':
                assert word==0xc1
                assert dispatch in dispatch_tables
                for target in dispatch_tables[dispatch]:merge(target,stack,low,high)
            else:merge(word,stack,low,high,dispatch)
        elif op=='RTS':
            if stack:
                merge(stack[-1],stack[:-1],low,high,dispatch)
            else:exits.add(pc)
        elif op in ['BRK','RTI']:
            raise AssertionError(('Unexpected source terminal',hex(pc),op))
        else:
            if pc==0x8541:
                assert op=='PLA' and stack,('Source abort underflow',hex(pc),stack)
                stack=stack[:-1]
            assert op not in ['TSX','TXS'],('Unmodeled source stack instruction',hex(pc),op)
            if mode=='rel':merge(pc+2+(v-256 if v>=128 else v),stack,low,high,dispatch)
            merge(pc+size,stack,low,high,dispatch)
    live={1:set(),2:set()}
    for a,b in reads.values():live[1].update(a);live[2].update(b)
    assert all(None not in s for s in live.values()),'Source pointer can be read before initialization'
    proof=dict(abstract_control_states=len(states),source_instruction_states=len({pc for pc,stack,dispatch in states}),
               original_abort_return_consumers=[0x8541,0x8542],max_abstract_call_depth=max(len(stack)for pc,stack,dispatch in states),
               all_conditional_paths_included=True,all_original_dispatch_destinations=len(set(x for row in dispatch_tables.values() for x in row)),
               exits=sorted(exits),live_low_writers=sorted(live[1]),live_high_writers=sorted(live[2]),
               dead_low_writers=sorted(writers[1]-live[1]),dead_high_writers=sorted(writers[2]-live[2]),
               read_predecessors={f'{pc:04x}':dict(low=sorted(a),high=sorted(b)) for pc,(a,b)in sorted(reads.items())},
               limits='Conservative call/abort-graph analysis of pinned source Init/Play and each original inline dispatcher table. All conditional paths are included. Ordinary PHA/PLA/PHP/PLP data-stack contents and numeric branch feasibility are not simulated here; actual physical stacks/data-dependent execution are separately compared against original source traces.')
    return live,proof
