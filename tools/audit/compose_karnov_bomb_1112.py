"""Compose original Karnov Bomb activation and native integration in memory."""
from hashlib import sha256
from pathlib import Path
import json
import re
import zipfile

from compose_metal_head_bridge_1112 import assemble_segments
from recover_karnov_actor_1101_v1 import ROM, EXPECTED as DONOR_SHA

R = Path(__file__).resolve().parents[2]
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PARENT = '8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582'
SOURCE = R / 'tools/reference/karnov_bomb_1112.s'
CHECKPOINT = R / 'docs/qa/checkpoints/2026-11-01'
CHR = 1048592
OLD_COOKIE = bytes.fromhex('a707011019505be1948c45eddedef362')
OWNED = {'actor': (399, 8, 0xa000), 'combat': (1019, 2, 0xc900),
         'options': (1021, 2, 0xd600), 'body': (407, 5, 0), 'hud': (1023, 1, 0)}
PINNED = {'actor': '86832d35a48aafc74cde43a6d2f9e28be647b0ebff78a1da970d058ec1088566',
          'combat': '9a337d813f94595f2d5d4b07774bed0d3c73678b67bc3008c6c943ef84e9e1ce',
          'options': '9aec1fcd047acc7930c4ba2464fec4be18ec2ccdac68bf5fb64893a0cae8040a',
          'body': '1bd3c6b0677039ac226391638af7456c6e619482c1af9c374258ed00f358c78a',
          'hud': 'cafb617aff7ec4322bec6e63e1265a36e8b3c01a681a95f03807df69176cea14'}
ORIGINS = dict(CONTROL_GATE=0xdc2c, LADDER_LOAN=0xd6e5, CLAPPER_LOAN=0xd7ef,
               SHIELD_LOAN=0xd8fc, SELECTION_LOAN=0xd950, DRAW_LOAN=0xd9a3,
               DRAW_ANCHOR_LOAN=0xd850, CONTACT_TAIL=0xcd79, HUD_TAIL=0xcd97,
               HUD_NAME_TAIL=0xcdb9)
LOAN_END = dict(CONTROL_GATE=0xdc38, LADDER_LOAN=0xd787, CLAPPER_LOAN=0xd8b2,
                SHIELD_LOAN=0xd93d, SELECTION_LOAN=0xd9a3, DRAW_LOAN=0xda2a,
                DRAW_ANCHOR_LOAN=0xd8b2, CONTACT_TAIL=0xcd97, HUD_TAIL=0xcdb0,
                HUD_NAME_TAIL=0xce00)
LOAN_END['CLAPPER_LOAN'] = ORIGINS['DRAW_ANCHOR_LOAN']
LOANS = ((0xd6e5, 0xd787), (0xd7ef, 0xd8b2), (0xd8fc, 0xd93d), (0xd950, 0xda2a))
SYMBOLS = dict(KrOptionsUnhandled=0xdc55, KrOptionsNativeTimers=0xdbd3,
    KrCameraLo=0xc821, KrCameraHi=0xc822, R0=3, R1=4, R2=5, R3=6,
    R4=7, R5=8, R6=9, R7=10, ScreenLeft_X_Pos=0x71f, ScreenLeft_PageLoc=0x71d,
    KrRebaseShots=0xb4a7, KrClearSourceShots=0xafa4, KrDrawShots=0xb650,
    KrShotPacket=0xc834, KrRenderCameraLo=0xc825, KrRenderCameraHi=0xc826,
    MetaspriteRenderLoop=0xa5ba, KrCombatOrdinary=0xc993, KCEnemy=0xc855,
    Enemy_Flag=0x10, Enemy_Y_HighPos=0xa5, Enemy_State=0x1f, Enemy_ID=0x17,
    Enemy_X_Position=0x76, Enemy_PageLoc=0x5d, Enemy_Y_Position=0xbe,
    ObjectOffset=0x0d, HandleEnemyFBallCol=0x9a8f, KrHudHaveIndex=0xdce1,
    KrHudDownB=0xcd4e, VRAM_Buffer1=0x4af, KrHudLease=0xdd9e,
    KrBombHudNewName=0xcdb0-36, KrHudOriginalNames=0xcd2a,
    KrHudNameCell=0x4b2, KrHudAfterName=0xdd5d)


