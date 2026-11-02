"""Prepare first native terrain/full-stage route; no helper or ROM mutation."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/excitebike-pose-1101-v3'


def main():
    rom=O/'current3.nes';pin='37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'
    assert sha(rom)==pin
    for name in ['native4','arthur-flower','shinobi-smoke']:
        q=json.loads((O/name/'capture/result.json').read_text())
        b=json.loads((O/name/'capture/binding.json').read_text())
        assert q['passed']and b['ROM_sha256']==pin and b['exit_code']==0
    source=R/'tools/reference/excitebike_full11_1102_v1.lua'
    prepare(O/'full11',rom,source.read_text(),
            [Path(__file__),source,O/'current3-composition.json',O/'native4/capture/result.json',O/'controller-windup-CPU.json'],
            expected=pin,timeout=240,allow_interactive=True,
            scope='Controller-only first full1-1 discovery: original Right/Bturbo,4update Up prelean,freshA8 and Up36; actual terrain/edge/enemy observations. Require same lives and active1-2. FourPNGs including64px thirdpipe approach,compact24frameCSV; no writes or helpers. A negative run determines actual native terrain/recovery limits before any helper proposal.')


if __name__=='__main__':main()
