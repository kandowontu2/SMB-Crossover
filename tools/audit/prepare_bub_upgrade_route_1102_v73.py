"""Keep the controller's runup retreat clear of already crossed native pipes."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-upgrades-root-route-1102-v73'
def main():
    O.mkdir(exist_ok=True);parent=R/'build/bub-upgrades-root-candidate-1102-v72';source=parent/'bub-full11/controller.lua';text=source.read_text()
    old='   local target=full_runup(obstacle)\n';assert text.count(old)==1
    text=text.replace(old,old+"   local prior=obstacles[full_index-1]\n   if prior and prior.kind=='pipe' and y+16>=prior.top then target=math.max(target,prior.right+8)end\n")
    rom=parent/'bub-original-upgrades.nes';pin=sha(rom)
    prepare(O/'bub-full11',rom,text,[Path(__file__),source,parent/'candidate.json',parent/'bub-full11/capture/bub-observer.json'],expected=pin,timeout=240,allow_interactive=True,scope='Same exact b7e2 candidate; controller retreat clamps to actual previous pipe right+8 instead of pressing left forever into its wall. Retains original seven crossings/full life/source hardware assertions. Prior controller negative atx647 after secondpipe is retained; no ROM/input-state/physics patch.')
if __name__=='__main__':main()
