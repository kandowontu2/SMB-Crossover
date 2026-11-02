"""Preserve the exact qualified nine-row private prototype without admission."""
import json
import zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/bubble-native-checkpoint-1102-v2'
P = R / 'build/bubble-bobble-source-1101-v1'


def main():
    O.mkdir(exist_ok=True)
    manifest = json.loads((P / 'qualified-native-proofs-1102-v1.json').read_text(encoding='utf-8'))
    assert manifest['passed'] and not manifest['ROM_written'] and not manifest['admitted']
    archive = R / manifest['archive']
    assert sha(archive) == manifest['archive_SHA256'] and archive.stat().st_size == 125352
    for name, info in manifest['files'].items():
        assert sha(R / name) == info['SHA256'], name
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert sorted(z.namelist()) == sorted(manifest['files'])
        for name in z.namelist():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            assert Path(name).suffix.lower() not in ['.nes', '.fds', '.dbg', '.png', '.o', '.mp4']
    cp = R / 'docs/qa/checkpoints/2026-11-02/bubble-native-core-v2'
    cp.mkdir(parents=True, exist_ok=True)
    assert not (cp / 'inputs.zip').exists()
    (cp / 'inputs.zip').write_bytes(archive.read_bytes())
    (cp / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    paths = sorted(n for n in manifest['files'] if n.startswith('tools/'))
    (cp / 'commit-files.txt').write_text('\n'.join(paths) + '\n', encoding='utf-8')
    p = R / 'docs/qa/continuation-current.json'
    q = json.loads(p.read_text(encoding='utf-8'))
    q['Bub_Bob_resource_followup'].update(
        private_native_checkpoint=str(cp.relative_to(R)),
        private_code_used_bytes=8158, immutable_helper_tail_used_bytes=207,
        shared_nine_row_worker_bytes=229, private_implemented_rows=[0,1,2,15,17,18,26,30,36],
        remaining='Nine private rows and common nine-row copy/auth/retirement CPU proofs are frozen oncf, '
                  'with explicit1cd8 rebase. Actual Hu/Main routing, enemy AI/contact/birth seams, '
                  'native Bub/Bob play and full1-1 remain gated. Cold menu static art/codec lease still pending.')
    q['previous_goal_turn_classification'] = 'progress'
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    result = dict(preserved=True, archive_bytes=archive.stat().st_size,
                  checkpoint=str(cp.relative_to(R)), plain_source_files=len(paths),
                  menu_admitted=False, native_playable=False)
    (O / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
