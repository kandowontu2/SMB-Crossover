"""Check existing Karnov lifts and first gap on the WWF helper successor."""
import json,re
from pathlib import Path
import propose_wwf_generic_helper_1102_v1 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
    out=P.R/'build/wwf-helper-stable-1102-v2'
    source=P.R/'build/karnov-pit-route-1101-v1/probe/controller.lua'
    text=source.read_text()
    labels=P.scoped_load(P.BASE)
    names=set(re.findall(r"\br\('([^']+)'",text))|set(re.findall(r"L\['([^']+)'\]",text))
    text='\n'.join(f'L[{json.dumps(n)}]={P.address(labels,n)}' for n in sorted(names))+'\n'+text
    old="local won=r('LevelNumber')~=0 or r('WorldNumber')~=0"
    assert text.count(old)==1
    text=text.replace(old,"local won=x>=1140 and r('Player_State')==0 and r('GameEngineSubroutine')==8 and r('NumberofLives')==lives")
    text=text.replace('"stage_complete":%s','"regression_crossing_complete":%s')
    rom=out/'candidate2.nes'
    prepare(out/'native-karnov-regression',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Foreign Karnov native lift regression: legal menu selection, both tall pipes and first gap, grounded beyond X1140 with unchanged lives. Not a full-stage clear. Unchanged previously exercised controls; no emulated writes.')

if __name__=='__main__':main()
