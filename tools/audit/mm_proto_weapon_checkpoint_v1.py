"""Freeze the compact MegaHard native review; no emulator or production writes."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE = D / 'mm-proto-weapon-boundary-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    checkpoint = R / 'docs/qa/checkpoints/2026-10-26/mega-hard-primary3b-v1'
    assert not out.is_relative_to(R)
    out.mkdir(parents=True, exist_ok=False)
    checkpoint.mkdir(parents=True, exist_ok=False)
    native = BASE / 'native-ready-v3/native'
    review = BASE / 'native-review-v3'
    rush = BASE / 'rush-visual-v3'
    verified = json.loads((review / 'proof.json').read_text())
    assert verified['passed'] and verified['actual_whole_image_samples'] == 34
    assert json.loads((rush / 'proof.json').read_text())['passed']
    # Bind the intended icon to the very same visible epochs used in the sheets.
    same_frame = []
    for line in (native / 'bass-diagnostic.jsonl').read_text().splitlines():
        q = json.loads(line)
        if q['kind'] != 'actual-visible-startFrame-font-hardware' or q['stamp']['frame'] not in (853, 856, 872, 873):
            continue
        s = q['state']
        assert s['InvHudActive'] == 1 and s['InvHudPhysical'] == s['actualChr'][8] == 243
        assert s['InvIndex'] == 24 and s['InvHudAmmo'] == 20
        assert s['HUDicon'] == [42, 43, 44, 45] and s['HUDname'] == [27, 30, 28, 17, 36, 36, 36]
        same_frame.append(dict(stamp=q['stamp'], HUDname=s['HUDname'], HUDicon=s['HUDicon'],
                               InvHudPhysical=s['InvHudPhysical'], actualChr=s['actualChr'],
                               InvIndex=s['InvIndex'], InvHudAmmo=s['InvHudAmmo']))
    assert len(same_frame) == 4
    icon = dict(passed=True, read_only=True, original_label='rushCoil', original_pickup_frame=10,
                same_visible_epochs=same_frame, raw_diagnostic_sha256=sha(native / 'bass-diagnostic.jsonl'),
                exact_generated_and_native_CHR_proof_sha256=sha(rush / 'proof.json'))
    (out / 'icon-same-frame.json').write_text(json.dumps(icon, indent=2) + '\n')
    copies = {
        'README.txt': R / 'docs/qa/mm-proto-weapon-native-2026-10-26.txt',
        'native-summary.json': native / 'native-mm-weapon-profile.json',
        'native-review.json': review / 'proof.json',
        'external-raw-manifest.json': review / 'external-raw-manifest.json',
        'actual-image-bindings.json': review / 'samples.json',
        'primary-actual-whole-images.png': review / 'primary-actual-whole-images.png',
        'support-actual-whole-images.png': review / 'support-actual-whole-images.png',
        'rush-850-885-actual-whole-images.png': rush / 'rush-850-885-actual-whole-images.png',
        'rush-read-only-proof.json': rush / 'proof.json',
        'rush-actual-pose-and-priority.json': rush / 'actual-rows.json',
        'rush-same-frame-icon.json': out / 'icon-same-frame.json',
        'original-art-oracle-negative-and-correction.txt': R / 'docs/qa/mm-proto-weapon-art-oracle-2026-10-26.txt',
        'original-native-negative.json': BASE / 'native-negative-v1/proof.json',
        'offline-review-v1-negative.json': BASE / 'native-review-v1/failure.json',
        'offline-review-v2-negative.json': BASE / 'native-review-v2/failure.json',
        'assembled-source-controls.json': BASE / 'native-ready-v3/assembled-controls.json',
        'actual-art-owner-controls.json': BASE / 'art-owner-controls-v1/proof.json',
    }
    for name, source in copies.items():
        shutil.copyfile(source, checkpoint / name)
        assert sha(source) == sha(checkpoint / name)
    frozen_source = D / 'root-current-roster-composition-v1/source'
    source_names = ['src/megaman_weapons.s', 'src/megaman_rush.s', 'src/megaman_rush_land.s',
                    'src/special_weapons.s', 'src/inventory.s', 'src/inventory_data.inc',
                    'src/protoman_legacy_shots.inc', 'src/special_art.inc', 'src/chr_map_mmc5.inc',
                    'tools/reference/build_special_art.py']
    sources = dict(ROM_sha256='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287',
                   frozen_source_root=str(frozen_source),
                   full_869_source_manifest_sha256='86eacaf0a954abf8cf0ff7fc8ee6b03b13fc406f2335b5d864eb96c554f868a6',
                   directly_reviewed_source={name: sha(frozen_source / name) for name in source_names},
                   game_patch=False, native_ready_sha256=sha(BASE / 'native-ready-v3/readiness.json'),
                   grant_sha256=sha(BASE / 'native-ready-v3/ROOT-native-grant-v1.json'))
    (checkpoint / 'exact-source.json').write_text(json.dumps(sources, indent=2) + '\n')
    tools = sorted([*R.glob('tools/audit/mm_proto_weapon_boundary*.py'),
                    R / 'tools/audit/mm_proto_weapon_boundary_v1.lua',
                    R / 'tools/audit/mm_proto_weapon_art_owner_controls_v1.py',
                    R / 'tools/audit/mm_proto_rush_visual_read_v1.py', Path(__file__)])
    reports = [R / 'docs/qa/mm-proto-weapon-boundary-2026-10-26.txt',
               R / 'docs/qa/mm-proto-weapon-art-oracle-2026-10-26.txt',
               R / 'docs/qa/mm-proto-weapon-native-2026-10-26.txt']
    tool_hashes = {str(p.relative_to(R)).replace('\\', '/'): sha(p) for p in tools}
    prerequisites = {p: h for p, h in json.loads((BASE / 'native-ready-v3/bindings.json').read_text()).items()
                     if Path(p).is_relative_to(R / 'tools') and p not in {str(q) for q in tools}}
    (checkpoint / 'owned-tools-and-imports.json').write_text(json.dumps(dict(
        owned_tools=tool_hashes, imported_local_prerequisites=prerequisites,
        qualification_scope='Finite frozen source/native evidence; not turnkey fresh-clone native reproduction.'), indent=2) + '\n')
    review_files = dict(stage_only_after_ROOT_review=[str(checkpoint.relative_to(R)).replace('\\', '/') + '/',
                        *tool_hashes, *[str(p.relative_to(R)).replace('\\', '/') for p in reports]],
                        no_git_actions_performed=True, no_game_patch=True)
    (checkpoint / 'review-files.json').write_text(json.dumps(review_files, indent=2) + '\n')
    visual = dict(agent_reviewed=True, actual_whole_stage_images=34, consecutive_Rush_images=36,
                  source_and_actual_shapes='Fly/landing beam and cloud are original source forms; exact native CHR families match.',
                  graphics_clean=False,
                  remaining='Charged-shot body omission and Rush872 overload part rejection remain. Exact final Flash color fidelity unproved.',
                  soundtrack_listening=False, full_1030_frame_manual_review=False,
                  images_original_completed_PPU=True, reference_art_public=False)
    (checkpoint / 'visual-review.json').write_text(json.dumps(visual, indent=2) + '\n')
    catalog = {str(p.relative_to(checkpoint)).replace('\\', '/'): sha(p)
               for p in sorted(checkpoint.rglob('*')) if p.is_file()}
    (checkpoint / 'catalog.json').write_text(json.dumps(catalog, indent=2, sort_keys=True) + '\n')
    for path in tools + reports:
        relative = path.relative_to(R)
        target = out / 'owned-files' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        assert sha(path) == sha(target)
    size = sum(p.stat().st_size for p in checkpoint.rglob('*') if p.is_file())
    assert size < 1000000
    proof = dict(passed=True, checkpoint=str(checkpoint), checkpoint_files=len(catalog) + 2,
                 checkpoint_bytes_before_proof=size, maximum_bytes=1000000,
                 catalog_sha256=sha(checkpoint / 'catalog.json'),
                 owned_tool_hashes=tool_hashes, native_profile_pass=True,
                 universal_graphics_pass=False, game_patch=False, native_worker_released=True,
                 builder_sha256=sha(__file__), review_files_sha256=sha(checkpoint / 'review-files.json'))
    (checkpoint / 'checkpoint-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    assert sum(p.stat().st_size for p in checkpoint.rglob('*') if p.is_file()) < 1000000
    final = dict(passed=True, proof_sha256=sha(checkpoint / 'checkpoint-proof.json'),
                 public_files={str(p.relative_to(checkpoint)).replace('\\', '/'): sha(p)
                               for p in sorted(checkpoint.rglob('*')) if p.is_file()},
                 external_source_files={str(p): sha(p) for p in sorted((out / 'owned-files').rglob('*')) if p.is_file()},
                 native_review_sha256=sha(review / 'proof.json'), rush_review_sha256=sha(rush / 'proof.json'))
    (out / 'receipt.json').write_text(json.dumps(final, indent=2, sort_keys=True) + '\n')
    print(json.dumps(proof, indent=2))
    print('Final receipt:', sha(out / 'receipt.json'))


if __name__ == '__main__':
    main()
