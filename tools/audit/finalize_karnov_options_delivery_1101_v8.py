"""Read back the exact installed update and preserve the Metal render component."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from build_storage_guard_v1 import preflight
from deliver_karnov_menu_health_1101_v3 import validate

R=Path(__file__).resolve().parents[2];O=R/'build/karnov-options-delivery-finalize-1101-v8'
D=R/'docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8'
M=R/'docs/qa/checkpoints/2026-11-01/metal-storm-render-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    preflight(private_root=O,reserved_bytes=1000000,reserved_files=10,fresh=True)
    O.mkdir(exist_ok=True);q=json.loads((D/'handoff.json').read_text())
    assert q['passed']and q['installed']and not q['backup_created']and not q['complete']
    assert sha(q['destination'])==sha(R/'build/karnov-host-resource-base-1101-v1/candidate.nes')==q['output_sha256']
    for k in ['source','native']:
        part=q[k];p=R/part['path'];assert sha(p)==part['sha256']
        with zipfile.ZipFile(p)as z:
            manifest=json.loads(z.read('files.json'));assert len(z.namelist())==part['members']
            for name,v in manifest.items():
                data=z.read(name);assert len(data)==v['bytes']and hashlib.sha256(data).hexdigest()==v['sha256']
    for v in q['components'].values():assert sha(R/v['path'])==v['sha256']
    for name in ['boots','boomerang','wings','combat-crouch','block-row','final-menu']:
        child=R/'build/karnov-options-native-1101-v8'/name
        ready=json.loads((child/'ready.json').read_text());validate(ready)
        result=json.loads((child/'capture/result.json').read_text());assert result['passed']and result['ROM_sha256']==q['output_sha256']
    # Preserve README's existing LF convention; the delivery writer used the
    # Windows text default. Content and all source/native packets stay exact.
    readme=R/'README.md';data=readme.read_bytes();readme.write_bytes(data.replace(b'\r\n',b'\n'))
    assert b'1c073196'in readme.read_bytes()and b'karnov-options-nightly-v8/README.md'in readme.read_bytes()
    metal=R/'build/metal-storm-render-host-1101-v7/source-proof.zip'
    expected='1b1aef299eaabdd197a7c2efc125d6aad98d1b4f2dcab277913aca2a74365d0c'
    assert sha(metal)==expected;M.mkdir(exist_ok=True)
    target=M/'source-proof.zip'
    if target.exists():assert sha(target)==expected
    else:shutil.copyfile(metal,target)
    metal_note=dict(passed=True,integrated=False,selectable=False,carrier_granted=False,
        source_packet=target.relative_to(R).as_posix(),sha256=expected,bytes=target.stat().st_size,
        actor_bytes=8083,renderer_lifecycle_bytes=2354,unfunded_gate_bytes=132,
        body_contexts=208,projectile_contexts=104,original_lifecycle_pairs=768,composed_frames=576,
        still_required=['Actual PRG/CHR/C2 and palette/world-sprite resource allocation','Cold loader, authenticated gate and native Main/ISR qualification','Source health/death/scenes/audio/native combat','Controller stage/shortcut/every-powerup tests'])
    (M/'handoff.json').write_text(json.dumps(metal_note,indent=2)+'\n',encoding='utf-8')
    continuation=R/'docs/qa/continuation-current.json';current=json.loads(continuation.read_text())
    current['active_source_components']=dict(metal_storm_v7=metal_note,
        karnov_equipment_HUD='Active worker: onefontpage with12originaliconcells,6Bproposeddisplaycache,440Bworker/tables. Placement/ownership/Main/native proof pending; no HUD in1c073196.',
        mario_the_tank='Active worker: reproduced author1.0.2a donor3396476e from public original SMB1Base source, original native movement/contact/destruction/boots rules. Source component freezing; no menu/runtime integration yet.')
    current['agents']='Three authorized workers continue compact source components: Karnov HUD, Metal Storm resource integration and Mario the Tank source behavior. Root delivered1c073196 and owns the only SMB Mesen queue. No entire build/ROM copies or frame dumps.'
    current['storage']=preflight(fresh=True)
    continuation.write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8')
    result=dict(passed=True,ROM_sha256=q['output_sha256'],installed_bytes_exact=True,
        archive_members_verified=True,six_native_runs_verified=True,README_LF_restored=True,
        code_and_native_packets_unchanged=True,metal_component_preserved=metal_note,storage=current['storage'],
        bindings={str(p.resolve()):sha(p)for p in [Path(__file__),D/'handoff.json',R/'README.md',M/'handoff.json',target]})
    for p in [O/'result.json',D/'delivery-finalized.json']:p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,ROM_sha256=q['output_sha256'],build_bytes=current['storage']['build_bytes'],build_files=current['storage']['build_files'])))


if __name__=='__main__':main()
