"""Small additive review checkpoint: one operand, exact scopes, actual images."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C = D / 'robot-color-rotation-candidate-v3'
S = D / 'robot-color-rotation-source-ready-v1'
N = D / 'robot-color-rotation-combined-ready-v1'
V = D / 'robot-color-rotation-native-review-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(V / 'proof.json') == '49fa6019159984c806e06d026ef2a0bede0bb97ca746077430bb1dc832bc9201'
    for f, h in json.loads((V / 'external-raw-manifest.json').read_text()).items():
        assert sha(f) == h, f
    for f, h in json.loads((N / 'bindings.json').read_text()).items():
        assert sha(f) == h, f
    copies = {}
    def copy(src, rel):
        dst = a.output / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copies[rel] = dict(source=str(src), sha256=sha(dst))
    copy(C / 'source/src/game.s', 'incremental-source/src/game.s')
    copy(C / 'source.patch', 'incremental-source.patch')
    for sub in ['proof.json', 'cpu-v3/proof.json', 'caller-v6/proof.json', 'build-controls-v1/proof.json']:
        copy(C / sub, 'source-proofs/' + sub.replace('/', '-'))
    for sub in ['proof.json', 'metadata-proof.json', 'readiness.json', 'launch-binding-v1.json', 'launch-outcome-v1.json']:
        src = N / sub if (N / sub).is_file() else S / sub
        copy(src, 'native/' + sub)
    for sub in ['proof.json', 'native-evidence.json', 'samples.json', 'external-raw-manifest.json']:
        copy(V / sub, 'native-review/' + sub)
    copy(N / 'native/native-mm-weapon-profile.json', 'native/native-six-component-summary.json')
    for f in sorted(V.glob('*.png')):
        copy(f, 'images/' + f.name)
    final = ['mm_proto_color_rotation_candidate_v3.py', 'mm_proto_color_rotation_cpu_v3.py',
             'mm_proto_color_rotation_caller_v6.py', 'mm_proto_color_rotation_freeze_v1.py',
             'mm_proto_color_rotation_combined_prepare_v1.py', 'mm_proto_color_rotation_native_review_v1.py',
             'mm_proto_color_rotation_checkpoint_v1.py']
    for name in final:
        copy(R / 'tools/audit' / name, 'tools/' + name)
    reports = [R / 'docs/qa/mm-proto-color-rotation-2026-10-26.txt', R / 'docs/qa/mm-proto-color-rotation-native-2026-10-26.txt']
    for f in reports:
        copy(f, 'reports/' + f.name)
    prerequisites = json.loads((N / 'bindings.json').read_text())
    put(a.output / 'external-prerequisites-by-hash.json', dict(
        source_ready=dict(path=str(S / 'proof.json'), sha256=sha(S / 'proof.json')),
        native_ready=dict(path=str(N / 'readiness.json'), sha256=sha(N / 'readiness.json')),
        native_bindings=dict(path=str(N / 'bindings.json'), sha256=sha(N / 'bindings.json'), count=len(prerequisites)),
        prior_df_source_checkpoint='docs/qa/checkpoints/2026-10-26/robot-base-palette-source-v1',
        original_false_evidence=dict(path=str(D / 'robot-balancer-budget-review-v1/proof.json'), sha256=sha(D / 'robot-balancer-budget-review-v1/proof.json')),
        reconstruction='This new source overlay/patch is incremental versus frozen df; full df helpers/config/entrypoint are in the prior checkpoint. Combined ce635 source is ROOT-owned and separately cataloged. No turnkey fresh-clone QA reproduction claim; original local reference/ROM/runtime dependencies stay external.'))
    put(a.output / 'visual-review.json', dict(reviewed=True, actual_whole_frame_placements=86,
        sheets=5, selected_frame_review_only=True, no_all1031frame_manual_review=True,
        stable_sampled_HUD_world_startup_busy_packet=True,
        residuals=['Charged shot720/724 partial body/shot omission', 'Crowded Rush868..873 part/body omission'],
        no_perfect_fairness_or_art_fidelity_claim=True, original_raw_pixels_unchanged=True))
    put(a.output / 'README.txt', 'SOURCE ca9a one-byte CPX threshold; NATIVE ce635 combined6ProtoHard cases PASS.\n'
        'Scopes remain distinct. ca9a standalone never launched. Earlier FALSEs retained.\n'
        'Intentional busy-frame world-palette deferral; Y/V dead-return details explicit.\n'
        'Actual counter/retry beyond diagnostic996 unlogged; source7retry proof separate.\n'
        'Selected86wholeframe review retains8sprite body/shot/Rush omissions.\n'
        'No ROM/reference audio/settings/raw lossless payloads are included.\n'
        'No production/default install, broad roster, perfect fairness or matched FPS claim.\n')
    catalog = {f.relative_to(a.output).as_posix():dict(sha256=sha(f), bytes=f.stat().st_size)
               for f in a.output.rglob('*') if f.is_file()}
    assert sum(x['bytes'] for x in catalog.values()) < 1024*1024
    put(a.output / 'catalog.json', catalog)
    owned = sorted((R / 'tools/audit').glob('mm_proto_color_rotation_*.py')) + reports
    put(a.output / 'review-files.json', dict(
        checkpoint=str(a.output), owned_files=[dict(path=f.relative_to(R).as_posix(), sha256=sha(f)) for f in owned],
        final_tools=final, earlier_tool_versions='Retained qualifier/prose negatives. Not game failures or source corrections.',
        Git_mutations_performed=False))
    put(a.output / 'proof.json', dict(checkpoint_verified=True, source_qualified=True,
        native_profile_pass=True, native_ROM_sha256='ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111',
        standalone_source_ROM_sha256='ca9a1c13e4f25a834ac665c4c9a6d67cf0be3c19ee7dc2af284a432e359be1fe',
        standalone_native_unrun=True, earlier_FALSEs_preserved=True, native_launches=1, retries=0, worker_released=True,
        payloads=len(catalog), payload_bytes=sum(x['bytes'] for x in catalog.values()),
        catalog_sha256=sha(a.output / 'catalog.json'), review_files_sha256=sha(a.output / 'review-files.json'),
        source_native_copy_bindings=copies, raw_payloads_or_ROM_audio_settings_copied=False,
        tool_sha256=sha(__file__), limits='Review/rollback checkpoint only. Exact incremental source and source/native scopes. No installation, full-roster, waveform, art-clean or matchedperformance claim.'))
    print(json.dumps(dict(checkpoint=str(a.output), proof_sha256=sha(a.output / 'proof.json'),
        review_files_sha256=sha(a.output / 'review-files.json'), payloads=len(catalog), bytes=sum(x['bytes'] for x in catalog.values())), indent=2))


if __name__ == '__main__':
    main()
