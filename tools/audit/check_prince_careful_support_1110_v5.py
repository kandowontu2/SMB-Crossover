"""Fund original careful-step cap support in the existing329 packet, in memory.

No frozen file is changed and no ROM, receipt or compiler temporary is written.
The old128B worker is assembled independently and matched to actual cold bytes.
"""
import argparse
import json
import re
import sys
from unittest.mock import patch
from py65.assembler import Assembler

import check_prince_floor_carrier_1110 as Q

C,N,I,F=Q.C,Q.N,Q.I,Q.Foot.F
SOURCE=Q.R/'tools/reference/prince_careful_support_1110_v5.s'
ORIGIN,BOUND,OLD,HOOK=0xd56a,0xd622,0xd6d1,0xa6f6
PARENT='c3fb87bcbab3a9ad2d3537f9444797fee50344c8a08195d8b9b4b02ff309bba3'


def assemble(bundle,*,old=False):
    text=SOURCE.read_text()
    if old:
        needle=' cmp #1\n beq ActionMode\n cmp #42\n bne Empty\nActionMode:\n'
        assert text.count(needle)==1
        text=text.replace(needle,' cmp #1\n bne Empty\n')
    origin=OLD if old else ORIGIN
    lines=[line.split(';',1)[0].strip() for line in text.splitlines()]
    labels={line[:-1]:origin for line in lines if line.endswith(':')}
    asm=Assembler(N.NesMPU(memory=[0]*65536))
    for _ in range(2):
        code=bytearray()
        for line in lines:
            if not line or line.startswith('.'):continue
            if line.endswith(':'):labels[line[:-1]]=origin+len(code);continue
            line=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\b',
                lambda m:f'${labels[m[1]]:04x}' if m[1] in labels else m[0],line)
            line=re.sub(r'#(\d+)\b',lambda m:f'#${int(m[1]):02x}',line)
            code.extend(asm.assemble(line,pc=origin+len(code)))
    return bytes(code),labels


def apply(seed):
    code,_=assemble(seed.bundle);old,_=assemble(seed.bundle,old=True)
    assert len(old)==128 and len(code)==132 and ORIGIN+len(code)<=BOUND
    assert bytes(seed.ram[2][OLD-0xc000:OLD-0xc000+128])==old,'Actual old worker differs from independent source'
    assert bytes(seed.ram[3][HOOK-0xa000:HOOK-0xa000+3])==bytes([0x20])+OLD.to_bytes(2,'little')
    assert Q.ADMISSION_PC+44==ORIGIN and Q.Foot.ORIGIN+103==Q.ADMISSION_PC
    assert bytes(seed.ram[2][ORIGIN-0xc000:BOUND-0xc000])==bytes([255])*(BOUND-ORIGIN),'Owned gap is not unused FF'
    before=[bytes(b) for b in seed.ram]
    seed.ram[2][ORIGIN-0xc000:ORIGIN-0xc000+len(code)]=code
    seed.ram[3][HOOK-0xa000+1:HOOK-0xa000+3]=ORIGIN.to_bytes(2,'little')
    for bank in (0,1):assert bytes(seed.ram[bank])==before[bank]
    assert bytes(seed.ram[2][:ORIGIN-0xc000])==before[2][:ORIGIN-0xc000]
    assert bytes(seed.ram[2][ORIGIN-0xc000+len(code):])==before[2][ORIGIN-0xc000+len(code):]
    changed=[i for i,(a,b) in enumerate(zip(before[3],seed.ram[3])) if a!=b]
    assert changed==[HOOK-0xa000+1,HOOK-0xa000+2],changed
    return seed


def proposal():
    parent=Q.proposal()
    assert parent[3]['in_memory_SHA256']==PARENT
    original=Q.Foot.apply
    def derivative(seed):return apply(original(seed))
    with patch.object(Q.Foot,'apply',derivative):result=Q.proposal()
    _,trial,chunks,layout,_,_,_=result
    assert result[0]['raw']==parent[0]['raw']
    original_chunks=parent[2]
    assert chunks[2]==original_chunks[2]
    allowed={2:set(range(ORIGIN-0xc000,ORIGIN-0xc000+132)),
        3:{HOOK-0xa000+1,HOOK-0xa000+2}}
    for old,new,bank,start in ((original_chunks[0],chunks[0],3,0),
                              (original_chunks[1],chunks[1],2,0x800)):
        diff={start+i for i,(a,b) in enumerate(zip(old,new)) if a!=b}
        assert diff<=allowed[bank],(bank,sorted(diff-allowed[bank])[:8])
    assert layout['carrier_pages']==parent[3]['carrier_pages'] and layout['loader_bytes']==446
    assert layout['spare']>=0 and layout['old_carriers_exact_art_bytes']==31072
    layout.update(derivative_parent_in_memory_SHA256=PARENT,
        careful_worker_half_open=[ORIGIN,ORIGIN+132],owned_FF_gap_half_open=[ORIGIN,BOUND],
        old_support_worker_half_open=[OLD,OLD+128],old_support_worker_preserved=True,
        donor_core_change='Only existing D297 JSR operand; original motor/actor/health/data unchanged',
        source_SHA256=Q.digest(SOURCE.read_bytes()))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route',action='store_true')
    parser.add_argument('--cold',action='store_true')
    args=parser.parse_args()
    result=proposal();_,trial,chunks,layout,program,_,_=result
    print('CAREFUL_LAYOUT '+json.dumps(layout,separators=(',',':')),flush=True)
    if args.cold:
        _,cold=Q.actual_cold(trial,chunks,layout,program)
        print('CAREFUL_COLD '+json.dumps(cold,separators=(',',':')),flush=True)
    if args.route:
        import check_prince_wait_pose_route_1110_v3 as Route
        with patch.object(Q,'proposal',lambda:result),patch.object(sys,'argv',[Route.__file__,'--park','careful']):Route.main()


if __name__=='__main__':main()
