"""Save the finite Mini ending milestone and explicit user pause, without ROMs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import subprocess
import build_storage_guard_v1 as G

R = Path(__file__).resolve().parents[2]
O = R / 'build/mini-mario-end-pause-root-1103-v50'
C = R / 'docs/qa/checkpoints/2026-11-03/mini-end-v50'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pin = 'ca90e8be125c55e7ae12413964ecf766c9b890525751ea1e0ad6ce225613f4db'

def main():
    G.preflight(private_root=O, reserved_bytes=4_000_000, reserved_files=70, fresh=True)
    O.mkdir(exist_ok=False)
    assert not C.exists()
    delivery = R / 'build/mini-mario-end-delivery-root-1103-v50'
    d = read(delivery / 'verified-delivery.json')
    assert d['ROM_SHA256'] == pin and d['Downloads_launch_verified'] and d['IPS_roundtrip']
    full = R / 'build/mini-mario-end-fixed-packets-1103-v49/full49'
    f = read(full / 'capture/result.json')
    assert f['passed'] and f['full_stage'] and not f['helpers_added']
    t = f['terminal_native']
    assert [t[k] for k in ['WorldNumber','LevelNumber','GameEngineSubroutine','Ready','NumberofLives']] == [0,1,8,2,2]
    release = json.loads(subprocess.check_output(['gh','api','repos/kandowontu2/SMB-Crossover/releases/latest'], text=True))
    assert release['tag_name'] == 'Current' and len(release['assets']) == 1
    asset = release['assets'][0]
    assert asset['name'] == 'SMB-Crossover-Latest-WIP-MMC5.ips'
    assert asset['digest'] == 'sha256:' + d['IPS_SHA256']
    sources = [
        'compose_mini_end_root_1103_v49.py', 'prepare_mini_mario_end_handoff_1103_v47.py',
        'prepare_mini_mario_native_end_1103_v48.py', 'freeze_mini_mario_native_end_1103_v49.py',
        'prepare_mini_mario_end_fixed_1103_v49.py', 'deliver_mini_end_root_1103_v50.py',
        'qualify_mini_end_cold_root_1103_v50.py', Path(__file__).name]
    files = [R / 'tools/audit' / n for n in sources]
    for root in [R/'build/mini-mario-end-fixed-packets-1103-v49/smoke49', full, delivery/'downloads-smoke']:
        files += [root/n for n in ['ready.json','controller.lua','run.py','capture/result.json','capture/binding.json']]
    files += [full/'capture/mini-active-1-2.png',full/'capture/mini-menu.png',full/'capture/native-end.csv']
    native = R/'build/mini-mario-native-end-1103-v48'
    files += [native/n for n in ['mini-native-end-v49.zip','mini-native-end-v49.json','mini-host-v48.json']]
    files += [R/'build/mini-mario-end-cold-root-1103-v50/receipt.json',
        R/'build/mini-mario-end-candidate-root-1103-v49/candidate.json',
        delivery/'verified-delivery.json', delivery/'SMB-Crossover-Latest-WIP-MMC5.ips', delivery/'release-notes.txt']
    negative = R/'build/mini-mario-end-handoff-1103-v47/native'
    files += [negative/n for n in ['ready.json','controller.lua','run.py','capture/result.json','capture/binding.json','capture/native-end.csv']]
    for p in files: assert p.is_file(),p
    archive = O/'inputs.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in files: z.write(p,p.relative_to(R).as_posix())
    publication = dict(tag='Current',latest=True,sole_asset=asset['name'],asset_SHA256=d['IPS_SHA256'],ROM_SHA256=pin)
    receipt = dict(passed=True,goal_complete=False,user_requested_pause=True,ROM_SHA256=pin,
        IPS_SHA256=d['IPS_SHA256'],Downloads_launch_verified=True,backup_created=False,
        full_nonshortcut_1_1=True,active_1_2=True,physical_frames=f['physical_frames'],lives=[2,2],helpers_added=False,
        repair='Native collision packets outside engine8; native coordinates for scripted drawing and lives portrait. Only Mini code carriers962..966 and16B cookie changed.',
        qualification='Candidate smoke/full route, native draw geometry, actual Downloads smoke, final kernel cold transitions/header poisons/copy faults; IPS roundtrip and published digest.',
        previous_checkpoint='docs/qa/checkpoints/2026-11-03/mini-nightly-v46',
        archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix():sha(p) for p in files},
        remaining=['Mini earned powerups, source actors/swim/climb/projectiles, original audio and performance.',
            'Prince locked: frozen180 zero OAM header must reserve4*(poseHeader&15),12..52B across408 poses. Proposed zero-growth STA SmPose funded by redundant pre-emitter STA SafecallA; uncompiled. Preserve five-owner layout; Prince cookieABA4, notABA9. No native Prince stage proof.',
            'DK Jr absent from public menu. All original roster/full-stage/powerup/Kirby audit requirements remain open.'])
    (O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (O/'publication.json').write_text(json.dumps(publication,indent=2)+'\n')
    C.mkdir(parents=True)
    for name in ['inputs.zip','receipt.json','publication.json']: (C/name).write_bytes((O/name).read_bytes())
    handoff=R/'docs/qa/continuation-current.json'
    h=read(handoff)
    mini=h['mini_mario_priority_1103']
    mini.update(status='DELIVERED_PLAYABLE_FULL11_PAUSED_BY_USER',checkpoint=C.relative_to(R).as_posix(),root_queue='FREE; all automated emulator runs terminal; helper work stopped.')
    mini['traversal'].update(full_stage_passed=True,physical_bound=7875,remaining='None for tested non-shortcut1-1 route; reaches active1-2. Shortcut/powerups/other stages remain unverified.')
    mini['remaining']=receipt['remaining']
    mini['repair_checkpoint']=C.relative_to(R).as_posix()
    h['goal_status']='PAUSED_BY_USER_INCOMPLETE'
    h['installed_nightly'].update(ROM_sha256=pin,IPS_SHA256=d['IPS_SHA256'],checkpoint=C.relative_to(R).as_posix(),verification_scope=receipt['qualification'])
    h['pause_request']='Pause after Mini Mario unlock; latest Mini ending repair delivered and all helpers stopped. Resume only when user requests.'
    handoff.write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps(dict(passed=True,checkpoint=str(C),archive_bytes=archive.stat().st_size,archive_SHA256=sha(archive),members=len(files),storage=G.preflight(fresh=True))))

if __name__ == '__main__': main()
