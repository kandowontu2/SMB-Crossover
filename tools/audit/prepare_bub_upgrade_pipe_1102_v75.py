"""Move the real jump input earlier for tall native pipe bubble crossings."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-upgrades-root-route-1102-v75'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-upgrades-root-route-1102-v73/bub-full11/controller.lua';text=source.read_text()
    old='and gap>=0 and gap<=16 then';assert text.count(old)==1
    text=text.replace(old,"and gap>=0 and gap<=(obstacle.kind=='pipe' and obstacle.top==144 and 24 or 16) then")
    rom=R/'build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes'
    prepare(O/'bub-full11',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,scope='Same candidate/controller only. Jump input for64px tall pipes uses actual source gap<=24 instead of<=16, giving ascent before collision against native pipe side after current physical cadence. Prior v73 actual ride too late atx721/y144 is retained. Real earned support/seven crossing/lives/hardware assertions remain unchanged; no physics/helper/ROM changes.')
if __name__=='__main__':main()
