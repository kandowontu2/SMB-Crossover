"""Compare the installed Mini-family command stream with a frame-mask encoding."""

import argparse
import json
from pathlib import Path
import sys

import measure_mini_audio_1108_v1 as M

sys.path.insert(0, str(M.ROOT/'tools/reference'))
from build_new_roster_audio import encode
from build_playlist_audio import lz


def stream(raw, start):
    pos = start
    output = bytearray()
    while True:
        flags = raw[pos]
        pos += 1
        for bit in range(8):
            value = raw[pos]
            pos += 1
            if not flags&(1<<bit):
                output.append(value)
                yield value, pos-start
                continue
            high = raw[pos]
            pos += 1
            distance = 1+value+((high&7)<<8)
            assert 1 <= distance <= min(len(output), 2048)
            for _ in range((high>>3)+3):
                value = output[-distance]
                output.append(value)
                yield value, pos-start


def project_stream(raw, start, macros):
    source = stream(raw,start)
    frames, writes, stack = [], [], []
    pos, bytes_read, macro_reads, calls = 0, 0, 0, 0

    def byte():
        nonlocal pos, bytes_read, macro_reads
        if stack:
            v = raw[pos]
            pos += 1
            macro_reads += 1
            return v
        v, bytes_read = next(source)
        return v

    for _ in range(300000):
        op = byte()
        if op in (0xff, 0x1c):
            assert not stack and not writes
            return frames, bytes_read, macro_reads, calls, op
        if op == 0xfe:
            frames.append(tuple(writes))
            writes.clear()
        elif op == 0x1d:
            n = byte()
            assert not writes and n > 0
            frames.extend([()]*n)
        elif op == 0x1f:
            pos = stack.pop()
        elif op >= 0x20:
            stack.append(pos)
            assert len(stack) <= 32
            pos = macros[op-0x20]
            calls += 1
        else:
            assert op < 16 or op == 21, op
            writes.append((op,byte()))
    raise AssertionError('Installed stream did not reach its authored terminal')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = M.ROM.read_bytes()
    assert M.sha(raw) == M.PIN
    b = M.bundle(raw)
    logical = lambda bank, pc: 16+8192*bank+(pc&8191)
    table = lambda name, index: raw[M.location(b,name)+index]
    low, high = (M.location(b,f'XgMacro{s}') for s in ('Lo','Hi'))
    macro_bank = (low-16)//8192
    macros = [logical(macro_bank, raw[low+i]+256*raw[high+i]) for i in range(high-low)]
    starts = {}
    for prefix in ('XgArea','XgLoop','XgEvent','XgEventLoop'):
        for i in range(7,14):
            at = logical(table(prefix+'Banks',i), table(prefix+'Lo',i)+256*table(prefix+'Hi',i))
            starts.setdefault(at,[]).append((prefix,i-7))

    rows, already = [], set()
    for at, clients in sorted(starts.items()):
        frames, size, macro_reads, calls, op = project_stream(raw,at,macros)
        duplicate = sum(len(f) != len(dict(f)) for f in frames)
        nonterminal_status = sum(any(r == 21 for r,_ in f[:-1]) for f in frames)
        frames_sorted = [tuple(sorted(dict(f).items())) for f in frames]
        mask = lz(encode(frames_sorted)+bytes([0xff if op == 0xff else 0xfe]))
        new = mask not in already
        already.add(mask)
        rows.append(dict(offset=at, clients=clients, source_frames=len(frames),
                         source_compressed_extent=size, macro_reads=macro_reads, macro_calls=calls,
                         frames_duplicate_register=duplicate, frames_status_before_other_register=nonterminal_status,
                         frame_mask_compressed_bytes=len(mask), unique_mask_bytes=len(mask) if new else 0,
                         terminal=op))
    total = sum(row['unique_mask_bytes'] for row in rows)
    result = dict(passed=True, parent_SHA256=M.PIN, family=7, unique_streams=len(rows),
                  minimum_extra_storage_if_existing_family_untouched=total,
                  mask_counterexample_frames=sum(row['frames_duplicate_register'] for row in rows),
                  mask_status_order_counterexample_frames=sum(row['frames_status_before_other_register'] for row in rows),
                  rows=rows, source_files=['src/expanded_audio.s','src/expanded_music.inc',
                                           'tools/reference/build_new_roster_audio.py','tools/reference/build_playlist_audio.py'],
                  scope='Actual installed pointer tables and 2 KiB LZSS/recursive macro semantics, bounded in memory. '
                        'Masked byte counts are sizing estimates. Existing codec does not preserve a source status write '
                        'before later commands in the same frame; any candidate requires matching ordered hardware writes. '
                        'No resource grant or ROM composition.')
    (args.output/'mask-feasibility.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
