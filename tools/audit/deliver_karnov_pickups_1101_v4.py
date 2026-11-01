"""Preserve the exact tested pickup WIP and replace the user's single nightly."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from build_storage_guard_v1 import preflight
from deliver_karnov_menu_health_1101_v3 import pack,validate

R=Path(__file__).resolve().parents[2]
J=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-pickup-native-1101-v4'
C=R/'build/karnov-pickup-composed-1101-v4'
D=R/'docs/qa/checkpoints/2026-11-01/karnov-pickup-nightly-v4'
EXPECTED='0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c'
PREVIOUS='e8d35a95ffe8e396dc1d8b32ca78d57d376fc14de9a2f4b37754012448fde09a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def receipt(path):
    q=json.loads(path.read_text());validate(q)
    assert q['passed'] and q['ROM_sha256']==EXPECTED,path
    return q


def main():
    preflight(private_root=O,reserved_bytes=4000000,reserved_files=8,fresh=True)
    assert not D.exists() and not (O/'binding.json').exists()
    assert sha(J/'candidate.nes')==EXPECTED
    stage=receipt(J/'terrain-assembly.json')
    assert stage['pickups'] and stage['menu_input'] and stage['health']
    suite=receipt(J/'menu-health-suite.json')
    for n,h in suite['receipts'].items():
        assert sha(J/n)==h;receipt(J/n)
    composed_path=C/'composed-core-old-emergence-main.json'
    composed=receipt(composed_path)
    assert composed['no_code_overlay']
    for key in ['core','old_owners','emergence','Main']:
        assert composed[key]['passed'],key
    assert composed['Main']['reserve_above_SMC']>=12
    native={};native_files={}
    for name in ['qualified-shots','qualified-menu']:
        child=O/name;ready=json.loads((child/'ready.json').read_text());validate(ready)
        binding=json.loads((child/'capture/binding.json').read_text())
        q=receipt(child/'capture/result.json')
        assert binding['exit_code']==0 and binding['ready_sha256']==sha(child/'ready.json')
        assert binding['ROM_sha256']==EXPECTED
        files=[p for p in child.rglob('*') if p.is_file()]
        assert len(files)<=64 and sum(p.suffix=='.png' for p in files)<=4
        assert sum(p.stat().st_size for p in files)<128000000
        for p in files:native_files[name+'/'+p.relative_to(child).as_posix()]=p
        native[name]=q
    shot=native['qualified-shots'];menu=native['qualified-menu']
    assert shot['rising_seen'] and shot['mature_seen'] and shot['source_owner_seen'] and shot['erased_seen']
    assert shot['source_weapon']==1 and shot['maximum_projectiles']==2
    assert len(menu['transitions'])==124 and not menu['anomalies']
    assert menu['heading_errors']==menu['visible_mask_writes']==0
    prior=R/'docs/qa/checkpoints/2026-11-01/karnov-menu-health-nightly-v3/source.zip'
    with zipfile.ZipFile(prior) as z:manifest=json.loads(z.read('files.json'))
    # Current copies of the prior compact source closure, plus this graft's
    # exact compiled fragments and receipts. No ROM, debug/object or tree copy.
    sources={n:Path(v['original']) for n,v in manifest.items() if not n.endswith('.json')}
    for n in ['entrypoint.s','cf_menu_body.inc','kr-kernel.s','kr-resident.inc','kr-terrain.inc',
        'kr-pickup-rom-context-v3.inc','kr-pickup-rom-align-v3.inc',
        'kr-pickup-rom-tail-v3.inc','kr-pickup-kernel-v3.inc','kr-pickup-rom-route-v4.inc','kr-pickup-rom-auth-v5.inc',
        'terrain-assembly.json','terrain-main-build.json','terrain-kernel-build.json',
        'terrain-first-link.json','terrain-images-build.json','terrain-final-link.json',
        'ingress-union-build.json','menu-health-suite.json',*suite['receipts']]:
        sources['host/'+n]=J/n
    tools=['build_karnov_gameplay_host_1101_v1.py','prepare_karnov_pickup_host_1101_v3.py','prepare_karnov_pickup_host_1101_v4.py','prepare_karnov_pickup_host_1101_v5.py',
        'check_karnov_pickup_composed_1101_v4.py','prepare_karnov_pickup_native_1101_v4.py',
        'prepare_karnov_pickup_final_native_1101_v5.py','deliver_karnov_pickups_1101_v4.py']
    for n in tools:sources['tools/audit/'+n]=R/'tools/audit'/n
    sources['tools/reference/karnov_pickups_1101_v2.inc']=R/'tools/reference/karnov_pickups_1101_v2.inc'
    sources['pickup-composed/final.json']=composed_path
    sources['pickup-composed/baseline.json']=C/'baseline.json'
    # Historical failing receipt keeps its exact generating checker alongside
    # it. Its old live-source binding is not a claim about today's checker.
    for n in ['negative-c917-reserve129.json','negative-c917-checker.py']:
        sources['pickup-composed/'+n]=C/n
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(nightly)==PREVIOUS
    carrier=R/'build/karnov-carrier-closure-1101-v4/source-and-proof.zip'
    assert sha(carrier)=='684aca698afd1e0a6e8db14bde684c0c2b46f303c204ccba54fa8fea171e23d1'
    pending_components=[('carrier-loader-bounds','karnov-carrier-loader-bounds-1101-v5/source-and-proof.zip','0bf639df7f17883e9c1165426d76e54974d6d39fc16553539304b317662ba070'),
        ('metal-storm-host','metal-storm-host-contract-1101-v4/source-proof.zip','71950815e98a78eef49d98dfa41c7067cb20106fd2d62b43ffe06ec98bcebbdf')]
    for _,name,expected in pending_components:assert sha(R/'build'/name)==expected
    D.mkdir();source=pack(D/'source.zip',sources);natives=pack(D/'native-results.zip',native_files)
    shutil.copyfile(carrier,D/'unallocated-carrier-closure.zip')
    component=dict(path=(D/'unallocated-carrier-closure.zip').relative_to(R).as_posix(),
        sha256=sha(D/'unallocated-carrier-closure.zip'),carrier_granted=False,integrated=False)
    next_components={}
    for name,origin,expected in pending_components:
        target=D/(name+'.zip');shutil.copyfile(R/'build'/origin,target);assert sha(target)==expected
        next_components[name]=dict(path=target.relative_to(R).as_posix(),sha256=expected,integrated=False)
    assert sha(J/'candidate.nes')==EXPECTED
    shutil.copyfile(J/'candidate.nes',nightly);assert sha(nightly)==EXPECTED
    verification=dict(ROM_sha256=EXPECTED,source_CPU_suite=list(suite['receipts']),
        composed={k:composed[k] for k in ['core','old_owners','emergence','Main']},
        double_shot_Main=shot['Main'],double_shot_ISR_returns=shot['ISR_returns'],maximum_projectiles=2,
        native_menu_transitions=124,native_menu_frames=menu['frames'],
        sampled_gray_anomalies=0,heading_errors=0,visible_mask_writes=0)
    result=dict(passed=True,installed=True,backup_created=False,user_requested_WIP=True,complete=False,
        destination=str(nightly),output_sha256=EXPECTED,replaced_sha256=PREVIOUS,
        selectable_identities=86,previously_verified_identities=85,total_menu_identities=90,
        selection='Rygar -> Select -> Karnov -> A/Start',checkpoint=D.relative_to(R).as_posix(),
        source=source,native=natives,verification=verification,unallocated_carrier_closure=component,next_components=next_components,
        changes=['Karnov block items now use original earned weapon/health state instead of Mario tiers.',
            'Items retain native emergence and award their original progression only on real collection.',
            'Authenticated block-item preparation avoids nested bank calls, retaining the required interrupt stack reserve.',
            'Mushrooms heal depleted original health or advance single/double/triple fireballs; healthy triple-shot flowers cycle original equipment stock0..9.',
            'Native item erase, pickup sound and score remain; existing menu, health/death and stomp fixes are retained.'],
        pending=['Original equipment activation/Select/HUD/icons and original audio remain unfinished.',
            'Karnov projectile-to-enemy/block combat remains an unintegrated source component pending resource and real Main stack qualification.',
            'Full1-1, shortcut and every-powerup controller playthroughs remain unfinished.',
            'Metal Storm, Shinobi and Excitebike are not selectable yet.'],
        diagnostics=['An initial firing fixture held B immediately after movement/collection; the original actor lost that edge on its walking-to-idle transition. The corrected controller fixture pulses B and observes two simultaneous source projectiles.',
            'Two predecessor prototypes failed actual Main block-spawn interrupt reserve. The c917 negative receipt and exact generating checker are preserved; it reached129 (only6 above SMC). The final direct preparation and authentication path reaches135, satisfying12. Only final exact-candidate results qualify this delivery.'],
        storage=preflight(fresh=True))
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (D/'README.md').write_text('''# Karnov contact-earned pickup WIP

The exact0162287e candidate replaces the single Downloads nightly, with no
backup. Reopen the ROM and start fresh. Rygar -> Select -> Karnov -> A/Start.

Actual native controller input hits the first mushroom block, observes its
emergence and contact pickup, then fires two original source projectiles.
The exact ROM also passes the124-transition roster sweep, original health /
death / restart / terrain / scene suite and composed pickup consumer checks.
See handoff.json for fixture boundaries and the actual Main interrupt result.

Mushrooms restore original depleted health or advance normal fireballs.
Flowers advance to triple shots, then cycle original equipment stock. Earned
stock is preserved, but equipment activation, Select UI and icons are not yet
wired. Native projectile combat, original audio and full-stage qualification
are unfinished. This remains86 selectable identities with Karnov as a WIP.

Packets contain compact source overlays, recipes and verification receipts;
their earlier composition dependencies remain required. No ROMs, object/debug
files or videos are embedded. The prior e8 ROM reference in the old-owner
differential is historical and was intentionally replaced in Downloads.
''',encoding='utf-8')
    (O/'binding.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    path=R/'docs/qa/continuation-current.json';state=json.loads(path.read_text())
    state['installed_nightly']=result;state['storage']=result['storage']
    state['current_priority']='Delivered current86 WIP0162287e with contact-earned Karnov pickups, actual double-shot firing and repaired Main interrupt stack reserve. Next native projectile combat, original option activation/HUD/audio, then full-stage qualification and remaining original-source roster integrations. Publish each usable WIP to the single Downloads ROM without backups.'
    k=state['Karnov_current'];k.update(installed=True,installed_nightly_sha256=EXPECTED,
        current_WIP_checkpoint=result['checkpoint'],current_pickups=dict(checkpoint=result['checkpoint'],
        ROM_sha256=EXPECTED,services=stage['implemented_services'],resident_bytes=stage['resident_bytes'],
        kernel_bytes=stage['kernel_bytes'],verification=verification))
    k['next']=result['pending']
    k['carrier_closure_v4']=component
    k['carrier_loader_bounds_v5']=next_components['carrier-loader-bounds']
    k['carrier_policy']='CHR1019/1020 remains ungranted. V4 closes Arthur descriptors, Special/HUD override retention and declared FF body pairing; V5 closes the five named high3 copy-loader bounds. Ordinary compiled/indirect window ownership, actual Main publication seams and final integrated binding remain. The current low-stack pickup route leaves2B resident tail and54B kernel, so the earlier70B loader-helper proposal also needs a newly funded layout.'
    state['next_original_components']=next_components
    state['agents']='Three authorized workers completed the composed pickup/Main proof, two compact unallocated-carrier audits and the Metal Storm original-source host contract. Root owns compilation, native Mesen queue and nightly delivery. All component packets are preserved here; historical workers are not automatically current.'
    state['other_full_objective_work'][0]='Karnov is selectable WIP with original movement, health/death/stomp and contact-earned pickups; projectile combat, equipment activation/HUD/icons, original audio and full-stage testing remain.'
    path.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['passed','destination','output_sha256','backup_created','source','native','storage']}))


if __name__=='__main__':main()
