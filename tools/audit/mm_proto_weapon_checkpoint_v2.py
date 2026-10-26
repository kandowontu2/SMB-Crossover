"""Publishable small evidence checkpoint for Mega PASS and matched Proto FAIL."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D/'mm-proto-weapon-boundary0a-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
get = lambda p: json.loads(Path(p).read_text())
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args();a.output.mkdir(parents=True, exist_ok=False)
    cp = R/'docs/qa/checkpoints/2026-10-26/mega-proto-primary0a-v1'
    cp.mkdir(parents=True, exist_ok=False)
    assert get(B/'mega-native-review-v1/proof.json')['passed']
    assert get(B/'proto-causal-comparison-v1/proof.json')['existing_installed3b_deadline_failure_demonstrated']
    copies = {
        'README.txt':R/'docs/qa/mm-proto-weapon-native0a-2026-10-26.txt',
        'preparation-scope.txt':R/'docs/qa/mm-proto-weapon-boundary0a-2026-10-26.txt',
        'source-only-readiness.json':B/'ready-v1/readiness.json',
        'source-body-equality.json':B/'ready-v1/source-delta.json',
        'Mega-native-summary.json':B/'mega-hard-ready-v2/native/native-mm-weapon-profile.json',
        'Mega-independent-review.json':B/'mega-native-review-v1/proof.json',
        'Mega-image-bindings.json':B/'mega-native-review-v1/samples.json',
        'Mega-rush-consecutive-bindings.json':B/'mega-native-review-v1/rush-consecutive-bindings.json',
        'Mega-primary-actual-whole-images.png':B/'mega-native-review-v1/primary-actual-whole-images.png',
        'Mega-support-actual-whole-images.png':B/'mega-native-review-v1/support-actual-whole-images.png',
        'Mega-rush-consecutive-actual-PPU.png':B/'mega-native-review-v1/rush-consecutive-actual-PPU.png',
        'Proto-original-negative.json':B/'proto-native-negative-v1/proof.json',
        'Proto-matched-causal-comparison.json':B/'proto-causal-comparison-v1/proof.json',
        'Proto-last-completed-375-pair.png':B/'proto-causal-comparison-v1/proto-last-completed-375-pair.png',
        'Proto-matched-source-body.json':B/'proto-installed3b-baseline-ready-v1/matched-source-proof.json',
        'source-preparation-first-negative.json':B/'mega-hard-ready-v1/failure.json',
        'both-variant-assembled-controls.json':B/'mega-hard-ready-v2/assembled-controls.json',
        'original-hardware-static-controls.json':B/'mega-hard-ready-v2/source-controls.json',
        'Mega-art-caller-controls.json':B/'mega-art-v1/proof.json',
        'Proto-art-caller-controls.json':B/'proto-art-v1/proof.json',
    }
    for name, source in copies.items():
        shutil.copyfile(source, cp/name);assert sha(source) == sha(cp/name)
    external = {}
    for manifest in [B/'mega-native-review-v1/external-raw-manifest.json',
                     B/'proto-causal-comparison-v1/external-raw-manifest.json']:
        for name, expected in get(manifest).items():
            assert sha(name) == expected, name
            external[name] = expected
    put(cp/'external-raw-hashes.json', dict(sorted(external.items())))
    dependencies = {}
    for name, expected in get(B/'ready-v1/bindings.json').items():
        assert sha(name) == expected, name
        dependencies[name] = expected
    tools = [R/'tools/audit'/n for n in [
        'mm_proto_weapon_boundary_prepare_v4.py', 'mm_proto_weapon_boundary_prepare_v5.py',
        'mm_proto_weapon_boundary_prepare_v6.py', 'mm_proto_weapon_art_owner_controls_v2.py',
        'mm_proto_weapon_boundary_live_models_v3.py', 'mm_proto_weapon_boundary0a_freeze_v1.py',
        'mm_proto_weapon_boundary0a_run_v1.py', 'mm_proto_weapon_baseline_run_v1.py',
        'mm_proto_weapon_boundary_review_v4.py', 'mm_proto_weapon_proto_causal_v1.py',
        'mm_proto_weapon_checkpoint_v2.py']]
    reports = [R/'docs/qa/mm-proto-weapon-boundary0a-2026-10-26.txt',R/'docs/qa/mm-proto-weapon-native0a-2026-10-26.txt']
    tool_hashes = {str(p.relative_to(R)).replace('\\','/'):sha(p) for p in tools}
    put(cp/'owned-tools-and-imports.json', dict(owned_tools=tool_hashes,
        local_prerequisites={n:h for n,h in dependencies.items() if Path(n).is_relative_to(R/'tools') and n not in {str(p) for p in tools}},
        all927_source_dependency_manifest=str(B/'ready-v1/bindings.json'),
        all927_source_dependency_manifest_sha256=sha(B/'ready-v1/bindings.json'),
        qualification_scope='Finite frozen source/native receipts, not turnkey fresh-clone native reproduction.'))
    put(cp/'visual-review.json', dict(agent_reviewed_Mega_selected_whole_images=34,
        agent_reviewed_Mega_consecutive_Rush_completed_PPU_images=36,
        universal_graphics_pass=False, Proto_six_components_not_reached=True,
        all375_Proto_completed_PPU_pairs_byte_exact=True,
        full1030_Mega_frames_manual_review=False, source_time_captures_can_precede_publication=True,
        original_Rush_streak_cloud_dog_spring_forms_coherent_in_selected_frames=True,
        overloaded_body_shot_visibility_and_final_palette_fidelity_not_closed=True))
    put(cp/'review-files.json', dict(stage_only_after_ROOT_review=[str(cp.relative_to(R)).replace('\\','/')+'/',
        *tool_hashes,*[str(p.relative_to(R)).replace('\\','/') for p in reports]],
        no_git_actions_performed=True, no_new_game_source_patch=True))
    catalog = {str(p.relative_to(cp)).replace('\\','/'):sha(p) for p in sorted(cp.rglob('*')) if p.is_file()}
    put(cp/'catalog.json',catalog)
    proof = dict(passed=True, checkpoint=str(cp), catalog_sha256=sha(cp/'catalog.json'),
        public_files_before_proof=len(catalog)+1, public_bytes_before_proof=sum(p.stat().st_size for p in cp.rglob('*') if p.is_file()),
        native_Mega_six_cases_pass=True, native_Proto_deadline_pass=False, existing_installed_Proto_failure=True,
        no_adoption=True, native_worker_released=True, no_new_native_launches=True,
        tool_sha256=sha(__file__), review_files_sha256=sha(cp/'review-files.json'))
    put(cp/'checkpoint-proof.json',proof)
    assert sum(p.stat().st_size for p in cp.rglob('*') if p.is_file()) < 1000000
    for source in tools+reports:
        target=a.output/'owned-files'/source.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    put(a.output/'receipt.json',dict(passed=True,checkpoint_proof_sha256=sha(cp/'checkpoint-proof.json'),
        public_files={str(p.relative_to(cp)).replace('\\','/'):sha(p) for p in sorted(cp.rglob('*')) if p.is_file()},
        owned_files={str(p):sha(p) for p in sorted((a.output/'owned-files').rglob('*')) if p.is_file()}))
    print(json.dumps(dict(proof=proof,receipt_sha256=sha(a.output/'receipt.json')),indent=2))


if __name__ == '__main__':
    main()
