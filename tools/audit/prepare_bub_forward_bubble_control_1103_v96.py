"""Keep original forward facing during the first bubble restart."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-earned-flower-1103-v96'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-earned-flower-1103-v93/bub-flower/controller.lua';text=source.read_text()
    before='return {right=best>12,left=best<4,a=true}';assert text.count(before)==1
    text=text.replace(before,'return {right=best>12,a=true}')
    rom=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
    prepare(O/'bub-flower',rom,text,[Path(__file__),source,R/'build/bub-earned-flower-1103-v93/bub-flower/capture/full11.json'],expected=PIN,timeout=240,allow_interactive=True,scope='Same privatecf7/controller-only progression.93 earns originalbubble support but Left alignment at the restart latchesLeft and failsforward crossing.96 removes only Left, permitting neutral/Right while retaining originalA/support callbacks; no emulated writes, physics/helper changes, or weakened crossing/earned-flower assertions.94/95 unreachable takeoff windows remain negatives.')
if __name__=='__main__':main()
