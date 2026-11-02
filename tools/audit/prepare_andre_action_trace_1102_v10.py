"""Inspect original attack state through the actual failing native encounter."""
from pathlib import Path
import propose_wwf_generic_helper_1102_v1 as P
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    source=O/'native-andre-contact/controller.lua';text=source.read_text()
    b=P.scoped_load(P.BASE)
    previous=0x4000+(P.address(b,'WfPreviousInput')&0x1fff)
    joy=P.address(b,'SavedJoypadBits')
    marker='   lastContact=updates;contactRows=contactRows+1'
    assert text.count(marker)==1
    insert=f"""
   if not actionFile then actionFile=assert(io.open(OUTPUT..'action.csv','w'));actionFile:write('update,x,joy,previous,action,action_counter,pose,pose_counter,damage\\n') end
   actionFile:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d\\n',updates,x,emu.read({joy},emu.memType.nesDebug),emu.read({previous},emu.memType.nesWorkRam),emu.read(0x403c,emu.memType.nesWorkRam),emu.read(0x403e,emu.memType.nesWorkRam),emu.read(0x4032,emu.memType.nesWorkRam),emu.read(0x4034,emu.memType.nesWorkRam),emu.read(0x4089,emu.memType.nesWorkRam)))
   actionFile:flush()
"""
    text=text.replace('local contactRows,lastContact=0,-1','local actionFile=nil\nlocal contactRows,lastContact=0,-1')
    text=text.replace(marker,marker+insert)
    rom=O/'candidate2.nes'
    prepare(O/'native-andre-action',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Original WWF RAM2 action/pose/input fields observed read-only during unchanged failing route. Max180 source-update CSV rows; no native RAM or ROM mutation.')
if __name__=='__main__':main()
