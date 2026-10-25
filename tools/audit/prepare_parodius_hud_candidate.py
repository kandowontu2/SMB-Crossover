"""Build an isolated MMC5 graphical Parodius-bar candidate from native masks."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load, address

ROOT = Path(__file__).resolve().parents[2]
HUD = '''
 ; All seven original frame/label cells fit inside the TV-safe28-column row.
 ; Like the Gradius HUD, renew font ownership even while its cells are clean.
 lda DisableScreenFlag
 jne GraphicalDone
 lda VvVariant
 clc
 adc #.lobyte(395)
 sta InvHudPhysical
 lda #.hibyte(396)
 sta X5HudChrUpper
 lda InvHudActive
 bne FontActive
 inc ReloadCHRBank
FontActive:
 lda #1
 sta InvHudActive
 lda VvHudDirty
 jeq GraphicalDone
 ldx VRAM_Buffer1_Offset
 cpx #40                    ;42-byte append and terminator fit84-byte queue.
 jcs GraphicalDone
 lda #$20
 sta VRAM_Buffer1,x
 lda #$22                   ;row1, columns2..29: sixteen-pixel side margins.
 sta VRAM_Buffer1+1,x
 lda #28
 sta VRAM_Buffer1+2,x
 lda VvVariant
 sec
 sbc #1
 tay
 lda GraphicalOffsets,y
 tay
 lda #28
 sta VvTemp2
GraphicalCells:
 lda PnHudCells,y
 sta VRAM_Buffer1+3,x
 iny
 inx
 dec VvTemp2
 bne GraphicalCells
 inx
 inx
 inx
 lda #$23
 sta VRAM_Buffer1,x
 lda #$c0
 sta VRAM_Buffer1+1,x
 lda #8
 sta VRAM_Buffer1+2,x
 txa
 clc
 adc #3
 tax
 lda #1
 sta VvTemp
 ldy #8
GraphicalAttributes:
 lda #$aa
 sta VvTemp2
 ; A cell starts two tiles into an attribute byte. Highlight its right
 ; quadrant here and the next byte's left quadrant, covering all32pixels.
 lda VvTemp
 and VvMeter
 beq RightNormal
 lda #$a6
 sta VvTemp2
RightNormal:
 lda VvTemp
 lsr
 and VvMeter
 beq LeftNormal
 lda VvTemp2
 and #$fc
 ora #1
 sta VvTemp2
LeftNormal:
 lda VvTemp2
 sta VRAM_Buffer1,x
 inx
 asl VvTemp
 dey
 bne GraphicalAttributes
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta VvHudDirty
GraphicalDone:
 rts
GraphicalOffsets:.byte 0,28,56
.include "parodius_hud.inc"
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for n in ['art', 'parent', 'output']:
        parser.add_argument('--' + n, type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    art = json.loads((args.art / 'manifest.json').read_text())
    assert art['prepared'] and not art['integrated'] and art['chr_bytes'] == 3072
    source = out / 'source'
    (source / 'src').mkdir(parents=True)
    (source / 'chr/characters').mkdir(parents=True)
    raw = (ROOT / 'src/parodius_render.s').read_text()
    start = raw.index('.proc PnHud\n') + len('.proc PnHud\n')
    end = raw.index('.endproc', start)
    raw = raw[:start] + '.if ::MAPPER_MMC5\n' + HUD + '.else\n' + raw[start:end] + '.endif\n' + raw[end:]
    (source / 'src/parodius_render.s').write_text(raw)
    raw = (ROOT / 'src/parodius.s').read_text()
    raw += '\n.pushseg\n.segment "PN_HUD_CHR"\n.incbin "chr/characters/parodius-hud.chr"\n.popseg\n'
    (source / 'src/parodius.s').write_text(raw)
    # Nested includes prefer their own file's directory. Stage the unchanged
    # parent too, so it reaches the candidate Parodius component, not ROOT's.
    shutil.copy2(ROOT / 'src/vic_viper.s', source / 'src')
    shutil.copy2(args.art / 'parodius_hud.inc', source / 'src')
    shutil.copy2(args.art / 'parodius-hud.chr', source / 'chr/characters')
    cfg = (ROOT / 'smb1base-mmc5-expanded.cfg').read_text()
    anchor = '    Z2_UI_CHR:load=VIC_CHR_MEM,type=ro,start=$62c00;'
    assert cfg.count(anchor) == 1
    cfg = cfg.replace(anchor, anchor + '\n    PN_HUD_CHR:load=VIC_CHR_MEM,type=ro,start=$63000; # Pages396..398; before Chip412.')
    (source / 'smb1base-mmc5-expanded.cfg').write_text(cfg)
    rom = out / 'candidate.nes'
    with (out / 'host-build.log').open('w') as log:
        result = subprocess.run([sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
                                 '--source-overlay', str(source), '--output', str(rom)],
                                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    assert result.returncode == 0, (out / 'host-build.log').read_text()[-3000:]
    old, new = load(args.parent), load(rom)
    assert len(old['raw']) == len(new['raw']) == 2097168
    chr_start = 16 + 1048576 + 396*1024
    assert old['raw'][chr_start:chr_start+3072] == bytes(3072)
    assert new['raw'][chr_start:chr_start+3072] == (args.art / 'parodius-hud.chr').read_bytes()
    assert old['raw'][16+1048576:chr_start] == new['raw'][16+1048576:chr_start]
    assert old['raw'][chr_start+3072:] == new['raw'][chr_start+3072:]
    for n, s in old['syms'].items():
        if 'seg' in s and address(old, n) < 0x8000:
            assert address(old, n) == address(new, n), n
    changes = [i for i, (a, b) in enumerate(zip(old['raw'], new['raw'])) if a != b]
    report = dict(compiled=True, adopted=False, goal_complete=False, ROM_sha256=sha(rom),
                  parent_ROM_sha256=sha(args.parent), new_font_pages=[396, 397, 398],
                  original_other_CHR_exact=True, existing_RAM_addresses_exact=True,
                  changed_PRG_banks=sorted(set((i-16)//8192 for i in changes if i < 16+1048576)),
                  art_manifest_sha256=sha(args.art / 'manifest.json'),
                  changed_source={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()},
                  scope='Private MMC5 seven-cell native graphical Parodius bars and full32px attribute cursor. Fonts are refreshed without per-frame VRAM redraw; queue guard retained. MMC3 keeps its prior text fallback until its background-font upload ownership is implemented. No gameplay, weapons, global palette, RAM or existing other-character graphics changes. Native pixels/cursor/boundaries/entry/exit/lag-CHR tests pending; no adoption.')
    (out / 'build-proof.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
