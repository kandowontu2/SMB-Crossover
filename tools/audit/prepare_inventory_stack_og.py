"""Build an isolated shallow inventory query from the pinned OF snapshot."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'build/checkpoints/injury-page-of'

LEAF = '''; Flatten the read-only Easy/Hard inventory predicate. The former four-bank
; gate chain can leave insufficient hardware stack for an audio NMI. Preserve
; its complete returned A/X/Y/P, including Roll's alternate-specific A result.
.pushseg
.segment "INVENTORY_LEGACY_LEAF"
.proc InventoryLegacyLeaf
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne CheckMac
  lda RlVariant
  bne Modern
  jmp Original
CheckMac:
  cmp #15
  beq Classic
  cmp #CHARACTER_SIMON
  bne CheckZ2
  pha
  lda Cv3Variant
  cmp #1
  bcc RestoreOriginal
  cmp #4
  bcs RestoreOriginal
  pla
  sec
  rts
CheckZ2:
  cmp #CHARACTER_LINK
  bne Original
  pha
  lda Z2Variant
  cmp #1
  bne RestoreOriginal
  pla
  sec
  rts
RestoreOriginal:
  pla
Original:
  ldx CrossoverBehaviorVersion
  bne Modern
  ldx SelectedCharacter
  cpx #CHARACTER_MEGAMAN
  bcc Modern
  cpx #CHARACTER_SIMON+1
  bcs Modern
Classic:
  sec
  rts
Modern:
  clc
  rts
.endproc
.popseg
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((PARENT / 'manifest.json').read_text())
    assert sha(PARENT / 'source.zip') == manifest['source_zip_sha256']
    assert sha(PARENT / 'candidate.nes') == manifest['rom_sha256']
    stage = out / 'source'
    with zipfile.ZipFile(PARENT / 'source.zip') as z:
        assert z.testzip() is None
        assert all((stage / n).resolve().is_relative_to(stage.resolve()) for n in z.namelist())
        z.extractall(stage)
    assert all(sha(stage / n) == h for n, h in manifest['source_files'].items())
    edits = {
        'src/inventory.s': ('farcall RlLegacyDispatch,jmp', 'farcall InventoryLegacyLeaf,jmp'),
        'src/entrypoint.s': ('.include "protoman_hurt_end.s"', '.include "protoman_hurt_end.s"\n.include "inventory_legacy_leaf.s"'),
        'smb1base-mmc5-expanded.cfg': ('    PROTO_HURT_END: load=X5_NEW_42,type=ro;', '    PROTO_HURT_END: load=X5_NEW_42,type=ro;\n    INVENTORY_LEGACY_LEAF: load=X5_NEW_42,type=ro;'),
    }
    changes = {}
    for name, (old, new) in edits.items():
        f = stage / name; text = f.read_text(); assert text.count(old) == 1
        before = sha(f); f.write_text(text.replace(old, new))
        changes[name] = dict(before=before, after=sha(f))
    f = stage / 'src/inventory_legacy_leaf.s'; assert not f.exists(); f.write_text(LEAF)
    changes['src/inventory_legacy_leaf.s'] = dict(before=None, after=sha(f))
    result = subprocess.run([sys.executable, str(stage / 'tools/build_mmc5_expanded.py'),
        '--workspace', str(stage), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
        '--output', str(out / 'candidate.nes')], cwd=stage, capture_output=True, text=True)
    (out / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
    old = (PARENT / 'candidate.nes').read_bytes(); new = (out / 'candidate.nes').read_bytes()
    assert len(old) == len(new) and old[:16] == new[:16]
    prg = old[4] * 16384 + ((old[9] & 15) << 8) * 16384
    changed = [i for i in range(prg // 8192) if old[16+i*8192:16+(i+1)*8192] != new[16+i*8192:16+(i+1)*8192]]
    assert changed == [59, 66] and old[16+prg:] == new[16+prg:]
    def labels(path):
        return {q[2]: q[1] for line in path.read_text().splitlines() if len(q := line.split()) == 3}
    before = labels(PARENT / 'candidate.lbl'); after = labels(out / 'candidate.lbl')
    assert all(after[n] == v for n, v in before.items()), 'Pre-existing symbol moved'
    proof = dict(prepared=True, accepted=False, parent_ROM_sha256=sha(PARENT / 'candidate.nes'),
        ROM_sha256=sha(out / 'candidate.nes'), source_changes=changes, changed_PRG_banks=changed,
        CHR_unchanged=True, all_preexisting_labels_unchanged=True,
        scope='Isolated source preparation. Requires actual CPU/interrupt/native route verification before adoption.')
    (out / 'preparation.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
