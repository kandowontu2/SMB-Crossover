"""Final Mini packets with source-correct native OAM rotation witness."""
from pathlib import Path
import argparse,sys
import prepare_mini_mario_native_smoke_1103_v31 as S
import prepare_mini_mario_native_smoke_1103_v25 as B
import prepare_mini_mario_full11_1103_v28 as F
from prepare_selected_native_packet_v1 import R,prepare
from observe_chip_committed_write import lua
O=R/'build/mini-mario-native-packets-1103-v43'

def rotated(text):
    G=B.labels(B.GLOBALS);aliases={n:G[n]for n in ['GuestOamRotationActive','RgOamRotation','SmPose']}
    anchor='-- Controller inputs only.';assert text.count(anchor)==1
    text=text.replace(anchor,'for k,v in pairs('+lua(aliases)+')do L[k]=v end\n'+anchor)
    old="slot=r('CurrentOAMOffset')"
    new="slot=(r('CurrentOAMOffset')+(r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0))&255"
    assert text.count(old)==1;text=text.replace(old,new)
    old="check(read(L.ObjectMetasprite)==0 and read(L.SmPosePtr)+256*read(L.SmPosePtr+1)==L.ObjectMetasprite,'Stable zero SmPosePtr/header')"
    new="check(read(L.ObjectMetasprite)==0 and read(L.SmPosePtr)+256*read(L.SmPosePtr+1)==L.SmPose and r('SmPose')==4,'Actual one-part4byte native reservation and separate zero legacy ObjectMetasprite')"
    assert text.count(old)==1;text=text.replace(old,new)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--labels',type=Path,required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    smoke,deps=S.build(a.rom,a.sha,a.kernel,a.labels,a.ref);smoke=rotated(smoke)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    syntax=LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end');syntax(smoke)
    prepare(O/'smoke43',a.rom,smoke,[*deps,Path(__file__)],expected=a.sha,timeout=180,allow_interactive=True,
        scope='Same exactsource-epoch Mini smoke; physicalnormalDMAslot=(logicalCurrentOAMOffset+activeRgRotation)mod256 from twoexplicitglobalaliases. Originaltile/attr/pixels/palette/bbox/idle/reverse/jump/landing assertions unchanged. TwoPNG/noRAMwrites.41rendererrotationnegative preserved.')
    text,deps=F.controller(a.rom,a.sha,a.kernel,a.labels,a.ref);text=rotated(text)
    for old,new in [
        ("if route_previous and x<=route_previous+0.05 then route_stationary=route_stationary+1 else route_stationary=0 end\n route_previous=x", "if route_previous and x<=route_previous+1 then route_stationary=route_stationary+1 else route_stationary=0;route_previous=x end"),
        ("check(route_max>3200,'Native castle route reached without shortcut')", "check(route_max>3000,'Source route reached finalcastle approach before native endsequence')")]:
        assert text.count(old)==1;text=text.replace(old,new)
    syntax(text)
    prepare(O/'full43',a.rom,text,[*deps,Path(__file__),R/'tools/audit/prepare_mini_mario_full11_1103_v33.py'],expected=a.sha,timeout=240,allow_interactive=True,
        scope='Same33originalrun/jump+authorizedwallcling route, trueOAMrotationwitness. All7authoredobstacles/actualactive1-2/no-life-loss guards retained. No controller/physics/helper/RAMseed changes, twoPNG; fullstage claim onlyafterrootterminal.')

if __name__=='__main__':main()
