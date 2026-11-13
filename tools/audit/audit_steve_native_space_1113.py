"""Read-only native PRG ownership census; no ROM or generated files."""
from hashlib import sha256
import json
from pathlib import Path
import re

import check_prince_brick_support_1111 as Host
import check_hogan_current_bounded_v1 as M

R = Path(__file__).resolve().parents[2]
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
TAIL = (5, 0x1fdf, 0x2000)
BANK5_SHA = '8dae80bf93754db1ced3fb5e9e6a3589014ed7d65f4ca97edda24b76a4f3d1ec'
TERMINAL = bytes.fromhex('2078bf90034c3ebbad02608d6a01a9908d6c01a9a28d6d01a98a4c5a01')


def audit(raw):
    assert raw[:4] == b'NES\x1a' and raw[4] == 64
    bundle = Host.C.Start.W.bundle(raw)
    runs = []
    for bank in range(128):
        data = raw[16+8192*bank:16+8192*(bank+1)]
        runs.extend((len(match[0]), bank, match.start())
                    for match in re.finditer(b'\xff{16,}', data))
    assert max(row[0] for row in runs) == 105
    bank, lo, hi = TAIL
    image = raw[16+8192*bank:16+8192*(bank+1)]
    assert sha256(image).hexdigest() == BANK5_SHA
    assert image[0x1fc2:lo] == TERMINAL and image[lo:hi] == b'\xff'*(hi-lo)
    assert M.location(bundle, 'SophiaWallAttached') == 16+8192*bank+0x1fc2
    assert M.address(bundle, 'SophiaWallAttached') == 0xbfc2
    # The final original path is a tailcall, so the alignment interval has
    # no fallthrough. Source and linked terminal bytes agree exactly.
    source = (R/'src/sophia_source_terrain.s').read_text()
    assert 'farcall SamusStopAtWallBanked, jmp\nOriginalEnd:' in source
    assert image[lo-3:lo] == bytes.fromhex('4c5a01')
    direct = [(0xa000+i, int.from_bytes(image[i+1:i+3], 'little'))
              for i in range(8190) if image[i] in (0x20, 0x4c)
              and 0xbfdf <= int.from_bytes(image[i+1:i+3], 'little') < 0xc000]
    assert not direct
    # Actual current Rogue page maps, rather than historical source table
    # locations, decide ownership of each complete 256-byte ROM data view.
    page_rows = []
    for mode, count, banks, highs in (
        ('lower', 192, 'RdaLowerBankTable', 'RdaLowerHighTable'),
        ('upper', 32, 'RdaUpperRawBankTable', 'RdaUpperRawHighTable')):
        at, high = M.location(bundle, banks), M.location(bundle, highs)
        for index in range(count):
            tag = raw[at+index] & 127
            start = (raw[high+index]-0xa0)*256
            assert 0 <= start <= 8192-256
            assert tag != bank
            page_rows.append((mode, index, tag, start))
    # The two largest apparent runs are still source-owned data. Replacing
    # them would alter complete Rogue page reads or valid body indices.
    assert (105, 80, 0x1c97) in runs and (70, 94, 0x13b3) in runs
    assert any(tag == 80 and start == 0x1c00 for _, _, tag, start in page_rows)
    art = (R/'src/rogue_dawn_art.inc').read_text()
    assert 'RdBodyIndex1:' in art and 'RdWeaponIndex0:' in art
    return dict(ROM_SHA256=sha256(raw).hexdigest(), physical_PRG_banks=128,
                FF_runs_at_least16=len(runs), total_FF_in_these_runs=sum(n for n, _, _ in runs),
                maximum_FF_run=max(runs), ready_512B_native_allocation=False,
                native_stub_proposal=dict(bank=bank, CPU_half_open=[0xbfdf, 0xc000],
                    file_half_open=[16+8192*bank+lo, 16+8192*bank+hi], bytes=hi-lo,
                    bank_SHA256=BANK5_SHA, old_terminal_PC=0xbfc2,
                    old_terminal_bytes=TERMINAL.hex(), Rogue_page_rows_excluding_bank5=len(page_rows)),
                formal_grant=False, runtime_or_interrupt_qualification=False,
                scope='Source-endpoint/current-byte/direct-target/Rogue-page-map audit. Root owns any new allocation; new injury entry ABI and Main/ISR/foreign controls remain required.',
                output_files=0)


if __name__ == '__main__':
    print(json.dumps(audit(ROM.read_bytes()), separators=(',', ':')))
