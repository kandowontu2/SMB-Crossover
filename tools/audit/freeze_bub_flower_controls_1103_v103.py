"""Keep two bounded controller negatives and the next-work handoff compact."""
import json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-flower-controls-freeze-1103-v103'
D=R/'docs/qa/checkpoints/2026-11-03/bub-flower-controller-v103'
def main():
    O.mkdir(exist_ok=True);sources=[Path(__file__),R/'tools/audit/prepare_bub_grounded_bubble_retry_1103_v100.py',R/'tools/audit/prepare_bub_settled_retry_1103_v102.py'];files=sources[:];rows=[]
    for version in[100,102]:
        p=R/f'build/bub-earned-flower-1103-v{version}/bub-flower';ready=json.loads((p/'ready.json').read_text());binding=json.loads((p/'capture/binding.json').read_text())
        assert binding['exit_code']==1 and binding['ready_sha256']==sha(p/'ready.json')and binding['ROM_sha256']==ready['ROM_sha256']=='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
        for name,h in ready['bindings'].items():assert sha(name)==h,name
        files.extend([p/'controller.lua',p/'run.py',p/'ready.json',p/'capture/binding.json',p/'capture/callback-error.json'])
        for name in['full11.json','flower.csv']:
            f=p/'capture'/name
            if f.exists():files.append(f)
        rows.append(dict(version=version,passed=False,kind='controller-only negative',reason='NativeState0 was assumed fully source-settled before issuing retry.'if version==100 else'First pipe crossed after release/retry correction; second pipe stalls X593..595/Y176 with zero original rides. No flower reached.'))
    D.mkdir(parents=True);archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in files:z.writestr(f.relative_to(R).as_posix(),f.read_bytes())
    with zipfile.ZipFile(archive)as z:
        for f in files:assert z.read(f.relative_to(R).as_posix())==f.read_bytes()
    assert archive.stat().st_size<256000
    receipt=dict(passed=True,tests_passed=False,installed_ROM_changed=False,archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,rows=rows,source_files=[f.relative_to(R).as_posix()for f in sources],scope='Retained diagnostic controllers; no flower/physics/helper or ability qualification. Tested/installed cf7 nightly remains unchanged. Next priority measured idle/walk cost and Prince/DK Jr native completion; resume earned-flower route with a source-bound bubble/contact trace rather than arbitrary input-window changes.',bindings={f.relative_to(R).as_posix():sha(f)for f in files})
    (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    p=R/'docs/qa/continuation-current.json';h=json.loads(p.read_text());h['bub_original_upgrades_current_1102'].update(flower_controller_checkpoint=D.relative_to(R).as_posix(),flower_latest_negative=rows[-1])
    h['root_queue_current_1102'].update(status='FREE',last_private_controller_sessions={'flower100':76728,'flower102':91710},next='cf7 nightly andLatestIPS delivered,pusheda76e18ff. Currentflower102negative frozen103(firstpipecleared,second0rides). Prioritize measuredemptyarea lag and Princecurrent130/131 nativequalification; DKtypedservices/bbox70frozen101, shared/currentpositiveowners pending. No newhelpers or ROM changes afterdelivery.')
    p.write_text(json.dumps(h,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='bindings'}))
if __name__=='__main__':main()
