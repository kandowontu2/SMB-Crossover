"""Detached 6502 contracts for proposed DK pointer-wrapper funding.

Flat component memory only: no cartridge or live overlay is composed.
"""
from collections import defaultdict
from hashlib import sha256
import itertools
import json

import measure_dkjr_floor_entry_fit_1114 as Fit

N=Fit.Indirect.G.N


def models(model,proposal):
    old=bytearray((i*29+11)&255 for i in range(65536))
    old[0xa000:0xbfe0]=model['original']['body'][:0x1fe0]
    new=bytearray(old)
    for row in proposal['fragments']:
        at=row['PC'];new[at:at+row['bytes']]=bytes.fromhex(row['proposed_hex'])
    return old,new


def execute(memory,pc,stop,*,a=85,x=37,y=0,p=0x61,sp=224,limit=20000):
    cpu=N.NesMPU(memory=memory,pc=pc);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=a,x,y,p,sp
    low=sp
    for step in range(limit):
        if cpu.pc==stop:return cpu,low,step
        assert memory[cpu.pc],('Detached BRK',hex(cpu.pc))
        low=min(low,cpu.sp);cpu.step()
    raise AssertionError(('Detached component bound',hex(cpu.pc),hex(stop)))


def run():
    proposal,model=Fit.measure(include_model=True)
    rows=[r for r in model['original']['rows']if r['exact_current']]
    labels=model['proposed']['symbols'];memories=models(model,proposal)
    translations=0;abi=0;digest=sha256();minimum=224
    for row in rows:
        oldpc=row['PC'];newpc=labels[row['label']]
        oldcell=oldpc+22
        newcell=model['original']['reader_cell']if row['operation']=='lda'else labels['StoreCell']
        # All256 pointer high values, low-byte edge cases and every Y are
        # factored: translation does not read Y; effective-index addition
        # is the same unchanged abs,Y opcode. Before-data stops permit
        # even code/MMIO addresses without claiming their data invariant.
        for high,low,y in itertools.product(range(256),(0,255),(0,255)):
            outputs=[]
            for index,memory in enumerate(memories):
                pointer=row['pointer'];memory[pointer:pointer+2]=bytes((low,high))
                cpu,depth,_=execute(memory,(oldpc,newpc)[index],(oldcell,newcell)[index],y=y)
                minimum=min(minimum,depth)
                at=(oldcell,newcell)[index]
                address=int.from_bytes(memory[at+1:at+3],'little')
                expected=low+256*(high|0xc0 if high<8 else high)
                assert address==expected
                # PHP/PLP normalizes B/U exactly as in the current wrapper.
                assert (cpu.a,cpu.x,cpu.y,cpu.p)==(85,37,y,0x71),(row['label'],index,high,low,y,hex(cpu.p))
                assert cpu.sp==(224 if index==0 else 222)
                outputs.append((address,(address+y)&65535))
            assert outputs[0]==outputs[1];translations+=1
        # Legal RAM data domains + a separate generic ROM-data domain.
        # All256 incoming P include V1, decimal and both incoming C values.
        for p,high,y in itertools.product(range(256),(2,4,0xe1),(0,255)):
            target=((high|0xc0 if high<8 else high)<<8)+7+y
            outputs=[]
            for index,memory in enumerate(memories):
                memory[row['pointer']:row['pointer']+2]=bytes((7,high))
                memory[target]=153
                cpu,depth,_=execute(memory,(oldpc,newpc)[index],(oldpc+25,newpc+3)[index],y=y,p=p)
                minimum=min(minimum,depth)
                outputs.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,memory[target]))
            assert outputs[0]==outputs[1],(row['label'],p,high,y,outputs)
            digest.update(bytes(outputs[0]));abi+=1
    whole=[];cycle_deltas=defaultdict(set);source_template=bytes((i*73+19)&255 for i in range(0x900))
    oldentry=model['original']['labels']['D_ea08'];newentry=labels['D_ea08']
    for operation,p,xpos,ypos,tile in itertools.product(range(5),(0x20,0x21,0x61,0xff),
            (0,248),(0,240),(0,127)):
        outputs=[];cycles=[]
        for index,memory in enumerate(memories):
            memory[0xc000:0xc900]=source_template
            memory[0xc000:0xc006]=bytes((xpos,ypos,tile,0x24,0x10,0x17))
            cpu=N.NesMPU(memory=memory,pc=(oldentry,newentry)[index])
            cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=operation,37,91,p,224
            cpu.stPushWord(0x5aff);depth=cpu.sp
            for steps in range(10000):
                if(cpu.pc,cpu.sp)==(0x5b00,224):break
                depth=min(depth,cpu.sp);cpu.step()
            else:raise AssertionError(('Whole draw bound',index,operation))
            minimum=min(minimum,depth)
            outputs.append(((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp),bytes(memory[0xc000:0xc900])))
            cycles.append(cpu.processorCycles)
        assert outputs[0]==outputs[1],('Whole original draw contract',operation,p,xpos,ypos,tile)
        digest.update(bytes(outputs[0][0])+outputs[0][1]);whole.append(operation)
        cycle_deltas[operation].add(cycles[1]-cycles[0])
    return dict(passed=True,detached_flat_component_model=True,ROM_composed=False,
        all17_current_wrappers=True,pointer_high_values=256,
        pointer_translation_edge_cases=translations,all256_P_ABI_cases=abi,
        whole_original_draw_operations=sorted(set(whole)),whole_draw_contexts=len(whole),
        source_RAM_bytes_exact_each_whole_case=0x900,aggregate_SHA256=digest.hexdigest(),minimum_SP=minimum,
        measured_extra_draw_cycles_by_operation={op:sorted(values)for op,values in cycle_deltas.items()},
        pointer_translation_algorithm_unchanged=True,existing_head_reader_bytes_changed=False,
        outputs_written=0,actual_IRQ_and_legal_native_caller_closure=False,
        scope='Detached CPU translation/AXYP/SP and source draw equivalence only. No ROM, live overlay, runtime admission, IRQ, candidate or native claim.')


if __name__=='__main__':print('DKJR_INDIRECT_CONTRACTS '+json.dumps(run(),separators=(',',':')),flush=True)
