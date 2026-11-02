"""Deliver five verified WWF clears; explicitly retain Andre's open route."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from nightly_patch_guard_v1 import check
O=R/'build/wwf-helper-stable-1102-v2'
D=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
def read(p):return json.loads(p.read_text())
def main():
    rom=O/'candidate2.nes';digest=sha(rom)
    assert digest=='f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'
    assert read(O/'caller-load-CPU.json')['passed'] and read(O/'proposal.json')['passed']
    runs=['native-hogan3',*[f'native-wwf-{i}' for i in range(1,5)],'native-karnov-regression']
    for name in runs:
        p=O/name;q=read(p/'ready.json');b=read(p/'capture/binding.json');result=read(p/'capture/result.json')
        assert result['passed'] and b['exit_code']==0 and b['ROM_sha256']==digest
        assert sha(p/'ready.json')==b['ready_sha256']
        for source,h in q['bindings'].items():assert sha(source)==h,source
    assert sha(D)=='1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'
    before=check(D);D.write_bytes(rom.read_bytes());after=check(D)
    assert sha(D)==digest
    source=O/'native-hogan3/controller.lua'
    prepare(O/'downloads-helper',rom,source.read_text(),[Path(__file__),source,D],expected=digest,timeout=240,allow_interactive=True,
            scope='Actual Downloads cold Hogan full1-1 into active1-2, no life loss, native helper carry. Five WWF clears qualified; Andre remains unqualified. No backup.')
    p=O/'downloads-helper/ready.json';q=read(p);q['ROM']=str(D);p.write_text(json.dumps(q,indent=2)+'\n')
    (O/'delivery.json').write_text(json.dumps(dict(installed=True,ROM_sha256=digest,previous_sha256=before['ROM_sha256'],destination=str(D),backup_created=False,downloads_launch_verified=False,before=before,after=after,verified_runs=runs,remaining='Andre combat route; complete roster and all powerups remain incomplete.'),indent=2)+'\n')
if __name__=='__main__':main()
