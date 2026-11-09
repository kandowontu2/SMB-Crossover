"""Skip duplicate native small-player side probes for Mini's exact BG guard."""
import argparse
import itertools
import json
from pathlib import Path

from prepare_mini_fireball_art_1108 import assemble, patch
from prepare_mini_mario_native_power_1103_v56 import N, address, bundle, location
from prepare_selected_native_packet_v1 import R, sha

BASE = R/'build/mini-fireball-gbc-1108/candidate.nes'
PIN = 'fc7d4554fed204e8efa4c4489ee70cd5c6529ce95e0d606ffee1cda525188ec5'
SOURCE = R/'tools/reference/mini_mario_empty_draw.s'
BANK = 20


def assert_source_offsets(b):
    for name, expected in [('BlockBuffer_X_Adder',[2,2,13,13]),
                           ('BlockBuffer_Y_Adder',[24,24,24,24])]:
        offset = location(b,name)+17
        assert b['raw'][offset:offset+4] == bytes(expected), name


def invoke_span(image, name, pc):
    image['segs']['mini_bg20'] = dict(start=str(0xa000),ooffs=str(16+BANK*8192))
    image['syms'][name] = dict(val=str(pc),seg='mini_bg20')


def new_code(output, original):
    source = SOURCE.read_text()
    exit_code = source.split('.segment "BG_SIDES"\n',1)[1].split('.segment ',1)[0]
    sides = source.rsplit('.segment "BG_SIDES"\n',1)[1]
    common = '.setcpu "6502"\n.export BackgroundHeight, ProbeSides\nTileInert=$bd5e\n.segment "SIDE"\n'
    config = 'MEMORY{C:start=$becc,size=52,file=%O;}SEGMENTS{SIDE:load=C,type=ro;}'
    old = common+exit_code+sides
    assert old.count(' ldx #0\n lda #0\n sec') == 1 and old.count(' iny\n cpy #21') == 1
    new = old.replace(' ldx #0\n lda #0\n sec',' ldx #0\n txa\n sec').replace(' iny\n cpy #21',' iny\n iny\n cpy #21')
    records = []
    for name,text in [('original',old),('deduplicated',new)]:
        asm = output/(name+'.s')
        asm.write_text(text,encoding='utf-8')
        obj = asm.with_suffix('.bin')
        symbols = assemble(asm,config,obj)
        records.append((obj.read_bytes(),symbols))
    (before,old_labels),(after,new_labels) = records
    raw = bytearray(original)
    at = lambda pc:16+BANK*8192+(pc&8191)
    patch(raw,at(0xbecc),before,after)
    guard = at(0xbbce)
    for label, opcode in [('BackgroundHeight',0x20),('ProbeSides',0x4c)]:
        a,b = old_labels[label],new_labels[label]
        before = bytes((opcode,a&255,a>>8))
        after = bytes((opcode,b&255,b>>8))
        found = raw[guard:guard+50].find(before)
        assert found>=0 and raw[guard:guard+50].count(before)==1
        patch(raw,guard+found,before,after)
    return raw,old_labels,new_labels


def compare_memory(a,b,ram_exclusions=None):
    assert a[:0x100]==b[:0x100] and a[0x200:0x2000]==b[0x200:0x2000]
    assert a[0x4000:0x8000]==b[0x4000:0x8000]
    assert a.rawtags==b.rawtags
    if not ram_exclusions:
        assert a.ram==b.ram
    else:
        for bank,(left,right) in enumerate(zip(a.ram,b.ram,strict=True)):
            excluded=ram_exclusions.get(bank,())
            assert all(x==y or any(lo<=offset<hi for lo,hi in excluded)
                       for offset,(x,y) in enumerate(zip(left,right,strict=True))),bank
    assert a.ppu_log==b.ppu_log and a.vram==b.vram and a.chr_latches==b.chr_latches


def verify(images, old_labels, new_labels):
    seeds = [N.fresh(image) for image in images]
    for image, labels in zip(images,(old_labels,new_labels),strict=True):
        invoke_span(image,'ProbeSides1108',labels['ProbeSides'])
    counts = {True:0,False:0}
    costs = {True:[],False:[]}
    # Include both block buffer pages, metatile edges and side failures at
    # either side. Write the actual native query's resolved cell addresses.
    for x,y,left,right in itertools.product([0,3,4,12,13,15,243,244,253,255],
            [32,47,63,96,112,153,176,191,205,206],
            [0,0x10,0x54,0xc2,0xc3,0xc4,0x26], [0,0x10,0xc2,0xc4]):
        pair = [N.fork(m) for m in seeds]
        outputs = []
        for m in pair:
            N.put(m,SelectedCharacter=41,Player_X_Position=x,Player_PageLoc=3,
                  Player_Y_Position=y,Player_Y_HighPos=1)
            cells = []
            for probe in (17,19):
                N.invoke(m,'BlockBufferColli_Side',y=probe)
                cells.append(m[9]+256*m[10]+m[5])
            for cell,tile in zip(cells,(left,right),strict=True):
                m[cell] = tile
            outputs.append(N.invoke(m,'ProbeSides1108',p=0x61,x=4,y=42))
        assert all(outputs[0][key]==outputs[1][key] for key in ('A','X','Y','P')), (x,y,left,right,outputs)
        compare_memory(*pair)
        ok = bool(outputs[0]['P']&1)
        counts[ok] += 1
        costs[ok].append(outputs[0]['CPU']-outputs[1]['CPU'])
    assert counts[True] and counts[False] and min(costs[True])>200
    return dict(successful_cases=counts[True],fallback_cases=counts[False],
                success_cycles_saved=[min(costs[True]),max(costs[True])],
                fallback_cycles_saved=[min(costs[False]),max(costs[False])])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    assert sha(BASE)==PIN
    before = BASE.read_bytes()
    base = bundle(before)
    assert_source_offsets(base)
    args.output.mkdir()
    raw,old_labels,new_labels = new_code(args.output,before)
    probe = verify([base,bundle(raw)],old_labels,new_labels)
    candidate = args.output/'candidate.nes'
    candidate.write_bytes(raw)
    # Packet runners use this exact ROM with the retained source labels.
    for suffix in ('.lbl','.dbg'):
        candidate.with_suffix(suffix).write_bytes(BASE.with_suffix(suffix).read_bytes())
    info = dict(passed=True,parent_SHA256=PIN,candidate_SHA256=sha(candidate),
                probe=probe,original_labels=old_labels,deduplicated_labels=new_labels,
                scope='Exact native side probe AXYP and memory equivalence across active Mini geometry. Full replay is separate.')
    (args.output/'candidate.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':
    main()
