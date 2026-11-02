"""Retain bounded controller evidence for the current Karnov full-stage clear."""
import json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/karnov-crouch-route-1102-v1'
def main():
    result=json.loads((O/'native-stair/capture/result.json').read_text())
    b=json.loads((O/'native-stair/capture/binding.json').read_text())
    assert result['passed'] and result['stage_complete'] and not result['died'] and b['exit_code']==0
    p=R/'docs/qa/checkpoints/2026-11-02/karnov-full11-v6';p.mkdir(exist_ok=True)
    paths=[]
    for name in ['native','native-ground','native-falling','native-postpit','native-gap3','native-stair']:
        paths.extend(x for x in (O/name).rglob('*') if x.is_file() and x.suffix in ['.json','.lua','.csv','.png'])
    with zipfile.ZipFile(p/'inputs.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for x in sorted(paths):z.write(x,x.relative_to(R).as_posix())
    report=dict(passed=True,ROM_sha256=b['ROM_sha256'],ROM_changed=False,result=result,new_helpers=False,existing_helpers=[dict(stage='1-1',center_x=704,left_x=688,initial_y=208,width=32),dict(stage='1-1',center_x=888,left_x=872,initial_y=208,width=32)],archive_SHA256=sha(p/'inputs.zip'),files=len(paths),scope='Controller-only active1-2/no death or life change; original crouch fire and native pipe lifts. Neither all-powerup nor both-mode qualification.')
    (p/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    n=R/'docs/qa/continuation-current.json';q=json.loads(n.read_text());q['Karnov_full11_1102']=report;n.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,files=len(paths),archive_bytes=(p/'inputs.zip').stat().st_size)))
if __name__=='__main__':main()
