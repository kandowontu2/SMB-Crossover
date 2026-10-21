"""Retain D's placement negative and append the same wrapper in a new tail segment."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/root49-sophia-land-fix-a'
C = R / 'build/verification/agent-lsr-sophia-feet-implementation-a/source-c'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(R / 'build/verification/agent49k-samus-water-up-direction-component-a'))
    from image import Image
    rejected = []
    for mapper in ('mmc3', 'mmc5'):
        a = Image(C / 'build' / f'smb-crossover-{mapper}.nes')
        b = Image(D / 'source-d/build' / a.path.name)
        shifts = {}
        for name in ('OBJECT_EX', 'LINK_HEAD_COLD'):
            old = next(z for z in a.segs.values() if z['name'] == name)
            new = next(z for z in b.segs.values() if z['name'] == name)
            assert new['start'] - old['start'] == 47 and new['size'] == old['size']
            shifts[name] = dict(old_start=old['start'], new_start=new['start'], bytes=old['size'])
        rejected.append(dict(mapper=mapper, old_new_ROM=[sha(a.path), sha(b.path)], shifted_segments=shifts,
            changed_ROM_bytes=sum(x != y for x, y in zip(a.raw, b.raw))))
    negative = D / 'placement-negative-d.json'
    assert not negative.exists()
    negative.write_text(json.dumps(dict(status='RETAINED_D_LAYOUT_NEGATIVE_NO_NATIVE_ADMISSION',
        reason='Appending to REMAINING_AUDIO shifts later bank7 object and Link code; use a new segment after both.',
        builds_passed=True, maps=rejected, main_changed=False), indent=2) + '\n')
    S = D / 'source-e'
    assert not S.exists()
    catalog = json.loads((D / 'source-catalog-d.json').read_text())
    for name, digest in catalog.items():
        source = D / 'source-d' / name
        assert sha(source) == digest, name
        target = S / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    generated = json.loads((D / 'preparation.json').read_text())['generated11']
    for name, digest in generated.items():
        source = D / 'source-d/build/generated' / name
        assert sha(source) == digest
        target = S / 'build/generated' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    leaf = S / 'src/sophia_land_audio.s'
    text = leaf.read_text()
    assert text.count('.segment "REMAINING_AUDIO"') == 1
    leaf.write_text(text.replace('.segment "REMAINING_AUDIO"', '.segment "SOPHIA_LAND_AUDIO"'))
    cfg = S / 'smb1base.cfg'
    text = cfg.read_text()
    anchor = '    LINK_HEAD_COLD: load = PRGA_07, type = ro, optional=yes;\n'
    assert text.count(anchor) == 1
    cfg.write_text(text.replace(anchor, anchor + '    SOPHIA_LAND_AUDIO: load = PRGA_07, type = ro, optional=yes; # Final47B tail; preserve earlier code PCs.\n'))
    driver = (D / 'build.py').read_text()
    assert driver.count("parent / 'source-d'") == 1
    (D / 'build-e.py').write_text(driver.replace("parent / 'source-d'", "parent / 'source-e'"))
    after = {name: sha(S / name) for name in catalog}
    original = json.loads((R / 'build/verification/agent-lsr-sophia-feet-implementation-a/revision-c.json').read_text())['source_sha256']
    changes = {name: dict(before=original[name], after=digest) for name, digest in after.items() if original[name] != digest}
    assert set(changes) == {'smb1base.cfg', 'src/sophia_land_audio.s', 'src/music_drivers/audio.s'}
    (D / 'source-catalog-e.json').write_text(json.dumps(after, indent=2) + '\n')
    (D / 'revision-e.json').write_text(json.dumps(dict(status='PREPARED_E_FINAL_BANK7_TAIL_NOT_BUILT_OR_ADMITTED',
        script_sha256=sha(__file__), parent_preparation_sha256=sha(D / 'preparation.json'),
        retained_negative_sha256=sha(negative), source_files=455,
        source_catalog_sha256=sha(D / 'source-catalog-e.json'), changes=changes,
        no_added_RAM=True, main_changed=False, accepted_release=False, goal_complete=False), indent=2) + '\n')
    print('Prepared source-e, preserving all source-c/source-d inputs and artifacts.')


if __name__ == '__main__':
    main()
