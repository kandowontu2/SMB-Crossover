"""Stage a TMNT-owned, interior world-sprite renderer from the frozen NZ source."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-render-oa')

FAST = '''; Only TnWorldDraw calls this helper. All linked world records have signed
; X offsets -8..0 and Y offsets -24..0. Keep general clipping/capacity handling
; at the edges. No additional RAM, sprites, CHR pages or gameplay state.
.pushseg
.segment "TMNT_CORE"
.proc TnFastWorldRender
.if ::MAPPER_MMC3
 farcall MetaspriteRenderLoop,jmp
.else
 lda R5
 bne Legacy
 lda R7
 cmp #1
 bne Legacy
 lda R4
 cmp #8
 bcc Legacy
 lda R6
 cmp #24
 bcc Legacy
 lda R3
 and #3                        ; preserve source records' fixed palettes
 bne Legacy
 ldx CurrentOAMOffset
 ldy #0
 lda (R0),y
 beq Empty
 bmi Legacy                    ; generic owns unusual/rejected headers
 tay
 and #3
 bne Legacy
 tya
 clc
 adc CurrentOAMOffset
 bcs Legacy
 lda GuestOamRotationActive
 beq Start
 txa
 clc
 adc RgOamRotation
 tax
Start:
Loop:
 lda (R0),y
 clc
 adc R4
 sta Sprite_X_Position,x
 dey
 lda (R0),y
 clc
 adc R6
 sta Sprite_Y_Position,x
 dey
 lda (R0),y
 ora R3
 and #$f3
 sta Sprite_Attributes,x
 dey
 lda (R0),y
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 dey
 bne Loop
 clv                           ; same final valid Y-page ADC overflow flag
 txa
 ldy GuestOamRotationActive
 beq Save
 sec
 sbc RgOamRotation
Save:
 sta CurrentOAMOffset
 ldy #0
 sec
 rts
Empty:
 clc
 rts
Legacy:
 farcall MetaspriteRenderLoop,jmp
.endif
.endproc
.export TnFastWorldRender
.popseg
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(); p.add_argument('--label', required=True)
    a = p.parse_args(); assert a.label and all(c.isalnum() or c in '-_' for c in a.label)
    out = OUT / a.label; out.mkdir(parents=True, exist_ok=False)
    parent = ROOT / 'build/checkpoints/tmnt-empty-render-nz'
    manifest = json.loads((parent / 'manifest.json').read_text())
    assert sha(parent / 'candidate.nes') == manifest['rom_sha256']
    source = out / 'source'
    with zipfile.ZipFile(parent / 'source.zip') as z:
        assert z.testzip() is None
        assert all((source / n).resolve().is_relative_to(source.resolve()) for n in z.namelist())
        z.extractall(source)
    assert all(sha(source / n) == h for n, h in manifest['source_files'].items())
    changes = {}

    def change(name, old, new):
        f = source / name; before = sha(f); text = f.read_text()
        assert text.count(old) == 1, name
        f.write_text(text.replace(old, new))
        changes[name] = dict(before=before, after=sha(f))

    change('src/tmnt_equipment_draw.s', '''.proc TnWorldDraw
 farcall MetaspriteRenderLoop
 BankPRGC #.bank(TnWorldArtStart)
''', '''.proc TnWorldDraw
 ; Keep every pre-existing linked address stable; skip the unused call padding.
CallStart:
 jsr TnFastWorldRender
 jmp CallEnd
 .res 12,$ea
CallEnd:
 .assert CallEnd-CallStart=18,error,"Preserve original farcall footprint"
 BankPRGC #.bank(TnWorldArtStart)
''')
    change('src/tmnt.s', '.include "tmnt_secondary_art.inc"\n',
           '.include "tmnt_secondary_art.inc"\n.include "tmnt_fast_render.s"\n')
    f = source / 'src/tmnt_fast_render.s'; assert not f.exists(); f.write_text(FAST)
    changes['src/tmnt_fast_render.s'] = dict(before=None, after=sha(f))
    z = subprocess.run([sys.executable, str(source / 'tools/build_mmc5_expanded.py'),
        '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
        '--output', str(out / 'candidate.nes')], cwd=source, capture_output=True, text=True)
    (out / 'build.log').write_text(z.stdout + z.stderr)
    assert z.returncode == 0, z.stdout + z.stderr
    old = (parent / 'candidate.nes').read_bytes(); new = (out / 'candidate.nes').read_bytes()
    banks = [b for b in range(128) if old[16+b*8192:16+(b+1)*8192] != new[16+b*8192:16+(b+1)*8192]]
    assert banks == [87], banks
    assert old[16+1048576:] == new[16+1048576:]
    report = dict(passed=True, ROM_sha256=sha(out/'candidate.nes'), parent_ROM_sha256=manifest['rom_sha256'],
                  source_changes=changes, changed_PRG_banks=banks, all_CHR_bytes_unchanged=True,
                  scope='Isolated source candidate; assembled differential and native verification pending.')
    (out/'source-proof.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
