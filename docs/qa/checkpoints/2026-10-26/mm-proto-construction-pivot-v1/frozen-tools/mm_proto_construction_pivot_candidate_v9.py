"""Private foreground pivot and equivalently translated native Vine experiment."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import traceback
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'root-current-roster-composition-v1'
EXPECTED = '3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def edit(path, old, new):
    raw = path.read_bytes()
    newline = '\r\n' if b'\r\n' in raw else '\n'
    old, new = (text.replace('\n', newline).encode() for text in (old, new))
    assert raw.count(old) == 1, (str(path), old)
    path.write_bytes(raw.replace(old, new))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(R)
    out.mkdir(parents=True, exist_ok=False)
    try:
        assert sha(P / 'candidate.nes') == EXPECTED
        manifest = json.loads((P / 'source-manifest.json').read_text())
        source = out / 'source'
        for relative, expected in manifest.items():
            old, dest = P / 'source' / relative, source / relative
            assert sha(old) == expected, relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(old, dest)
        rom = (P / 'candidate.nes').read_bytes()
        for bank, start, end in [(4, 0xbf33, 0xbf8b), (66, 0xb9c0, 0xbb50)]:
            region = rom[16 + bank * 8192 + start % 8192:16 + bank * 8192 + end % 8192] if end < 0xc000 else rom[16 + bank * 8192 + start % 8192:16 + (bank + 1) * 8192]
            assert region == bytes([255]) * (end - start), (bank, hex(start), hex(end))
        engine = source / 'src/metasprite_engine.s'
        edit(engine, '''  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq RotateGuestOAM
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lda #0
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
RotateGuestOAM:''', '''.if ::ENABLE_MMC5_EXPANDED
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lsr
  bcc MmPivotNonMega
  jmp MmConstructionPivotBegin
MmPivotNonMega:
  lsr
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
.else
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq RotateGuestOAM
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lda #0
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
.endif
RotateGuestOAM:''')
        edit(engine, '  ; Give weapons the first OAM slots.', '''.if ::ENABLE_MMC5_EXPANDED
::MmConstructionPivotClear:
.endif
  ; Give weapons the first OAM slots.''')
        edit(engine, '''  sta Sprite_Y_Position,x
  cpx #0
  bne ClearPlayerOAM

InitObjectLoop:''', '''  sta Sprite_Y_Position,x
.if !::ENABLE_MMC5_EXPANDED
  cpx #0
.endif
  bne ClearPlayerOAM
.if ::ENABLE_MMC5_EXPANDED
  sec                         ; DEX already owns final NZ, original CPX0 owns C.
  nop                         ; Preserve the following genuine resident PCs.
.endif

InitObjectLoop:''')
        edit(engine, '''    lda GuestOamRotationActive
    beq LegacyTailClear
      ; The full ring was hidden at entry; no linear tail clear is needed.
      pla''', '''    lda GuestOamRotationActive
    beq LegacyTailClear
.if ::ENABLE_MMC5_EXPANDED
    lsr                         ; Original1 ->0; encoded delta|1 remains nonzero.
    bne MmConstructionPivotExitBranch
.endif
      ; The full ring was hidden at entry; no linear tail clear is needed.
::MmConstructionPivotRosterTail:
      pla''')
        edit(engine, ''' .res 17,$ea
::WorldFirebarAdmissionDone:
 rts
 .assert *-WorldFirebarDrawAdmission=39,lderror,"Late world admission span"''', '''.if ::ENABLE_MMC5_EXPANDED
::MmConstructionPivotExitBranch:
 jmp MmConstructionPivotExit
 .res 10,$ea
.else
 .res 17,$ea
.endif
::WorldFirebarAdmissionDone:
 rts
.if ::ENABLE_MMC5_EXPANDED
 .assert *-WorldFirebarDrawAdmission=35,lderror,"Pivot resident span"
.else
 .assert *-WorldFirebarDrawAdmission=39,lderror,"Late world admission span"
.endif''')
        weapons = source / 'src/megaman_weapons.s'
        edit(weapons, '''  .res 110,$ea
  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"''', '''::MmConstructionPivotBegin:
  lda #1
  sta GuestOamRotationActive
  farcall KbOamPriority
  lda SpriteShuffleOffset
  lsr
  bcs PivotNative
  jsr MmConstructionPivotActive
  bcc PivotNative
  lda RgOamFirst
  sec
  sbc RgOamPlayerStart         ; Delta from native rotation to previous body pivot.
  beq PivotNative
  tax
  clc
  adc #40                    ; Native partial writers start40; maximum is five lifts +two Vine groups.
  cmp #89
  bcs PivotNative            ; Keep the maximum168-byte native partial span contiguous.
  txa
  ora #1
  sta GuestOamRotationActive ; Existing boolean owner: aligned delta in bits2..7.
  lda RgOamPlayerStart
  eor #$ff
  clc
  adc #1
  sta RgOamRotation
PivotNative:
  jmp MmConstructionPivotClear
::MmConstructionPivotExit:
  lda CurrentOAMOffset
  cmp RgOamPlayerStart
  bne PivotBodyEmitted
  jmp MmConstructionPivotRejected
PivotBodyEmitted:
  lda RgOamRotation
  sec
  sbc GuestOamRotationActive
  clc
  adc #1
  sta RgOamRotation          ; Original rotation restored, encoded image tag stays.
  lda CurrentOAMOffset
  clc
  adc RgOamRotation
  tax                       ; A already equals exact original physical return X.
  sec
  sbc RgOamRotation          ; Exact original last SBC V, including128/0.
  jmp MmConstructionPivotRosterTail
  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"''')
        # Clone only the original cold native leaf. The source remains present
        # at its genuine old entry; the one DrawVine farcall uses this copy.
        native_text = (source / 'src/ryu_platform.s').read_text()
        body = native_text.split('.proc RyuPlatformOriginalDrawVine\n', 1)[1].split('\n.endproc', 1)[0]
        assert body.count('  ldx Vine_ObjOffset,y') == 1
        body = body.replace('  ldx Vine_ObjOffset,y        ;get offset to vine\n', '')
        begin = body.index('  ldx #$00                   ;start with the first sprite again')
        end = body.index('  ldy R0                     ;return offset set earlier', begin)
        clip = '''.repeat 6,I
  lda Vine_Start_Y_Position
  sec
  sbc Sprite_Y_Position,y
  cmp #$64
  bcc :+
    lda #$f8
    sta Sprite_Y_Position,y
  :
  .if I<>5
    iny
    iny
    iny
    iny
  .endif
.endrepeat
  ldx #6
  sec                        ; Exact final CPX6 C; LDY R0 restores native NZ.
'''
        body = body[:begin] + clip + body[end:]
        extra = '''
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "MM_CONSTRUCTION_ACTIVE"
.proc MmConstructionPivotActive
  lda OperMode
  eor #1
  ora MmDeathFlag
  bne No
  lda OperMode_Task
  cmp #3
  bne No
  lda GameEngineSubroutine
  cmp #8
  bne No
  lda ObjectMetasprite
  beq No
  lda ObjectVerticalFlip
  bmi No
  sec
  rts
No:
  clc
  rts
.endproc
.proc MmConstructionPivotRejected
  php                        ; Preserve original header rejection V and X.
  lda RgOamRotation
  sec
  sbc GuestOamRotationActive
  clc
  adc #1
  sta RgOamRotation
  plp
  jmp MmConstructionPivotRosterTail
.endproc
.proc MmConstructionPivotClearTag
  ldy #0
  sty CurrentOAMOffset
  lda GuestOamRotationActive
  and #1
  sta GuestOamRotationActive
  lda #$f8
  jmp OAMClear
.endproc
.segment "MM_CONSTRUCTION_VINE"
.proc MmConstructionVine
  lda GuestOamRotationActive
  and #$fc
  beq Native
  lda CurrentOAMOffset
  clc
  adc GuestOamRotationActive
  sec
  sbc #1
  sta CurrentOAMOffset
  jsr Body
  php
  pha
  lda CurrentOAMOffset
  sec
  sbc GuestOamRotationActive
  clc
  adc #1
  sta CurrentOAMOffset
  lda R2
  sec
  sbc GuestOamRotationActive
  clc
  adc #1
  sta R2
  pla
  plp
  rts
Native:
  jmp Body
Body:
''' + body + '''
.endproc
.proc MmConstructionSmallLift
  lda GuestOamRotationActive
  and #$fc
  beq Native
  lda CurrentOAMOffset
  clc
  adc GuestOamRotationActive
  sec
  sbc #1
  sta CurrentOAMOffset
  farcall CrossoverDrawSmallPlatform
  php
  pha
  tya
  pha
  lda CurrentOAMOffset
  sec
  sbc GuestOamRotationActive
  clc
  adc #1
  sta CurrentOAMOffset
  pla
  sec
  sbc GuestOamRotationActive
  clc
  adc #1
  tay
  pla
  plp
  rts
Native:
  farcall CrossoverDrawSmallPlatform
  rts
.endproc
.assert *-MmConstructionVine<=$190,error,"Vine/lift copies exceed genuine66 gap"
.popseg
.endif
'''
        raw = weapons.read_bytes()
        newline = '\r\n' if b'\r\n' in raw else '\n'
        weapons.write_bytes(raw + extra.replace('\n', newline).encode())
        vine = source / 'src/sprite_render.s'
        edit(vine, '  farcall RyuPlatformOriginalDrawVine\n', '''.if ::ENABLE_MMC5_EXPANDED
  farcall MmConstructionVine
.else
  farcall RyuPlatformOriginalDrawVine
.endif
''')
        # The remaining native partial writer uses the same retained image tag.
        # Its existing three resident dump calls are source-equivalent inline
        # stores, paying the added dispatch cost on all foreign paths.
        edit(vine, '  farcall CrossoverDrawSmallPlatform\n', '''.if ::ENABLE_MMC5_EXPANDED
  farcall MmConstructionSmallLift
.else
  farcall CrossoverDrawSmallPlatform
.endif
''')
        lift = source / 'src/level_variants.s'
        for count, comment in [(6, 'dump tile number into all six sprites'),
                               (6, 'dump attributes into all six sprites'),
                               (3, 'dump vertical coordinate into Y coordinates')]:
            oldline = ('       farcall DumpSixSpr              ;' + comment) if count == 6 else ('TopSP: farcall DumpThreeSpr            ;' + comment)
            newlines = ('TopSP:\n' if count == 3 else '') + '.if ::ENABLE_MMC5_EXPANDED\n'
            newlines += '\n'.join('       sta Sprite_Data+' + str(offset) + ',y' for offset in range((count - 1) * 4, -1, -4)) + '\n.else\n' + oldline.removeprefix('TopSP: ') + '\n.endif'
            edit(lift, oldline, newlines)
        edit(lift, 'ExSPl: ldx ObjectOffset            ;get enemy object offset and leave\n       rts\n\n.endproc', 'ExSPl: ldx ObjectOffset            ;get enemy object offset and leave\n       rts\n.if ::ENABLE_MMC5_EXPANDED\n       .res 9,$ea                  ; Retain the genuine leaf end.\n.endif\n\n.endproc')
        # Full replacement invalidates only the encoding; no NMI work is added.
        edit(engine, '''MoveAllSpritesOffscreen:
  ldy #0
  sty CurrentOAMOffset''', '''MoveAllSpritesOffscreen:
.if ::ENABLE_MMC5_EXPANDED
  jmp MmConstructionPivotClearTag
  .res 2,$ea
.else
  ldy #0
  sty CurrentOAMOffset
.endif''')
        cfg = source / 'smb1base-mmc5-expanded.cfg'
        edit(cfg, '    METASPRITE: load = PRGA_04, type = ro;\n', '''    METASPRITE: load = PRGA_04, type = ro;
    MM_CONSTRUCTION_ACTIVE: load=PRGA_04,type=ro,start=$bf33;
''')
        edit(cfg, '    MM_BASIC_REMAINDER: load=X5_NEW_42_TAIL,type=ro,start=$b9a8;\n', '''    MM_BASIC_REMAINDER: load=X5_NEW_42_TAIL,type=ro,start=$b9a8;
    MM_CONSTRUCTION_VINE: load=X5_NEW_42_TAIL,type=ro,start=$b9c0;
''')
        changed = [rel for rel, h in manifest.items() if sha(source / rel) != h]
        assert sorted(changed) == ['smb1base-mmc5-expanded.cfg', 'src/level_variants.s', 'src/megaman_weapons.s', 'src/metasprite_engine.s', 'src/sprite_render.s']
        (out / 'source-manifest.json').write_text(json.dumps({rel: sha(source / rel) for rel in manifest}, indent=2) + '\n')
        patch = []
        for rel in changed:
            patch += list(difflib.unified_diff((P / 'source' / rel).read_text().splitlines(True),
                          (source / rel).read_text().splitlines(True), fromfile='3b/' + rel, tofile='private/' + rel))
        (out / 'source.patch').write_text(''.join(patch))
        command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'),
                   '--workspace', str(source), '--compiler', str(R / 'tools/Windows/cc65/bin/cl65.exe'),
                   '--output', str(out / 'candidate.nes')]
        result = subprocess.run(command, cwd=source, capture_output=True, text=True)
        (out / 'build.json').write_text(json.dumps(dict(command=command, exit=result.returncode,
                                stdout=result.stdout, stderr=result.stderr), indent=2) + '\n')
        assert result.returncode == 0, result.stdout + result.stderr
        old, new = scoped_load(P / 'candidate.nes'), scoped_load(out / 'candidate.nes')
        labels = []
        old_labels, new_labels = qualified(P / 'candidate.nes'), qualified(out / 'candidate.nes')
        for name, value in old_labels.items():
            if name not in new_labels or new_labels[name] != value:
                labels.append(dict(name=name, old=value, new=new_labels.get(name)))
        newrom = (out / 'candidate.nes').read_bytes()
        delta = [i for i, (x, y) in enumerate(zip(rom, newrom)) if x != y]
        assert len(rom) == len(newrom)
        assert {int((i - 16) // 8192) for i in delta} <= {0, 4, 26, 66}
        assert all(i < 16 + 128 * 8192 for i in delta)
        proof = dict(built=True, source_only=True, qualified=False, native_launches=0,
                     parent_ROM_sha256=EXPECTED, ROM_sha256=sha(out / 'candidate.nes'),
                     source_files=len(manifest), changed_source=changed, changed_ROM_bytes=len(delta),
                     changed_banks=sorted({int((i - 16) // 8192) for i in delta}),
                     genuine_changed_old_labels=labels, new_RAM_allocations=0, NMI_code_changed=False,
                     MoveAll_foreground_code_cost=16, regular_foreign_draw_cost_unproved=True,
                     Vine_original_source_kept=True, original_clip_loop_unrolled_without_store_omission=True,
                     notes='Unqualified private candidate. Bool owner now encodes aligned whole-image delta|1; literal native turn and contiguity fallback. Normal original rotation restored at body exit. Vine copy translates source group addresses and restores logical cursor/R2/AXYP; full controls pending. No timing or fairness acceptance.',
                     tool_sha256=sha(__file__))
        (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
        print(json.dumps(proof, indent=2))
    except BaseException as error:
        (out / 'failure.json').write_text(json.dumps(dict(passed=False, error=repr(error),
               traceback=traceback.format_exc(), tool_sha256=sha(__file__)), indent=2) + '\n')
        (out / 'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    main()
