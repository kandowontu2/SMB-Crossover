"""Current Prince window/math/preimage census only; no remap placement grant."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
import current_prince_body_research_f11_1114 as Current
import check_current_world_sprite_windows_1114 as Old


def run(current):
    P=Old.New.Previous.Prince
    _,chunks,_=P.extract(current.original);runtime,metadata,state=chunks
    assert P.extract(current.original)==P.extract(current.reference1daca)
    R=Old.R
    base=R/'tools/audit/prepare_prince_climb_funded_1109_v1.py'
    mixed=R/'tools/audit/check_prince_run_support_funding_1110.py'
    geometry=Old.pure_function(base,'geometry',{})
    geometry=Old.pure_function(mixed,'geometry',{'P':SimpleNamespace(geometry=geometry)})
    poses=parts=0;page_counts=Counter();indices=Counter();tiles=set();page_ids=set();three=[]
    for frame in range(239):
        result=geometry(metadata,frame)
        if result is None:continue
        prefix,records=result;n=prefix[0]&15;pages=list(prefix[1:1+((prefix[0]>>4)&3)])
        assert len(records)==3*n and 1<=len(pages)<=3
        for tile in records[1::3]:
            assert tile&1==0 and tile<192
            index=Old.tile_window(tile);assert index<len(pages)
            mapped=tile+65
            assert mapped<=255 and Old.tile_window(mapped)==index+5 and mapped&62==tile&62
            indices[index]+=1;tiles.add(tile);parts+=1
        page_counts[len(pages)]+=1;page_ids.update(pages);poses+=1
        if len(pages)==3:three.append(dict(frame=frame,pages=pages))
    assert poses==204
    pads=[]
    i=0
    while i<len(runtime):
        if runtime[i]!=234:i+=1;continue
        end=i+1
        while end<len(runtime)and runtime[end]==234:end+=1
        if end-i>=9:
            pads.append(dict(CPU_half_open=[0xa000+i,0xa000+end],bytes=end-i,
                preimage_SHA256=sha256(runtime[i:end]).hexdigest(),
                surrounding_hex=runtime[max(0,i-8):min(len(runtime),end+8)].hex(),
                unchanged_in_e418=not(i<8099 and end>7650),
                free_or_granted=False))
        i=end
    # Actual source mapping is disassembled directly; the frozen renderer
    # checker/default remains untouched and is never fed a newer image.
    from py65.devices.mpu6502 import MPU
    from py65.disassembler import Disassembler
    memory=bytearray(65536);memory[0xa000:0xa000+len(runtime)]=runtime
    memory[0xc800:0xc800+len(metadata)]=metadata
    d=Disassembler(MPU(memory=memory));code=[]
    for lo,hi in((0xbc30,0xbc55),(0xbc6f,0xbc97),(0xbdc3,0xbde2),(0xd79c,0xd7c9)):
        pc=lo
        while pc<hi:
            size,instruction=d.instruction_at(pc)
            code.append(dict(PC=pc,hex=bytes(memory[pc:pc+size]).hex(),instruction=instruction));pc+=size
    return dict(current_input=current.metadata(),runtime_SHA256=sha256(runtime).hexdigest(),
        metadata_SHA256=sha256(metadata).hexdigest(),poses=poses,facings=2,parts_per_facing=parts,
        renderer_BBC1_BDE2_unchanged_in_e418=True,
        page_counts=dict(page_counts),page_ids=sorted(page_ids),source_windows=sorted(indices),three_page_poses=three,
        uniform_option=dict(window_map={0:5,1:6,2:7},tile_transform='even tile +65',
            all_pattern_pair_offsets_exact=True,all_pixels_metadata_and_scripts_unchanged=True,
            native_windows_0_through4_unoccupied_by_this_option=True,
            publisher_helper_bytes=9,publisher_flag_liveness_not_yet_proven=True,
            tile_wrapper_bytes_with_P_preservation=9,placement_granted=False),
        code=code,EA_runs_at_least9=pads,
        pure_reader_sources={p.name:sha256(p.read_bytes()).hexdigest()for p in(base,mixed)},
        gameplay_or_render_fixtures=0,ROM_changes=0,Mesen=False,outputs=0)


if __name__=='__main__':
    q=run(Current.load(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')));q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(q,separators=(',',':')),flush=True)
