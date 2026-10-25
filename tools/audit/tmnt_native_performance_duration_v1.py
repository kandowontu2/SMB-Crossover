"""Private CPU trial: exact final ADC replaces TMNT's repeated duration adds.

This is a binary/CPU experiment on an explicitly historical held adapter, not
a canonical source build, current integration or native performance pass.
"""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import itertools
import json
import shutil
from py65.assembler import Assembler
from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
OB = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')
BASE = '5af948178620e7abcbb7c15c538815841afc6a42a3b86d1cffe6f2861e24fbb7'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--plays', type=int, default=12000)
    a = p.parse_args()
    assert sha(a.rom) == BASE and 0 < a.plays <= 12000
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    old = load(a.rom)
    zp, ram = address(old, 'TnAudioZp'), address(old, 'TnAudioRam')
    asm = Assembler(NesMPU())
    # Original source stores channel X in RAM+$92 before reaching this loop.
    # All selected source executions assert that invariant at the actual entry.
    instructions = [f'LDA ${zp+2:04x}', 'ASL A', 'ASL A', 'ASL A', 'ASL A',
                    f'ORA ${ram+16:04x},X', 'TAX', 'LDA $A300,X',
                    'LDX #$01', f'STX ${zp+2:04x}', f'LDX ${ram+0x92:04x}',
                    'CLC', f'ADC ${ram+16:04x},X', f'DEC ${zp+2:04x}', 'RTS']
    helper = bytearray()
    for line in instructions:
        helper.extend(asm.assemble(line, pc=0xa200+len(helper)))
    (out / 'helper.s').write_text('\n'.join(instructions)+'\n')
    data = bytearray(a.rom.read_bytes())
    offset = lambda pc: 16+123*8192+pc-0xa000
    assert data[offset(0xa200):offset(0xa200)+len(helper)] == b'\xff'*len(helper)
    assert data[offset(0xa300):offset(0xa400)] == b'\xff'*256
    expected = bytes.fromhex('187d1074c6e0d0f8f003')
    assert data[offset(0xac7c):offset(0xac86)] == expected
    data[offset(0xa200):offset(0xa200)+len(helper)] = helper
    data[offset(0xa300):offset(0xa400)] = bytes(n*base for n in range(16) for base in range(16))
    data[offset(0xac7c):offset(0xac86)] = bytes.fromhex('2000a24c89ac')+b'\xea'*4
    candidate = out / 'candidate.nes'
    candidate.write_bytes(data)
    for suffix in ['.dbg', '.lbl', '.map']:
        shutil.copy2(a.rom.with_suffix(suffix), candidate.with_suffix(suffix))
    new = load(candidate)
    coverage = json.loads((OB / 'probe-v2/coverage.json').read_text())
    assert coverage['source_sha256'] == 'f220e8d069e321f392526d41e46f5d0f72966d5a22e56d2b269607c678bd58d9'
    prepared = json.loads((OB / 'driver-v3/preparation.json').read_text())
    move = lambda pc: pc+8192 if pc < 49152 else pc-8192
    sites = {move(q['pc']): q for q in prepared['APU_stores']}
    helpers = {address(old, q['helper']): q['helper'] for q in prepared['APU_stores']}
    loop_inputs = Counter()

    def bus(b):
        m = Memory(b)
        m.page(1, 123)
        m.page(2, 124)
        m[address(b, 'CurrentBankC')] = 252
        return m

    component = 0
    for n, base, channel, flags, y in itertools.product(range(1, 16), range(16), range(6),
                                                       [0x20, 0x61, 0xee, 0xff], [0, 1, 127, 255]):
        results = []
        for b in [old, new]:
            m = bus(b)
            m[zp+2], m[ram+16+channel], m[ram+0x92] = n, base, channel
            c = NesMPU(memory=m, pc=0xac7c)
            c.a, c.x, c.y, c.p, c.sp = base, channel, y, flags, 253
            for _ in range(400):
                if c.pc == 0xac8c:
                    break
                c.step()
            else:
                raise AssertionError('Duration component timeout')
            results.append((c.a, c.x, c.y, c.p & 207, c.sp, m[zp+2], m[ram+4+channel]))
        assert results[0] == results[1], (n, base, channel, flags, y, results)
        component += 1

    def call(b, m, c, entry, tick, song):
        c.sp = 253
        m[510], m[511] = 255, 1
        m.writes = []
        for i in range(16):
            m[address(b, 'GuestNativeDirty')+i] = 0
        if tick == -1:
            c.a, c.x, c.y, c.pc = song-1, 0, 0, address(b, 'TnNativeInit')
        else:
            c.pc = address(b, entry)
        begin = c.processorCycles
        stores = []
        for _ in range(50000):
            if c.pc == 512:
                break
            if c.pc == 0xac7c:
                n, base = m[zp+2], m[ram+16+c.x]
                assert 1 <= n <= 15 and base < 16 and c.x == m[ram+0x92], (song, tick, n, base, c.x, m[ram+0x92])
                loop_inputs[n, base, c.x] += 1
            if c.pc in helpers:
                ret = (m[256+(c.sp+1) % 256]+256*m[256+(c.sp+2) % 256]+1) & 65535
                site = sites.get(ret-3)
                if site:
                    index = c.x if site['mode'] == 'abx' else c.y if site['mode'] == 'aby' else 0
                    stores.append([site['address']+index, c.a])
            c.step()
        else:
            raise AssertionError(('Original/optimized call timeout', song, tick, hex(c.pc)))
        return (c.a, c.x, c.y, c.p & 207, c.sp, bytes(m[zp:zp+14]), bytes(m[ram:ram+216]),
                bytes(m[address(b, 'GuestNativeApu'):address(b, 'GuestNativeApu')+32]),
                tuple(m.banks)), stores, c.processorCycles-begin

    rows, total_calls, total_stores = [], 0, 0
    for song, info in coverage['songs'].items():
        path = OB / f'probe-v2/song-{int(song):02d}.json.gz'
        assert sha(path) == info['capture_sha256']
        expected = json.loads(gzip.decompress(path.read_bytes()))[:a.plays+1]
        contexts = [(b, bus(b)) for b in [old, new]]
        contexts = [(b, m, NesMPU(memory=m)) for b, m in contexts]
        costs = [[], []]
        for q in expected:
            pair = [call(b, m, c, 'TnNativePlay', q['call'], int(song)) for b, m, c in contexts]
            assert pair[0][0] == pair[1][0], ('Full driver return/state differs', song, q['call'])
            assert pair[0][1] == pair[1][1] == q['writes'], ('Ordered original APU request differs', song, q['call'])
            for i, r in enumerate(pair):
                costs[i].append(r[2])
            total_calls += 1
            total_stores += len(q['writes'])
        delta = [y-x for x, y in zip(*costs)]
        rows.append(dict(song=int(song), calls=len(expected), parent_cycles=sum(costs[0]),
                         candidate_cycles=sum(costs[1]), max_added_cycles=max(delta),
                         max_saved_cycles=-min(delta), parent_peak=max(costs[0]), candidate_peak=max(costs[1])))
        print('song', song, 'calls', len(expected), 'delta', sum(delta), flush=True)
    proof = dict(passed=True, canonical_source_build=False, native_run=False, current_build=False,
                 parent_ROM_sha256=BASE, candidate_ROM_sha256=sha(candidate),
                 original_source_sha256=coverage['source_sha256'], component_cases=component,
                 full_source_calls=total_calls, ordered_original_APU_requests=total_stores,
                 source_loop_entries_checked=sum(loop_inputs.values()), loop_inputs=[[*k, v] for k, v in sorted(loop_inputs.items())],
                 songs=rows, helper_bytes=len(helper), lookup_bytes=256, new_RAM_bytes=0,
                 tool_sha256=sha(Path(__file__)), scope=__doc__,
                 caveats=['Exact source nibble and saved-X invariants checked at actual entry; only legal source channel0..5.',
                          'PC/debug/map names are retained historical metadata; new helper has no fabricated debug aliases.',
                          'Private duration counter intermediate writes differ; all final driver registers, source private state and ordered source APU requests match.',
                          'No source/tick/store/channel deletion and no production or mapper/mirror integration claim.'])
    (out / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps({k: proof[k] for k in ['passed', 'candidate_ROM_sha256', 'component_cases', 'full_source_calls',
                                           'ordered_original_APU_requests', 'source_loop_entries_checked']}))


if __name__ == '__main__':
    main()
