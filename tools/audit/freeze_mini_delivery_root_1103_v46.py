"""Save delivered Mini, exact evidence and the user-requested pause handoff."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
import build_storage_guard_v1 as G
from nightly_patch_guard_v1 import check
R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-wrap-root-1103-v46'
D=R/'docs/qa/checkpoints/2026-11-03/mini-nightly-v46'
PIN='8daf59cc958e2a3a645882ea53c6bd75e9a7c641793054f8ce534358f369a7d7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads((R/p).read_text())

def main():
    G.preflight(private_root=O,reserved_bytes=12000000,reserved_files=5,fresh=True)
    delivery=read('build/mini-mario-delivery-root-1103-v30/verified-delivery.json')
    assert delivery['Downloads_launch_verified'] and delivery['ROM_SHA256']==PIN and delivery['IPS_roundtrip']
    assert check(delivery['destination'])['ROM_sha256']==PIN
    paths={Path(__file__).resolve()};sources=set()
    manifests=[
        ('build/mini-mario-host-1103-v22/mini-native-host-v30.json',None),
        ('build/mini-mario-host-1103-v22/mini-final-host-v45.json','git_source_files'),
        ('build/mini-mario-owner-1103-v15/source-stage.json','source_files'),
        ('build/mini-mario-menu-1103-v14/mini-art-menu-source-v19.json',None),
        ('build/mini-mario-frontend-final-1103-v42/receipt.json','commit_files'),
        ('build/mini-mario-final-supplement-1103-v45/receipt.json','commit_files'),
        ('build/prince-body-owner-1103-v178/source-stage.json',None),
        ('build/bub-powered-trajectory-1103-v92/powered-trajectory-freeze-v99.json','source_commit_files')]
    for name,key in manifests:
        p=R/name;q=read(name);paths.add(p)
        archive=Path(q['archive']);archive=archive if archive.is_absolute()else R/archive
        assert sha(archive)==q['archive_SHA256'],archive;paths.add(archive)
        if key:sources.update(q[key])
    sources.update((R/'build/mini-mario-menu-1103-v14/commit-files-v19.txt').read_text().splitlines())
    sources.update([
        'tools/audit/prepare_mini_native_tile_1103_v13.py',
        'tools/audit/prepare_mini_native_render_1103_v15.py',
        'tools/audit/measure_mini_native_gates_1103_v23.py',
        'tools/audit/grant_mini_private_resources_root_1103_v24.py',
        'tools/audit/compose_mini_nightly_root_1103_v27.py',
        'tools/audit/compose_mini_anchor_root_1103_v28.py',
        'tools/audit/compose_mini_scroll_root_1103_v32.py',
        'tools/audit/compose_mini_graphics_root_1103_v35.py',
        'tools/audit/compose_mini_publication_root_1103_v40.py',
        'tools/audit/compose_mini_ready_root_1103_v44.py',
        'tools/audit/deliver_mini_nightly_root_1103_v30.py',
        'tools/audit/qualify_mini_delivery_cold_root_1103_v43.py',
        'tools/audit/freeze_mini_final_cold_1103_v29.py',
        'tools/audit/freeze_mini_final_cold_1103_v40.py',
        'tools/audit/prepare_combined_foreign_native_root_1103_v119.py',
        'tools/audit/prepare_combined_ex_labels_root_1103_v120.py',
        'tools/audit/measure_prince_body_owner_1103_v178.py',
        'tools/audit/check_prince_body_owner_1103_v179.py',
        'tools/audit/prepare_prince_body_backing_1103_v180.py',
        'tools/audit/check_prince_body_cold_1103_v181.py',
        'tools/audit/check_prince_body_reader_1103_v182.py',
        'tools/audit/check_prince_body_isr_1103_v183.py',
        'tools/audit/freeze_prince_body_source_1103_v184.py',
        Path(__file__).relative_to(R).as_posix()])
    sources.discard('');paths.update(R/p for p in sources)
    paths.update([R/'build/mini-mario-candidate-root-1103-v44/candidate.json',
        R/'build/mini-mario-delivery-cold-root-1103-v43/receipt.json',
        R/'docs/qa/allocations/mini-mario-private-resources-1103-v24.json',
        R/'build/mini-mario-final-owner-1103-v29/source-stage.json',
        R/'build/mini-mario-final-owner-1103-v40/source-stage.json'])
    for name in ['mini-mario-native-packets-1103-v43','mini-mario-delivery-root-1103-v30',
                 'combined-foreign-native-root-1103-v119','combined-ex-labels-root-1103-v120']:
        root=R/'build'/name
        if root.exists():paths.update(p for p in root.rglob('*')if p.is_file()and p.suffix.lower()in{'.py','.lua','.json','.png','.csv','.txt','.ips','.log'})
    # Retain the preceding tested patch as a compact Git checkpoint input so
    # this integration can be reverted after the sole release asset changes.
    prior=R/'build/bub-earned-delivery-1103-v98/SMB-Crossover-Latest-WIP-MMC5.ips'
    assert sha(prior)=='7fae59278cda3952d5b12a89670e0a623bb114a5f4fd92c3d667f13d704dd5a1';paths.add(prior)
    assert len(paths)<500 and all(p.is_file()for p in paths)
    assert all(p.suffix.lower()not in{'.nes','.fds','.gb','.exe','.dbg','.o'}for p in paths)
    O.mkdir(exist_ok=False);D.mkdir(parents=True,exist_ok=False);members=[]
    with ZipFile(D/'inputs.zip','w',ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(paths):
            name=p.relative_to(R).as_posix();data=p.read_bytes();z.writestr(name,data)
            members.append(dict(path=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
    assert (D/'inputs.zip').stat().st_size<8000000
    with ZipFile(D/'inputs.zip')as z:
        for m in members:assert hashlib.sha256(z.read(m['path'])).hexdigest()==m['SHA256']
    full=read('build/mini-mario-native-packets-1103-v43/full43/capture/result.json')
    crossings=full['phases']['fullstage']['actual_obstacle_clears']
    assert len(crossings)==7 and full['last']['lives']==2 and not full['helpers_added']
    assert not full['passed'] and not full['full_stage']
    receipt=dict(delivered=True,paused_at_user_request=True,ROM_SHA256=PIN,
        destination=delivery['destination'],IPS_SHA256=delivery['IPS_SHA256'],IPS_roundtrip=True,
        selectable_identities=93,displayed_identities=94,Mario_variant=8,Mini_raw=41,
        scope='Actual Downloads cold Mario Select-to-Mini, Start, idle20, walking/reversal, 35.875px held jump/landing, exact source sprite/6x7box/CHR968/OAMrotation and one-part reservation. No backups, matching sidecar patches or new helpers.',
        traversal=dict(full_stage_passed=False,physical_bound=22000,all_four_pipes_and_three_pits_crossed=True,crossings=crossings,wall_restarts=3,lives=[2,2],last_source_x=full['last']['x']/16,
            remaining='Test reached flagpole but did not verify active1-2 before bound. Terminal native mode/selection was not captured: inspect end handoff on resume; do not infer its exact cause or claim full1-1 clear.'),
        remaining=['Mini flagpole/end handoff is first resume item.','Lives/entry portrait and native end-animation coordinate synchronization need review.','Original source actors/swim/climb/projectiles, earned powerups, original audio and performance audit remain incomplete.','Prince remains locked; DK Jr remains absent from the public menu. Prince180 source cannot be applied with its old ABA9 cookie after the five-owner layout moved it toABA4.'],
        archive_SHA256=sha(D/'inputs.zip'),archive_bytes=(D/'inputs.zip').stat().st_size,members=members,source_files=sorted(sources),
        source_component_archives='Original Mini world/host, art/menu, full five-owner/cold/IRQ corpus and final observer supplement are retained compactly; archives are not recursively expanded.',
        guard=check(delivery['destination']))
    (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (O/'commit-files.txt').write_text('\n'.join(sorted(sources))+'\n')
    h=R/'docs/qa/continuation-current.json';current=json.loads(h.read_text())
    current['previous_installed_nightly_cf7']=current['installed_nightly']
    current['installed_nightly']=dict(installed=True,ROM_sha256=PIN,destination=delivery['destination'],backup_created=False,downloads_launch_verified=True,IPS_SHA256=delivery['IPS_SHA256'],IPS_roundtrip=True,checkpoint=D.relative_to(R).as_posix(),verification_scope=receipt['scope'])
    current['mini_mario_priority_1103']=dict(status='DELIVERED_INITIAL_PLAYABLE_PAUSE_REQUESTED',user_request='Pause after unlocking Mini Mario in the nightly.',selection='Highlight Mario; Select until MINI MARIO (variant8/raw41).',checkpoint=D.relative_to(R).as_posix(),traversal=receipt['traversal'],remaining=receipt['remaining'],root_queue='FREE; all automated emulator runs terminal; helper work stopped.')
    current['goal_status']='PAUSED_AT_USER_REQUEST_INCOMPLETE'
    h.write_text(json.dumps(current,indent=2)+'\n')
    notes=R/'build/mini-mario-delivery-root-1103-v30/release-notes.txt'
    notes.write_text(notes.read_text()+'\nKnown limitation: the non-shortcut controller run crossed all four pipes and three gaps with lives2to2 and three wall-jump restarts, but did not complete the flagpole/next-stage handoff within the bound. Full1-1 validation, powerups, audio and remaining Mini abilities are unfinished. No helper platforms were added. Work is paused at the user\'s request after this unlock.\n')
    print(json.dumps(dict(saved=True,ROM_SHA256=PIN,archive_bytes=receipt['archive_bytes'],files=len(members),sources=len(sources),full_stage_passed=False)))

if __name__=='__main__':main()
