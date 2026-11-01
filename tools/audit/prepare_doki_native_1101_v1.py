"""Prepare one original Doki/USA identity, controller-only and capture bounded."""
from pathlib import Path
import argparse,json,sys
from prepare_selected_native_packet_v1 import R,prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from observe_chip_committed_write import lua


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--variant',type=int,required=True);ap.add_argument('--expected',required=True);a=ap.parse_args();assert 0<=a.variant<8
    b=scoped_load(a.joint/'candidate.nes');template=R/'tools/reference/doki_native_bounded_1101_v1.lua'
    args=dict(sha256=a.expected,variant=a.variant,main_return=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1,chr=list(b['raw'][1048592+796*1024:1048592+808*1024]))
    names=['S2Variant','S2Air','S2Animation','S2Movement','S2InjuryStart','S2Holding','S2Face','S2Ready']
    text='DOKI_ARGS='+lua(args)+'\n'+''.join('L['+json.dumps(n)+']='+str(address(b,n))+'\n'for n in names)+'L.S2Meta='+str(address(b,'S2Graphics::DokiMeta'))+'\n'+template.read_text()
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(text);assert ok,error
    prepare(a.output,a.joint/'candidate.nes',text,[Path(__file__),template,a.joint/'graphics-assembly.json'],expected=a.expected,timeout=160,scope='One Doki/USA cold identity and real native opening route. Exact body descriptors, CHR/OAM/display, real ISR preservation, jump/landing/camera. Four PNG cap; no full-stage claim.')


if __name__=='__main__':main()
