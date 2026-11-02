"""Check pinned disassembly byte annotations against the user's exact SMS ROM."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'build/sonic-sms-reference-1102-v1'


def main():
    receipt = json.loads((O / 'receipt.json').read_text())
    with zipfile.ZipFile(receipt['source_ROM_archive']) as z:
        rom = z.read(receipt['member'])
    assert hashlib.sha256(rom).hexdigest() == receipt['ROM_SHA256']
    with zipfile.ZipFile(O / 'reference.zip') as z:
        source = z.read('src/prediet.asm').decode()
    rows, size, player_rows, player_bytes = 0, 0, 0, 0
    covered = set()
    for line in source.splitlines():
        m = re.search(r'; ([0-9A-F]{2}):([0-9A-F]{4}) - ((?:[0-9A-F]{2}(?: |$))+)', line)
        if not m:
            continue
        bank, addr, data = int(m[1], 16), int(m[2], 16), bytes.fromhex(m[3])
        offset = bank * 0x4000 + addr % 0x4000
        assert rom[offset:offset + len(data)] == data, (bank, addr, line)
        rows += 1
        size += len(data)
        covered.update(range(offset, offset + len(data)))
        if bank == 1 and 0x48c8 <= addr < 0x5225:
            player_rows += 1
            player_bytes += len(data)
    assert rows == 16102 and size == 36029
    table = bytes.fromhex('10003000080000080210003000020000080204000c000200000201100030000800000802')
    assert rom[0x4dcb:0x4def] == table
    q = dict(passed=True, ROM_SHA256=receipt['ROM_SHA256'], revision=receipt['revision'],
             annotated_instructions=rows, annotated_bytes=size, distinct_bytes=len(covered),
             player_region_48C8_5225=dict(annotated_instructions=player_rows, annotated_bytes=player_bytes),
             physics_table_4DCB_4DEF=table.hex(),
             scope='Exact byte comments and physics table match the original ROM. This does not assemble instruction text, validate annotations semantically, reproduce the complete ROM, or qualify an NES port.')
    (O / 'byte-audit.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q))


if __name__ == '__main__':
    main()
