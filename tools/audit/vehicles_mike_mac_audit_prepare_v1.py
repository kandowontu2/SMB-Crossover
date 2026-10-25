"""Private, address-stable TMNT pickup coordinates / Mac extra-life proposal."""
from pathlib import Path
import argparse, difflib, hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = 'f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', required=True, type=Path)
    a = p.parse_args()
    out = a.packet.resolve()
    source = out/'source'
    assert sha(out/'baseline.nes') == EXPECTED
    manifest = json.loads((out/'frozen-source.json').read_text())
    for name, digest in manifest.items():
        assert sha(source/name) == digest, name
    command = [sys.executable, str(ROOT/'tools/build_mmc5_expanded.py'),
               '--workspace', str(source), '--compiler', str(ROOT/'tools/Windows/cc65/bin/cl65.exe')]
    subprocess.run(command+['--output', str(out/'rebuilt-baseline.nes')], check=True)
    assert sha(out/'rebuilt-baseline.nes') == EXPECTED
    edits = {
        'src/tmnt_equipment.s': (
            ' lda Enemy_X_Position,x\n clc\n adc #4\n sta EnemyBoundingBoxCoord,y\n'
            ' lda Enemy_X_Position,x\n clc\n adc #12\n sta EnemyBoundingBoxCoord+2,y',
            ' jsr TnPickupScreenBox\n .res 13,$ea ; original sixteen-byte horizontal span'),
        'src/little_mac_core.s': (
            ' lda LmLife\n cmp NumberofLives\n jne NewLife',
            ' jsr LmLifeAdvanced\n jcc NewLife\n .res 3,$ea ; preserve the original life-test span'),
    }
    patch = ''
    for name, (old, new) in edits.items():
        f = source/name
        before = f.read_text()
        assert before.count(old) == 1, name
        after = before.replace(old, new)
        f.write_text(after)
        patch += ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                            fromfile='a/'+name, tofile='b/'+name))
    f = source/'src/entrypoint.s'
    before = f.read_text()
    after = before + '''
; Append after all existing contributors; existing code/RAM/CHR addresses stay fixed.
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "TMNT_CORE"
; PowerUpObjHandler has already computed this actor's relative position.
; Native collision boxes are screen-relative. Reapply native edge clipping
; after narrowing the completed 16px Kiai icon to its visible center.
.proc TnPickupScreenBox
 lda Enemy_Rel_XPos
 clc
 adc #4
 sta EnemyBoundingBoxCoord,y
 lda Enemy_Rel_XPos
 clc
 adc #12
 sta EnemyBoundingBoxCoord+2,y
 inx
 iny
 iny
 iny
 iny
 jsr CheckRightScreenBBox
 dey
 dey
 dey
 dey
 rts
.endproc
.segment "LM_CORE"
; Gaining a life retains boxing HP, stars, stamina and active moves.
; Record increases immediately so the next real death remains detectable.
.proc LmLifeAdvanced
 lda NumberofLives
 cmp LmLife
 sta LmLife
 rts
.endproc
.popseg
.endif
'''
    f.write_text(after)
    patch += ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                        fromfile='a/src/entrypoint.s', tofile='b/src/entrypoint.s'))
    (out/'implementation.patch').write_text(patch)
    subprocess.run(command+['--output', str(out/'candidate.nes')], check=True)
    sys.path.insert(0, str(ROOT/'tools/audit'))
    from check_tmnt_render_oa import load
    from check_tmnt_audio_fallback_oc import qualified
    base, candidate = load(out/'baseline.nes'), load(out/'candidate.nes')
    old_qualified, new_qualified = qualified(out/'baseline.nes'), qualified(out/'candidate.nes')
    assert all(new_qualified.get(n) == v for n, v in old_qualified.items())
    for name, s in base['syms'].items():
        if 'seg' not in s:
            assert candidate['syms'][name]['val'] == s['val'], name
        elif s.get('type') == 'lab':
            assert candidate['syms'][name]['val'] == s['val'], name
    old, new = base['raw'], candidate['raw']
    assert old[16+1048576:] == new[16+1048576:]
    changed = [i for i, (x, y) in enumerate(zip(old, new)) if x != y]
    report = dict(base_ROM_sha256=sha(out/'baseline.nes'), candidate_ROM_sha256=sha(out/'candidate.nes'),
                  changed_ROM_bytes=len(changed), changed_PRG_banks=sorted(set((i-16)//8192 for i in changed)),
                  CHR_unchanged=True, all_existing_addresses_unchanged=True, new_RAM_allocations=0,
                  qualified_existing_symbols_checked=len(old_qualified),
                  patch_sha256=sha(out/'implementation.patch'),
                  scope='Private CPU proposal only; not installed or native-qualified.')
    (out/'prepare.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
