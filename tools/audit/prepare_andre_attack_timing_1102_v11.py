"""Allow original walk action to retire before a fresh local punch edge."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    source=O/'native-andre3/controller.lua';text=source.read_text()
    text=text.replace('local function nearest()','local combatStart=nil\nlocal function nearest()',1)
    marker='  local danger=nearest()';assert text.count(marker)==1
    text=text.replace(marker,marker+'\n  if ground and danger and danger<=44 then combatStart=combatStart or updates else combatStart=nil end')
    old='pad.right=false;pad.b=updates%18<3';assert text.count(old)==2
    text=text.replace(old,'pad.right=false;local attackAge=(updates-(combatStart or updates))%18;pad.b=attackAge>=2 and attackAge<5')
    rom=O/'candidate2.nes'
    prepare(O/'native-andre-timing',rom,text,[Path(__file__),source,O/'native-andre-action/capture/action.csv'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller-only source-directed attack timing: two neutral source updates retire original walk before fresh punch edge, local18update repeat. Actual active1-2/no-life-loss and native helper carry retained.')
if __name__=='__main__':main()
