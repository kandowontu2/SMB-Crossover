"""Prepare a private KB candidate for Bass's missing bottom-side contact."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'build/verification/bass-corner-kh'


def main():
    assert not O.exists()
    source = O / 'source'
    source.mkdir(parents=True)
    with zipfile.ZipFile(R / 'build/checkpoints/rygar-walk-kb/source.zip') as archive:
        archive.extractall(source)
    p = source / 'smb1base.cfg'
    text = p.read_text()
    old = '    ZELDA_WRAP_MEM:start=$c000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;'
    new = '''    BASS_CORNER_PREFIX:start=$a000, size=$0800, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;
    BASS_CORNER_MEM:start=$a800, size=$0400, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;
    BASS_CORNER_SUFFIX:start=$ac00, size=$1000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;
    ZELDA_WRAP_MEM:start=$dc00, size=$0400, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;'''
    assert text.count(old) == 1
    text = text.replace(old, new).replace('SEGMENTS {', 'SEGMENTS {\n    BASS_CORNER: load=BASS_CORNER_MEM, type=ro, optional=yes;')
    p.write_text(text)
    p = source / 'src/characters.s'
    text = p.read_text()
    old = '''.proc CrossoverSourceSideProbe
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne Native
  farcall SophiaSourceSideProbe, jmp
Native:
  jmp BlockBufferColli_Side
.endproc'''
    new = '''.proc CrossoverSourceSideProbe
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bcc Native
  farcall BassCornerSideDispatch, jmp
Native:
  jmp BlockBufferColli_Side
  .assert *-CrossoverSourceSideProbe=28,error,"Keep original resident side-query span"
.endproc'''
    assert text.count(old) == 1
    p.write_text(text.replace(old, new))
    p = source / 'src/entrypoint.s'
    p.write_text(p.read_text() + '\n.if ::ENABLE_CROSSOVER\n.include "bass_corner.s"\n.endif\n')
    p = source / 'src/bass_corner.s'
    p.write_text('''; Bass's ordinary standing side row sampled Y+12 and Y+24, missing
; the bottom seven pixels of his source body (bottom=Y+32). Retain every
; original query first, then sample the last interior pixel when it was empty.
; This fixes that coverage hole; it does not replace source corner calcAxis.
; No temporary player relocation, new state, velocity bypass or tile mutation.
.pushseg
.segment "BASS_CORNER"
.proc BassCornerSideDispatch
  cmp #CHARACTER_SOPHIA
  beq Sophia
  cmp #CHARACTER_BASS
  bne Native
  cpy #34                       ; standing left lower sample
  beq Lower
  cpy #36                       ; standing right lower sample
  bne Native
Lower:
  jsr BlockBufferColli_Side
  bne Done                      ; all prior contacts keep the original ABI
  ; Do not wrap a query through the HUD or bottom of the visible buffers.
  lda Player_Y_HighPos
  cmp #1
  bne Empty
  lda MmYFraction
  ora MmYFraction+1
  cmp #1
  lda Player_Y_Position
  adc #31                       ; ceil(Y+32)-1, retaining Q8.16 fraction
  bcs Empty
  cmp #32
  bcc Empty
  cmp #240
  bcs Empty
  and #$f0
  sec
  sbc #32
  cmp R2
  beq Empty                     ; same row was already read
  sta R2
  tay
  lda (R6),y                    ; original query's genuine X column/pointer
  sta R3
  ldy Local_eb                  ; restore original lower-probe Y, not tile row
  iny
Done:
  rts
Empty:
  lda #0
  rts
Sophia:
  farcall SophiaSourceSideProbe, jmp
Native:
  jmp BlockBufferColli_Side
.endproc
.assert * <= $ac00,error,"Bass corner exceeds its reserved cold page"
.popseg
''')
    report = dict(status='PRIVATE_CANDIDATE_NOT_ADOPTED', checkpoint='rygar-walk-kb',
                  changes=['smb1base.cfg', 'src/characters.s', 'src/entrypoint.s', 'src/bass_corner.s'],
                  scope='Additional ordinary Bass standing lower-side cell only; native integer X quantization retained. Not full source calcAxis or all pose parity.',
                  game_installed=False, goal_complete=False)
    (O / 'candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    print(source)


if __name__ == '__main__':
    main()
