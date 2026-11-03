"""Review exact combined83 typed imports and emit a private performance candidate."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/combined-owner-auth-root-1103-v116'
P = ROOT/'build/bub-menu-candidate-1102-v2'
ALLOC = ROOT/'docs/qa/allocations/combined-owner-auth-1103-v116.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    review_path = P/'combined-auth-v90-callers.json'
    recipe_path = P/'combined-auth-v90-composition.json'
    review = json.loads(review_path.read_text())
    recipe = json.loads(recipe_path.read_text())
    assert review['passed'] and recipe['passed']
    assert not review['ROM_written'] and not recipe['ROM_written']
    for q in (review,recipe):
        for name,digest in q['bindings'].items():
            assert sha((ROOT/name).read_bytes()) == digest,name
    assert [r['CPU'] for r in review['all_four_Sh_callers']] == [0xA7AB,0xA8DD,0xABDA,0xAC8D]
    assert [r['CPU'] for r in review['compiled_current_bank65_JSR_JMP_callers']['CoCheckCode']] == [0xA75A,0xA824]
    final = json.loads((P/'combined-auth-source-v89.json').read_text())
    assert final['passed'] and not final['cache_used'] and not final['new_RAM_used']
    assert final['complete_auth_checks_per_Main'] == 13
    for name in ('combined-auth-v84-contracts.json','combined-auth-v85-lifecycle.json',
            'combined-auth-v86-ISR.json','combined-auth-v87-nested.json','combined-auth-v88-references.json'):
        proof = json.loads((P/name).read_text())
        assert proof['passed'],name
        for path,digest in proof.get('bindings',{}).items():
            assert sha((ROOT/path).read_bytes()) == digest,(name,path)
    sys.path.insert(0,str(ROOT/'tools/audit'))
    import prepare_bub_combined_auth_review_1103_v90 as source
    raw,reproduced,_ = source.image()
    assert sha(raw) == recipe['expected_memory_SHA256'] == reproduced['expected_memory_SHA256']
    assert recipe['expected_memory_SHA256'] == '80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
    base_path = ROOT/recipe['base_candidate']
    base = base_path.read_bytes()
    assert sha(base) == recipe['base_SHA256'] == '6c9e85a94d34a4623d21789d5293c61af2ad14d214f5780f57613a51ae6bb25a'
    assert sum(a!=b for a,b in zip(base,raw)) == recipe['total_changed_bytes'] == 11525
    assert recipe['all_other_CHR_pages_byte_identical'] and recipe['all_out_of_recipe_bytes_byte_identical']
    assert not recipe['DK_scene_or_menu_admission_added'] and recipe['scene_gate_remains_37_to_39']
    grant = dict(granted=True,status='EXACT_PRIVATE_SOURCE_COMPOSITION_NATIVE_TEST_ONLY',
        base_candidate_SHA256=recipe['base_SHA256'],expected_candidate_SHA256=sha(raw),
        reviewed_layers=recipe['ordered_exact_preimage_layers'],
        typed_contracts=review['ABI'],private_DK_code_pages=recipe['code_pages'],
        private_DK_art_pages=recipe['art_helper_pages'],
        scope='Exact101+83 overapproved113/159 and unchanged105frontend. Approves only measured531/97/176/73 resident source envelopes, three public raw39 full-auth primitive vectors, previously approved DKbbox/rare gates and existing private11carriers. Every call still checks both16Bheaders; no cache/globalRAM/otherpadding lease. Public A800 saves originalAXYP exceptC, including wrongowner frame; private helpers carry-only within named saved callers. All fixed native callers and primitive restore/NZ paths reviewed.',
        limitations=['No nightly/install approval until native validation.',
            'Prince graphical bank0 issue from176/177 is retained, outside this common-source change.',
            'Raw40 scene/menu admission is not included; no DKplayable or helper crossing claim.',
            '4251cycles/Main is a CPU-model result, not a measured frame-rate improvement.',
            review['limits']],
        bindings={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (
            Path(__file__),review_path,recipe_path,P/'combined-auth-source-v89.json',
            ROOT/'docs/qa/allocations/prince-live-lifetime-1103-v113.json',
            ROOT/'docs/qa/allocations/dkjr-shared-gates-1103-v104.json')})
    assert not ALLOC.exists()
    ALLOC.write_text(json.dumps(grant,indent=2)+'\n')
    candidate = OUT/'combined-auth-private.nes'
    candidate.write_bytes(raw)
    assert sha(candidate.read_bytes()) == sha(raw)
    for suffix in ('.lbl','.dbg'):
        candidate.with_suffix(suffix).write_bytes(base_path.with_suffix(suffix).read_bytes())
    result = dict(passed=True,private_native_candidate=True,installed=False,
        candidate=candidate.relative_to(ROOT).as_posix(),candidate_SHA256=sha(raw),
        native_scope_pending='Bub/Bob full1-1 andmaturity, Shinobi/Ex/Prince native regressions. DKmenu/scene andPrinceCHRfix are separate. Downloads remainscf7.',
        source_review=review_path.relative_to(ROOT).as_posix(),composition_recipe=recipe_path.relative_to(ROOT).as_posix(),
        grant=ALLOC.relative_to(ROOT).as_posix())
    (OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    handoff = ROOT/'docs/qa/continuation-current.json'
    current = json.loads(handoff.read_text())
    current['bub_performance_current_1102'].update(
        root_private_candidate=result['candidate'],root_private_candidate_SHA256=sha(raw),
        root_private_grant=result['grant'],combined_auth_status='EXACT83_TYPED_SOURCE_GRANTED_NATIVE_PENDING')
    handoff.write_text(json.dumps(current,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
