"""Finite current-menu reader domains and Mike's exact sprite-data aliases."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

import check_remaining_roster_starts_1110 as Menu
from check_tmnt_render_oa import address, location

R, I, W = Menu.R, Menu.I, Menu.W
OUT = R/'build/mike-alternate-prototypes-1110'
ROM = R/'build/manual-wide-floor-native-1110/candidate.nes'
PIN = '74fde1dba64b17f7f9028c3da1d5948c041e9af11fb37fca4d241d834724318e'


def main():
    raw = ROM.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    bundle = W.bundle(raw)
    reads = Counter()
    names = Counter()
    tiles = Counter()
    prior = I.F.invoke

    def visit(cpu):
        if cpu.pc < 0x8000:
            return
        model = cpu.memory
        bank = model.rawtags[(cpu.pc-0x8000)//8192] & 127
        if (bank, cpu.pc) == (76, 0xbbcf):
            assert model[cpu.pc:cpu.pc+2] == [0xb1, 5]
            pointer = model[5] + 256*model[6] + cpu.y
            reads[(pointer-0xbced)//16] += 1
        if (bank, cpu.pc) == (81, 0xb7f9):
            names[cpu.a] += 1
        if (bank, cpu.pc) == (76, 0xbc63):
            assert model[cpu.pc:cpu.pc+3] == [0xb9, 0xfd, 0xbe]
            tiles[cpu.y//4] += 1

    def invoke(model, name, **kw):
        extra = kw.pop('watch', None)
        def watch(cpu):
            visit(cpu)
            if extra:
                extra(cpu)
        result = prior(model, name, watch=watch, **kw)
        if name in ('QueueSelection', 'CrossoverMenuInput') and I.N.get(model, 'CrossoverMenuState') == 2:
            prior(model, 'DrawSelectionPreview', watch=watch)
        return result

    I.F.invoke = invoke
    try:
        menu = Menu.inventory(raw)
    finally:
        I.F.invoke = prior
    leaves = sorted(name for name in bundle['syms']
                    if re.fullmatch(r'Jn(?:Pose[0-6][RL]|Shot\d+_[01](?:Left)?|Item\d+|Heart|Star|BigHeart|BatNativeRecord\d+)', name))
    unique, aliases = {}, {}
    for name in leaves:
        at = location(bundle, name)
        blob = raw[at:at+raw[at]+1]
        assert blob[0] % 4 == 0 and len(blob) < 128
        if blob in unique:
            aliases[name] = unique[blob]
        else:
            unique[blob] = name
    compact_bytes = 280 + sum(map(len, unique))
    result = dict(passed=True, ROM_SHA256=PIN, ROM_written=False,
                  native_run=False, menu_profiles=menu['distinct_named_entries'],
                  FmNames_read_rows=dict(sorted(reads.items())),
                  FmNames_unread_rows=sorted(set(range(33))-set(reads)),
                  FmPreviewTiles_read_rows=dict(sorted(tiles.items())),
                  FmPreviewTiles_unread_rows=sorted(set(range(33))-set(tiles)),
                  NrNames_read_rows=dict(sorted(names.items())),
                  NrNames_unread_rows=sorted(set(range(43))-set(names)),
                  Mike_original_art_bytes=1033, Mike_unique_leaf_records=len(unique),
                  Mike_leaf_records=len(leaves), Mike_compact_art_bytes=compact_bytes,
                  Mike_exact_source_funding_bytes=1033-compact_bytes, Mike_aliases=aliases,
                  scope='All exact74fde32slot Select states and both confirmation buttons. '
                        'Unread finite rows are candidates only; aliasing needs source reader '
                        'bounds and whole-menu regression. Mike identical leaf aliases preserve '
                        'complete headers/tiles/attributes/coordinates. No new execution lease.',
                  source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'funding.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
