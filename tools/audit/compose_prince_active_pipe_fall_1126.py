"""Keep physical feet authoritative during active Prince pipe falls.

Retains fbc1 neutral behavior and grants the same pipe-only check to exact
actions7/17/49 with active input. Running jumps and grabs keep the old rule.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import struct

import compose_prince_idle_walkoff_1126 as Fallback


Narrow = Fallback.Narrow
World, Funding = Narrow.World, Narrow.Funding
Pipe, H, P = Fallback.Pipe, Fallback.H, Narrow.Previous
PARENT = Fallback.PARENT
FALLBACK = 'fbc1ebd24fb347afbf165c34df3e927b7a123c92fed9482219f96ee55bafa0d3'
CANDIDATE = '83b387931d2cf22981b6267fe062d246ba684d1bcb62e066d932dc9ae82aee40'
START, END = Narrow.START, Narrow.END


def replace(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after)


def workers():
    text = World.SOURCE.read_text()
    text = replace(text, Funding.FIRST_FOOT, ' jsr FirstFoot')
    _, symbols = World.Old.source()
    symbols['FirstFoot'] = 0xC5E9
    original, _, _ = World.assemble(text, symbols)
    text = replace(text, ''' lda #0
 sta Wall
 sta Sweep
 sta BestTop+1''', '''InitialWorldClear:
 stx Wall
 stx Sweep
 stx BestTop+1''')
    # Delivered Prepare has an explicit LDX0 immediately before its unchanged
    # final query-coordinate writes, so the three initial clears can use X.
    # All column query X values are Cell+24 then Cell+40, with Cell aligned32.
    # Thus the former (queryX&F0)+8 is exactly queryX, without a carry.
    first = text.index(' lda PpQueryX\n and #$f0\n')
    last = text.index(' sec\n sbc $c60f', first)
    # The positive Hand result already left C1; removing the ADD also makes
    # the following SEC redundant before the unchanged full-width subtract.
    text = text[:first] + 'AlignedWallCenter:\n lda PpQueryX\n' + text[last + len(' sec\n'):]
    # A found-floor path no longer consumes the scan registers. Keep Top in
    # PointRead-preserved X during the roof walk, committing it at TopDone.
    first = text.index(' txa\n and #$f0\n sta Top\nTopLoop:')
    last = text.index('TopDone:', first) + len('TopDone:')
    text = text[:first] + ''' txa
 and #$f0
 tax
TopLoop:
 cpx #33
 bcc TopDone
 txa
 sbc #1
 sta PpQueryY
 jsr PpHostReadPoint
 bcc TopDone
 txa
 sbc #16
 tax
 bcs TopLoop
TopDone:
 stx Top''' + text[last:]
    text = replace(text, ''' lda Top
 ora #15
 cmp Foot
 bcs KeepTop''', ''' ldx Top
 tya
 and #$fc
 cmp #$10
 bne OriginalPipeThreshold
 lda $dc
 beq PhysicalPipeThreshold
 lda $c616
 cmp #7
 beq PhysicalPipeThreshold
 and #$df
 cmp #17
 bne OriginalPipeThreshold
PhysicalPipeThreshold:
 ; Every admitted route leaves C1. Top>=32, so DEX cannot wrap or borrow.
 dex
 txa
 bcs HeightThresholdReady
OriginalPipeThreshold:
 txa
 ora #15
HeightThresholdReady:
 cmp Foot
 bcs KeepTop''')
    text = replace(text, '''Scan:
 cpy ScanEnd+1
 bcc InScan
 bne NextColumn
 cpx ScanEnd
 bcc InScan
 bne NextColumn
InScan:''', '''Scan:
 cpy ScanEnd+1
 bcc InScan
 bne EndScannedColumn
 cpx ScanEnd
 bcc InScan
 beq InScan
EndScannedColumn:
 jmp NextColumn
InScan:''')
    text = replace(text, ''' lda $c618
 cmp #3
 beq Falling
 cmp #4
 bne Ready''', ''' lda $c618
 sec
 sbc #3
 cmp #2
 bcs Ready''')
    first = text.index('AdvanceScan:')
    last = text.index('NextColumn:', first)
    advance = text[first:last]
    text = text[:first] + text[last:]
    text = replace(text, ' jsr PpHostReadPoint\n bcc AdvanceScan\n txa',
                   ' jsr PpHostReadPoint\n bcs NativeFloorFound\n' + advance
                   + 'NativeFloorFound:\n tay\n txa')
    text = replace(text, 'Found:\n jmp NextColumn\nNextColumn:', 'Found:\nNextColumn:')
    text = replace(text, ''' sta PpQueryX
 bcc Column
 inc PpQueryX+1
 jmp Column''', ''' sta PpQueryX
 bcc NextColumnNoCarry
 inc PpQueryX+1
NextColumnNoCarry:
 jmp Column''')
    text = replace(text, ''' lda BestTop
 eor #$ff
 beq TestWall''', ''' ldx BestTop
 inx
 beq TestWall''')
    text = replace(text, '''TestFloor:
 lda BestTop
 eor #$ff
 beq SaveMaterial
SolidFloor:
 lda BestTop
 sta Baseline''', '''TestFloor:
 txa
 beq SaveMaterial
SolidFloor:
 dex
 stx Baseline''')
    current, labels, _ = World.assemble(text, symbols)
    assert len(current) <= END - START, len(current)
    return original.ljust(END - START, b'\xea'), current.ljust(END - START, b'\xea'), labels


def transform(raw, reverse=False):
    parts, rows, _, _ = Pipe.extract(raw)
    core, metadata, state, private = parts
    old, new, _ = workers()
    before, after = (new, old) if reverse else (old, new)
    at = START - 0xA000
    assert core[at:END - 0xA000] == before
    core = core[:at] + after + core[END - 0xA000:]
    chunks = core, metadata, state, private
    extra = Pipe.Packet.CHR + Pipe.PAGE * 1024
    carrier = Pipe.Cold._backing(raw) + raw[extra:extra + 1024]
    packed, _ = Pipe.split_packed(carrier, Pipe.HEAD + 2, rows)
    packed[0] = Pipe.Packet.encode(core)
    config = list(rows)
    config[0] = rows[0][:2] + (len(packed[0]), len(core))
    assert len(packed[0]) <= 0xDC00 - Pipe.Cold.WRAP
    header = bytearray(carrier[:Pipe.HEAD + 2])
    struct.pack_into('<16H', header, Pipe.TABLE - 32, *(v for row in config for v in row))
    image, cookie, used = Pipe.write_packet(raw, header, chunks, packed, Pipe.PAGES)
    assert Pipe.extract(image) == (chunks, tuple(config), cookie, used)
    return image


def compose(raw):
    assert H(raw) == PARENT
    image = transform(raw)
    assert H(image) == CANDIDATE
    assert transform(image, reverse=True) == raw
    return image


def inverse(image):
    assert H(image) == CANDIDATE
    raw = transform(image, reverse=True)
    assert H(raw) == PARENT
    return raw


static_extents = Fallback.static_extents


def check(raw, baseline, image):
    assert H(baseline) == FALLBACK
    counts = Counter()
    for action in range(256):
        for mode in (0, 3, 4, 255):
            for input_bits in (0, 10):
                for x in (724, 765, 770):
                    outputs = []
                    for rom in (baseline, image):
                        memory = P.fixture(rom, x=x, action=action, mode=mode)
                        memory[0xDC] = input_bits
                        outputs.append(P.invoke(memory))
                    before, after = outputs
                    counts['all_actions'] += 1
                    if input_bits == 0 or action not in (7, 17, 49):
                        assert before == after, (action, mode, input_bits, x, outputs)
                        counts['neutral_and_other_active_actions_exact'] += 1
                    elif before['material'] != after['material']:
                        assert x == 770 and [q['material'] for q in outputs] == [1, 0]
                        counts['active_false_pipe_support_removed'] += 1
                    else:
                        assert before['registers'] == after['registers']
                        assert before['surface'] == after['surface']
    for layout in ('brick', 'flat', 'covered'):
        for action in (0, 1, 3, 4, 7, 17, 28, 49):
            for input_bits in (0, 1, 8, 10, 128, 255):
                for top in (112, 144, 160, 176, 208):
                    for delta in (0, 1, 3, 15, 16, 20):
                        outputs = []
                        for rom in (baseline, image):
                            memory = P.fixture(rom, layout=layout, action=action, mode=3,
                                               top=top, foot=top+delta)
                            memory[0xDC] = input_bits
                            outputs.append(P.invoke(memory))
                        assert outputs[0] == outputs[1], (layout, action, input_bits, top, delta, outputs)
                        counts['nonpipe_returns_exact'] += 1
    targets = []
    for left, top, x in ((608, 160, 649), (736, 144, 770)):
        for action in (7, 17, 49):
            for delta in (0, 1, 3, 9, 15):
                outputs = []
                for rom in (baseline, image):
                    memory = P.fixture(rom, left=left, top=top, x=x, action=action, mode=3,
                                       foot=top+delta, query=left)
                    memory[0xDC] = 10
                    outputs.append(P.invoke(memory))
                assert [q['material'] for q in outputs] == [1, 0], (left, action, delta, outputs)
                targets.append(dict(left=left, top=top, x=x, action=action, foot=top+delta,
                                    input=10, before=outputs[0], after=outputs[1]))
    return dict(counts=dict(counts), targets=targets,
                scope='Seeded CPU WorldMaterial fixtures; static contextual tile filter identity; no native route/IRQ/Mesen claim')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output == (Pipe.Packet.R / 'build/prince-walkoff-1126').resolve()
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    raw = Fallback.inverse(installed) if H(installed) == FALLBACK else installed
    if H(raw) == CANDIDATE:
        raw = inverse(raw)
    baseline = Fallback.compose(raw)
    assert H(baseline) == FALLBACK
    image = compose(raw)
    proof = check(raw, baseline, image)
    proof.update(parent_SHA256=H(raw), fallback_SHA256=H(baseline), candidate_SHA256=H(image),
                 inverse_exact=True, fallback_inverse_exact=Fallback.inverse(baseline)==raw,
                 source_SHA256=H(Path(__file__).read_bytes()),
                 envelope=[START, END], generated_files=2, native_run=False, installed=False)
    (output / 'candidate-idle.nes').write_bytes(image)
    (output / 'receipt-idle.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k:v for k,v in proof.items() if k != 'targets'}), flush=True)


if __name__ == '__main__':
    main()
