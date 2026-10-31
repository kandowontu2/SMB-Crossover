"""Brake before Peach's hover; retain the first native Goomba-contact failure."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_smb2_firstlooks_bg_eye_v6 as V
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location


def main():
    source=R/'build/smb3plus-menu-native-1031-v1/peach'
    folder=R/'build/smb3plus-peach-native-braked-1031-v1/peach'
    assert not folder.exists()
    ready=json.loads(B.read(source/'ready.json'));B.bound(ready)
    negative=json.loads(B.read(source/'capture/result.json'))
    assert not negative['passed'] and negative['reason']=='native death/life loss'
    b=scoped_load(Path(ready['ROM']))
    text=B.read(source/'controller.lua')
    old='age>=20 and age<45 then b.right=true end';assert text.count(old)==1
    text=text.replace(old,'age>=20 and age<35 then b.right=true end')
    old='age>=45 and age<200 then b.a=true end';assert text.count(old)==1
    text=text.replace(old,'age>=75 and age<230 then b.a=true end')
    label='M3Injury'
    assert label in b['syms']
    prefix=f'L["{label}"]={address(b,label)}\nB["{label}"]={(location(b,label)-16)//8192}\n'
    text=prefix+text
    text+='''
local injuryFile=assert(io.open(OUTPUT..'injury-observations.csv','w'))
injuryFile:write('frame,worldX,Y,sourceX,sourceY,state\\n');injuryFile:flush()
emu.addMemoryCallback(function()
 if bank(L.M3Injury)~=B.M3Injury then return end
 injuryFile:write(table.concat({frame,r('Player_X_Position')+256*r('Player_PageLoc'),
  r('Player_Y_Position'),emu.getState()['cpu.x'],emu.getState()['cpu.y'],r('Player_State')},',')..'\\n');injuryFile:flush()
end,emu.callbackType.exec,L.M3Injury)
'''
    folder.mkdir(parents=True);script=folder/'controller.lua';B.write(script,text)
    runner=folder/'run.py';B.write(runner,V.RUN)
    ready['bindings'].update({str(p):B.sha(p) for p in [Path(__file__),source/'ready.json',
        source/'capture/result.json',source/'capture/binding.json',script,runner]})
    ready['retained_native_negative']=str(source/'capture/result.json')
    ready['controller_change']='Right20..34, brake35..74, A75..229; same body/palette/background/landing/Main/ISR assertions, no RAM or enemy writes.'
    B.write(folder/'ready.json',json.dumps(ready,indent=2)+'\n')
    print(json.dumps(dict(prepared=str(folder/'ready.json'),native=False)))


if __name__=='__main__':main()
