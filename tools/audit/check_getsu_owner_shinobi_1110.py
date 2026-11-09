"""Rebind the moved Shinobi cookie index and shared-overlay transitions."""

import argparse
import json
from pathlib import Path

import check_getsu_fuma_owner_1110 as O
from check_getsu_owner_vectors_1110 import reconstruct


SH_LOAD, SH_AUTH, SH_RETIRE = 0xa87f, 0xa800, 0xa849


def load(m):
    O.scene(m, 36)
    before = m.ppu_reads
    result = O.invoke(m, SH_LOAD)
    assert result['P'] & 1 and result['A'] == 83 and result['X'] == 71 and result['Y'] == 109
    assert O.headers(m)[0] == O.headers(m)[1]
    result['PPU_reads'] = m.ppu_reads - before
    O.clear_logs(m)
    return result


def qualify(root):
    b = O.Page.bundle()
    trial, proof, _, _ = reconstruct(root)
    refs = [(O.Page.Front.off(65, pc), n) for pc, n in ((SH_AUTH, 18), (SH_RETIRE, 54), (SH_LOAD, 140))]
    for at, size in refs:
        a, z = b['raw'][at:at + size], trial['raw'][at:at + size]
        differences = [i for i in range(size) if a[i] != z[i]]
        assert differences == ([14] if size == 18 else [])
    m, n = O.blank(b), O.blank(trial)
    a, z = load(m), load(n)
    assert m.ram == n.ram and a == z
    sh_cookie = O.headers(n)[0]
    assert sh_cookie[:2] == bytes((0xa7, 36))
    assert O.invoke(O.N.fork(n), SH_AUTH)['P'] & 1
    for bank in (2, 3):
        for i in range(16):
            a, z = O.N.fork(m), O.N.fork(n)
            for machine in (a, z):
                machine.ram[bank][0x1fe0 + i] ^= 1
            assert O.invoke(a, SH_AUTH) == O.invoke(z, SH_AUTH)
            assert not O.invoke(z, SH_AUTH)['P'] & 1 and not z.ram_writes
    a, z = O.N.fork(m), O.N.fork(n)
    assert O.invoke(a, SH_RETIRE) == O.invoke(z, SH_RETIRE)
    assert a.ram == z.ram and a.ram[2][0x1fe0] == a.ram[3][0x1fe0] == 0
    fresh = O.N.fork(n)
    O.cold(fresh, 42)
    gf_cookie = bytes.fromhex(proof['cookie'])
    assert O.headers(fresh) == (gf_cookie, gf_cookie)
    load(fresh)
    assert O.headers(fresh) == (sh_cookie, sh_cookie)
    for bank in (2, 3):
        assert bytes(fresh.ram[bank][:0x800]) == bytes(n.ram[bank][:0x800])
    return dict(passed=True, ROM_written=False, parent_SHA256=O.PIN,
                memory_only_SHA256=proof['expected_memory_only_SHA256'], auth_header_byte_poisons=32,
                cold_and_retire_exact=True, Sh_to_Getsu_and_reverse=True, Shinobi_cookie=sh_cookie.hex(),
                proof_SHA256=O.SHA((root / 'proof.json').read_bytes()), source_SHA256=O.SHA(Path(__file__).read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    root = parser.parse_args().output.resolve()
    q = qualify(root)
    (root / 'shinobi.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q))


if __name__ == '__main__':
    main()
