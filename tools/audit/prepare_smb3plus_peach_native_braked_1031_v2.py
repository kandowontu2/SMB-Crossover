"""Keep the16px walk assertion; hold Right two more frames before braking."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_smb2_firstlooks_bg_eye_v6 as V
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def main():
    source=R/'build/smb3plus-peach-native-braked-1031-v1/peach'
    folder=R/'build/smb3plus-peach-native-braked-1031-v2/peach'
    assert not folder.exists()
    ready=json.loads(B.read(source/'ready.json'));B.bound(ready)
    negative=json.loads(B.read(source/'capture/result.json'))
    assert not negative['passed'] and negative['walked']==15 and negative['landed']
    assert negative['source_Main']==negative['source_movement']==negative['main_updates']==360
    b=scoped_load(Path(ready['ROM']));text=B.read(source/'controller.lua')
    old='age>=20 and age<35 then b.right=true end';assert text.count(old)==1
    text=text.replace(old,'age>=20 and age<37 then b.right=true end')
    names=['MbFloatExpired','MbFloatTimer','MbFloatReady']
    text=''.join(f'L["{n}"]={address(b,n)}\n' for n in names)+text
    text+='''
local hoverFile=assert(io.open(OUTPUT..'hover-observations.csv','w'))
hoverFile:write('frame,held,ready,timer,expired,Y\\n');hoverFile:flush()
emu.addMemoryCallback(function()
 if phase~='game' or bank(P.main_return)~=B.GameLoop then return end
 hoverFile:write(table.concat({frame,r('SavedJoypadBits'),r('MbFloatReady'),r('MbFloatTimer'),
  r('MbFloatExpired'),r('Player_Y_Position')},',')..'\\n');hoverFile:flush()
end,emu.callbackType.exec,P.main_return)
'''
    folder.mkdir(parents=True);script=folder/'controller.lua';B.write(script,text)
    runner=folder/'run.py';B.write(runner,V.RUN)
    ready['bindings'].update({str(p):B.sha(p) for p in [Path(__file__),source/'ready.json',
        source/'capture/result.json',source/'capture/binding.json',script,runner]})
    ready['retained_brake_fixture_negative']=str(source/'capture/result.json')
    ready['controller_change']='Right20..36, brake37..74, A75..229. Original16px walk and all native assertions retained; read-only hover logging added.'
    B.write(folder/'ready.json',json.dumps(ready,indent=2)+'\n')
    print(json.dumps(dict(prepared=str(folder/'ready.json'),native=False)))


if __name__=='__main__':main()
