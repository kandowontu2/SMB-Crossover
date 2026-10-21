"""Identify pure-black extra player layers in the generated pose tables.

Bit 2 is metadata, stripped before hardware OAM. Body palette colors and mixed
face/skin sprites are retained. Normal builds run this after CHR packing so
regenerated artwork is tagged without requiring reference games or captures.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
PART = re.compile(r'(\s*\.byte MetaspriteVramOffset\{\$([0-9a-fA-F]+)\}, \{SPRITE_BANK_0\}, \$)([0-9a-fA-F]+)(,.*)')


def table(text, name):
    match = re.search(r'^'+re.escape(name)+r':\s*\n\s*\.byte ([^\n]+)', text, re.M)
    if not match:
        raise ValueError('Missing pose table: '+name)
    return [s.strip() for s in match[1].split(',')]


def number(s):
    return int(s[1:], 16) if s.startswith('$') else int(s, 0)


def main():
    # ChrPhysicalMap is emitted over sixteen lines.
    map_text = (ROOT/'src/chr_map_mmc3.inc').read_text().split('ChrPhysicalMap:\n', 1)[1].split('.popseg', 1)[0]
    mapping = [number(n.strip()) for line in map_text.splitlines() if '.byte ' in line
               for n in line.split('.byte ', 1)[1].split(',')]
    assert len(mapping) == 256
    chr_data = (ROOT/'chr/characters/packed-mmc3.chr').read_bytes()
    files = [('samus_metasprites.inc', 'SamusPose'),
             *[(role.lower()+'_metasprites.inc', 'Rg'+role) for role in ('BILL','LINK','SIMON','LANCE')],
             *[(role.lower()+'_metasprites.inc', 'Xg'+role) for role in ('PIT','RYGAR','LUIGI','BASS','RYU','SOPHIA')],
             ('bass_special_poses.inc', 'SsBass'),
             ('megaman_special_poses.inc', 'SsMega'), ('megaman_metasprites.inc', None)]
    report = {}
    for filename, prefix in files:
        path = ROOT/'src'/filename
        text = path.read_text()
        if prefix:
            banks = [number(v) for v in table(text, prefix+'Banks')]
            refs = {side: [v.lstrip('<>') for v in table(text, prefix+side+'Lo')]
                    for side in ('Left','Right')}
            if prefix=='SamusPose' and 'SamusCrouchBanks:' in text:
                banks += [number(v) for v in table(text,'SamusCrouchBanks')]
                for side in ('Left','Right'):
                    refs[side] += [v.lstrip('<>') for v in table(text,'SamusCrouch'+side+'Lo')]
        else:
            banks = [number(v) for v in table(text, 'MegaManSpriteBanks')]
            declarations = re.findall(r'^MetaspriteData "[^"]+", (\w+), (\w+)', text, re.M)[:len(banks)]
            refs = {side: [v[index] for v in declarations] for index, side in enumerate(('Left','Right'))}
        aliases = dict(re.findall(r'^(\w+)\s*=\s*(\w+)\s*$', text, re.M))
        def resolve(name):
            seen = set()
            while name in aliases:
                assert name not in seen, name
                seen.add(name);name = aliases[name]
            return name
        contexts = {}
        for side, labels in refs.items():
            assert len(labels) == len(banks), (filename, side)
            for label, bank in zip(labels, banks):
                contexts.setdefault(resolve(label), set()).add(bank)
        tagged = total = 0
        current = None
        output = []
        for line in text.splitlines():
            label = re.fullmatch(r'(\w+):', line)
            if label:
                current = label[1]
            match = PART.fullmatch(line)
            if match and current in contexts:
                tile, attr = int(match[2], 16), int(match[3], 16) & ~4
                total += 1
                black = attr & 3 == 3
                for bank in contexts[current]:
                    start = mapping[bank]*1024+tile*16
                    data = chr_data[start:start+32]
                    assert len(data) == 32, (filename, bank, tile)
                    black &= any(data) and not any(data[8:16]+data[24:32])
                if black:
                    attr |= 4;tagged += 1
                line = match[1]+f'{attr:02x}'+match[4]
            output.append(line)
        updated = '\n'.join(output)+'\n'
        if updated != text:
            path.write_text(updated)
        report[filename] = {'body_parts': total, 'black_overlay_parts': tagged}
    (ROOT/'build/player-outline-tags.json').write_text(json.dumps(report, indent=2)+'\n')
    roles = [(), ('megaman_metasprites.inc','megaman_special_poses.inc'),
             ('samus_metasprites.inc',), ('bill_metasprites.inc','lance_metasprites.inc'),
             ('link_metasprites.inc',), ('simon_metasprites.inc',),
             ('pit_metasprites.inc',), ('rygar_metasprites.inc',), (),
             ('bass_metasprites.inc','bass_special_poses.inc'),
             ('ryu_metasprites.inc',), ('sophia_metasprites.inc',),
             ('luigi_metasprites.inc',)]  # Scrooge owns the legacy generated Luigi art.
    flags=[int(any(report[name]['black_overlay_parts'] for name in names)) for names in roles]
    generated=('; Generated from actual tagged body and special-pose records.\n'
               '.pushseg\n.segment "METASPRITE"\nPlayerOutlineCharacters:\n'
               '  .byte '+','.join(map(str,flags))+'\n.popseg\n')
    (ROOT/'src/player_outline_flags.inc').write_text(generated)
    print('Player outlines:', sum(v['black_overlay_parts'] for v in report.values()), 'extra black sprite parts tagged')


if __name__ == '__main__':
    main()
