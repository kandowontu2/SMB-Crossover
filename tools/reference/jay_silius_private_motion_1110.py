"""Link frozen Journey to Silius movement into a proposed private A window."""
from hashlib import sha256
from pathlib import Path
import re

from sonic_sms_compact_cold_worker_1110 import assemble

REFERENCE = Path(__file__).resolve().parent
PINNED = {
    'jay_silius_original_input_1110.s': '1c338759bf4f215dca200514d540a1c761bc09bfb2e352836e79bd790852c5e7',
    'jay_silius_original_motion_1110.s': '7dc9bb8d4bbda5dc8709e1c9ae69f7906dcbe8c59ecd4448625fa61bbc7049bc',
    'jay_silius_host_tile_1110.s': '1a927d85c8958f1765518bf68b6d9133b99ff739028b4bc8f219899aaa1da244',
}
ORIGIN = 0xa000
SCRATCH = 0xc0f0
PROBE_INDEX = 0xc0fa
SERVICES = {'OriginalWeaponInput': 0xb000, 'OriginalTerrainEvent': 0xb003}
PLAYER_PROBES = ('HeadProbes', 'FootProbes', 'LeftProbes', 'RightProbes', 'SupportProbes')
RAM_OPERAND = re.compile(r'(?m)^( +[a-z]{3} )\$([0-9a-f]{2}|0[0-7][0-9a-f]{2})(?=\s*(?:$|,[xXyY]))')


def source(name):
    path = REFERENCE / name
    assert sha256(path.read_bytes()).hexdigest() == PINNED[name], path
    return path.read_text()


def replace_once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after)


def build(*, donor_terrain=False):
    control, motion, tile = (source(name) for name in PINNED)
    before, _, remainder = motion.partition('.segment "TILE_READ"')
    assert remainder.count('.segment "PLAYER_PROBES"') == 1
    records = remainder.split('.segment "PLAYER_PROBES"\n', 1)[1]
    text = control + '\n' + before
    text = re.sub(r'(?m)^(Original\w+ = \$[0-9a-f]+|\.segment "\w+")\n', '', text)
    text = re.sub(r'(?m)^;.*$', '', text)
    ram_fields = {int(value, 16) for _, value in RAM_OPERAND.findall(text)}
    assert len([v for _, v in RAM_OPERAND.findall(text) if len(v) == 2]) == 222
    # Actual bank mirror, previous pad, and the pinned stock input import's
    # cooldown, selection and inline-dispatch pointer also belong to Jay.
    ram_fields.update((0x52, 0xb6, 0xb8, 0xf4, 0xf5, 0x0163))
    ram = {field:0xc000 + i for i, field in enumerate(sorted(ram_fields - {2, 3}))}
    ram.update({2:SCRATCH, 3:SCRATCH + 1})
    assert max(a for k,a in ram.items() if k not in (2, 3)) < SCRATCH
    text = RAM_OPERAND.sub(lambda m: f'{m[1]}${ram[int(m[2],16)]:04x}', text)

    # Only player X0 reaches this packet. The exact 5 records are immutable.
    # X indexes the packed record during loads, Y retains the donor's local
    # byte index. X is restored before the native tile ABI and on every exit.
    start = text.index('ProbeTerrain:\n')
    end = text.index('NextSample:\n', start)
    text = text[:start] + f'''ProbeTerrain:
 sty ${SCRATCH + 2:04x}
 lda ProbeOffsets,y
 tax
 clc
 adc #$62
 sta ${ram[0]:04x}
 lda #$d0
 sta ${ram[1]:04x}
 ldy #0
 lda HeadProbes,x
 sta ${ram[10]:04x}
 iny
 inx
''' + text[end:]
    assert text.count('lda ($00),Y') == 4 and 'lda ($02),Y' not in text
    head, tail = text.split('NextSample:\n')
    sample, tail = tail.split(' sty ', 1)
    assert sample.count(' iny\n') == 4
    sample = sample.replace('lda ($00),Y', 'lda HeadProbes,x').replace(' iny\n',' iny\n inx\n')
    text = head + 'NextSample:\n' + sample + f' stx ${PROBE_INDEX:04x}\n ldx #0\n sty ' + tail
    text = replace_once(text, f' ldy ${ram[8]:04x}\n dec ${ram[10]:04x}\n bne NextSample\n rts',
        f' ldy ${ram[8]:04x}\n ldx ${PROBE_INDEX:04x}\n dec ${ram[10]:04x}\n bne NextSample\n ldx #0\n rts')
    text = replace_once(text, ' jsr ReadPackedNativeTile',
                        ' jsr OriginalDonorTile' if donor_terrain else ' jsr JayHostTile')
    offsets = ',0,'.join(f'{name}-HeadProbes' for name in PLAYER_PROBES)
    # The source MMC1 leaf ends with LSR #4, then A=B6=0, preserving C bit3
    # of its input. Keep that logical result without touching host mapper I/O.
    local_leaves = f'''
OriginalFreshButtons:
 lda ${ram[0x162]:04x}
 eor ${ram[0x163]:04x}
 and ${ram[0x162]:04x}
 rts
OriginalSelectPRG:
 sta ${ram[0xf1]:04x}
 lsr A
 lsr A
 lsr A
 lsr A
 lda #0
 sta ${ram[0xb6]:04x}
 rts
OriginalSoundRequest:
 sta ${ram[0xd1]:04x}
 lda #2
 sta ${ram[0xd0]:04x}
 rts
ProbeOffsets:
 .byte {offsets}
'''
    definitions = {**SERVICES, 'OriginalDonorTile':0xd002, 'Scratch':SCRATCH}
    assignments = ''.join(f'{name} = ${value:04x}\n' for name, value in definitions.items())
    packet = assignments + '.segment "PRIVATE"\n' + text + local_leaves + records
    if not donor_terrain:
        labels = re.findall(r'(?m)^(\w+):', tile)
        for label in labels:
            if label != 'JayHostTile':
                tile = re.sub(rf'\b{label}\b', f'HostTile_{label}', tile)
        packet += '\n' + tile.replace('.segment "JAY_TILE"', '.segment "PRIVATE"')
    labels = re.findall(r'(?m)^(\w+):', packet)
    assert len(set(labels)) == len(labels), 'Duplicate labels across input, motion and terrain'
    result = assemble(packet, {'PRIVATE':(ORIGIN, 2048)})
    relative = [ins['operand'] - ins['pc'] - 2 for ins in result['instructions'] if ins['mode'] == 'rel']
    result.update(ram=ram, services=SERVICES, origin=ORIGIN,
                  donor_terrain=donor_terrain, probe_index=PROBE_INDEX,
                  branch_displacements=dict(count=len(relative), minimum=min(relative), maximum=max(relative)))
    return result
