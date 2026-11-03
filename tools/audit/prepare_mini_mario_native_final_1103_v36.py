"""One bounded packet root: corrected smoke35 and unchanged route36."""
from pathlib import Path
import argparse,sys
import prepare_mini_mario_native_smoke_1103_v31 as S
import prepare_mini_mario_full11_1103_v28 as F
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/mini-mario-native-packets-1103-v36'

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--labels',type=Path,required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    smoke,deps=S.build(a.rom,a.sha,a.kernel,a.labels,a.ref)
    prepare(O/'smoke35',a.rom,smoke,[*deps,Path(__file__)],expected=a.sha,timeout=180,allow_interactive=True,
        scope='Unchanged31/32 exactsource-epoch Mini smoke rebound to graphics32 successor: idle20/right16/reverse/A20/apex/support, originalbbox, stablezero, trueMMC5sprite/physicalsourcepixels/DMA/P0. TwoPNG/noRAMwrites. Prior firstscrollnegative preserved.')
    text,deps=F.controller(a.rom,a.sha,a.kernel,a.labels,a.ref)
    for old,new in [
        ("if route_previous and x<=route_previous+0.05 then route_stationary=route_stationary+1 else route_stationary=0 end\n route_previous=x", "if route_previous and x<=route_previous+1 then route_stationary=route_stationary+1 else route_stationary=0;route_previous=x end"),
        ("check(route_max>3200,'Native castle route reached without shortcut')", "check(route_max>3000,'Source route reached finalcastle approach before native endsequence')")]:
        assert text.count(old)==1;text=text.replace(old,new)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    prepare(O/'full36',a.rom,text,[*deps,Path(__file__),R/'tools/audit/prepare_mini_mario_full11_1103_v33.py'],expected=a.sha,timeout=240,allow_interactive=True,
        scope='Same33source-adaptive originalRight+B/jump+authorizedwallcling route rebound to graphics32 successor. Actual4pipes/3authoredpits/no-life-loss/active1-2/source>3000 and highwaterstall guards. TwoPNG/noRAMseeds/helpers/physicschanges. No stage claim untilrootrun.')

if __name__=='__main__':main()
