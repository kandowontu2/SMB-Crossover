"""Three-way integrate frozen Ryu O into the tested private AB ancestry."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-bro-union-ab'
F = V / 'agent-lsr-ryu-source-body-o'
H = V / 'root49-easy-ryu-union-ai'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    assert sha(P / 'report.json') == '68567961c9ec02603c055aff83ff89185427361d5f84f313d9c755aabcb3b4ee'
    assert sha(F / 'implementation-freeze-o.json') == 'be0e4181de7a3370a9b84ec8dd217731cd2468d1b7b0280b6d57451166a9bf6d'
    old = json.loads((P / 'report.json').read_text())
    frozen = json.loads((F / 'implementation-freeze-o.json').read_text())
    assert all(sha(R / x['path']) == x['sha256'] for x in frozen['files'].values())
    assert all(sha(P / 'source' / n) == h for n, h in old['source_hashes'].items())
    H.mkdir();shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    expected = dict(old['source_hashes'])
    report = dict(status='MERGING_FROZEN_RYU_O_OVER_AB', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), source_freeze_sha256=sha(F / 'implementation-freeze-o.json'),
                  merges=[], builds=[], main_changed=False, accepted_release=False, goal_complete=False)
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for name, pair in frozen['source_delta'].items():
        before = F / 'frozen-o/before' / name
        after = F / 'frozen-o/after' / name
        assert sha(before) == pair['before'] and sha(after) == pair['after']
        folder = H / 'merges' / Path(name).stem;folder.mkdir(parents=True)
        paths = [folder / n for n in ['current.s', 'base.s', 'incoming.s']]
        for path, source in zip(paths, [S / name, before, after]):
            path.write_text(source.read_text())
        result = subprocess.run(['git', 'merge-file', '--stdout'] + [str(p) for p in paths], cwd=R, capture_output=True)
        merged = folder / 'merged.s';merged.write_bytes(result.stdout)
        report['merges'].append(dict(path=name, exit=result.returncode, current_sha256=sha(paths[0]),
                                     base_sha256=sha(paths[1]), incoming_sha256=sha(paths[2]), result_sha256=sha(merged)))
        save();assert result.returncode == 0, name
        shutil.copyfile(merged, S / name);expected[name] = sha(S / name)
    for name, h in frozen['new_source'].items():
        assert name not in expected and not (S / name).exists()
        incoming = F / 'frozen-o/after' / name;assert sha(incoming) == h
        shutil.copyfile(incoming, S / name);expected[name] = h
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    needle = 'ROOT = Path(' + repr(str(P / 'source')) + ')';assert text.count(needle) == 1
    driver.write_text(text.replace(needle, 'ROOT = Path(' + repr(str(S)) + ')'))
    spec = importlib.util.spec_from_file_location('ryu_ai_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    for mapper in ['mmc3', 'mmc5']:
        log = H / (mapper + '-build.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(log));report['builds'].append(row);save();assert rc == 0
        im = m.Image(S / 'build' / ('smb-crossover-' + mapper + '.nes'))
        prior = m.Image(P / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        assert all(im.ram[n] == a for n, a in prior.ram.items())
        assert set(im.ram) - set(prior.ram) == {'RyuSourceBodyProfile'} and im.ram['RyuSourceBodyProfile'] == 0x7fe4
        assert len(im.raw) == len(prior.raw) and im.raw[:16] == prior.raw[:16] and im.raw[524304:] == prior.raw[524304:]
        for name in ['MM3_AUDIO'] + [s['name'] for s in prior.segs.values() if 'DPCM' in s['name']]:
            a = next(s for s in im.segs.values() if s['name'] == name);b = next(s for s in prior.segs.values() if s['name'] == name)
            assert (a['start'], a['size'], a['ooffs']) == (b['start'], b['size'], b['ooffs'])
            assert im.raw[a['ooffs']:a['ooffs'] + a['size']] == prior.raw[b['ooffs']:b['ooffs'] + b['size']]
        deltas = {}
        for name in ['GUEST', 'BILL_GFX', 'LEGACY_COLD', 'SAMUS', 'ROSTER', 'SPECIAL_EXTRA', 'OBJECT', 'COLLISION', 'EXPANDED', 'SPECIAL_MM']:
            a = next(s for s in im.segs.values() if s['name'] == name);b = next(s for s in prior.segs.values() if s['name'] == name)
            deltas[name] = a['size'] - b['size']
        assert deltas == dict(GUEST=0, BILL_GFX=0, LEGACY_COLD=844, SAMUS=0, ROSTER=18, SPECIAL_EXTRA=0, OBJECT=25, COLLISION=33, EXPANDED=5, SPECIAL_MM=3), deltas
        row.update(ROM_sha256=sha(im.path), old_RAM_globals=len(prior.ram), old_RAM_addresses_exact=True,
                   appended_RAM={'RyuSourceBodyProfile': 0x7fe4}, header_CHR_size_exact=True,
                   audio_bytes_and_addresses_exact=True, segment_deltas=deltas,
                   segments={name: next(s for s in im.segs.values() if s['name'] == name) for name in deltas})
        save()
    assert len(expected) == 428 and all(sha(S / n) == h for n, h in expected.items())
    report.update(status='PASS_PRIVATE_RYU_O_AB_UNION_AI_BUILD_ONLY', source_hashes=expected)
    save();print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
