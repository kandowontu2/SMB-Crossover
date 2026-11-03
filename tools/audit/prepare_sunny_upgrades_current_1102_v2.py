"""Wait for actual transform completion and observe the fire SFX write."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R
O=R/'build/sunny-upgrades-current-1102-v2'

def main():
    source=R/'tools/audit/prepare_sunny_upgrades_current_1102_v1.py';text=source.read_text()
    text=text.replace("O=R/'build/sunny-upgrades-current-1102-v1'","O=R/'build/sunny-upgrades-current-1102-v2'")
    text=text.replace("['sunny_upgrades_11_v4.lua'","['sunny_upgrades_11_v5.lua','sunny_upgrades_11_v4.lua'")
    anchor="    prepare(O/'native',ROM,text,[Path(__file__),source,*deps],expected=sha(ROM),timeout=240,"
    assert anchor in text
    patch='''    text=text.replace("if r('PlayerStatus')>=1 then mushroomSeen=true end","if r('GuestPowerupActive')==0 and r('PlayerStatus')>=1 then mushroomSeen=true end")
    text=text.replace("if r('PlayerStatus')==2 then flowerSeen=true end","if r('GuestPowerupActive')==0 and r('PlayerStatus')==2 then flowerSeen=true end")
    text=text.replace(" if r('Square1SoundQueue')&32~=0 then fireCues=fireCues+1 end",'')
    hook="emu.addMemoryCallback(function(_,v)if entered and r('SelectedCharacter')==23 and v&32~=0 then fireCues=fireCues+1 end end,emu.callbackType.write,C.ram.Square1SoundQueue)\\n"
    text=text.replace("hook('GameLoopOwned',function()",hook+"hook('GameLoopOwned',function()")
'''
    text=text.replace(anchor,patch+anchor)
    scope={'__name__':'sunny_upgrades','__file__':str(Path(__file__))};exec(compile(text,str(source),'exec'),scope);scope['main']()
if __name__=='__main__':main()
