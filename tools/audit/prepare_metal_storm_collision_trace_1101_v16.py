"""Observe real collision adapter stack and wall calls after dispatch admission."""
from pathlib import Path
import re
import prepare_metal_storm_dispatch_1101_v16 as P
from prepare_selected_native_packet_v1 import prepare,sha
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
def main():
    b=qualified(P.O/'candidate.nes')
    labels={m[2]:int(m[1],16) for line in (P.R/'build/metal-storm-native-integration-1101-v12/native-component.lbl').read_text().splitlines() if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
    c=(P.P.O/'native-diagnostic/controller.lua').read_text()
    c=c.replace('if #events>=90 then return end','if #events>=90 or id<7 then return end')
    c=c.replace("s['cpu.a'],s['cpu.sp']", "s['cpu.y'],r('R0')")
    # Existing array columns12/13 now mean nativeY and R0, not A/SP.
    hooks=''
    for i,name,bank in [(7,'Ms12Adder',2),(8,'SamusStopAtWallBanked',138)]:
        pc=labels[name] if name in labels else address(b,name);reg='CurrentBankC' if bank==2 else 'CurrentBank'
        hooks+=f"emu.addMemoryCallback(function() if r('{reg}')=={bank} then event({i}) end end,emu.callbackType.exec,{pc})\n"
    c=c.replace('local function shot',hooks+'local function shot')
    prepare(P.O/'collision-trace',P.O/'candidate.nes',c,[Path(__file__)],expected=sha(P.O/'candidate.nes'),timeout=90,
            scope='Read-only actual collision call trace, at most90 events. Last columns are Y,R0. Native smoke remains a failure until coordinates/rendering recover.')
if __name__=='__main__':main()
