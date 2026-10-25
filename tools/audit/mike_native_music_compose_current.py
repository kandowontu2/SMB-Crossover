"""Freeze an accepted parent and compose only the four reviewed Mike music edits.

All game sources and build outputs stay in the explicitly external destination.
This is a preparation/structural check, not a native qualification claim.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
from check_tmnt_audio_fallback_oc import qualified

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['output', 'installed', 'donor', 'coverage', 'prior-inputs']:
        p.add_argument('--' + n, type=Path, required=True)
    p.add_argument('--parent-sha256', required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    assert sha(a.installed) == a.parent_sha256
    out.mkdir(parents=True, exist_ok=False)
    source_files = sorted([x for top in ['src', 'inc'] for x in (ROOT / top).rglob('*') if x.is_file()] + [ROOT / 'smb1base-mmc5-expanded.cfg'])
    prior = json.loads(a.prior_inputs.read_text())
    assets = {n: sha(ROOT / n) for n in prior['shared_assets']}
    frozen = dict(parent_ROM_sha256=a.parent_sha256,
                  source_files={x.relative_to(ROOT).as_posix(): sha(x) for x in source_files},
                  shared_assets=assets, source_file_count=len(source_files), shared_asset_count=len(assets))
    (out / 'frozen-inputs.json').write_text(json.dumps(frozen, indent=2) + '\n')
    for name in ['baseline-source', 'source', 'faithful-source']:
        for f in source_files:
            target = out / name / f.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, target)

    def run(name, command):
        with (out / (name + '.log')).open('w') as log:
            z = subprocess.run([sys.executable] + [str(x) for x in command], cwd=ROOT,
                               stdout=log, stderr=subprocess.STDOUT)
        assert z.returncode == 0, (name, z.returncode)

    def build(name, source, flag=None):
        cmd = [ROOT / 'tools/build_mmc5_expanded.py', '--workspace', ROOT,
               '--source-overlay', source, '--output', out / (name + '.nes')]
        if flag:
            cmd += ['--flag-off', flag]
        run('build-' + name, cmd)

    build('baseline', out / 'baseline-source')
    assert sha(out / 'baseline.nes') == a.parent_sha256
    run('prepare-fast', [ROOT / 'tools/audit/mike_native_music_prepare_fast.py',
                         '--source', out / 'source', '--coverage', a.coverage])
    run('prepare-faithful', [ROOT / 'tools/audit/mike_native_music_prepare.py',
                             '--source', out / 'faithful-source', '--coverage', a.coverage])
    build('candidate', out / 'source')
    build('faithful-v5', out / 'faithful-source')
    for flag in ['mmc3', 'mmc5']:
        build('candidate-' + flag, out / 'source', flag)
    expected_standards = {'mmc3': 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',
                          'mmc5': 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}
    assert {n: sha(out / ('candidate-' + n + '.nes')) for n in expected_standards} == expected_standards
    before = frozen['source_files']
    after = {x.relative_to(out / 'source').as_posix(): sha(x) for x in (out / 'source').rglob('*') if x.is_file()}
    changes = {n: dict(before_sha256=before.get(n), after_sha256=after.get(n)) for n in sorted(set(before) | set(after)) if before.get(n) != after.get(n)}
    assert set(changes) == {'src/entrypoint.s', 'src/expanded_audio.s', 'src/mike_native_music.s', 'smb1base-mmc5-expanded.cfg'}, changes
    old, new, donor = [x.read_bytes() for x in [out / 'baseline.nes', out / 'candidate.nes', a.donor]]
    bank = lambda raw, i: raw[16 + i * 8192:16 + (i + 1) * 8192]
    diff = {i: sum(x != y for x, y in zip(bank(old, i), bank(new, i))) for i in range(128)}
    diff = {i: n for i, n in diff.items() if n}
    assert diff == {38: 29, 115: 7446, 126: 3}, diff
    assert all(bank(new, i) == bank(donor, i) for i in [38, 115])
    assert all(bank(old, i) == bank(new, i) for i in range(128) if i not in diff)
    assert old[:16] == new[:16] and old[16 + 127 * 8192:] == new[16 + 127 * 8192:]
    qb, qa = qualified(out / 'baseline.nes'), qualified(out / 'candidate.nes')
    symbols = {str(k): [v, qa.get(k)] for k, v in qb.items() if qa.get(k) != v}
    assert set(symbols) == {str(('KbAudioFamily', 'Kirby'))}, symbols
    assert symbols[str(('KbAudioFamily', 'Kirby'))] == [0xcbd4, 0xcbe2]
    assert all(sha(ROOT / n) == v for n, v in before.items())
    assert all(sha(ROOT / n) == v for n, v in assets.items())
    result = dict(passed=True, accepted=False, native_qualified=False,
                  parent_ROM_sha256=a.parent_sha256, candidate_ROM_sha256=sha(out / 'candidate.nes'),
                  faithful_ROM_sha256=sha(out / 'faithful-v5.nes'), donor_ROM_sha256=sha(a.donor),
                  changed_source_files=changes, changed_PRG_bytes=diff,
                  donor_banks38_115_exact=True, all_other_banks_including86_119_127_exact=True,
                  CHR_exact=True, retained_qualified_symbols=len(qb) - len(symbols),
                  genuine_private_symbol_exception=symbols, ordinary_target_hashes=expected_standards,
                  all_ROOT_inputs_still_exact=True, tool_sha256=sha(Path(__file__)))
    (out / 'composition.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
