"""Trace the earlier menu profile that first sets the inherited native tier."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-head-status-history-1103-v86'
PIN='cc7b9bddfd39c62fadb5c1afc34bc82361432eab5a8a8e5b5a18bde184813a4e'
def main():
    O.mkdir(exist_ok=True)
    source=R/'build/bub-head-start-status-1103-v85/bub-status/controller.lua'
    text=source.read_text();needle=" if r('SelectedCharacter')~=39 then return end";assert text.count(needle)==1
    text=text.replace(needle," local owner=r('SelectedCharacter')")
    needle='local key=tostring(pc)';assert text.count(needle)==1
    text=text.replace(needle,'local key=tostring(owner)..\':\'..tostring(pc)')
    needle='status_writes[key]={pc=pc,';assert text.count(needle)==1
    text=text.replace(needle,'status_writes[key]={owner=owner,frame=frame,pc=pc,')
    rom=R/'build/bub-head-root-candidate-1103-v81/bub-source-head.nes'
    prepare(O/'bub-history',rom,text,[Path(__file__),source],expected=PIN,timeout=90,allow_interactive=True,scope='Same private diagnostic, source/hardware assertions and no writes. Observe all actual menu owners and first native-tier setter, not only raw39. One deduplicated write-history JSON; no earned-powerup or installed claim.')
if __name__=='__main__':main()
