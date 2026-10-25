"""Read-only linker-gap and original music-call inventory for a private plan."""
from pathlib import Path
from collections import defaultdict
import argparse, hashlib, json
from py65.disassembler import Disassembler
from verify_native_relocation import NesMPU
from link_pit_rygar_sophia_audit_cpu import scoped_load
from mike_parodius_rom_probe import RomBus, SOURCE, EXPECTED

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    b = scoped_load(a.rom)
    used = defaultdict(list)
    for seg in b['segs'].values():
        if 'ooffs' not in seg:
            continue
        off, size = int(seg['ooffs'], 0), int(seg['size'], 0)
        if not (16 <= off < 16 + 128 * 8192) or not size:
            continue
        for i in range(128):
            lo, hi = max(off, 16 + i * 8192), min(off + size, 16 + (i + 1) * 8192)
            if lo < hi:
                used[i].append([lo - 16 - i * 8192, hi - 16 - i * 8192, seg['name']])
    gaps = []
    reserved = {63: 'future TMNT native music', 123: 'Mac native music',
                124: 'future TMNT cold adapter', 125: 'CV3 fixed mirror and cold block',
                126: 'low resident bank; private dead pads already reserved',
                127: 'fixed code and all existing DPCM'}
    for i in range(128):
        cursor = 0
        for lo, hi, name in sorted(used[i]):
            if lo > cursor:
                gaps.append(dict(bank=i, first=cursor, end=lo, bytes=lo - cursor,
                                 excluded=reserved.get(i), kind='declared-segment gap'))
            cursor = max(cursor, hi)
        if cursor < 8192:
            gaps.append(dict(bank=i, first=cursor, end=8192, bytes=8192 - cursor,
                             excluded=reserved.get(i), kind='declared tail'))
    raw = SOURCE.read_bytes()
    assert sha(SOURCE) == EXPECTED
    calls = []
    for i in range(16):
        body = raw[16 + i * 8192:16 + (i + 1) * 8192]
        for at in range(len(body) - 2):
            if body[at:at + 3] in [bytes.fromhex('2020fe'), bytes.fromhex('4c20fe')]:
                calls.append(dict(bank=i, offset=at, cpu_address=(0xe000 if i == 15 else 0xc000 if i == 14 else 0x8000) + at,
                                  context_before=body[max(0, at - 24):at].hex(), context_after=body[at:at + 12].hex()))
    m = RomBus(raw)
    c = NesMPU(memory=m)
    dis = Disassembler(c)
    instructions = []
    for lo, hi in [(0xfe07, 0xfe42), (0xc542, 0xc720), (0x80a2, 0x81ff)]:
        instructions.append(f'\nSPAN {lo:04X}..{hi:04X}')
        while lo < hi:
            n, text = dis.instruction_at(lo)
            instructions.append(f'{lo:04X} {text}')
            lo += n
    (out / 'original-control-disassembly.txt').write_text('\n'.join(instructions) + '\n')
    report = dict(passed=True, ROM_sha256=sha(a.rom), original_ROM_sha256=EXPECTED,
                  source_only=True, allocated_nothing=True, game_changes=False,
                  gaps=gaps, candidate_tail_bytes=sum(g['bytes'] for g in gaps if not g['excluded']),
                  largest_candidates=sorted([g for g in gaps if not g['excluded']], key=lambda x: -x['bytes'])[:24],
                  bank38_segments=used[38], bank125_entirely_reserved=True,
                  original_FE20_calls=calls, original_FE20_call_count=len(calls),
                  original_header_bytes=list(raw[:16]),
                  current_header_bytes=list(b['raw'][:16]), tool_sha256=sha(Path(__file__)),
                  limits='Linker-declared gaps only; no interior padding or apparent FF bytes claimed free. Reservations are retained. Calls are raw opcode candidates pending control-flow proof.')
    (out / 'layout.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['ROM_sha256', 'candidate_tail_bytes', 'largest_candidates', 'bank38_segments', 'original_FE20_call_count']}))


if __name__ == '__main__':
    main()