def archive(name, digest):
    path = CHECKPOINT / name
    assert sha256(path.read_bytes()).hexdigest() == digest, path
    return zipfile.ZipFile(path)


def source_closure(old):
    with archive('karnov-hud-nightly-v9/source.zip',
                 'ae5e53e01d7796f6d5beab97668b4f02a270c5dc60027d1cda181b6dfe11f777') as packet:
        source = packet.read('host/karnov-options-portable-v7.inc').decode()
        controls = packet.read('host/kr-options-host-v8.inc').decode()
        terrain = packet.read('host/kr-terrain.inc').decode()
    assert 'cmp #0\n beq KrOptionsSupported\n cmp #3\n beq KrOptionsSupported\n cmp #7' in controls
    assert 'jsr Kr_C28C\n beq KrOptionsUnhandled' in controls
    assert 'ora #4\n sta KrState+$21\n jsr KrOptionsNative' in controls
    assert terrain.count('jsr KrOptionsControls') == terrain.count('jsr KrOptionsTick') == 1
    assert source.count('JMP Kr_ED2B') == 1 and source.count('Kr_ED2B:') == 1
    # Every original compiled vector remains exact. Five unavailable item
    # destinations lie inside the source spans temporarily loaned here.
    options = old['options']
    vectors = tuple(int.from_bytes(options[i:i + 2], 'little') for i in range(0x47, 0x59, 2))
    assert vectors == (0xd659, 0xd695, 0xd6e5, 0xd787, 0xd7ef, 0xd850, 0xd88d, 0xd8b2, 0xd8fc)
    assert [i for i, value in enumerate(vectors) if any(a <= value < b for a, b in LOANS)] == [2, 4, 5, 6, 8]
    direct = []
    for role in ('actor', 'combat', 'options'):
        origin = OWNED[role][2]
        for match in re.finditer(b'[\x20\x4c](?=..)', old[role], flags=re.S):
            at = match.start()
            pc = origin + at
            target = int.from_bytes(old[role][at + 1:at + 3], 'little')
            if any(a <= target < b for a, b in LOANS) and not any(a <= pc < b for a, b in LOANS):
                direct.append((role, pc, target))
    return vectors, direct


def pixels(old, modified, donor):
    with archive('karnov-render-component-v1/source-proof.zip',
                 '90565aa146cbf5592ab58b3ad401846f549b04320e488027501764a45286d2a7') as packet:
        report = json.loads(packet.read('host/render-art.json'))
        assert old['body'] == packet.read('host/kr-body.chr')
        meta = packet.read('host/kr-pose-meta.bin')
    def glyph(body, page, pair):
        at = page * 1024 + pair * 32
        return bytes(body[at:at + 32])
    body = modified['body']
    copied = {1: 28, 2: 29, 3: 30, 4: 31}
    used407 = {v['packet'][i] // 2 for v in report['profiles'] if v['page'] == 0
               for i in range(1, len(v['packet']), 4)}
    assert not set(copied.values()) & used407
    for old_pair, new_pair in copied.items():
        body[new_pair * 32:new_pair * 32 + 32] = glyph(old['body'], 3, old_pair)
    donor_chr = donor[16 + 131072:]
    bomb = dict(zip((0x41, 0x43, 0x45, 0x47, 0x49, 0x4b), (1, 2, 3, 29, 30, 31)))
    for tile, pair in bomb.items():
        at = 12 * 1024 + (tile & 0x3e) * 16
        body[3072 + pair * 32:3072 + (pair + 1) * 32] = donor_chr[at:at + 32]
    actor = modified['actor']
    meta_at = old['actor'].find(meta)
    assert meta_at >= 0 and old['actor'].count(meta) == 1
    cells = 0
    for profile in report['profiles']:
        row, page = profile['index'], profile['page']
        at = meta_at + profile['pointer'] - 0xd000
        assert bytes(actor[at:at + len(profile['packet'])]) == bytes(profile['packet'])
        if row in (26, 58):
            assert page == 3 and actor[meta_at + 128 + row] == 3
            actor[meta_at + 128 + row] = 0
        for i in range(1, len(profile['packet']), 4):
            pair = profile['packet'][i] // 2
            if row in (26, 58):
                actor[at + i] = copied[pair] * 2
                assert glyph(body, 0, copied[pair]) == glyph(old['body'], 3, pair)
            else:
                assert glyph(body, page, pair) == glyph(old['body'], page, pair), (row, page, pair)
            cells += 1
    assert all(glyph(body, 3, p) == glyph(old['body'], 3, p) for p in report['free_pairs_used'])
    for tile, destination in zip((0x84, 0x85, 0x94, 0x95), range(0x3c, 0x40)):
        at = 38 * 1024 + (tile & 63) * 16
        pattern = donor_chr[at:at + 16]
        modified['hud'][16 * destination:16 * (destination + 1)] = pattern[8:] + pattern[:8]
    return dict(donor_bomb_tiles=bomb, exact_existing_body_cells=cells,
                remapped_body_rows=[26, 58], exact_existing_projectile_pairs=7,
                donor_icon_tiles=[0x84, 0x85, 0x94, 0x95], hud_icon_tiles=list(range(0x3c, 0x40)))


