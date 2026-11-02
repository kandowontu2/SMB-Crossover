"""Compact source/native checkpoint; no ROM, debug tree or capture sequences."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha

def main():
    own=R/'build/thomas-checkpoint-1102-v3';own.mkdir(exist_ok=True)
    dest=R/'docs/qa/checkpoints/2026-11-02/thomas-six-lifts-v3'
    assert not dest.exists();dest.mkdir(parents=True)
    p=R/'build/thomas-current-candidate-1102-v3';d=R/'build/thomas-delivery-1102-v3'
    proof=json.loads((p/'native-qualified.json').read_text());delivery=json.loads((d/'published-receipt.json').read_text())
    assert proof['passed'] and delivery['downloads_launch_verified'] and proof['ROM_sha256']==delivery['ROM_sha256']
    paths={Path(__file__),p/'composition.json',p/'native-qualified.json',d/'published-receipt.json',R/'build/thomas-current-lifts-1102-v2/lift.s',R/'build/thomas-current-lifts-1102-v2/source-stage.json'}
    for directory in [p/'native-six-lifts',d/'downloads-smoke']:
        paths.update(x for x in directory.rglob('*') if x.is_file() and x.suffix in {'.json','.lua','.py','.csv','.png','.log'})
    for name in ['build_thomas_late_lifts_1102_v1','check_thomas_constructor_input_1102_v1','build_thomas_current_lifts_1102_v2','compose_thomas_late_lifts_1102_v3','prepare_thomas_six_lifts_1102_v3','qualify_thomas_six_lifts_1102_v3','deliver_thomas_lifts_1102_v3','publish_thomas_lifts_1102_v3']:
        paths.add(R/'tools/audit'/(name+'.py'))
    assert len(paths)<100 and sum(x.stat().st_size for x in paths)<4000000
    archive=dest/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for x in sorted(paths):z.write(x,x.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for x in paths:assert z.read(x.relative_to(R).as_posix())==x.read_bytes()
    receipt=dict(passed=True,ROM_sha256=proof['ROM_sha256'],IPS_SHA256=delivery['IPS_SHA256'],native=proof,delivery=delivery,
                 archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,files={x.relative_to(R).as_posix():sha(x) for x in sorted(paths)})
    (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (own/'receipt.json').write_text(json.dumps(dict(checkpoint=str(dest),archive_bytes=archive.stat().st_size,files=len(paths)),indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(dest),archive_bytes=archive.stat().st_size,files=len(paths))))

if __name__=='__main__':main()
