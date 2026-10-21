"""Combine frozen Bill M source, measured Pit BI, and scoped Ryu E."""
from pathlib import Path
import hashlib, importlib.util, json, re, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-advanced-union-ap'
B = V / 'agent49-bill-advanced-parity-h'
E = V / 'agent-lsr-ryu-corner-head-e'
I = V / 'root49-easy-pit-empty-be'
H = V / 'root49-easy-combined-bq'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    pins = {
        P / 'report.json': 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e',
        B / 'source-freeze-m.json': 'cb12e369100e065d01eb335e3b40440e49307e519003deefa3218baf74535e54',
        E / 'implementation-freeze.json': 'ac4095308afe1256e708254a2b68423795e889b916b4d89c24fba41b23402878',
        I / 'freeze-bi.json': '2442526554d3ac401a542d77998c5569681eb6929bbb6c0ea992a96159833078',
        V / 'root49-ryu-corner-review-bp/report.json': '37404c2bda61e7e448ef22d8f3e11e89e87c7cc7ddd2a0a4ace1835868419536',
    }
    for path, digest in pins.items():
        assert sha(path) == digest, path
    parent = json.loads((P / 'report.json').read_text())['source_hashes']
    bill = json.loads((B / 'source-freeze-m.json').read_text())
    bill_source = Path(bill['merged_AP_M_source'])
    catalog = B / 'source-final-ap-m-catalog.json'
    assert sha(catalog) == bill['final_catalog_sha256']
    expected = json.loads(catalog.read_text())
    assert len(expected) == bill['final_count'] == 439 and not bill['removed']
    assert all(sha(P / 'source' / n) == h for n, h in parent.items())
    assert all(sha(bill_source / n) == h for n, h in expected.items())
    assert set(bill['changed_or_new']) == {n for n, h in expected.items() if parent.get(n) != h}
    for n, values in bill['changed_or_new'].items():
        assert values == {'AP': parent.get(n), 'M': expected[n]}
        assert sha(B / bill['overlay'] / n) == expected[n]
    ryu = json.loads((E / 'implementation-freeze.json').read_text())
    assert all(sha(E / n) == h for n, h in ryu['files'].items())
    pit = json.loads((I / 'freeze-bi.json').read_text())
    assert all(sha(R / x['path']) == x['sha256'] for x in pit['files'])
    for mapper, artifacts in bill['actual_built_files'].items():
        assert all(sha(bill_source / 'build' / ('smb-crossover-' + mapper + '.' + ext)) == h for ext, h in artifacts.items())
    H.mkdir()
    shutil.copytree(bill_source, S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    report = dict(status='MERGING_SOURCE_FROZEN_COMPONENTS_BQ', script_sha256=sha(__file__),
                  references={str(p.relative_to(R)): h for p, h in pins.items()},
                  Bill_source_only_freeze_admission_pending=True,
                  merges=[], builds=[], main_changed=False, accepted_release=False, goal_complete=False,
                  scope='Private build union only. Full H native/source admission, actual merged native checks, ordinary routes and final media remain required.')
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    # These Ryu source files do not overlap Bill M changes. Preserve the raw
    # frozen bytes; only the shared linker segment ordering needs integration.
    for n, digest in ryu['overlay_after_sha256'].items():
        if n == 'smb1base.cfg':
            continue
        incoming = E / 'overlay' / n
        assert sha(incoming) == digest
        if n in parent:
            assert expected[n] == parent[n]
        else:
            assert n not in expected and not (S / n).exists()
        shutil.copyfile(incoming, S / n)
        report['merges'].append(dict(path=n, method='DISJOINT_AP_DELTA', before=expected.get(n), after=digest))
        expected[n] = digest
    cfg = S / 'smb1base.cfg'
    base_cfg = (P / 'source/smb1base.cfg').read_text()
    incoming_cfg = (E / 'overlay/smb1base.cfg').read_text()
    ryu_lines = re.findall(r'(?m)^[ \t]*RYU_COLD:[^\n]*\n', incoming_cfg)
    assert len(ryu_lines) == 1
    assert incoming_cfg.replace(ryu_lines[0], '') == base_cfg
    current = cfg.read_bytes()
    anchors = list(re.finditer(rb'(?m)^[ \t]*BILL_COLD:[^\r\n]*(\r?\n)', current))
    assert len(anchors) == 1 and b'RYU_COLD:' not in current
    anchor = anchors[0]
    addition = ryu_lines[0].rstrip('\n').encode() + anchor.group(1)
    after_cfg = current[:anchor.end()] + addition + current[anchor.end():]
    merge_cfg = H / 'merges/config'
    merge_cfg.mkdir(parents=True)
    (merge_cfg / 'Bill-M.cfg').write_bytes(current)
    shutil.copyfile(P / 'source/smb1base.cfg', merge_cfg / 'AP.cfg')
    shutil.copyfile(E / 'overlay/smb1base.cfg', merge_cfg / 'Ryu-E.cfg')
    cfg.write_bytes(after_cfg)
    report['merges'].append(dict(path='smb1base.cfg', method='EXACT_E_SINGLE_SEGMENT_ADDITION_AFTER_BILL_COLD',
                                 before=expected['smb1base.cfg'], after=sha(cfg)))
    expected['smb1base.cfg'] = sha(cfg)
    # The two authors changed different parts of this shared weapon file. Git's
    # actual three-way result is retained, rather than selecting a whole side.
    name = 'src/megaman_weapons.s'
    folder = H / 'merges/megaman_weapons'
    folder.mkdir()
    sources = [S / name, P / 'source' / name, I / 'frozen-bi/src/megaman_weapons.s']
    paths = [folder / n for n in ['current.s', 'base.s', 'incoming.s']]
    for target, source in zip(paths, sources):
        target.write_text(source.read_text())
    result = subprocess.run(['git', 'merge-file', '--stdout'] + [str(p) for p in paths], cwd=R, capture_output=True)
    merged = folder / 'merged.s'
    merged.write_bytes(result.stdout)
    row = dict(path=name, method='ACTUAL_THREE_WAY_MERGE', exit=result.returncode,
               Bill_M_sha256=sha(paths[0]), AP_sha256=sha(paths[1]), Pit_BI_sha256=sha(paths[2]), after=sha(merged))
    report['merges'].append(row)
    save()
    assert result.returncode == 0, result.stderr
    shutil.copyfile(merged, S / name)
    expected[name] = sha(S / name)
    assert len(expected) == 440 and all(sha(S / n) == h for n, h in expected.items())
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    needle = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(needle) == 1
    driver.write_text(text.replace(needle, 'ROOT = Path(' + repr(str(S)) + ')'))
    spec = importlib.util.spec_from_file_location('combined_bq_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for mapper in ['mmc3', 'mmc5']:
        with (H / (mapper + '-build.log')).open('wb') as stream:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(H / (mapper + '-build.log')))
        report['builds'].append(row)
        save()
        assert rc == 0
        new = module.Image(S / 'build' / ('smb-crossover-' + mapper + '.nes'))
        old = module.Image(bill_source / 'build' / ('smb-crossover-' + mapper + '.nes'))
        assert old.ram == new.ram and len(old.raw) == len(new.raw)
        assert old.raw[:16] == new.raw[:16] and old.raw[524304:] == new.raw[524304:]
        before = {x['name']: x for x in old.segs.values()}
        now = {x['name']: x for x in new.segs.values()}
        changes = {n: now[n]['size'] - x['size'] for n, x in before.items() if now[n]['size'] != x['size']}
        assert changes == {'GUEST': 18, 'ROSTER': 23}, changes
        assert set(now) - set(before) == {'RYU_COLD'}
        cold, bill_cold = now['RYU_COLD'], now['BILL_COLD']
        assert cold['size'] == 497 and cold['start'] == bill_cold['start'] + bill_cold['size']
        assert (cold['ooffs'] - 16) // 8192 == (bill_cold['ooffs'] - 16) // 8192 == 25
        assert cold['ooffs'] + cold['size'] <= 16 + 26 * 8192
        assert old.raw[cold['ooffs']:cold['ooffs'] + cold['size']] == bytes([255]) * 497
        audio = {}
        for n, x in before.items():
            if x.get('type') == 'bss':
                assert (x['start'], x['size']) == (now[n]['start'], now[n]['size'])
            if x.get('type') != 'ro' or not ('AUDIO' in n or 'DPCM' in n or n == 'MUSIC' or n.startswith('XG_MUSIC')):
                continue
            y = now[n]
            assert all(x[k] == y[k] for k in ['start', 'size', 'ooffs'])
            assert old.raw[x['ooffs']:x['ooffs'] + x['size']] == new.raw[y['ooffs']:y['ooffs'] + y['size']]
            audio[n] = x['size']
        a, b = old.hook('RosterDrawShots'), new.hook('RosterDrawShots')
        size = old.sym('RosterDrawShots')['size']
        assert size == new.sym('RosterDrawShots')['size']
        assert old.raw[a['rom_offset']:a['rom_offset'] + size] == new.raw[b['rom_offset']:b['rom_offset'] + size]
        row.update(ROM_sha256=sha(new.path), RAM_header_CHR_size_exact_vs_M=True,
                   old_RO_audio_addresses_bytes_exact=audio, segment_deltas=changes,
                   RYU_COLD=cold, BILL_COLD=bill_cold, shared_bank25_tail_free=16 + 26 * 8192 - cold['ooffs'] - cold['size'],
                   U_projectile_ownership_guard_exact=True)
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    assert all(sha(bill_source / n) == h for n, h in json.loads(catalog.read_text()).items())
    report.update(status='PASS_PRIVATE_COMBINED_BQ_BUILD_ONLY_ADMISSION_PENDING', source_hashes=expected)
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
