"""Combined Ex turbo-jump and unchanged Arthur flower/torch native packets."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
O=R/'build/excitebike-pose-1101-v3'


def main():
    composition=json.loads((O/'current3-composition.json').read_text());assert composition['passed']
    windup=json.loads((O/'controller-windup-CPU.json').read_text())
    assert windup['passed']and windup['selected']['windup']==40 and windup['selected']['rise']==61
    negative=json.loads((O/'native3/capture/result.json').read_text())
    diagnosis=json.loads((O/'native3/capture/diagnosis.json').read_text())
    assert not negative['passed'] and diagnosis['hardware_checks']==1303 and diagnosis['hardware_failures']==0
    text=(O/'native3/controller.lua').read_text()
    old="{'prepare',180,1},{'prelean',4,9},{'jump',36,9}"
    assert text.count(old)==1
    text=text.replace(old,"{'prepare',40,65},{'prelean',4,73},{'jump',36,73}")
    old="pad.right=(bits&1)~=0;pad.left=(bits&2)~=0;pad.up=(bits&8)~=0"
    assert text.count(old)==1;text=text.replace(old,old+";pad.b=(bits&64)~=0")
    assert text.count('part==6 and steps>=150')==1
    text=text.replace('part==6 and steps>=150','part==6 and steps>=30')
    refs=[Path(__file__),O/'current3-composition.json',O/'controller-windup-CPU.json',
          O/'native3/controller.lua',O/'native3/capture/result.json',O/'native3/capture/diagnosis.json']
    prepare(O/'native4',O/'current3.nes',text,refs,expected=composition['ROM_SHA256'],timeout=150,allow_interactive=True,
            scope='Combined installed Arthur b9+Ex repair. Same cold/idle/coast/reverse/hardware checks; source-verified40epoch original Bturbo then4prelean and8epoch freshA before observed firstenemy. Unchanged >30px rise/no-life-loss assertion;3PNGs, passive source input/angle/speed/launch. No writes/full1-1/install claim.')
    # Rebind the exact controller which passed on the installed b9 candidate.
    # Do not regenerate or modify Arthur's source or controller route.
    ar=R/'build/arthur-side-clamp-1101-v8/flower-maturity'
    ready=json.loads((ar/'ready.json').read_text());result=json.loads((ar/'capture/result.json').read_text())
    assert ready['ROM_sha256']==composition['base_ROM_SHA256'] and result['passed']
    assert result['reason']=='Natural flower and original B-driven torch'
    prepare(O/'arthur-flower',O/'current3.nes',(ar/'controller.lua').read_text(),
            [Path(__file__),O/'current3-composition.json',ar/'controller.lua',ar/'ready.json',ar/'capture/result.json'],
            expected=composition['ROM_SHA256'],timeout=150,allow_interactive=True,
            scope='Exact unchanged passing b9 Arthur parkedflower/landwalk controller on combined Ex+Arthur candidate. Genuine firstflower release/maturity/originalpickup and B-driven torch/no-life-loss assertions; no writes or helpers. Full1-1 remains separate.')


if __name__=='__main__':main()
