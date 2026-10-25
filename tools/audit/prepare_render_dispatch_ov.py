"""Prepare a private shallow graphics/draw router from the accepted OJ source."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'build/checkpoints/collision-dispatch-oj'
SOURCE = '''; Select the first existing owner without visiting unrelated family banks.
; Preserve Roll's original alternate override and A/P at its and Mac's leaves.
.pushseg
.segment "HOT_RENDER_GATE"
.macro HotRender Name,Roll,Kirby,Chip,Mac,Mike,Mario3,Vic,Turtle,Original
.proc Name
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_BASS
 bne NotRoll
 lda RlVariant
 beq NotRoll
 pla
 plp
 farcall Roll,jmp
NotRoll:
 lda SelectedCharacter
 cmp #20
 jcs Fallback
 cmp #14
 bcc ToKirby
 beq ToChip
 cmp #15
 beq ToMac
 cmp #16
 beq ToMike
 cmp #17
 beq ToMario3
 cmp #18
 beq ToVic
 pla
 plp
 farcall Turtle,jmp
ToKirby:
 pla
 plp
 farcall Kirby,jmp
ToChip:
 pla
 plp
 farcall Chip,jmp
ToMac:
 pla
 plp
 farcall Mac,jmp
ToMike:
 pla
 plp
 farcall Mike,jmp
ToMario3:
 pla
 plp
 farcall Mario3,jmp
ToVic:
 pla
 plp
 farcall Vic,jmp
Fallback:
 pla
 plp
 farcall Original,jmp
.endproc
.endmacro
HotRender HotPlayerGraphics,RlGraphics,KbGraphicsDispatch,CdGraphicsDispatch,LmGraphicsGate,JnGraphicsDispatch,M3GraphicsDispatch,VvGraphicsDispatch,TnGraphics,RlGraphicsDispatch
HotRender HotNewCharacterDraw,RlDraw,CdNewDrawDispatch,CdNewDrawDispatch,LmDrawGate,JnDrawDispatch,M3NewDrawDispatch,VvDrawDispatch,TnDraw,RlDrawDispatch
.popseg
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    stage = out / 'source'
    m = json.loads((PARENT / 'manifest.json').read_text())
    assert sha(PARENT / 'source.zip') == m['source_zip_sha256']
    assert sha(PARENT / 'candidate.nes') == m['rom_sha256']
    with zipfile.ZipFile(PARENT / 'source.zip') as z:
        assert z.testzip() is None
        assert all((stage / n).resolve().is_relative_to(stage.resolve()) for n in z.namelist())
        z.extractall(stage)
    assert all(sha(stage / n) == h for n, h in m['source_files'].items())
    changes = {}
    edits = {
        'src/player.s': [('farcall RlGraphicsDispatch', 'farcall HotPlayerGraphics')],
        'src/kirby_draw.s': [('farcall RlDrawDispatch,jmp', 'farcall HotNewCharacterDraw,jmp')],
        'src/entrypoint.s': [('.include "hot_collision_gate.s"', '.include "hot_collision_gate.s"\n.include "hot_render_gate.s"')],
        'smb1base-mmc5-expanded.cfg': [('    HOT_COLLISION_GATE: load=X5_NEW_42,type=ro;',
                                      '    HOT_COLLISION_GATE: load=X5_NEW_42,type=ro;\n    HOT_RENDER_GATE: load=X5_NEW_42,type=ro;')],
    }
    for name, pairs in edits.items():
        f = stage / name
        text = f.read_text()
        before = sha(f)
        for old, new in pairs:
            assert text.count(old) == 1, (name, old)
            text = text.replace(old, new)
        f.write_text(text)
        changes[name] = dict(before=before, after=sha(f))
    f = stage / 'src/hot_render_gate.s'
    assert not f.exists()
    f.write_text(SOURCE)
    changes['src/hot_render_gate.s'] = dict(before=None, after=sha(f))
    run = subprocess.run([sys.executable, str(stage / 'tools/build_mmc5_expanded.py'), '--workspace', str(stage),
                          '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
                          '--output', str(out / 'candidate.nes')], cwd=stage, capture_output=True, text=True)
    (out / 'build.log').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, (run.stdout + run.stderr)[-4000:]
    old, new = (PARENT / 'candidate.nes').read_bytes(), (out / 'candidate.nes').read_bytes()
    assert len(old) == len(new) and old[:16] == new[:16] and old[16 + 1048576:] == new[16 + 1048576:]
    changed = [i for i in range(128) if old[16 + i * 8192:16 + (i + 1) * 8192] != new[16 + i * 8192:16 + (i + 1) * 8192]]
    assert set(changed) == {1, 4, 66}, changed
    q = dict(prepared=True, accepted=False, parent_ROM_sha256=m['rom_sha256'], ROM_sha256=sha(out / 'candidate.nes'),
             source_changes=changes, changed_PRG_banks=changed, header_and_CHR_exact=True,
             scope='Private two-call shallow rendering router. Existing graphics/draw leaves, RAM, CHR, audio and physics are untouched. Requires exact leaf-admission/return and IRQ comparisons, native matched performance/render checks and regressions before any adoption.')
    (out / 'preparation.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
