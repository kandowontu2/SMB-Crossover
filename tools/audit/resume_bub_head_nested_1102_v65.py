"""Run64 after discarding only fixture output-log history before cloning.

CPU/bus state is unchanged; old cold/startup write logs are not CPU inputs.
"""
import argparse,hashlib
from pathlib import Path
import check_bub_head_nested_phases_1102_v64 as P
from prepare_selected_native_packet_v1 import sha

def critical(m):
    return(P.H.state(m),P.H.audio(m),bytes(m.vram),m.rawtags[:],m.banks[:],m.chr_latches[:],
        m.upper,m.lastset,m.ppu_addr,m.toggle,m.buffer,m.ppuctrl,m.ppu_reads,m.protection[:],m.corrupt_at,
        bytes(list.__getitem__(m,slice(0,65536))))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['gather','replay'],required=True);parser.add_argument('--identity',type=int,choices=[0,1]);args=parser.parse_args()
    original=P.H.seeds;original_bindings=P.bindings
    def seeds(b,route):
        result=original(b,route)
        for m,cell in result:
            before=critical(m)
            # Append-only Python diagnostics, not emulated registers/RAM,
            # mapper/PPU state, a readback latch, clocks or hardware history.
            m.writes=[];m.ram_writes=[];m.ppu_log=[]
            assert critical(m)==before
        return result
    def bindings():
        files=[Path(__file__),P.R/'tools/audit/arthur_cache_host_controls_v1.py',P.R/'tools/audit/check_tmnt_render_oa.py',P.R/'tools/audit/verify_native_relocation.py']
        return {**original_bindings(),**{str(f.relative_to(P.R)):sha(f)for f in files}}
    P.H.seeds=seeds;P.bindings=bindings
    try:
        if args.phase=='gather':assert args.identity is not None;P.gather(args.identity)
        else:P.replay()
    finally:P.H.seeds=original;P.bindings=original_bindings

if __name__=='__main__':main()
