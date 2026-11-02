"""Native world probes must return tile/coordinate outputs, not rejection AXYP."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_dispatch_1101_v16 as P
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
O=R/'build/metal-storm-probes-1101-v17'
def main():
    O.mkdir(exist_ok=True);b=qualified(P.O/'candidate.nes');raw=bytearray(b['raw']);patches=[]
    for row,name in [(10,'BlockBufferColli_Head'),(14,'BlockBufferColli_Side')]:
        pc=address(b,name);assert 0x8000<=pc<0xa000
        at=16+78*8192+0xb6d+3*row;old=bytes(raw[at:at+3]);assert old==bytes([0x4c,0xdc,0xab])
        new=bytes([0x4c,pc&255,pc>>8]);raw[at:at+3]=new
        patches.append(dict(row=row,native=name,offset=at,old=old.hex(),new=new.hex()))
    source=R/'tools/reference/metal_storm_native_transport_1101_v12.inc'
    t=source.read_text();old='.repeat 37,I\n jmp Ms12Enter\n.endrepeat';assert t.count(old)==1
    new='.repeat 37,I\n .if I=10\n  jmp BlockBufferColli_Head\n .elseif I=14\n  jmp BlockBufferColli_Side\n .else\n  jmp Ms12Enter\n .endif\n.endrepeat'
    (O/'metal_storm_native_transport.inc').write_text('.import BlockBufferColli_Head,BlockBufferColli_Side\n'+t.replace(old,new))
    (O/'candidate.nes').write_bytes(raw)
    for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
    q=dict(passed=True,installed=False,ROM_sha256=P.P.sha(O/'candidate.nes'),base_ROM_sha256=P.P.sha(P.O/'candidate.nes'),patches=patches,
           rationale='ROM veneers for typed head/side probes use canonical native block-buffer routines and their genuine A/Y/R4/R5 outputs. The generic RAM reject handler preserves incoming A and cannot implement this query contract.')
    (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
