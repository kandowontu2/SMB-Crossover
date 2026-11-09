"""Run real c8 vectors at each reached changed cold-loader instruction."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_getsu_fuma_owner_1110 as Owner
from check_mini_audio_mixer_irq_1108_v2 import lag_path


O = Owner
STOP = 0x5b00


def reconstruct(root):
    proof = O.Page.load_json(root / 'proof.json')
    assert proof['passed'] and proof['parent_SHA256'] == O.PIN and not proof['scene_admitted']
    b = O.Page.bundle()
    raw = bytearray(b['raw'])
    body = (root / 'kernel.bin').read_bytes()
    assert len(body) == 2048 and O.SHA(body) == proof['kernel_SHA256']
    spans = []
    for p in proof['patch_PRG']:
        at, old, new = p['file_offset'], bytes.fromhex(p['old_hex']), bytes.fromhex(p['new_hex'])
        assert len(old) == len(new) and raw[at:at + len(old)] == old
        raw[at:at + len(new)] = new
        spans.append((p['physical_PRG'] | 128, *p['CPU_half_open']))
    for i, page in enumerate(proof['code_pages']):
        at = page['file_offset']
        assert O.SHA(raw[at:at + 1024]) == page['SHA256']
        raw[at:at + 1024] = body[i * 1024:(i + 1) * 1024]
    assert O.SHA(raw) == proof['expected_memory_only_SHA256']
    return dict(b, raw=bytes(raw)), proof, spans, body


def entry(m):
    m[0x16a], m[0x16c], m[0x16d] = 83, O.COLD & 255, O.COLD >> 8
    c = O.NesMPU(memory=m, pc=0x15a)
    c.a, c.x, c.y, c.p, c.sp = O.CO, 71, 109, 0x21, 224
    c.stPushWord(STOP - 1)
    return c


def clone(c):
    n = O.NesMPU(memory=O.N.fork(c.memory), pc=c.pc)
    n.a, n.x, n.y, n.p, n.sp = c.a, c.x, c.y, c.p, c.sp
    return n


def regs(c):
    return c.pc, c.a, c.x, c.y, c.p & 0xcf, c.sp


def mapper(c):
    m = c.memory
    return tuple(m.rawtags), m.ppu_addr, m.toggle, m.buffer, m.ppuctrl, tuple(m.chr_latches), m.upper, m.lastset


def live(c):
    m = c.memory
    return (bytes(m[3:11]), bytes(m[0x15a:0x17b]), bytes(m[0x101 + c.sp:0x200]),
            tuple(bytes(bank) for bank in m.ram))


def step(c):
    assert c.memory[c.pc] != 0, ('linked BRK', hex(c.pc), c.memory.rawtags)
    c.step()


def interrupt(c, kind):
    m = c.memory
    old, state, mapping = regs(c), live(c), mapper(c)
    skip = m[0x13a]
    lag, regular = lag_path(m)
    if kind == 'FF':
        assert m[0x0139] == 255 and m[0x0775]
        c.nmi()
    else:
        assert not c.p & 4
        c.irq()
        assert c.pc == 0x8000
    floor = 224
    visits = Counter()
    for _ in range(30000):
        if (c.pc, c.sp) == (old[0], old[5]):
            break
        floor = min(floor, c.sp)
        assert c.p & 4, ('forced-blank interrupt unexpectedly allows nested IRQ', kind, hex(c.pc))
        if c.pc in (lag, regular):
            visits[c.pc] += 1
        step(c)
    else:
        raise AssertionError(('vector return bound', kind, hex(c.pc), m.rawtags))
    assert regs(c) == old and live(c) == state, (kind, hex(old[0]))
    assert visits[lag] == (kind == 'FF') and visits[regular] == 0
    assert m[0x13a] == (skip + (kind == 'FF')) & 255
    new = mapper(c)
    if kind == 'FF':
        assert new[1:] == mapping[1:], ('cold PPU stream changed by NMI', hex(old[0]), mapping, new)
    if new[0] != mapping[0]:
        ins = bytes(m[c.pc:c.pc + 3])
        assert ins in (bytes.fromhex('8d1551'), bytes.fromhex('8d1651'), bytes.fromhex('8e1651'))
        window = 1 if ins[1] == 0x15 else 2
        assert new[0][window] == m[0x145 if window == 1 else O.CURRENT]
        assert all(mapping[0][i] == new[0][i] for i in range(4) if i != window)
    assert floor >= 0x7b
    return floor


def qualify(b, proof, spans, body):
    # Include every reached instruction in the compacted worker, remote
    # typed bridge, common mapper/headers, and resident A transport.
    ranges = tuple(spans) + ((251, 0xaf40, 0xafcd), (251, 0xb9d6, 0xb9f9), (193, 0xae00, 0xb013))
    all_counts, floor = Counter(), 224
    resumed = 0
    for owner in range(37, 43):
        print('Actual cold vectors owner', owner, flush=True)
        m = O.blank(b)
        O.scene(m, owner)
        c = entry(m)
        points = set()
        for _ in range(4_000_000):
            if c.pc == STOP:
                break
            if c.pc < 0x8000:
                used = 0x15a <= c.pc < 0x17b
                tag = m.rawtags[1]
            else:
                tag = m.rawtags[(c.pc - 0x8000) // 8192]
                used = any(tag == bank and lo <= c.pc < hi for bank, lo, hi in ranges)
            if used:
                phase = (m.ram[2][0x1fe0], m.ram[3][0x1fe0]) if owner == 42 else None
                key = tag, c.pc, c.sp, c.p & 4, phase
                if key not in points:
                    points.add(key)
                    O.clear_logs(m)
                    for kind in ('FF', 'IRQ') if not c.p & 4 else ('FF',):
                        # Keep the active PPU latch in the resumed trace
                        # while testing each representative cut separately.
                        fork = clone(c)
                        floor = min(floor, interrupt(fork, kind))
                        all_counts[owner, kind] += 1
                    if owner == 42 and tag == 251 and c.pc in (0xaf40, 0xb9d6):
                        floor = min(floor, interrupt(c, 'FF'))
                        resumed += 1
            step(c)
        else:
            raise AssertionError(('full cold bound', owner, hex(c.pc)))
        assert c.p & 1 and c.sp == 224
        assert len(points) > 100
        if owner == 42:
            cookie = bytes.fromhex(proof['cookie'])
            assert O.headers(m) == (cookie, cookie)
            assert bytes(m.ram[3][:2048]) == body
    return dict(actual_cuts={f'{owner}/{kind}': n for (owner, kind), n in sorted(all_counts.items())},
                minimum_SP=floor, own_full_cold_resumed_vectors=resumed,
                cold_nested_IRQ_enabled=False,
                scope='One cut per mapped PC, foreground SP and interrupt mask. Raw42 additionally distinguishes header validity phases. Real audio, PPU cursor and live application state checked.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    root = parser.parse_args().output.resolve()
    b, proof, spans, body = reconstruct(root)
    q = dict(passed=True, ROM_written=False, parent_SHA256=O.PIN,
             memory_only_SHA256=proof['expected_memory_only_SHA256'],
             proof_SHA256=O.SHA((root / 'proof.json').read_bytes()), vectors=qualify(b, proof, spans, body),
             source_SHA256=O.SHA(Path(__file__).read_bytes()))
    (root / 'irq.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q))


if __name__ == '__main__':
    main()
