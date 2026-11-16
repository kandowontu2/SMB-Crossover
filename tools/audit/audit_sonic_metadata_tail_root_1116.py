"""Read-only current Sonic metadata-tail producer/capacity review; no new CPU."""
from hashlib import sha256
from pathlib import Path
import json, struct

R = Path(__file__).resolve().parents[2]
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d'
SOURCES = {
    'tools/reference/sonic_sms_ring_feedback_1110.py': '7d79ea99c9b6dcc03c409fbc98612aacf81047d8b311f02adb411c2a8ab2924e',
    'tools/reference/sonic_sms_ring_live_1110.py': 'c86e7879346387dc62e715a84d1e0bb40f3ffd4005436fe13bc081063bdfc57a',
    'tools/reference/sonic_sms_native_effects_1110.py': '5dfe216183cf8909dd7482b4b120bb668b2374b9e84c0e946b4824b46c9253f9',
}


def H(raw):
    return sha256(raw).hexdigest()


def review(raw):
    assert H(raw) == PIN
    for path, pin in SOURCES.items():
        assert H((R/path).read_bytes()) == pin
    producer = (R/next(iter(SOURCES))).read_text()
    assert "{'SONIC_COLD': (0xd25e, 139), 'COLD_TAIL': (0xd31f, 225)}" in producer
    assert "result['used']['SONIC_COLD'] == 124 and result['used']['COLD_TAIL'] == 37" in producer
    page = lambda n: raw[1048592+n*1024:1048592+(n+1)*1024]
    kernel = b''.join(page(n) for n in (*range(321, 328), 330))
    meta = page(328)
    assert meta[:8] == b'SMSONIC4'
    # The producer's explicit37-byte tail is17 bytes of dispatch followed
    # by ten 16-bit page IDs. Its declared225-byte section leaves188 bytes.
    code = bytes.fromhex('c90ab00bc908d004a9d485044c68d23860')
    assert meta[0x31f:0x330] == code
    pages = struct.unpack('<10H', meta[0x330:0x344])
    assert pages == (*range(321, 328), 330, 333, 334)
    assert meta[0x344:] == b'\xff'*188
    assert meta[0x2da:0x2e9] == b'\xff'*15
    cold = meta[0x25e:0x2da]
    assert cold.count(bytes.fromhex('a5050aaabd31d38d3051bd30d38d2351')) == 1
    assert cold.count(bytes.fromhex('e605a505c90890b74c1fd3')) == 1
    # The loop increments its owning index and tail CMP10 bounds the ten
    # rows. ASL/TAX gives0..18, so the two table loads stop atD343.
    table = [int.from_bytes(meta[0x101+3*i:0x103+3*i], 'little') for i in range(38)]
    assert all(meta[0x100+3*i] == 0x4c for i in range(38))
    assert not any(0xd344 <= target < 0xd400 for target in table)
    domains = ((3, 0xa000, kernel), (2, 0xd000, meta),
               (2, 0xd400, page(333)), (2, 0xd800, page(334)))
    controls = []
    indexed_leads = []
    for bank, base, data in domains:
        for i in range(len(data)-2):
            op = data[i]
            operand = int.from_bytes(data[i+1:i+3], 'little')
            if op in (0x20, 0x4c) and 0xd344 <= operand < 0xd400:
                controls.append(dict(bank=bank, PC=base+i, opcode=op, target=operand))
            if op in (0xbd, 0xb9, 0xdd, 0xd9) and 0xd245 <= operand < 0xd400:
                indexed_leads.append(dict(bank=bank, PC=base+i, opcode=op, base=operand))
    assert not controls
    assert {(q['PC'], q['base']) for q in indexed_leads} == {
        (0xd211, 0xd24e), (0xd220, 0xd256), (0xd22f, 0xd252),
        (0xd2ba, 0xd331), (0xd2c0, 0xd330)}
    # The other three conservative leads are the original four-row draw
    # tables. DrawIndex resets to0 and loops until4; DrawFlip is exactly
    # the shifted carry bit,0/1. The XOR tile index also stays0..3.
    assert meta[0x1ea:0x1f2] == bytes.fromhex('4a4aa9002a8d29c1')
    assert meta[0x1fb:0x200] == bytes.fromhex('a9008d28c1')
    assert meta[0x21b:0x223] == bytes.fromhex('984d29c1a8b956d2')
    assert meta[0x242:0x24c] == bytes.fromhex('ee28c1ad28c1c904d0b4')
    assert meta[0x24e:0x25a] == bytes.fromhex('00001010040c040c00022022')
    out = dict(passed=True, ROM_SHA256=PIN, source_SHA256=H(Path(__file__).read_bytes()),
               producer_pins=SOURCES, metadata_page328_SHA256=H(meta),
               declared_section=[0xd31f, 0xd400], produced_extent=[0xd31f, 0xd344],
               tail_37_SHA256=H(meta[0x31f:0x344]), unused_tail=[0xd344, 0xd400],
               capacity_bytes=188, cold_table_pages=list(pages), cold_table_last_read=0xd343,
               service_targets_in_tail=[], conservative_literal_controls=controls,
               conservative_indexed_read_leads=indexed_leads,
               indexed_read_classification='Two cold-table reads bound throughD343; '
                   'three original draw-table reads bind0..3 and stop byD259',
               unclassified_literal_or_indexed_leads=[],
               scope='Producer extent, cold table, service targets and enumerated literal/indexed '
                     'readers proven; not arbitrary-pointer exclusion, writer closure or code allocation',
               new_game_bytes_executed=False, ROM_written=False, Mesen=False, outputs=0)
    out['receipt_SHA256'] = H(json.dumps(out, sort_keys=True, separators=(',', ':')).encode())
    return out


if __name__ == '__main__':
    print('RESULT '+json.dumps(review(ROM.read_bytes()), separators=(',', ':')), flush=True)
