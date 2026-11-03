"""Retain exact four native regressions and the reviewed private composition."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

R = Path(__file__).resolve().parents[2]
O = R/'build/combined-native-root-freeze-1103-v117'
N = R/'build/bub-combined-auth-native-1103-v91'
D = R/'docs/qa/checkpoints/2026-11-03/combined-auth-native-v117'
PIN = '80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    O.mkdir(exist_ok=False)
    prepared = json.loads((N/'prepared.json').read_text())
    assert prepared['ROM_SHA256'] == PIN
    paths = {Path(__file__), N/'prepared.json'}
    sources = [
        'tools/audit/grant_combined_auth_root_1103_v116.py',
        'tools/audit/prepare_bub_combined_auth_review_1103_v90.py',
        'tools/audit/prepare_bub_combined_auth_native_1103_v91.py',
        'docs/qa/allocations/combined-owner-auth-1103-v116.json',
        'build/bub-menu-candidate-1102-v2/combined-auth-v90-composition.json',
        'build/bub-menu-candidate-1102-v2/combined-auth-v90-callers.json',
    ]
    paths.update(R/p for p in sources)
    for p,h in prepared['bindings'].items():
        assert sha((R/p).read_bytes()) == h,p
    rows = []
    for p in prepared['packets']:
        packet = R/p['packet']; capture = packet/'capture'
        ready_path = packet/'ready.json'
        ready = json.loads(ready_path.read_text())
        binding = json.loads((capture/'binding.json').read_text())
        assert ready['ROM_sha256'] == binding['ROM_sha256'] == PIN
        assert binding['exit_code'] == 0
        assert binding['ready_sha256'] == sha(ready_path.read_bytes())
        for path,digest in ready['bindings'].items():
            assert sha(Path(path).read_bytes()) == digest,path
        q = json.loads((capture/('full11.json' if p['task']=='full11' else 'earned-mushroom.json')).read_text())
        observer = (json.loads((capture/'bub-observer.json').read_text())
                    if p['task']=='full11' else q['observer'])
        assert q['passed'] and observer['passed'] and observer['failures'] == 0
        assert observer['ROM_sha256'] == PIN and observer['identity'] == p['identity']
        assert not observer['script_RAM_writes']
        if p['task']=='full11':
            assert q['full_stage'] and q['world']==0 and q['level']==1 and q['engine']==8
            assert q['initial_lives']==q['final_lives']==2 and not q['helpers_added']
        else:
            assert q['observed_immature'] and q['observed_mature']
            assert q['source_flags']==q['native_status']==1 and q['lives']==2
        pngs = list(capture.glob('*.png')); assert len(pngs)<=4
        baseline=p['baseline']['frames']; actual=observer['physical_frames']
        rows.append(dict(identity=p['identity'],task=p['task'],passed=True,
            physical_frames=actual,baseline_physical_frames=baseline,
            fewer_physical_frames=baseline-actual,completed_Main=observer['completed_Main'],
            checks=observer['checks'],failures=0,pops=observer['pops'],
            source_bubble_rides=observer['source_bubble_ride_restarts'],
            helpers_added=False,PNG_count=len(pngs),packet=p['packet']))
        for f in packet.rglob('*'):
            if f.is_file():
                assert f.suffix.lower() not in ('.nes','.mp4','.avi','.state'),f
                paths.add(f)
    D.mkdir(parents=True,exist_ok=False)
    members=[]
    with ZipFile(D/'inputs.zip','w',ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(paths):
            data=f.read_bytes(); name=f.relative_to(R).as_posix()
            z.writestr(name,data)
            members.append(dict(path=name,bytes=len(data),SHA256=sha(data)))
    with ZipFile(D/'inputs.zip') as z:
        assert len(z.namelist())==len(members)
        for p in members:
            data=z.read(p['path'])
            assert sha(data)==p['SHA256'] and data==(R/p['path']).read_bytes()
    receipt=dict(passed=True,installed=False,ROM_SHA256=PIN,rows=rows,
        archive_SHA256=sha((D/'inputs.zip').read_bytes()),
        archive_bytes=(D/'inputs.zip').stat().st_size,members=members,
        scope='Four actual native runs on exact private80d3. Unchanged cf7 adaptive controller policy/assertions, natural menu/earned mushroom and nonshortcut full1-1. All retained PNGs visually inspected by root. No new helpers or RAM seeds.',
        limits='Different adaptive trajectories/Main counts: whole-route video frame reduction is not exact-input replay or a universal framerate guarantee. Prince graphics fix, DK menu admission and Shinobi/Excitebike native regressions remain separate. Downloads stays cf7; no new nightly delivered.')
    (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    h=R/'docs/qa/continuation-current.json'; current=json.loads(h.read_text())
    current['bub_performance_current_1102'].update(
        combined_auth_status='PRIVATE80D3_BUB_BOB_NATIVE_FULL11_AND_EARNED_MUSHROOM_PASS',
        combined_auth_native_checkpoint=D.relative_to(R).as_posix(),
        combined_auth_native_scope=receipt['scope'],combined_auth_native_limits=receipt['limits'])
    h.write_text(json.dumps(current,indent=2)+'\n')
    stage=[Path(__file__).relative_to(R).as_posix(),*sources[:4],
           (D/'inputs.zip').relative_to(R).as_posix(),(D/'receipt.json').relative_to(R).as_posix(),
           h.relative_to(R).as_posix()]
    (O/'stage-files.txt').write_text('\n'.join(stage)+'\n')
    (O/'receipt.json').write_text(json.dumps(dict(passed=True,checkpoint=str(D),rows=rows),indent=2)+'\n')
    print(json.dumps(dict(passed=True,rows=rows,archive_bytes=receipt['archive_bytes'],members=len(members))))


if __name__=='__main__':
    main()
