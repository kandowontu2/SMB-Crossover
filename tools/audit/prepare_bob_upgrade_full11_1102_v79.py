"""Reuse the qualified current route and genuine Bob Select menu metadata."""
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-upgrades-root-bob-1102-v79'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-upgrades-root-route-1102-v78/bub-full11/controller.lua';bob=R/'build/bub-menu-candidate-1102-v2/native-current-landing-bob-full11-source-wall/controller.lua'
    text=source.read_text();match=re.search(r'^local Q=(.*)$',bob.read_text(),re.M);assert match
    assert '["bob"]=1' in match[1] and '["tag"]="BOB"' in match[1]
    text,n=re.subn(r'^local Q=.*$',lambda m:'local Q='+match[1],text,count=1,flags=re.M);assert n==1
    assert text.count('["identity"]=0')==1;text=text.replace('["identity"]=0','["identity"]=1')
    rom=R/'build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes'
    prepare(O/'bob-full11',rom,text,[Path(__file__),source,bob,R/'build/bub-upgrades-root-route-1102-v78/bub-full11/capture/full11.json'],expected=sha(rom),timeout=240,allow_interactive=True,scope='Same exactb7e2, genuine Select twice fromMrGimmick toBob and confirm. Current source hooks/fullcookie remain rebound; observerrequires identity1. Same originalbubble/source supported stairs and all fourpipes/threepits plus naturalcombat/lives/hardwareguards; no emulated writes/helpers/earnedblockclaim.')
if __name__=='__main__':main()
