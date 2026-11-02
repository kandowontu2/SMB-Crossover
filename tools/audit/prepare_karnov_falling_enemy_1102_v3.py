"""Stop before the naturally falling Goomba reaches Karnov's head."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/karnov-crouch-route-1102-v1'
def main():
    source=O/'native-ground/controller.lua';text=source.read_text()
    old=" and math.abs(ey-r('Player_Y_Position'))<48";assert text.count(old)==1
    text=text.replace(old,'')
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    prepare(O/'native-falling',rom,text,[Path(__file__),source,O/'native-ground/capture/result.json'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller-only wait/crouch fire before overhead Goombas fall into contact; previous grounded replay only reacted after enemy fell within48pixels. Original code unchanged, full active1-2 and no death required.')
if __name__=='__main__':main()
