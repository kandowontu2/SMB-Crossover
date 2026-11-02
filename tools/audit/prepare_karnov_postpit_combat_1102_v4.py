"""Preserve verified pipe traversal; use early falling-enemy response after pit1."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/karnov-crouch-route-1102-v1'
def main():
    source=O/'native-falling/controller.lua';text=source.read_text()
    old='if flag>0 and flag<128 and id<21';assert text.count(old)==1
    text=text.replace(old,'if wx>=1140 and flag>0 and flag<128 and id<21')
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    prepare(O/'native-postpit',rom,text,[Path(__file__),source,O/'native-falling/capture/result.json'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller correction: retain previously verified pre1140pipe inputs, do not wait on enemies below pipe tops; early falling enemy response only after first pit. No ROM changes, real active1-2 required.')
if __name__=='__main__':main()
