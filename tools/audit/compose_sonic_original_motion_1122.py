"""Newly authored rolling/charge/variable jump, exact a6, memory output only.

Only the existing Sonic motion allocation, one dedicated constructor store,
and its complete packet cookie change. No assets, native terrain, shared
controller policy, ROM files, or historical source builders are produced.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/reference'))
from sonic_sms_compact_cold_worker_1110 import assemble

ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = 'a6d91e368657a0ee1458391542e98adafcec45991ebecbe4521a648513cfa4df'
SOURCE = R / 'tools/reference/sonic_original_motion_1122.s'
CHR = 1048592
CODE_PAGES = (*range(321, 328), 330)
COOKIE_PAGES = CODE_PAGES + (328, 333, 334, 224, 226)
COOKIE_AT = 1034472
LAYOUT = {'ROLL': (0xa283, 0xa406-0xa283),
          'JUMP': (0xa406, 0xa492-0xa406),
          'ROLLJUMP': (0xa492, 0xa4e6-0xa492)}


def H(data):
    return sha256(data).hexdigest()


def page(raw, n):
    return raw[CHR+n*1024:CHR+(n+1)*1024]


def kernel(raw):
    return b''.join(page(raw, n) for n in CODE_PAGES)


@lru_cache(maxsize=1)
def program():
    p = assemble(SOURCE.read_text(encoding='ascii'), LAYOUT)
    assert p['symbols']['OriginalRoll'] == 0xa283
    assert p['symbols']['OriginalJump'] == 0xa406
    assert p['symbols']['OriginalRollingJump'] == 0xa492
    assert not any(i['mode'] in ('zpg', 'zpx', 'zpy', 'inx', 'iny', 'ind') for i in p['instructions'])
    return p


def proposal(parent):
    assert isinstance(parent, bytes) and len(parent) == 2097168 and H(parent) == PIN, 'Exact installed a6 only'
    p = program()
    old = kernel(parent)
    assert old[0x283:0x28d] == bytes.fromhex('a9008d49c0ad42c0c918')
    assert old[0x406:0x40b] == bytes.fromhex('ad58c0d0') + old[0x40a:0x40b]
    assert old[0x492:0x497] == bytes.fromhex('ad56c02980')
    assert old[0x4e6:0x4ef] == bytes.fromhex('18ad50c06d54c08d50')
    incoming = []
    for origin, data in ((0xa000, old), (0xd000, page(parent, 328)),
                         (0xd400, page(parent, 333)), (0xd800, page(parent, 334))):
        for i in range(len(data)-2):
            target = int.from_bytes(data[i+1:i+3], 'little')
            if (data[i] in (0x20, 0x4c, 0x6c) and 0xa283 <= target < 0xa4e6 and
                    not 0xa283 <= origin+i < 0xa4e6):
                incoming.append((origin+i, target))
    assert incoming == [(0xa532, 0xa283), (0xa571, 0xa492), (0xa577, 0xa406), (0xb4fd, 0xa283)]
    # Literal readers/writers do not name the two new persistent bytes.
    for at in (0xc097, 0xc098):
        assert all(at.to_bytes(2, 'little') not in data for data in
                   (old, page(parent, 328), page(parent, 333), page(parent, 334)))
    replacement = bytearray(old)
    logical = []
    for name, (start, size) in LAYOUT.items():
        data = p['images'][name] + b'\xea' * (size-p['used'][name])
        logical.append((start, old[start-0xa000:start-0xa000+size], data, name))
        replacement[start-0xa000:start-0xa000+size] = data
    reset = bytes.fromhex('a9008d47c08d48c08d58c08daac08dabc0')
    assert old.count(reset) == 1, 'Dedicated constructor reset must be unique'
    at = old.index(reset) + 2
    reset_pc = 0xa000 + at
    target = p['symbols']['OriginalMotionReset']
    reset_new = b'\x20' + target.to_bytes(2, 'little')
    logical.append((reset_pc, old[at:at+3], reset_new, 'fresh constructor reset'))
    replacement[at:at+3] = reset_new
    out = bytearray(parent)
    for index, n in enumerate(CODE_PAGES):
        out[CHR+n*1024:CHR+(n+1)*1024] = replacement[index*1024:(index+1)*1024]
    old_cookie = parent[COOKIE_AT:COOKIE_AT+16]
    assert old_cookie == bytes.fromhex('a72b01') + sha256(b''.join(page(parent, n) for n in COOKIE_PAGES)).digest()[:13]
    cookie = old_cookie[:3] + sha256(b''.join(page(out, n) for n in COOKIE_PAGES)).digest()[:13]
    out[COOKIE_AT:COOKIE_AT+16] = cookie
    result = bytes(out)
    spans = []
    owned = set(range(COOKIE_AT, COOKIE_AT+16))
    for pc, before, after, name in logical:
        cursor = 0
        while cursor < len(after):
            first = pc-0xa000+cursor
            count = min(len(after)-cursor, 1024-first%1024)
            file = CHR + CODE_PAGES[first//1024]*1024 + first%1024
            a, b = before[cursor:cursor+count], after[cursor:cursor+count]
            assert parent[file:file+count] == a
            assert result[file:file+count] == b
            owned.update(range(file, file+count))
            spans.append(dict(PC=pc+cursor, file=file, bytes=count, role=name,
                              old_SHA256=H(a), new_SHA256=H(b)))
            cursor += count
    changed = {i for i, (a, b) in enumerate(zip(parent, result, strict=True)) if a != b}
    assert changed <= owned
    assert all(page(result, n) == page(parent, n) for n in (224, 226, 328, 333, 334))
    q = dict(parent_SHA256=PIN, candidate_SHA256=H(result), source_SHA256=H(SOURCE.read_bytes()),
             source_file=str(SOURCE), code_used=p['used'], spans=spans,
             cookie_file=COOKIE_AT, old_cookie=old_cookie.hex(), cookie=cookie.hex(),
             new_state={'previous_accepted_pad': 0xc097, 'charge': 0xc098},
             retained_literal_control_entries=incoming,
             changed_bytes=len(changed), all_unowned_bytes_exact=True,
             no_asset_native_terrain_or_shared_controller_changes=True,
             outputs=0, physical_ROM_or_native_qualification=False)
    return result, q


if __name__ == '__main__':
    _, q = proposal(ROM.read_bytes())
    print('RESULT ' + json.dumps(q, separators=(',', ':')), flush=True)
