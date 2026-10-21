"""Collect the completed actual menu/contact tests without relabeling negatives."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=R/'build/verification/root49-menu-validation-s2.json';assert not out.exists()
    refs={};receipts=[]
    def read(p):
        p=Path(p);refs[str(p.relative_to(R))]=sha(p);return json.loads(p.read_text())
    candidate=read(R/'build/verification/root49-menu-options-private-s2/report.json')
    assert candidate['status']=='PASS_PRIVATE_MENU_S2_BUILD_LAYOUT_ONLY'
    for row in candidate['builds']:
        for value in row['outputs'].values():assert sha(value['path'])==value['sha256']
    for tag in ('root-s2-mmc3-b','root-s2-mmc5-ui-b'):
        folder=R/'build/verification/menu-options-behavior-ui-b'/('binding-'+tag)
        binding=read(folder/'binding.json');ui=read(folder/'native-output/result.json')
        assert ui['passes']and ui['steps']==31 and ui['frames']==2691 and ui['controller_only']and not ui['emulated_writes']
        assert ui['title_gamecore']==ui['demo_entries']==0
        assert sha(binding['rom'])==binding['rom_sha256']
    core=read(R/'build/verification/agent49-menu-combat-root-w/root-core-summary.json')
    assert core['status']=='PASS_CORE_MENU_COMBAT_MATRIX'and len(core['cases'])==12
    for row in core['cases']:
        receipt=read(row['receipt']);assert sha(row['receipt'])==row['receipt_sha256']
        assert receipt['status']=='PASS_BOUNDED_SEEDED_NATIVE_COMPONENT'and receipt['exit']==0
        receipts.append(row['case'])
    w3=R/'build/verification/agent49-menu-combat-root-w3'
    assert sha(w3/'freeze.json')=='197f29598c2fd73f6201003fb5785a2eacba74fdbf0ada1a458f496c95276b16'
    plan=read(w3/'plan.json');assert len(plan['cases'])==35
    for case in plan['cases']:
        binding=read(case['binding_path']);assert sha(case['binding_path'])==case['binding_sha256']
        for value in binding['references']+[binding['wrapper'],binding['core'],binding['freeze']]:
            assert sha(value['path'])==value['sha256']
        receipt_path=Path(case['binding_path']).parent/'root-native-receipt.json'
        receipt=read(receipt_path)
        assert receipt['status']=='PASS_BOUNDED_SEEDED_NATIVE_COMPONENT'and receipt['exit']==0,case['case']
        assert sha(receipt['log']['path'])==receipt['log']['sha256']
        raw=Path(receipt['log']['path']).read_text();assert 'PASS 'in raw and 'FAIL 'not in raw
        receipts.append(case['case'])
    smoke=read(w3/'imported-root-smoke.json')
    assert smoke['root_reported_exit']==0 and len(smoke['literal_case_pass_lines'])==14
    assert sha(smoke['binding']['path'])==smoke['binding']['sha256']
    assert sha(smoke['log']['path'])==smoke['log']['sha256']
    receipts.append(smoke['case']['case']);assert len(set(receipts))==48
    a=read(R/'build/verification/root-menu-migration-targeted-a/root-native-summary.json')
    accepted=[q for q in a['cases']if q['test']not in('player-outlines','player-outlines-render')]
    assert len(accepted)==12 and all(q['passed']for q in accepted)
    b=read(R/'build/verification/root-menu-migration-targeted-b/root-native-summary.json')
    assert b['status']=='PASS_CORRECTED_OUTLINE_TESTS'and len(b['cases'])==4
    assert all(q['passed']for q in b['cases'])
    for q in accepted+b['cases']:assert sha(q['log'])==q['log_sha256']
    high=read(R/'build/verification/agent49-menu-behavior-combat-v2/negative-classification.json')
    assert high['status']=='HOST_CLASSIFIED_UNEXERCISED_NATIVE_FIXTURE_NOT_RUNTIME_DEFECT'
    result=dict(status='PASS_MENU_S2_UI_CONTACT_AND_PROTECTED_ATTACKS',script_sha256=sha(__file__),
        references=refs,UI_mappers=2,UI_steps_per_mapper=31,ordinary_contact_groups=16,
        seeded_ordinary_arenas_per_mapper=688,protected_attack_groups=32,targeted_regression_cases=16,
        accepted_groups=receipts,default_behavior='1.0',default_shadows='OFF',
        actual_screenshots_visually_reviewed=True,character_select_setting_removed=True,
        original_negatives_retained=True,PCM_audio_review_claim=False,full_roster_route_claim=False,
        qualification='Actual native controller UI plus seeded native contact/score/bounce/effect-dispatch/attack-priority controls. Generic BowserFlame21 arena was unexercised; its exclusion/pipeline is compiled-literal to R and protected projectile21 contacts are checked independently. Broader full-roster routes and final recordings remain open.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out))
if __name__=='__main__':main()
