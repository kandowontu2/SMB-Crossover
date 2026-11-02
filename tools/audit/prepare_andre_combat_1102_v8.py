"""Do not suppress grounded enemy responses during the jump cooldown."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    source=O/'native-andre2/controller.lua';text=source.read_text()
    marker='  local danger=nearest()'
    assert text.count(marker)==1
    text=text.replace(marker,marker+'\n  if ground and danger and danger<=44 then pad.right=false;pad.b=updates%18<3 end')
    rom=O/'candidate2.nes'
    prepare(O/'native-andre3',rom,text,[Path(__file__),source,O/'native-andre2/capture/result.json'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller-only correction: ground combat remains available during postlanding jump cooldown. Original attack pulse and ROM unchanged; actual active1-2 with unchanged lives still required.')
if __name__=='__main__':main()
