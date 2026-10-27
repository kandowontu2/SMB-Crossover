"""Merge frozen cheats into the existing unbound sound draft; never clone it."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json

R = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', type=Path, required=True)
    parser.add_argument('--cheats-freeze', type=Path, required=True)
    args = parser.parse_args()
    source = args.draft/'source'
    assert source.is_dir() and args.cheats_freeze.is_dir()
    ready = json.loads((args.cheats_freeze/'readiness.json').read_text())
    assert ready['passed'] and ready['source_ready_for_parent_composition'] and not ready['adopted']
    for row in ready['bindings']:
        assert sha(Path(row['path'])) == row['sha256'], row['path']
    changed = json.loads((args.cheats_freeze/'changed-sources.json').read_text())['changed_files']
    assert len(changed) == 9
    for row in changed:
        original = R/row['path']
        assert (sha(original) if original.exists() else None) == row['original_sha256'], row['path']
        assert sha(Path(row['source_path'])) == row['candidate_sha256']
    for row in changed:
        target = source/row['path']
        if row['path'] == 'src/entrypoint.s':
            base = (R/row['path']).read_text()
            proposal = Path(row['source_path']).read_text()
            assert proposal.startswith(base)
            existing = target.read_text()
            assert existing.count('.include "sound_test.s"') == 1
            assert '.include "cheats_four.s"' not in existing
            target.write_text(existing+proposal[len(base):], newline='\n')
        else:
            target.write_bytes(Path(row['source_path']).read_bytes())
    # The sound frontend already retains parent focus and adds the fourth row.
    menu = (source/'src/character_select.s').read_text()
    assert 'cmp #4\n.else\n  cmp #3' in menu
    assert 'sta GuestOamRotationActive\n.if !::ENABLE_MMC5_EXPANDED\n  sta CrossoverOptionsFocus' in menu
    assert 'OpenCheats:\n.if ::ENABLE_MMC5_EXPANDED\n  lda #0\n  sta CrossoverOptionsFocus' in menu
    manifest = {p.relative_to(source).as_posix(): sha(p) for p in sorted(source.rglob('*'))
                if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    (args.draft/'composed-source-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    result = dict(source_only=True, installed=False, native_run=False,
                  cheats_readiness_sha256=sha(args.cheats_freeze/'readiness.json'),
                  cheats_bindings_verified=len(ready['bindings']),
                  cheats_parent_ROM=ready['ROM_sha256'], source_files=len(manifest),
                  reused_existing_draft=True, source_clones=0)
    patch = ''
    for name in sorted(manifest):
        path = source/name
        if path.suffix not in ('.s', '.inc', '.cfg'):
            continue
        old = (R/name).read_text() if (R/name).exists() else ''
        new = path.read_text()
        if old != new:
            patch += ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                               fromfile='a/'+name, tofile='b/'+name))
    (args.draft/'composed-implementation.patch').write_text(patch)
    (args.draft/'composition.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
