"""Rebind the verified Mario the Tank walk and observe the shared side gate."""
import argparse
import json
from pathlib import Path

from prepare_selected_native_packet_v1 import R, prepare, sha

PRIOR = R/'build/mario-tank-visible-host-1101-v5/native-final-smoke'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    controller=PRIOR/'controller.lua'
    bound=json.loads((PRIOR/'ready.json').read_text())
    assert bound['bindings'][str(controller)]==sha(controller)
    text=controller.read_text()
    assert 'emu.write' not in text
    anchor="local frame,age,phase,done,cycles=0,0,'title',false,0"
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'''
L.MarioVariant=0x730a
local tankSide=0
emu.addMemoryCallback(function()
 local p=emu.convertAddress(0xb755)
 if p and p.memType==emu.memType.nesWorkRam and p.address==0x5755 then tankSide=tankSide+1 end
end,emu.callbackType.exec,0xb755)
''')
    assert text.count('emu.stop(')==1
    text=text.replace('emu.stop(',"assert(tankSide>0,'Actual Tank side entry reached in WRAM 2');print('TANK_SIDE '..tankSide);emu.stop(")
    prepare(args.output,args.rom,text,[Path(__file__),controller,PRIOR/'ready.json'],expected=sha(args.rom),
            timeout=120,allow_interactive=True,scope='Controller-only Tank walk with actual shared side entry and boot sprites.')


if __name__=='__main__':
    main()
