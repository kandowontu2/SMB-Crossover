"""Prepare a private no-op robot selection repair after exact baseline rebuild."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = 'f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--baseline', type=Path, help='Reuse only an exact previously reproduced accepted baseline')
    a = p.parse_args()
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = out/'source'
    source.mkdir()
    for name in ['src', 'inc', 'chr', 'audio']:
        shutil.copytree(ROOT/name, source/name)
    shutil.copytree(ROOT/'build/generated', source/'build/generated')
    for name in ['build_options.ini', 'smb1base-mmc5-expanded.cfg', 'smb1base.cfg']:
        shutil.copyfile(ROOT/name, source/name)
    original = source/'src/inventory.s'
    before = original.read_text()
    command = [sys.executable, str(ROOT/'tools/build_mmc5_expanded.py'),
               '--workspace', str(source), '--compiler', str(ROOT/'tools/Windows/cc65/bin/cl65.exe')]
    if a.baseline:
        assert sha(a.baseline) == EXPECTED
        for suffix in ['.nes', '.dbg', '.lbl', '.map']:
            shutil.copyfile(a.baseline.with_suffix(suffix), (out/'baseline.nes').with_suffix(suffix))
        previous = a.baseline.parent/'source'
        # Verify the entire current build snapshot against the earlier snapshot,
        # allowing only that earlier proposal's inventory edit.
        for item in source.rglob('*'):
            if item.is_file() and item.relative_to(source).as_posix() != 'src/inventory.s':
                assert sha(item) == sha(previous/item.relative_to(source)), str(item)
        prior = json.loads((a.baseline.parent/'prepare.json').read_text())
        assert hashlib.sha256(before.encode()).hexdigest() == prior['source_before_sha256']
    else:
        subprocess.run(command+['--output', str(out/'baseline.nes')], check=True)
    assert sha(out/'baseline.nes') == EXPECTED, 'Root snapshot differs from accepted base; do not propose on an unbound baseline.'
    edits = [
        ('    ldx SelectedCharacter\n    lda #0\n    sta InvSelected,x\n    jmp Changed',
         '    ldx SelectedCharacter\n    lda #0\n .if ::ENABLE_MMC5_EXPANDED\n    jsr InventorySelectionCommit\n .else\n    sta InvSelected,x\n .endif\n    jmp Changed'),
        ('Changed:\n  inc InvDirty\n  jsr InventoryClearActive\n  jmp Hud',
         'Changed:\n  inc InvDirty\n .if ::ENABLE_MMC5_EXPANDED\n  nop                          ; Commit owns cleanup, preserving the old span.\n  nop\n  nop\n .else\n  jsr InventoryClearActive\n .endif\n  jmp Hud'),
        ('Chosen:\n  ldx SelectedCharacter\n  lda InvCandidate\n  sta InvSelected,x\n  rts\n.endproc',
         'Chosen:\n  ldx SelectedCharacter\n  lda InvCandidate\n .if ::ENABLE_MMC5_EXPANDED\n  jmp InventorySelectionCommit\n  nop                          ; Tail call keeps the old span and stack depth.\n .else\n  sta InvSelected,x\n  rts\n .endif\n.endproc'),
    ]
    after = before
    for old, new in edits:
        assert after.count(old) == 1
        after = after.replace(old, new)
    original.write_text(after)
    patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                fromfile='a/src/inventory.s', tofile='b/src/inventory.s'))
    entry = source/'src/entrypoint.s'
    entry_before = entry.read_text()
    entry_after = entry_before + '''
; Append after every original INVENTORY contributor: no old label moves.
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "INVENTORY"
; Source2.02 destroys robot attacks only when the equipped weapon changes.
; Non-robot behavior is unchanged. No additional RAM or stack frame.
.proc InventorySelectionCommit
  cpx #CHARACTER_MEGAMAN
  beq Check
  cpx #CHARACTER_BASS
  bne Commit
Check:
  cmp InvSelected,x
  beq Done
Commit:
  sta InvSelected,x
  jmp InventoryClearActive
Done:
  rts
.endproc
.popseg
.endif
'''
    entry.write_text(entry_after)
    patch += ''.join(difflib.unified_diff(entry_before.splitlines(True), entry_after.splitlines(True),
                fromfile='a/src/entrypoint.s', tofile='b/src/entrypoint.s'))
    (out/'implementation.patch').write_text(patch)
    subprocess.run(command+['--output', str(out/'candidate.nes')], check=True)
    old, new = (out/'baseline.nes').read_bytes(), (out/'candidate.nes').read_bytes()
    changed = [i for i, (x, y) in enumerate(zip(old, new)) if x != y]
    assert len(old) == len(new)
    assert old[16+1048576:] == new[16+1048576:], 'CHR must remain byte-identical'
    report = dict(base_ROM_sha256=sha(out/'baseline.nes'), candidate_ROM_sha256=sha(out/'candidate.nes'),
                  source_before_sha256=hashlib.sha256(before.encode()).hexdigest(),
                  source_after_sha256=sha(original), implementation_patch_sha256=sha(out/'implementation.patch'),
                  changed_ROM_bytes=len(changed), changed_PRG_banks=sorted(set((i-16)//8192 for i in changed)),
                  CHR_unchanged=True, new_RAM_allocations=0, root_source_unchanged=(ROOT/'src/inventory.s').read_text()==before,
                  status='Private assembled proposal, not installed or admitted through native verification.')
    (out/'prepare.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
