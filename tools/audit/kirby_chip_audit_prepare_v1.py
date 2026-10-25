"""Build a private, old-PC-preserving vertical-page contact repair."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
BASE = 'f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--baseline', type=Path)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output/'source'
    source.mkdir()
    for name in ['src', 'inc', 'chr', 'audio']:
        shutil.copytree(ROOT/name, source/name)
    shutil.copytree(ROOT/'build/generated', source/'build/generated')
    for name in ['build_options.ini', 'smb1base-mmc5-expanded.cfg', 'smb1base.cfg']:
        shutil.copy2(ROOT/name, source/name)
    command = [sys.executable, str(ROOT/'tools/build_mmc5_expanded.py'), '--workspace', str(source),
        '--compiler', str(ROOT/'tools/Windows/cc65/bin/cl65.exe')]
    if a.baseline:
        assert sha(a.baseline) == BASE
        for suffix in ['.nes','.dbg','.lbl','.map']:
            shutil.copy2(a.baseline.with_suffix(suffix), (a.output/'baseline.nes').with_suffix(suffix))
        for path in source.rglob('*'):
            if path.is_file():
                prior = a.baseline.parent/'source'/path.relative_to(source)
                # Only the earlier proposal's three altered files may differ.
                if path.relative_to(source).as_posix() not in ['src/kirby_weapons.s','src/chip_dale_boxes.s','src/entrypoint.s']:
                    assert sha(path) == sha(prior), str(path)
    else:
        subprocess.run(command+['--output', str(a.output/'baseline.nes')], check=True)
    assert sha(a.output/'baseline.nes') == BASE, 'Source snapshot is no longer the accepted f00 build.'
    changes = {}
    path = source/'src/kirby_weapons.s'
    before = path.read_text()
    token = '  cpx #6\n  jcs No\n'
    assert before.count(token) == 1
    after = before.replace(token, '  jsr KbContactSlotAdmission\n  bcs No\n  nop\n  nop\n')
    path.write_text(after)
    changes['src/kirby_weapons.s'] = (before, after)
    path = source/'src/chip_dale_boxes.s'
    before = path.read_text()
    token = '.proc CdBoxEnemies'
    head, tail = before.split(token)
    old = ' lda Enemy_Flag,x\n beq Next\n bmi Next\n'
    assert tail.count(old) == 1
    after = head+token+tail.replace(old, ' jsr CdContactSlotAdmission\n bcc Next\n nop\n')
    path.write_text(after)
    changes['src/chip_dale_boxes.s'] = (before, after)
    path = source/'src/entrypoint.s'
    before = path.read_text()
    after = before+'\n; Contact objects on another vertical page cannot overlap a visible shot.\n.if ::ENABLE_MMC5_EXPANDED\n'
    after += '''.pushseg
.segment "KIRBY_ABILITIES"
.proc KbContactSlotAdmission
  cpx #6
  bcs Inactive
  lda Enemy_Y_HighPos,x
  cmp #1
  bne Inactive
  clc                         ; Original valid-slot CPX carry remains clear.
  rts
Inactive:
  sec
  rts
.endproc
.popseg
.pushseg
.segment "CD_LOGIC"
.proc CdContactSlotAdmission
  lda Enemy_Y_HighPos,x
  cmp #1
  bne Inactive
  lda Enemy_Flag,x
  beq Inactive
  bmi Inactive
  sec
  rts
Inactive:
  clc
  rts
.endproc
.popseg
'''
    after += '.endif\n'
    path.write_text(after)
    changes['src/entrypoint.s'] = (before, after)
    patch = ''.join(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
        fromfile='a/'+name, tofile='b/'+name)) for name,(old,new) in changes.items())
    (a.output/'implementation.patch').write_text(patch)
    subprocess.run(command+['--output', str(a.output/'candidate.nes')], check=True)
    labels = lambda path: {q[2]:q[1] for line in path.read_text().splitlines() if len(q:=line.split()) == 3}
    oldlabels, newlabels = labels((a.output/'baseline.lbl')), labels(a.output/'candidate.lbl')
    assert all(newlabels[k] == v for k,v in oldlabels.items()), 'An exported old PC/RAM label moved.'
    old, new = [(a.output/n).read_bytes() for n in ['baseline.nes','candidate.nes']]
    assert old[16+1048576:] == new[16+1048576:]
    changed = [i for i,(x,y) in enumerate(zip(old,new)) if x != y]
    report = dict(base_ROM_sha256=sha(a.output/'baseline.nes'), candidate_ROM_sha256=sha(a.output/'candidate.nes'),
        implementation_patch_sha256=sha(a.output/'implementation.patch'), changed_bytes=len(changed),
        changed_PRG_banks=sorted({(i-16)//8192 for i in changed}),
        all_old_exported_labels_exact=True, CHR_exact=True, new_RAM_bytes=0,
        root_source_unchanged=all((ROOT/name).read_text() == old for name,(old,new) in changes.items()),
        status='Private assembled CPU proposal. Native contact/page-boundary checks remain required.')
    (a.output/'binding.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
