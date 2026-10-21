"""Retain Sophia's source brick-none and non-ground coin head dispatch."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-sophia-source-terrain-if'
D = V / 'root49-sophia-source-terrain-ij'
S = D / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def edit(n, a, b):
    p = S / n
    raw = p.read_bytes()
    eol = '\r\n' if b'\r\n' in raw else '\n'
    a, b = (x.replace('\n', eol).encode() for x in (a, b))
    assert raw.count(a) == 1, (n, a[:70])
    p.write_bytes(raw.replace(a, b))


def main():
    assert not D.exists()
    prior = json.loads((P / 'preparation.json').read_text())
    for n, h in prior['source_sha256'].items():
        assert sha(P / 'source' / n) == h, n
        p = S / n
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(P / 'source' / n, p)
    shutil.copytree(P / 'source/build/generated', S / 'build/generated')

    # In a disabled build these resident guest helpers do not exist. Preserve
    # the original native side calls in that configuration, as for head calls.
    p = S / 'src/collision.s'
    raw = p.read_bytes()
    eol = b'\r\n' if b'\r\n' in raw else b'\n'
    a = b'  jsr CrossoverSourceSideProbe'
    assert raw.count(a) == 2
    b = eol.join((b'.if ::ENABLE_CROSSOVER', a, b'.else',
                  b'  jsr BlockBufferColli_Side', b'.endif'))
    p.write_bytes(raw.replace(a, b))

    # Coins use pickup dispatch even though their native attribute includes
    # SOLID. Hidden blocks are not Ground for BRICK_NONE (source groundAbove).
    edit('src/sophia_source_terrain.s',
         '  beq Next\n  tax\n  lda MTileAttribute,x',
         '''  beq Next
  cmp #$c2
  jeq ReturnTile
  cmp #$c3
  jeq ReturnTile
  cmp #$5f
  beq Hidden
  cmp #$60
  bne Solid
Hidden:
  jsr SophiaSourceBrickEffectGate
  beq Next
Solid:
  ldx R3
  lda MTileAttribute,x''')
    edit('src/sophia_source_terrain.s',
         '''  lda #4
  sta R4                       ; source has no native origin-nibble head gap.''',
         '''  ; The real query remains in R3/R6/R7. R4 only gates native block
  ; effects: BRICK_NONE skips them while retaining canonical solid contact.
  jsr SophiaSourceBrickEffectGate
  sta R4''')
    edit('src/sophia_source_terrain.s',
         '.proc SophiaSourceHeadProbe',
         '''; Sophia.checkState: hover always has BRICK_NONE; underwater has it
; outside jumpRise (classic is false in the represented source mode). This
; gate returns the native admission nibble, without changing tile or velocity.
.proc SophiaSourceBrickEffectGate
  lda XgHoverActive
  bne None
  lda MmUnderwater
  beq Bounce
  lda XgRise
  beq None
Bounce:
  lda #4
  rts
None:
  lda #0
  rts
.endproc

.proc SophiaSourceHeadProbe''')

    driver = (P / 'build-driver.py').read_text()
    assert driver.count(repr(str(P / 'source'))) == 1
    (D / 'build-driver.py').write_text(driver.replace(repr(str(P / 'source')), repr(str(S))))
    record = dict(prior)
    record.update(
        status='PRIVATE_TERRAIN_BRICK_NONE_COIN_CORRECTION_PREPARED',
        parent_IF_sha256=sha(P / 'preparation.json'),
        source_sha256={n: sha(S / n) for n in prior['source_sha256']},
        script_sha256=sha(__file__),
        correction='Full native IF caller established hover block effects and C2/C3 false ceiling. Gate effects with source BRICK_NONE, skip invisible blocks in that state, and preserve coin dispatch before solid-axis response. Also guard side helper calls in disabled builds; crossover bytes must remain identical for those guards.',
        source_bindings={
            n: sha(R / n) for n in (
                'reference/crossover2/extracted/scripts/com/smbc/characters/Sophia.as',
                'reference/crossover2/extracted/scripts/com/smbc/ground/Brick.as')},
        scope=prior['scope'] + ' Classic flag is not modeled; this gate represents classic=false source behavior.',
        main_changed=False)
    (D / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(status=record['status'], sources=len(record['source_sha256']))))


if __name__ == '__main__':
    main()
