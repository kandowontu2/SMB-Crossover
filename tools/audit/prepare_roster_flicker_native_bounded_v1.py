"""Observe every roster identity transition without frame-image sequences."""
from pathlib import Path
import argparse,json,sys
from prepare_selected_native_packet_v1 import R,prepare


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--expected',required=True)
    a=ap.parse_args()
    template=R/'tools/reference/roster_flicker_native_bounded_v1.lua'
    text='local EXPECTED_SHA='+json.dumps(a.expected)+'\n'+template.read_text()
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(text)
    assert ok,error
    prepare(a.output,a.joint/'candidate.nes',text,[Path(__file__),template,a.joint/'source-stage.json'],expected=a.expected,timeout=180,
            scope='Cold controller-only D-pad snake through32 slots and full Select wrap for all86 identities. Per-frame display/static-portrait fingerprints and visible-scanline PPU/CHR events; at most4PNG. Diagnostic, not gameplay qualification.')


if __name__=='__main__':main()
