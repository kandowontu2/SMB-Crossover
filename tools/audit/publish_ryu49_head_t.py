"""Publish the exact six-file Ryu correction after source-backed staged checks."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / 'build/verification/agent-lsr-s2-head-n2-a'
PARENT = ROOT / 'build/checkpoints/roster-audit-v49-menu-options-s2'
OUT = ROOT / 'build/checkpoints/roster-audit-v49-ryu-head-t'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not OUT.exists(), 'Fresh checkpoint only'
    suite_path = PRIVATE / 'root-qa-suite-a/report.json'
    suite = json.loads(suite_path.read_text())
    assert suite['status'] == 'FAIL_RETAINED_PRIVATE_HEAD_REGRESSIONS'
    assert suite['cases'] == 759 and suite['exit'] == 1
    assert suite['failures'] == ['ryu-ground-wall-launch failed for smb-crossover-mmc3',
                                 'ryu-ground-wall-launch failed for smb-crossover-mmc5']
    assert suite['source_fixtures_and_compiled_exact_after']
    staged_path = ROOT / 'build/verification/root49-ryu-ceiling-fixture-v/staged-regression-review.json'
    assert sha(staged_path) == 'ec03a1e6a37afe4f29d9eddc3b3124594c30695b992128254fa0762403c4802d'
    staged = json.loads(staged_path.read_text())
    assert staged['status'] == 'PASS_STAGED_SOURCE_BACKED_RYU_REGRESSIONS_759_PLUS_2'
    assert staged['staged_total'] == 761 and not staged['one_green_full_run']
    assert staged['old_build_distinguishing_negative_mappers'] == 2
    assert staged['actual_guarded_source_geometry_mappers'] == 2
    for n, h in staged['references'].items():
        assert sha(ROOT / n) == h
    revised_fixture = ROOT / 'build/verification/root49-ryu-ceiling-fixture-v/ryu-ground-wall-launch.lua'
    fixture_target = ROOT / 'tests/ryu-ground-wall-launch.lua'
    old_fixture_hash = sha(fixture_target)
    revised_fixture_hash = sha(revised_fixture)
    frozen = PRIVATE / 'implementation-publication-freeze.json'
    assert sha(frozen) == 'b9777225aa4026bf598b0a7418ed193ca4877eab8461456d647b388d7f8d5e17'
    binding = json.loads(frozen.read_text())
    review_path = PRIVATE / 'actual-review-b.json'
    assert sha(review_path) == binding['review_sha256']
    review = json.loads(review_path.read_text())
    assert review['head_native']['executions'] == 36 and review['behavior_native']['passed_cases'] == 196
    parent_path = PARENT / 'manifest.json'
    assert sha(parent_path) == 'c9e8eede0cd2a06f2e473eea91f75407fc16cc2037f0ee8b27b3fe1b905e6d45'
    parent = json.loads(parent_path.read_text())['source_hashes']
    assert len(parent) == 410 and all(sha(ROOT / n) == h for n, h in parent.items())
    built_path = PRIVATE / 'report-b.json'
    assert sha(built_path) == '3d2f3f3841958b945ddbd05727e14263031a66c8aae0e0d31d6befddcad58c51'
    tested = json.loads(built_path.read_text())['source_catalog']
    assert len(tested) == 412
    assert all(sha(PRIVATE / 'source' / n) == h for n, h in tested.items())
    changes = binding['exact_changed_files']
    assert len(changes) == 6
    assert set(n for n, h in tested.items() if parent.get(n) != h) == set(changes) | {'README.md'}
    for n, row in changes.items():
        assert parent.get(n) == row['before'] and tested[n] == row['after']
        assert (not (ROOT / n).exists()) if row['before'] is None else sha(ROOT / n) == row['before']
    archive = ROOT / binding['after_archive']
    assert sha(archive) == binding['after_archive_sha256']
    with zipfile.ZipFile(archive) as z:
        for n, h in tested.items():
            assert hashlib.sha256(z.read(n)).hexdigest() == h
    for n, h in suite['fixture_and_runner_hashes'].items():
        assert sha(ROOT / n) == h and sha(PRIVATE / 'source' / n) == h
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    assert workspace_bytes(ROOT) + 200_000_000 < 50_000_000_000
    OUT.mkdir()
    for n in changes:
        (ROOT / n).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PRIVATE / 'source' / n, ROOT / n)
    shutil.copyfile(revised_fixture, fixture_target)
    assert sha(fixture_target) == revised_fixture_hash
    # The private archive still has the pre-publication S2 README. Preserve the
    # actual START/OPTIONS instructions, then add the new component status.
    readme = ROOT / 'README.md'
    before_readme = sha(readme)
    assert before_readme == parent['README.md']
    old = 'This is a playable port in progress. [The parity audit](docs/reference/parity.md) records differences from the Flash version.'
    text = readme.read_text(encoding='utf8')
    assert text.count(old) == 1
    text = text.replace(old, old + '\n\nThe current provisional v49 build corrects Ryu\'s upward block response and preserves the START/OPTIONS menu. Regression coverage comprises759 unchanged passes plus the independently source-backed ceiling fixture on both mappers:761 staged passes, with the original two failures retained. Focused head and behavior checks also pass. Full roster routes, all upgrades, source geometry and final recordings remain in progress; see [the current evidence and limits](docs/qa/roster-provisional-v49.md).')
    readme.write_text(text, encoding='utf8')
    cat = dict(tested, **{'README.md': sha(readme)})
    assert all(sha(ROOT / n) == h for n, h in cat.items())
    refs = [parent_path, frozen, built_path, review_path, suite_path, staged_path]
    report = dict(status='BUILDING_WORKING_RYU_HEAD_T', accepted_release=False, goal_complete=False,
        source_hashes=cat, compiler_source_files=412, source_changes=list(changes),
        tested_private_source_hashes=tested, documentation_delta=dict(
            preserved_S2_menu_instructions=True, README_before=before_readme, README_after=sha(readme),
            runtime_sources_exact_tested_private=True),
        staged_regression_coverage=dict(unchanged_passes=759, source_revised_mapper_passes=2,
            staged_total=761, one_green_full_run=False, original_failures_retained=True),
        fixture_migration=dict(path='tests/ryu-ground-wall-launch.lua', before=old_fixture_hash,
            after=revised_fixture_hash, source_backed_actual_query_and_old_build_negative=True),
        script_sha256=sha(__file__), parent_checkpoint=PARENT.name,
        references=[dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for p in refs], builds=[])

    def save():
        (OUT / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    expected = dict(mmc3='63dc6248c04823075872c665131880711fab26aebc2d2b37a1b75f8a4ac0afac',
                    mmc5='7c9d9d1b2dff3c52a5f69cee007dde7fdc29d6ec393ae0326b461ca99c597e2b')
    for mapper in ['mmc3', 'mmc5']:
        command = [sys.executable, 'tools/build.py', '--mapper', mapper]
        with (OUT / f'build-{mapper}.log').open('wb') as log:
            code = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        assert code == 0, mapper
        actual = ROOT / f'build/smb-crossover-{mapper}.nes'
        candidate = PRIVATE / 'source/build' / actual.name
        assert sha(actual) == expected[mapper] and actual.read_bytes() == candidate.read_bytes()
        assert actual.with_suffix('.lbl').read_bytes() == candidate.with_suffix('.lbl').read_bytes()
        outputs = {}
        for ext in ['nes', 'dbg', 'lbl', 'map', 'lst']:
            p = actual.with_suffix('.' + ext)
            shutil.copyfile(p, OUT / p.name)
            outputs[ext] = dict(path=str(p.relative_to(ROOT)), sha256=sha(p))
        report['builds'].append(dict(mapper=mapper, outputs=outputs,
                                   ROM_and_labels_exact_tested_candidate=True))
        save()
    assert all(sha(ROOT / n) == h for n, h in cat.items())
    source_zip = OUT / 'source-v49-ryu-head-t.zip'
    with zipfile.ZipFile(source_zip, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(cat):
            z.write(ROOT / n, n)
        z.writestr('archived-file-hashes.json', json.dumps(cat, indent=2) + '\n')
    report.update(status='PASS_WORKING_RYU_HEAD_T_BOTH_MAPPERS',
        source_archive_sha256=sha(source_zip), workspace_bytes=workspace_bytes(ROOT),
        qualification='Bounded Ryu ordinary-head correction and exact foot closure relocation; menu defaults unchanged. Water/body/cache/multicell source fidelity and full roster/weapon/final-recording work remain open. S2 recordings retain their original hashes.')
    save()
    print(json.dumps(dict(status=report['status'], checkpoint=str(OUT),
                          manifest_sha256=sha(OUT / 'manifest.json'))), flush=True)


if __name__ == '__main__':
    main()
