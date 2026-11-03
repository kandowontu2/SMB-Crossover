"""Distinct full route for camera fix; high-water stall and native castle handoff."""
from pathlib import Path
import argparse,sys
import prepare_mini_mario_full11_1103_v28 as P
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/mini-mario-full11-packet-1103-v33'

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--labels',type=Path,required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    text,deps=P.controller(a.rom,a.sha,a.kernel,a.labels,a.ref)
    old="if route_previous and x<=route_previous+0.05 then route_stationary=route_stationary+1 else route_stationary=0 end\n route_previous=x"
    new="if route_previous and x<=route_previous+1 then route_stationary=route_stationary+1 else route_stationary=0;route_previous=x end"
    assert text.count(old)==1;text=text.replace(old,new)
    old="check(route_max>3200,'Native castle route reached without shortcut')"
    new="check(route_max>3000,'Source route reached finalcastle approach before native endsequence')"
    assert text.count(old)==1;text=text.replace(old,new)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    prepare(O/'full11',a.rom,text,[*deps,Path(__file__)],expected=a.sha,timeout=240,allow_interactive=True,
        scope='Distinct Mini nonshortcut1-1 cameraexport successor. Same original run/jump+authorizedwallcling inputs, all7authoredobstacles and actualactive1-2/lives guards. Highwater400sourceepoch stallbound tolerates1pxoscillation; source>3000approach guard acknowledges nativeengine5castle owns laterwalk. No sourcephysics/helper/RAMwrites; twoPNG.28viewporttimernegative preserved.')

if __name__=='__main__':main()
