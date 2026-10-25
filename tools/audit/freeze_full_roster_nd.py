"""Publish the reviewed playthrough repair build after combined-ROM checks."""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil, subprocess, sys, zipfile

R = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--entry', type=Path, required=True)
    p.add_argument('--matrix', type=Path, required=True)
    p.add_argument('--features', type=Path, required=True)
    p.add_argument('--adapters', type=Path, required=True)
    a = p.parse_args()
    final = R/'build/checkpoints/full-roster-nd'
    assert not final.exists(), 'Preserve the existing checkpoint'
    out = R/'build/verification/freeze-full-roster-nd-staging'
    attempt = 1
    while out.exists():
        attempt += 1
        out = R/'build/verification'/('freeze-full-roster-nd-staging-v'+str(attempt))
    rom = a.rom.resolve()
    digest = sha(rom)
    entry, matrix, features, adapters = map(read, (a.entry, a.matrix, a.features, a.adapters))
    assert entry['rom_sha256'] == digest and entry['identities'] == 32
    assert len(entry['results']) == 32 and all(v['exit'] == 0 for v in entry['results'].values())
    assert matrix['ROM_sha256'] == digest and matrix['passed'] and matrix['completed'] == 18
    assert len(matrix['results']) == 18 and all(v['passed'] for v in matrix['results'].values())
    assert all(v['result']['cleared'] and v['result']['deaths'] == 0 for v in matrix['results'].values())
    route_bindings = {}
    for name, row in matrix['results'].items():
        folder = Path(row['output'])
        manifest = read(folder/'manifest.json')
        assert manifest['ROM_sha256'] == digest and manifest['fixed_replay']
        assert manifest['controller_only'] and not manifest['memory_writes']
        assert sha(folder/'inputs.csv') == manifest['inputs_sha256']
        assert read(folder/'result.json') == row['result']
        assert read(folder/'chr-audit-summary.json')['failure'] is None
        assert read(folder/'stomp-summary.json')['failure'] is None
        route_bindings[name] = dict(manifest_sha256=sha(folder/'manifest.json'),
            inputs_sha256=sha(folder/'inputs.csv'), result_sha256=sha(folder/'result.json'))
    assert features['sha256'] == digest and len(features['results']) == 14
    assert all(v == 0 for v in features['results'].values())
    assert adapters == {'bounce': 0, 'outline-mike': 0, 'outline-samus': 0}
    adapter_binding = read(a.adapters.parent/'binding.json')
    assert adapter_binding['ROM_sha256'] == digest
    assert len(adapter_binding['fixtures']) == 3 and all(v['exit'] == 0 for v in adapter_binding['fixtures'].values())
    proto = read(R/'build/verification/new-roster-1-1-nd/proto-palette-final.json')
    assert proto['passed'] and proto['ROM_sha256'] == digest and proto['compiled_cases'] == 768
    menu_visuals = {}
    for name in entry['results']:
        key = name.lower().replace(' ', '-')
        for file in ('selection.png', 'lives.png'):
            image = a.entry.parent/key/'build/verification'/file
            reviewed = R/'build/verification/new-roster-1-1-nd/menu-entry-c'/key/'build/verification'/file
            assert image.read_bytes() == reviewed.read_bytes(), (name, file)
            menu_visuals[name+'/'+file] = sha(image)
    parent = read(R/'build/checkpoints/full-roster-nc/manifest.json')
    names = set(parent['source_files'])
    names.update(str(f.relative_to(R)).replace('\\', '/') for f in (R/'tools/audit').glob('*_nd.py'))
    names.update((
        'tools/audit/archive_capture_headroom_ne.py',
        'tools/playthroughs/new_roster_run_nd.py', 'tools/playthroughs/new_roster_policy_nd.lua',
        'tools/reference/build_x5_menu.py', 'tools/reference/build_ordinary_body_layout.py',
        'src/x5_menu_ui.s', 'tests/full-roster-entry.lua',
        'chr/characters/bass-arm-source-plan.json',
        'docs/qa/new-roster-playthroughs-2026-10-23.md'))
    assert all((R/n).is_file() for n in names)
    paths = {'mmc5-expanded': rom}
    expected_standard = {
        'mmc3': '97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4',
        'mmc5': '7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128'}
    for mapper, expected in expected_standard.items():
        paths[mapper] = R/'build/verification/new-roster-1-1-nd'/('standard-'+mapper+'-final.nes')
        assert sha(paths[mapper]) == expected, mapper
    hashes = {n: sha(R/n) for n in sorted(names)}
    source_changes = {n: h for n, h in hashes.items() if parent['source_files'].get(n) != h}
    artifacts = [f.with_suffix(ext) for f in paths.values() for ext in ('.nes', '.lbl', '.dbg', '.map')]
    sys.path.insert(0, str(R/'tools'))
    from playthroughs.roster_run import workspace_bytes
    used = workspace_bytes(R)
    reserve = 4*sum(f.stat().st_size for f in artifacts)+3*sum((R/n).stat().st_size for n in names)
    assert used+reserve < 30_000_000_000, (used, reserve)
    evidence = dict(ROM_sha256=digest, identities=32, added_identities=18,
        entry=entry, controller_replays=matrix, features=features, native_adapters=adapters,
        source_changes=source_changes, adapter_binding=adapter_binding,
        route_bindings=route_bindings, reviewed_menu_images=menu_visuals, proto_palette_cases=proto,
        mode='Easy', route='surface 1-1 through restored control in 1-2',
        no_deaths=True, emulated_route_writes=False, posting_video_work_deferred=True,
        scope='Eighteen controller-only Easy surface-route clears, 32 cold identity/menu/lives checks, and labeled focused ability/component tests. Sampled visual review plus consecutive suspect-event frames; not an exhaustive frame-by-frame, all-weapons, Hard-mode or full-campaign certification.')
    out.mkdir(parents=True)
    (out/'completion-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    with zipfile.ZipFile(out/'source.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(names):
            z.write(R/n, n)
    assert all(sha(R/n) == h for n, h in hashes.items()), 'Sources changed during freeze'
    # Rebuild all three targets from only the extracted source bundle. The
    # compiler is an explicit external dependency, not a hidden source overlay.
    unpacked = out/'roundtrip-source'
    with zipfile.ZipFile(out/'source.zip') as z:
        z.extractall(unpacked)
    compiler = R/'tools/Windows/cc65/bin/cl65.exe'
    roundtrips = {}
    for mapper, path in paths.items():
        target = out/'roundtrip-builds'/(mapper+'.nes')
        command = [sys.executable, str(unpacked/'tools/build_mmc5_expanded.py'),
            '--workspace', str(unpacked), '--compiler', str(compiler), '--output', str(target)]
        if mapper != 'mmc5-expanded':
            command += ['--flag-off', mapper]
        result = subprocess.run(command, cwd=unpacked, capture_output=True, text=True)
        (out/('roundtrip-'+mapper+'.log')).write_text(result.stdout+result.stderr)
        assert result.returncode == 0, ('Source-bundle rebuild failed', mapper)
        assert sha(target) == sha(path), ('Source-bundle ROM differs', mapper)
        roundtrips[mapper] = dict(ROM_sha256=sha(target), exact=True, path=str(target))
    final.mkdir(parents=True)
    for name in ('source.zip', 'completion-evidence.json'):
        shutil.copyfile(out/name, final/name)
    for mapper, path in paths.items():
        for ext in ('.nes', '.lbl', '.dbg', '.map'):
            target = final/'build'/('smb-crossover-'+mapper+ext)
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext), target)
            shutil.copyfile(target, R/'build'/target.name)
    report = dict(parent, status='ADDED_ROSTER_1_1_REVIEW_AND_REPAIRS_VERIFIED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), parent_checkpoint='full-roster-nc',
        ROMs={m: sha(f) for m, f in paths.items()}, source_zip_sha256=sha(final/'source.zip'),
        source_files=hashes, completion_evidence=evidence,
        source_bundle_rebuilds=roundtrips,
        scope=evidence['scope'], space_before_freeze=dict(bytes=used, reserved_upper_bound=reserve, cap=30_000_000_000))
    report['limitations'] = parent['limitations']+[
        'New route proof covers Easy surface 1-1; Hard full routes, shortcut routes and every ability remain outside this pass.',
        'Visual review uses contact sheets and consecutive suspect frames, with original lossless streams retained; no claim that every individual frame was manually viewed.',
        'SMB3 world art uses stable area palettes to preserve native enemy colors; source highlight green is adapted to the native world green.']
    (final/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    (R/'build/verification/root-current62-roster-nd.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(final), ROMs=report['ROMs'], source_zip_sha256=report['source_zip_sha256'])))


if __name__ == '__main__':
    main()
