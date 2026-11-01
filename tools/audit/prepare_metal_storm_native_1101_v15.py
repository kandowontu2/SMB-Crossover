"""Cold controller-only Metal selection and movement smoke; no state writes."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_metal_storm_menu_1101_v15 as P
def main():
    source=P.R/'build/mario-tank-visible-host-1101-v5/native-final-smoke/controller.lua'
    c=source.read_text()
    c=c.replace("elseif phase=='select' then pad.select=true end", "elseif phase=='select' then\n   if cycles<3 then pad.right=true elseif cycles==3 then pad.down=true else pad.select=true end end")
    c=c.replace('cycles==7','cycles==5').replace("r('MarioVariant')==7","r('SelectedCharacter')==35")
    c=c.replace("r('SelectedCharacter')==0","r('SelectedCharacter')==35")
    c=c.replace("r('MarioVariant')","r('SelectedCharacter')").replace('"variant":','"selected":')
    prepare(P.O/'native-smoke',P.O/'candidate.nes',c,[Path(__file__),source],expected=sha(P.O/'candidate.nes'),timeout=90,
            scope='Cold title, right three/down/Select, Metal Storm Start,36 walking frames. Controller only. No health/combat/audio or full-level claim.')
if __name__=='__main__':main()
