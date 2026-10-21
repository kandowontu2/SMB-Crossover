"""Combine frozen Link L and Bill growth with root N; regenerate shared art once."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys, zipfile

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-cold-bank-n'
H = V / 'root49-easy-union-t'
S = H / 'source'
L = V / 'agent-lsr-easy-link-rect-animation-k/frozen-l'
G = V / 'agent49-bill-growth-e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    prior = json.loads((P / 'report.json').read_text())
    assert sha(P / 'report.json') == '1de5d6742cf75542bb4ffe4f28feade4b1d5d95dcfc9a8f3e859e81ed2853c47'
    assert all(sha(P / 'source' / n) == h for n, h in prior['source_hashes'].items())
    u = json.loads((R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json').read_text())
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    assert sha(L / 'implementation-freeze-l.json') == 'db65b7086a1ba201401519f3dd5857601f351a591edd27028a97b855da575719'
    assert sha(G / 'freeze.json') == '334db5953e6b9f10951786cd5632f3e90fbb7b482f9c35542a52eed5ba2b343f'
    lf = json.loads((L / 'implementation-freeze-l.json').read_text())
    gf = json.loads((G / 'freeze.json').read_text())
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    report = dict(status='MERGING_FROZEN_LINK_L_BILL_GROWTH', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), Link_L_freeze_sha256=sha(L / 'implementation-freeze-l.json'),
                  Bill_growth_freeze_sha256=sha(G / 'freeze.json'), merges=[], builds=[],
                  main_changed=False, complete_Easy_behavior=False, accepted_release=False, goal_complete=False,
                  clock_qualification='No reset admitted: source freeze/unfreeze callgraph is under separate review.')

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    def merge(name, base_bytes, incoming, layer):
        assert incoming.is_file(), incoming
        folder = H / 'merges' / layer / Path(name).stem
        folder.mkdir(parents=True)
        current, base, other = [folder / n for n in ['current.s', 'base.s', 'incoming.s']]
        current.write_text((S / name).read_text())
        base.write_text(base_bytes.decode().replace('\r\n', '\n'))
        other.write_text(incoming.read_text())
        result = subprocess.run(['git', 'merge-file', '--stdout', str(current), str(base), str(other)], cwd=R, capture_output=True)
        merged = folder / 'merged.s'
        merged.write_bytes(result.stdout)
        report['merges'].append(dict(layer=layer, path=name, exit=result.returncode,
                                     current_sha256=sha(current), base_sha256=sha(base),
                                     incoming_sha256=sha(other), result_sha256=sha(merged)))
        save()
        if result.returncode == 1 and (layer, name) == ('BillGrowth', 'src/megaman_weapons.s'):
            # Both changes belong here: Bill jumps past its new rectangle setup;
            # Simon still applies the source whip envelope after the shared setup.
            lines = result.stdout.decode().splitlines()
            starts = [i for i, line in enumerate(lines) if line.startswith('<<<<<<<')]
            assert len(starts) == 1
            i = starts[0]
            assert lines[i + 1:i + 4] == ['  farcall EasyWhipEnvelope', '=======', 'EnemyBoundsReady:']
            assert lines[i + 4].startswith('>>>>>>>')
            lines[i:i + 5] = ['EnemyBoundsReady:', '  farcall EasyWhipEnvelope']
            merged.write_text('\n'.join(lines) + '\n')
            report['merges'][-1].update(explicit_resolution='Retain both Bill entry label and Simon whip envelope',
                                         resolved_sha256=sha(merged))
            save()
        else:
            assert result.returncode == 0, (layer, name)
        shutil.copyfile(merged, S / name)

    save()
    ancestor = V / 'agent-lsr-easy-link-rect-animation-k/frozen-k/source-link-rectangle-k.zip'
    if not ancestor.exists():
        choices = list((V / 'agent-lsr-easy-link-rect-animation-k/frozen-k').glob('*.zip'))
        assert len(choices) == 1
        ancestor = choices[0]
    assert sha(ancestor) == lf['parent_archive_sha256']
    with zipfile.ZipFile(ancestor) as archive:
        for name in lf['runtime_overlay']:
            incoming = L / 'after' / name
            assert sha(incoming) == lf['source_catalog'][name]
            if name not in archive.namelist():
                assert not (S / name).exists()
                shutil.copyfile(incoming, S / name)
            else:
                merge(name, archive.read(name), incoming, 'LinkL')
    gr = json.loads((G / 'build-report.json').read_text())
    growth_runtime = ['src/roster_weapons.s', 'src/megaman_weapons.s']
    growth_generators = ['tools/reference/build_roster_assets.py', 'tools/reference/build_lance_assets.py',
                         'tools/reference/build_ordinary_body_layout.py', 'tools/reference/pack_chr.py']
    for name in growth_runtime + growth_generators:
        incoming = G / 'overlay' / name
        assert sha(incoming) == gf['files'][incoming.relative_to(R).as_posix()]
        base = V / 'agent49-bill-projection-d/source' / name
        assert sha(base) == gr['changes'][name]['parent_sha256']
        assert sha(incoming) == gr['changes'][name]['after_sha256']
        merge(name, base.read_bytes(), incoming, 'BillGrowth')
    layout = 'chr/characters/ordinary-body-growth-layout.json'
    assert not (S / layout).exists()
    incoming = G / 'overlay' / layout
    assert sha(incoming) == gf['files'][incoming.relative_to(R).as_posix()]
    shutil.copyfile(incoming, S / layout)
    proposal = V / 'agent-lsr-easy-link-rect-animation-k/generator-union-proposal-l'
    pd = json.loads((proposal / 'proposal.json').read_text())
    gen = 'tools/reference/build_roster_assets.py'
    assert sha(S / gen) == pd['parent_sha256']
    patch = proposal / 'generator-link-end-l.patch'
    assert sha(patch) == pd['patch_sha256']
    result = subprocess.run(['git', 'apply', '--unsafe-paths', '--directory=' + str(S), str(patch)], cwd=R, capture_output=True)
    report['generator_patch_exit'] = result.returncode
    report['generator_patch_diagnostic'] = result.stderr.decode(errors='replace')
    save()
    assert result.returncode == 0
    assert sha(S / gen) == pd['after_sha256']
    # Lance's shared extractor imports this immutable atlas at module load.
    atlas = R / 'docs/reference/expanded-atlas.json'
    (S / 'docs/reference').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(atlas, S / 'docs/reference/expanded-atlas.json')
    report['reference_atlas_sha256'] = sha(atlas)
    # Reference pixels stay at the immutable project location; only generated outputs go to S.
    generator = H / 'regenerate.py'
    generator.write_text('from pathlib import Path\nimport sys\nfrom PIL import Image\n'
                         + 'S=Path(' + repr(str(S)) + ');R=Path(' + repr(str(R)) + ')\n'
                         + "sys.path.insert(0,str(S/'tools/reference'))\nimport build_megaman_assets as a\n"
                         + "a.ROOT=S;a.REF=R/'reference/crossover'\n"
                         + "a.sprite_image=lambda meta,frame:Image.open(R/meta['png_directory']/f'{frame}.png').convert('RGBA')\n"
                         + 'import build_roster_assets as b\nb.ROOT=S\nb.main()\n'
                         + 'import build_lance_assets as l\nl.ROOT=S\nl.main()\n')
    with (H / 'regenerate.log').open('wb') as f:
        rc = subprocess.run([sys.executable, str(generator)], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
    report['regenerate_exit'] = rc
    report['regenerate_log_sha256'] = sha(H / 'regenerate.log')
    save()
    assert rc == 0
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    spec = importlib.util.spec_from_file_location('union_r_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for mapper in ['mmc3', 'mmc5']:
        log = H / (mapper + '-build.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(log))
        report['builds'].append(row)
        save()
        assert rc == 0
        im = mod.Image(S / ('build/smb-crossover-' + mapper + '.nes'))
        before = mod.Image(P / ('source/build/smb-crossover-' + mapper + '.nes'))
        assert im.ram == before.ram and len(im.raw) == len(before.raw)
        for name in ['MM3_AUDIO', 'LEGACY_COLD'] + [s['name'] for s in before.segs.values() if 'DPCM' in s['name']]:
            seg = next(s for s in im.segs.values() if s['name'] == name)
            oldseg = next(s for s in before.segs.values() if s['name'] == name)
            assert (seg['start'], seg['size']) == (oldseg['start'], oldseg['size'])
            assert im.raw[seg['ooffs']:seg['ooffs'] + seg['size']] == before.raw[oldseg['ooffs']:oldseg['ooffs'] + oldseg['size']]
        row.update(ROM_sha256=sha(im.path), RAM_exact=True, ROM_size_exact=True, audio_and_cold_bytes_exact=True,
                   segments={n: next(s for s in im.segs.values() if s['name'] == n)
                             for n in ['GUEST', 'SAMUS', 'SPECIAL_EXTRA', 'SPECIAL_ROSTER', 'PLAYER', 'ROSTER', 'TITLE', 'RENDER', 'BILL_GFX', 'LINK_GFX']})
        save()
    # Record the exact generated source tree, excluding build products and Python caches.
    report['source_hashes'] = {p.relative_to(S).as_posix(): sha(p) for p in sorted(S.rglob('*'))
                               if p.is_file() and p.relative_to(S).parts[0] != 'build'
                               and '__pycache__' not in p.parts}
    assert sha(S / 'src/menu_behavior.s') == prior['source_hashes']['src/menu_behavior.s']
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_LINK_L_BILL_GROWTH_UNION_R_BUILD_ONLY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
