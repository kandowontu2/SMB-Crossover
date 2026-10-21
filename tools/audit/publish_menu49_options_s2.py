"""Publish the tested menu candidate and rebuild the two working ROMs."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, zipfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT/'build/verification/root49-menu-options-private-s2'
OUT = ROOT/'build/checkpoints/roster-audit-v49-menu-options-s2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode = True
    assert not OUT.exists()
    built = json.loads((PRIVATE/'report.json').read_text())
    assert sha(PRIVATE/'report.json') == 'b01d2e9ea5e6a9ea178bd3bc6d41fea10d5ec024befe9d53fea96efd5d4ad131'
    assert built['status'] == 'PASS_PRIVATE_MENU_S2_BUILD_LAYOUT_ONLY'
    parent_path = ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json'
    parent = json.loads(parent_path.read_text())['source_hashes']
    cat = built['source410_hashes']
    assert len(parent) == 409 and len(cat) == 410
    assert all(sha(ROOT/n) == h for n,h in parent.items())
    assert all(sha(PRIVATE/'source'/n) == h for n,h in cat.items())
    refs = [PRIVATE/'report.json', parent_path]
    regression = ROOT/'build/verification/root49p-sophia-integrated-private-r/qa-suite-a/report.json'
    r = json.loads(regression.read_text())
    assert r['status'] == 'PASS_FULL_UNCHANGED_INTEGRATED_R_REGRESSIONS', r['status']
    assert r['cases'] == 761 and not r['failures'] and r['source409_and_original_fixtures_compiled_exact_after']
    refs.append(regression)
    for mapper, tag in [('mmc3','root-s2-mmc3-b'),('mmc5','root-s2-mmc5-ui-b')]:
        folder = ROOT/'build/verification/menu-options-behavior-ui-b'/('binding-'+tag)
        binding = json.loads((folder/'binding.json').read_text())
        result = json.loads((folder/'native-output/result.json').read_text())
        assert result['passes'] and result['steps'] == 31 and result['controller_only'] and not result['emulated_writes']
        target = next(x for x in built['builds'] if x['mapper'] == mapper and not x['baseline'])
        assert binding['rom_sha256'] == target['outputs']['nes']['sha256']
        refs += [folder/'binding.json', folder/'native-output/result.json']
    combat = ROOT/'build/verification/root49-menu-validation-s2.json'
    combat_result = json.loads(combat.read_text())
    assert combat_result['status'] == 'PASS_MENU_S2_UI_CONTACT_AND_PROTECTED_ATTACKS', combat_result
    refs.append(combat)
    for mapper in ('mmc3','mmc5'):
        refs.append(ROOT/f'build/verification/root49p-sophia-integrated-performance-s-{mapper}-review-a.json')
    sys.path.insert(0,str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+200_000_000 < 50_000_000_000
    OUT.mkdir()
    changed = [n for n,h in cat.items() if parent.get(n) != h]
    assert len(changed) == 11
    for n in changed:
        p = ROOT/n
        p.parent.mkdir(parents=True,exist_ok=True)
        if n not in parent: assert not p.exists()
        shutil.copyfile(PRIVATE/'source'/n,p)
    assert all(sha(ROOT/n) == h for n,h in cat.items())
    # Runtime source inputs matched the tested candidate above. Record the
    # documentation-only delta before rebuilding the identical ROMs below.
    readme = ROOT/'README.md'
    text = readme.read_text(encoding='utf8')
    old = 'Start opens character selection from the static title.'
    assert text.count(old) == 1
    text = text.replace(old, 'The static title offers START and OPTIONS. Up/Down chooses a row; A or Start confirms. START opens character selection.')
    old = ('Press Down from the bottom character row to highlight **PLAYER OUTLINES**.\n'
           'A, Start, Select, Left or Right toggles it; Up returns to the roster. OFF omits\n'
           'extra black mask sprites while retaining normal body colors and face details.\n'
           'The gold option row starts OFF and survives character changes and deaths until reset.')
    assert text.count(old) == 1
    text = text.replace(old, ('OPTIONS contains **PLAYER SHADOWS** (default OFF) and **BEHAVIOR** (default 1.0).\n'
        'Up/Down highlights a setting; A, Start, Select, Left or Right toggles it. B returns\n'
        'to the title. Shadows OFF omits extra black mask sprites while retaining normal\n'
        'body colors and face details. Behavior 1.0 lets the roster stomp ordinary enemies;\n'
        '2.02 retains the previous character-specific contact rules. Special body attacks,\n'
        'hazards and underwater rules keep their existing priority. Preferences persist\n'
        'through selection, gameplay and deaths until reset. Character select contains\n'
        'only character selection. See [menu validation](docs/qa/menu-options-v49.md).'))
    readme.write_text(text,encoding='utf8')
    validated_cat = dict(cat)
    cat = dict(cat, **{'README.md':sha(readme)})
    report = dict(status='BUILDING_WORKING_MENU_OPTIONS',accepted_release=False,goal_complete=False,
        parent_checkpoint=parent_path.parent.name,source_hashes=cat,compiler_source_files=410,
        validated_candidate_source_hashes=validated_cat,documentation_update='README Play instructions; runtime sources unchanged from the tested candidate.',
        source_changes=changed,script_sha256=sha(__file__),references=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in refs],builds=[])
    def save(): (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for mapper in ('mmc3','mmc5'):
        with (OUT/f'build-{mapper}.log').open('wb') as log:
            p = subprocess.run([sys.executable,'tools/build.py','--mapper',mapper],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        assert p.returncode == 0,mapper
        actual = ROOT/f'build/smb-crossover-{mapper}.nes'
        candidate = PRIVATE/'source/build'/actual.name
        assert actual.read_bytes() == candidate.read_bytes()
        assert actual.with_suffix('.lbl').read_bytes() == candidate.with_suffix('.lbl').read_bytes()
        files = {}
        for ext in ('.nes','.dbg','.lbl','.map','.lst'):
            src = actual.with_suffix(ext)
            shutil.copyfile(src,OUT/src.name)
            files[ext[1:]] = dict(path=str(src.relative_to(ROOT)),sha256=sha(src))
        report['builds'].append(dict(mapper=mapper,outputs=files,ROM_and_labels_exact_tested_candidate=True))
        save()
    assert all(sha(ROOT/n) == h for n,h in cat.items())
    with zipfile.ZipFile(OUT/'source-v49-menu-options-s2.zip','x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(cat): z.write(ROOT/n,n)
        z.writestr('archived-file-hashes.json',json.dumps(cat,indent=2)+'\n')
    report.update(status='PASS_WORKING_MENU_OPTIONS_BOTH_MAPPERS',source_archive_sha256=sha(OUT/'source-v49-menu-options-s2.zip'),
        workspace_bytes=workspace_bytes(ROOT),qualification='Requested START/OPTIONS and behavior modes tested on both mappers. This working checkpoint includes the separately validated Sophia optimization. Full roster playthroughs, every weapon and final recordings remain open.')
    save()
    print(json.dumps(dict(status=report['status'],checkpoint=str(OUT),manifest_sha256=sha(OUT/'manifest.json')),indent=2))

if __name__ == '__main__': main()
