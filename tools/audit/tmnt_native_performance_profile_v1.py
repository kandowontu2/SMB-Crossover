"""Attribute the held TMNT music adapter's actual compiled CPU work.

This is a CPU-only original-song fixture. No emulator, game source mutation,
waveform, hardware DMC stall or completed-gameplay cadence claim follows.
"""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import json
from py65.disassembler import Disassembler
from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--calls', type=int, default=600)
    a = p.parse_args()
    assert sha(a.rom) == a.expected_sha256
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    b = load(a.rom)
    m = Memory(b)
    m.page(1, 0)
    m.page(2, 13)
    for n, v in dict(SelectedCharacter=19, OperMode=1, GameEngineSubroutine=8,
                     CurrentBank=128, CurrentBankC=141, Player_Y_HighPos=1).items():
        m[address(b, n)] = v
    totals, hits, calls = Counter(), Counter(), []
    labels = {address(b, n): n for n in b['syms'] if n.startswith('TnSourceSTA')}
    writer_sites = Counter()
    traces = []
    peak = 0
    for tick in range(a.calls+1):
        m[address(b, 'FrameCounter')] = tick & 255
        m[address(b, 'AreaMusicQueue')] = 1 if tick == 0 else 0
        m[address(b, 'EventMusicQueue')] = 0
        for i in range(16):
            m[address(b, 'GuestNativeDirty')+i] = 0
        c = NesMPU(memory=m, pc=address(b, 'ExpandedAudioUpdate'))
        c.sp = 253
        c.stPushWord(0x5aff)
        dis = Disassembler(c)
        row, own, writers = [], Counter(), 0
        for _ in range(50000):
            if c.pc == 0x5b00:
                break
            pc = c.pc
            bank = m.banks[(pc-32768)//8192] if pc >= 32768 else -1
            text = dis.instruction_at(pc)[1]
            start = c.processorCycles
            state = [c.a, c.x, c.y, c.p, c.sp]
            if bank == 123 and pc in labels:
                writers += 1
                ret = (m[256+(c.sp+1) % 256]+256*m[256+(c.sp+2) % 256]+1) & 65535
                writer_sites[labels[pc], ret, m[ret]] += 1
            c.step()
            elapsed = c.processorCycles-start
            key = bank, pc, text
            totals[key] += elapsed
            hits[key] += 1
            own[key] += elapsed
            row.append([bank, pc, text, elapsed, state])
        else:
            raise AssertionError(('Audio wrapper timeout', tick, hex(c.pc), m.banks))
        assert c.sp == 253
        calls.append(dict(tick=tick, cycles=c.processorCycles, writer_calls=writers))
        if tick and c.processorCycles >= peak:
            peak = c.processorCycles
            traces = row
            peak_tick = tick
            peak_top = own
    with gzip.open(out / 'peak-CPU-trace.json.gz', 'wt') as f:
        json.dump(traces, f, separators=(',', ':'))
    def catalog(counts):
        return [dict(bank=k[0], PC=k[1], instruction=k[2], cycles=v, calls=hits[k])
                for k, v in counts.most_common(70)]
    proof = dict(passed=True, native_run=False, production_changes=False,
                 ROM_sha256=sha(a.rom), tool_sha256=sha(Path(__file__)),
                 calls=calls, initialization_cycles=calls[0]['cycles'],
                 play_calls=a.calls, mean_play_cycles=sum(r['cycles'] for r in calls[1:])/a.calls,
                 peak_play_cycles=peak, peak_tick=peak_tick,
                 all_calls_hotspots=catalog(totals), peak_call_hotspots=catalog(peak_top),
                 writer_sites=[dict(helper=k[0], return_PC=k[1], next_opcode=k[2], calls=v)
                               for k, v in writer_sites.most_common()],
                 peak_CPU_trace_sha256=sha(out / 'peak-CPU-trace.json.gz'),
                 dependencies={str(ROOT / 'tools/audit' / n): sha(ROOT / 'tools/audit' / n)
                               for n in ['check_tmnt_render_oa.py', 'verify_native_relocation.py']},
                 scope=__doc__)
    (out / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps({k: proof[k] for k in ['passed', 'ROM_sha256', 'play_calls', 'mean_play_cycles',
                                           'peak_play_cycles', 'peak_tick', 'peak_call_hotspots']}, indent=2))


if __name__ == '__main__':
    main()
