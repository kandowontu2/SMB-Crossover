"""Freeze two separate root-reviewed scopes; never installs a source candidate."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
BASE = R / 'docs/qa/checkpoints/2026-10-31'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def freeze(name, files, receipts, facts, description):
    output = BASE / name
    assert not output.exists(), output
    bindings = {}
    for receipt in receipts:
        for path, digest in load(receipt)['bindings'].items():
            assert sha(path) == digest, ('Recorded input drift', path)
            assert path not in bindings or bindings[path] == digest
            bindings[path] = digest
    paths = {Path(path).resolve() for path in [*files, *receipts, Path(__file__)]}
    bindings.update({str(path): sha(path) for path in paths})
    output.mkdir(parents=True)
    archive = output / 'source-and-evidence.zip'
    members = {}
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(paths):
            assert path.is_relative_to(R) and path.suffix not in ['.nes', '.o', '.exe']
            relative = path.relative_to(R).as_posix()
            bundle.write(path, relative)
            members[relative] = sha(path)
    with zipfile.ZipFile(archive) as bundle:
        for relative, digest in members.items():
            assert hashlib.sha256(bundle.read(relative)).hexdigest() == digest
    dump(output / 'archive-members.json', members)
    (output / 'README.md').write_text(description + '\n', encoding='utf-8', newline='\n')
    dump(output / 'handoff.json', dict(**facts, bindings=bindings,
         archive=dict(path=str(archive), sha256=sha(archive), members=len(members),
                      bytes=archive.stat().st_size),
         root_reviewed=True, installed_ROM_unchanged=True))
    print(json.dumps(dict(packet=name, bindings=len(bindings), members=len(members),
                         archive_bytes=archive.stat().st_size, handoff_sha256=sha(output / 'handoff.json'))))


def main():
    source = R / 'build/future-start-masks-1031-v1'
    controls = R / 'build/future-start-mask-controls-1031-v1/controls.json'
    stage = load(source / 'source-stage.json')
    checks = load(controls)
    assert stage['passed'] and checks['passed'] and checks['actual_Start_pairs'] == 18432
    assert stage['new_helper_bytes'] == 405 and stage['changed_ROM_bytes'] == 49
    files = [source / 'joint/entrypoint.s', source / 'joint/src/character_select.s',
             source / 'joint/src/cf_menu_body.inc', source / 'joint/candidate.cfg',
             source / 'joint/candidate.map', source / 'joint/candidate.cv3-mirror.json',
             R / 'tools/audit/prepare_future_start_masks_1031_v1.py',
             R / 'tools/audit/check_future_start_masks_1031_v1.py',
             R / 'tools/audit/private_build_outputs_v1.py', R / 'tools/prepare_cv3_dmc_mirror.py']
    files += list(source.glob('*-build.json')) + list(source.glob('*-link.json'))
    freeze('future-start-masks-source-v1', files, [source / 'source-stage.json', controls],
           dict(status='SOURCE_ONLY_NO_NEW_ADMISSION', candidate_sha256=stage['candidate'],
                parent_sha256=stage['parent'], native=False, ready=74, identities=86,
                actual_Start_pairs=18432, unchanged_current_Start_boundaries=688,
                grant=dict(owner='Existing CHAR_SELECT menu helper', old_reserved_bytes=400,
                           reserved_bytes=405, newly_granted_source_owned_FF_bytes=5,
                           physical_bank=29, helper_start_file=242859, helper_end_exclusive_file=243264),
                masks=dict(Thomas_Shinobi_slot10_FmAlts=68, WWF_slot28_FmGroups=7)),
           'Jointly source-built future Thomas/Shinobi and WWF Start masks against installed Ready74. '
           'Root grants five additional preexisting FF bytes within the existing menu-owned helper, '
           'raising its limit from400 to405 bytes. All other ROM bytes and the complete CHR payload are exact. '
           '18,432 original/candidate CPU pairs and688 unchanged current menu Start boundaries pass. '
           'These characters remain pending: no new admission, native qualification or installation.')

    native = R / 'build/current74-benj-peach-native-1031-v1/peach'
    result = load(native / 'capture/result.json')
    binding = load(native / 'capture/binding.json')
    assert result['passed'] and result['body_P0_source_exact'] and binding['exit_code'] == 0
    assert result['main_updates'] == 180 and result['vector_guards'] == 360
    assert result['ROM_sha256'] == stage['parent']
    assert sha(Path.home() / 'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes') == stage['parent']
    files = [R / 'tools/audit/prepare_current74_benj_peach_native_1031_v1.py',
             native / 'controller.lua', native / 'run.py', *sorted((native / 'capture').iterdir())]
    assert len(list((native / 'capture').glob('*.png'))) == 4
    freeze('current74-benj-peach-native-v1', files, [native / 'ready.json'],
           dict(status='NATIVE_VISUAL_CHECK_PASS', ROM_sha256=result['ROM_sha256'],
                passed=True, Main_updates=180, actual_vector_guards=360,
                root_reviewed_full_PNGs=['selected', 'lives', 'entered', 'endpoint'],
                actual_P0=[22, 48, 39], full_level_or_powerups_verified=False),
           'Root launched the exact installed Ready74 cart after confirming Mesen was closed. '
           'Peach has the donor normal P0 palette163027 on selection, lives and gameplay. '
           'All four full-frame PNGs were reviewed;180 genuine Main updates and360 interrupt guards pass. '
           'No video, full-level or every-powerup claim. Existing MARIO HUD text remains.')


if __name__ == '__main__':
    main()
