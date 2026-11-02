"""Exercise Andre's attack while descending into the enemy group after pipe3."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    source=O/'native-wwf-5/controller.lua';text=source.read_text()
    marker='if jumping then pad.a=jumpAge<36 end'
    assert text.count(marker)==1
    text=text.replace(marker,'if jumping then pad.a=jumpAge<36;pad.b=updates%18<3 end')
    rom=O/'candidate2.nes'
    prepare(O/'native-andre2',rom,text,[Path(__file__),source,O/'native-wwf-5/capture/result.json'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller-only Andre route adds freshBattack pulses while jumping. Previous unchanged Hogan controller landed into enemygroup afterpipe3 and lostlife atX805. No ROM/physics/helpers changed; retain full1-1/active1-2/no-life-loss assertions.')
if __name__=='__main__':main()
