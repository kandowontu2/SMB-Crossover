"""Keep Prince's original running-jump floor rule while repairing walk-off.

The complete WorldMaterial source is rebuilt inside its existing 449-byte
envelope. Only action4 keeps the original coarse same-tile floor threshold.
No loader, private-worker, state, metadata or external entry changes occur.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import struct

import build_prince_worldmaterial_research_1114 as World
import prince_prepare_funding_research_1114 as Funding
import compose_prince_walkoff_1126 as Previous


Pipe, H = Previous.Pipe, Previous.H
PARENT = '2b4f9ad02f0cc0460927c3181095b978a0777ce4eff24fd167802ae3cb6fafa7'
CANDIDATE = None
START, END = 0xBDE2, 0xBFA3


def workers(*, idle=False, neutral_pipe=False):
    if neutral_pipe:
        idle = True
    text = World.SOURCE.read_text()
    assert text.count(Funding.FIRST_FOOT) == 1
    text = text.replace(Funding.FIRST_FOOT, ' jsr FirstFoot')
    _, symbols = World.Old.source()
    symbols['FirstFoot'] = 0xC5E9
    original, _, _ = World.assemble(text, symbols)
    # A jump in progress retains exactly the original threshold. Other
    # current-row ordinary actions test the existing physical feet at the
    # surface itself, including the unprojected Foot==Top case. The final
    # CMP always supplies C0 when FirstFoot executes, preserving sourceX-6.
    before = ''' lda Top
 ora #15
 cmp Foot
 bcs KeepTop'''
    after = ''' lda Top
 ldx $c616
 cpx #4
 beq RunningJumpThreshold
 sec
 sbc #1
 jmp HeightThresholdReady
RunningJumpThreshold:
 ora #15
HeightThresholdReady:
 cmp Foot
 bcs KeepTop'''
    if idle:
        after = ''' lda Top
 ldx $c616
 bne OriginalFloorThreshold
 ldx $dc
 bne OriginalFloorThreshold
 cmp #208
 bcs OriginalFloorThreshold
 sec
 sbc #1
 bcs HeightThresholdReady
OriginalFloorThreshold:
 ora #15
HeightThresholdReady:
 cmp Foot
 bcs KeepTop'''
    if neutral_pipe:
        # The positive floor point's raw tile is retained in otherwise-dead
        # Y. Within the newly affected same tile, a pipe cap query is also
        # the real top row. Shaft/deeper points retain the old threshold.
        after = ''' ldx Top
 lda $dc
 bne OriginalPipeThreshold
 tya
 and #$fc
 cmp #$10
 bne OriginalPipeThreshold
 txa
 sbc #1
 bcs HeightThresholdReady
OriginalPipeThreshold:
 txa
 ora #15
HeightThresholdReady:
 cmp Foot
 bcs KeepTop'''
    assert text.count(before) == 1
    text = text.replace(before, after)
    if idle:
        before = '''Scan:
 cpy ScanEnd+1
 bcc InScan
 bne NextColumn
 cpx ScanEnd
 bcc InScan
 bne NextColumn
InScan:'''
        after = '''Scan:
 cpy ScanEnd+1
 bcc InScan
 bne EndScannedColumn
 cpx ScanEnd
 bcc InScan
 beq InScan
EndScannedColumn:
 jmp NextColumn
InScan:'''
        assert text.count(before) == 1
        text = text.replace(before, after)
    if idle:
        # A positive point immediately above Top means Top>=48. Subtracting
        # 16 therefore cannot borrow, so this branch is an unconditional JMP
        # replacement inside the bounded native top-row domain.
        before = ' sbc #16\n sta Top\n jmp TopLoop'
        after = ' sbc #16\n sta Top\n bcs TopLoop'
        assert text.count(before) == 1
        text = text.replace(before, after)
    # Equivalent unsigned range test; all following paths reload A and
    # recompute flags before consuming either value.
    before = ''' lda $c618
 cmp #3
 beq Falling
 cmp #4
 bne Ready'''
    after = ''' lda $c618
 sec
 sbc #3
 cmp #2
 bcs Ready'''
    assert text.count(before) == 1
    text = text.replace(before, after)
    # Make empty scans loop close to their branch and allow a found floor
    # to fall through to NextColumn. Both leave the original scan registers
    # and PointRead carry contract intact.
    first = text.index('AdvanceScan:')
    last = text.index('NextColumn:', first)
    advance = text[first:last]
    text = text[:first] + text[last:]
    marker = ' jsr PpHostReadPoint\n bcc AdvanceScan\n txa'
    assert text.count(marker) == 1
    text = text.replace(marker, ' jsr PpHostReadPoint\n bcs NativeFloorFound\n'
                        + advance + 'NativeFloorFound:\n txa')
    if neutral_pipe:
        assert text.count('NativeFloorFound:\n txa') == 1
        text = text.replace('NativeFloorFound:\n txa', 'NativeFloorFound:\n tay\n txa')
    assert text.count('Found:\n jmp NextColumn\nNextColumn:') == 1
    text = text.replace('Found:\n jmp NextColumn\nNextColumn:', 'Found:\nNextColumn:')
    # X is dead after Decide and restored from the entry stack. Reuse it
    # for the BestTop+1 sentinel instead of loading that sentinel twice.
    before = ''' lda BestTop
 eor #$ff
 beq TestWall'''
    after = ''' ldx BestTop
 inx
 beq TestWall'''
    assert text.count(before) == 1
    text = text.replace(before, after)
    before = '''TestFloor:
 lda BestTop
 eor #$ff
 beq SaveMaterial
SolidFloor:
 lda BestTop
 sta Baseline'''
    after = '''TestFloor:
 txa
 beq SaveMaterial
SolidFloor:
 dex
 stx Baseline'''
    assert text.count(before) == 1
    text = text.replace(before, after)
    current, labels, _ = World.assemble(text, symbols)
    assert len(current) <= END - START, len(current)
    return original.ljust(END - START, b'\xea'), current.ljust(END - START, b'\xea'), labels


def transform(raw, reverse=False, *, idle=False, neutral_pipe=False):
    parts, rows, _, _ = Pipe.extract(raw)
    core, metadata, state, private = parts
    old, new, _ = workers(idle=idle, neutral_pipe=neutral_pipe)
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
    if CANDIDATE:
        assert H(image) == CANDIDATE
    assert transform(image, reverse=True) == raw
    return image


def inverse(image):
    raw = transform(image, reverse=True)
    assert H(raw) == PARENT
    return raw


def static_extents(raw):
    (core, _, _, _), _, _, _ = Pipe.extract(raw)
    return ((3, START - 0xA000, core[START - 0xA000:END - 0xA000]),)


def check(raw, image):
    proof = Previous.check(raw, image)
    counts = Counter()
    for layout in ('cap', 'brick', 'flat', 'covered'):
        for top in (112, 144, 160, 176, 208):
            for foot_delta in (0, 1, 2, 3, 15, 16, 20):
                for x in (721, 724, 746, 765, 766, 770, 777):
                    for mode in (1, 3, 4, 255):
                        before, after = (Previous.invoke(Previous.fixture(rom, layout=layout, x=x,
                                                       top=top, foot=top + foot_delta, action=4, mode=mode))
                                         for rom in (raw, image))
                        assert before == after, (layout, top, foot_delta, x, mode, before, after)
                        counts['original_action4_returns_exact'] += 1
    proof['running_jump_exemption'] = dict(counts)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    image = compose(raw)
    proof = check(raw, image)
    old, new, labels = workers()
    proof.update(parent_SHA256=H(raw), candidate_SHA256=H(image), inverse_exact=True,
                 envelope=[START, END], envelope_bytes=len(new),
                 source_SHA256=H(Path(__file__).read_bytes()),
                 jump_threshold=labels['RunningJumpThreshold'],
                 native_run=False, installed=False, generated_files=2)
    args.output.mkdir(exist_ok=True)
    (args.output / 'candidate-narrow.nes').write_bytes(image)
    (args.output / 'receipt-narrow.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k not in ('examples', 'third_edge_primitive')}), flush=True)


if __name__ == '__main__':
    main()