def transform(raw):
    assert len(raw) == 2097168
    old = {role: raw[CHR + page * 1024:CHR + (page + count) * 1024]
           for role, (page, count, _) in OWNED.items()}
    assert all(sha256(image).hexdigest() == PINNED[role] for role, image in old.items())
    vectors, direct = source_closure(old)
    assert direct == [('options', 0xd639, 0xd950)], direct
    modified = {name: bytearray(data) for name, data in old.items()}
    constants = dict(SYMBOLS)
    def packet_offset(match):
        name = 'KrShotPacket' + match[1]
        constants[name] = SYMBOLS['KrShotPacket'] + int(match[1])
        return name
    constants['KrHudHintCell'] = SYMBOLS['VRAM_Buffer1'] + 18
    source = re.sub(r'\bKrShotPacket\+(\d+)', packet_offset, SOURCE.read_text())
    source = source.replace('VRAM_Buffer1+18', 'KrHudHintCell')
    chunks, symbols = assemble_segments(source, ORIGINS, constants)
    assert all(len(code) <= LOAN_END[name] - ORIGINS[name] for name, code in chunks.items()), {
        name: (len(code), LOAN_END[name] - ORIGINS[name]) for name, code in chunks.items()}

    def change(role, pc, before, after):
        at = pc - OWNED[role][2]
        assert len(before) == len(after) and old[role][at:at + len(before)] == before, (role, hex(pc), before.hex())
        modified[role][at:at + len(after)] = after

    def j(op, pc):
        return bytes([op]) + pc.to_bytes(2, 'little')

    def hook(role, pc, old_pc, new_name, opcode=0x20):
        change(role, pc, j(opcode, old_pc), j(opcode, symbols[new_name]))

    for name, code in chunks.items():
        start, end = ORIGINS[name], LOAN_END[name]
        role = 'combat' if name.endswith('_TAIL') else 'options'
        at = start - OWNED[role][2]
        if role == 'combat':
            assert old[role][at:at + end - start] == b'\xff' * (end - start)
            end = start + len(code)
        change(role, start, old[role][at:at + end - start], code.ljust(end - start, b'\xea'))
    for index in (2, 4, 5, 6, 8):
        change('options', 0xd647 + 2 * index, vectors[index].to_bytes(2, 'little'), b'\x12\xd6')
    change('options', 0xd639, b'\x4c\x50\xd9', b'\x4c\x12\xd6')
    hook('options', 0xdc07, 0xdc5d, 'KrBombCycle')
    hook('options', 0xdbf5, 0xdbd3, 'KrBombThenTimer', 0x4c)
    hook('actor', 0xb184, 0xb4a7, 'KrBombRebaseShots')
    hook('actor', 0xb0a5, 0xafa4, 'KrBombSceneClear')
    hook('actor', 0xb62d, 0xb650, 'KrBombDrawWithShots')
    change('combat', 0xc990, b'\xad\x65\xc0', j(0x20, symbols['KrBombContactWithShots']))
    change('options', 0xdcc6, bytes.fromhex('a200ad8ec0f00ae8c903f005e8c907d008ad8fc03de9ddd002a203'),
           j(0x4c, symbols['KrBombHudChoice']).ljust(27, b'\xea'))
    for pc in (0xdd26, 0xdce1):
        change('options', pc, bytes.fromhex('bcecdd'), j(0xbc, symbols['KrBombHudStocks']))
    change('options', 0xdd4b, bytes.fromhex('bdf3dd'), j(0xbd, symbols['KrBombHudNames']))
    change('options', 0xdd78, bytes.fromhex('bdf0dd'), j(0xbd, symbols['KrBombHudTiles']))
    hint = bytes.fromhex('b94ecd99c1048810f7')
    change('options', 0xdd95, hint, j(0x4c, symbols['KrBombHudHint']).ljust(len(hint), b'\xea'))
    # Keep every old address by adding the fifth name in the granted tail.
    name = bytes((0x0b, 0x18, 0x16, 0x0b, 0x24, 0x24, 0x24, 0x24, 0x24))
    change('combat', 0xcdb0, b'\xff' * len(name), name)
    change('options', 0xdd4e, bytes.fromhex('a8a200'), j(0x4c, symbols['KrBombHudNameStart']))

    donor = ROM.read_bytes()
    assert sha256(donor).hexdigest() == DONOR_SHA
    art = pixels(old, modified, donor)
    cookie = bytes.fromhex('a7070111') + sha256(b'Karnov Bomb 1112\0' +
        b''.join(modified[k] for k in ('actor', 'combat', 'options', 'body', 'hud'))).digest()[:12]
    change('actor', 0xbfe0, OLD_COOKIE, cookie)
    resident = 0x3bad5
    assert raw[resident:resident + 16] == OLD_COOKIE and raw.count(OLD_COOKIE) == 2
    result = bytearray(raw)
    for role, (page, count, _) in OWNED.items():
        at = CHR + page * 1024
        assert len(modified[role]) == count * 1024
        result[at:at + len(modified[role])] = modified[role]
    result[resident:resident + 16] = cookie
    changes = [i for i, (a, b) in enumerate(zip(raw, result)) if a != b]
    runs = []
    for offset in changes:
        if runs and offset == runs[-1][-1] + 1:
            runs[-1][-1] = offset
        else:
            runs.append([offset, offset])
    patches = [dict(offset=lo, before=raw[lo:hi + 1].hex(), after=result[lo:hi + 1].hex())
               for lo, hi in runs]
    return bytes(result), dict(parent_SHA256=sha256(raw).hexdigest(), candidate_SHA256=sha256(result).hexdigest(),
        cookie=cookie.hex(), changes=len(changes), patches=patches,
        loaned=[list(s) for s in LOANS], closed_external_direct_sites=direct,
        sizes={k: len(v) for k, v in chunks.items()}, art=art,
        symbols={k: v for k, v in symbols.items() if k.startswith('KrBomb')})


def inverse(raw, report):
    """Recover the exact parent from the compact patch preimages."""
    assert sha256(raw).hexdigest() == report['candidate_SHA256']
    result = bytearray(raw)
    for patch in report['patches']:
        at = patch['offset']
        before, after = bytes.fromhex(patch['before']), bytes.fromhex(patch['after'])
        assert len(before) == len(after) and raw[at:at + len(after)] == after
        result[at:at + len(after)] = before
    assert sha256(result).hexdigest() == report['parent_SHA256']
    return bytes(result)


if __name__ == '__main__':
    raw = NIGHTLY.read_bytes()
    candidate, report = transform(raw)
    assert inverse(candidate, report) == raw
    print(json.dumps({k: v for k, v in report.items() if k != 'patches'}, separators=(',', ':')))
