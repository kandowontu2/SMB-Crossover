"""Retain the successful native route and the diagnostics that explain it."""
import json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    result=json.loads((O/'native-andre-timing/capture/result.json').read_text())
    assert result['passed'] and result['initial_lives']==result['final_lives']==2 and result['level']==1 and result['engine']==8
    helper=json.loads((O/'native-andre-timing/capture/helper-contact.json').read_text());assert helper['native_carry_calls']==64
    p=R/'docs/qa/checkpoints/2026-11-02/andre-clear-v11';p.mkdir(exist_ok=True)
    paths=[]
    for name in ['native-andre3','native-andre-contact','native-andre-action','native-andre-timing']:
        paths.extend(x for x in (O/name).rglob('*') if x.is_file() and x.suffix in ['.json','.lua','.csv','.png'])
    with zipfile.ZipFile(p/'inputs.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for x in sorted(paths):z.write(x,x.relative_to(R).as_posix())
    report=dict(ROM_sha256=sha(O/'candidate2.nes'),passed=True,ROM_changed=False,result={k:v for k,v in result.items() if k!='trace'},helper=helper,archive_SHA256=sha(p/'inputs.zip'),files=len(paths),scope='Actual controller-only full1-1 active1-2, unchanged lives. Earlier missed-punch negatives retained. Not both modes or all powerups.')
    (p/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    n=R/'docs/qa/continuation-current.json';q=json.loads(n.read_text())
    q['wwf_helper_delivery_1102']['qualified'].append('Andre the Giant')
    q['wwf_helper_delivery_1102']['remaining']='All6 full1-1 pass on current nightly; both-mode and all-powerup qualification remain incomplete.'
    q['andre_contact_followup']=report
    n.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,files=len(paths),archive_bytes=(p/'inputs.zip').stat().st_size)))
if __name__=='__main__':main()
