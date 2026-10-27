"""Independent, bounded reader for the Lua-only NESPPU01 qualification.

--source-check runs no emulator and writes no binary fixture. --review reads
ROOT's later one-shot output and writes ONE small proof beside it. No PNGs,
source/runtime copies, extraction, input changes or subprocess launch.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct

R = Path(__file__).resolve().parents[2]
LUA = Path(__file__).with_name('final_inventory_compact_capture_lua_qual_v1.lua')
ADAPTER = Path(__file__).with_name('final_inventory_compact_capture_v1.lua')
FRAME_BYTES = 256 * 240 * 4
MAGIC = b'NESPPU01' + struct.pack('<HHI', 256, 240, 32)
HEAD = struct.Struct('<BBHIIII')
CAP_BYTES, CAP_FILES = 10_000_000, 8
MASK = 0xffffffff


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bind(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path.read_bytes()))


def noise(n):
    value = 731
    out = bytearray()
    for _ in range(n):
        value = (1664525 * value + 1013904223) & MASK
        out.extend(value.to_bytes(4, 'little'))
    return bytes(out)


def repeated(n):
    return (0xff102030).to_bytes(4, 'little') * n


def mixed(n):
    return b''.join((0xff102030 if i % 257 < 129 else (i * 2654435761) & MASK)
                    .to_bytes(4, 'little') for i in range(n))


def change(raw, at, mask):
    pos = at * 4
    return raw[:pos] + (int.from_bytes(raw[pos:pos+4], 'little') ^ mask).to_bytes(4, 'little') + raw[pos+4:]


def xor(raw, mask):
    return b''.join((int.from_bytes(raw[i:i+4], 'little') ^ mask).to_bytes(4, 'little')
                    for i in range(0, len(raw), 4))


def checksum(raw):
    assert len(raw) % 4 == 0
    h = 2166136261
    for pos in range(0, len(raw), 4):
        h = ((h ^ int.from_bytes(raw[pos:pos+4], 'little')) * 16777619) & MASK
    return h


def decode(mode, payload, previous, size):
    """This reader does not import the adapter's existing Python decoder."""
    assert mode in (0, 1, 2) and 0 <= size <= FRAME_BYTES
    if mode == 0:
        result = payload
    else:
        result = bytearray()
        p = 0
        while p < len(payload):
            control = payload[p]
            p += 1
            count = (control & 0x7f) + 1
            encoded = 4 if control & 0x80 else count * 4
            assert p + encoded <= len(payload), 'Incomplete RLE token'
            part = payload[p:p+encoded]
            p += encoded
            result.extend(part * count if control & 0x80 else part)
            assert len(result) <= size, 'RLE overrun'
        if mode == 2:
            assert previous is not None and len(previous) == len(result), 'Missing XOR predecessor'
            result = bytearray(a ^ b for a, b in zip(result, previous))
        result = bytes(result)
    assert len(result) == size, 'Wrong decoded size'
    return result


def micro_cases():
    small = noise(257)
    return [
        ('raw-one', noise(1), None, True, 0),
        ('repeat-two', repeated(2), None, True, 1),
        *[(f'repeat-{n}', repeated(n), None, True, 1) for n in (127, 128, 129)],
        *[(f'literal-{n}', noise(n), None, True, 0) for n in (127, 128, 129)],
        ('mixed-257', mixed(257), None, True, 1),
        ('xor-identical', small, small, False, 2),
        ('xor-sparse', change(small, 128, 0x55aa0102), small, False, 2),
        ('keyframe-forbids-xor', small, small, True, 0),
        ('xor-constant', small, xor(small, 0x55aa55aa), False, 2),
    ]


def expected_records():
    noisy, solid = noise(FRAME_BYTES // 4), repeated(FRAME_BYTES // 4)
    for n in range(1, 67):
        raw = (solid if n == 1 else change(noisy, 257, 0x55aa0102) if n == 4
               else mixed(FRAME_BYTES // 4) if n == 5
               else change(noisy, 1023, 0xa0ff00ff) if n == 66 else noisy)
        mode = 1 if n in (1, 5) else 0 if n in (2, 6, 65) else 2
        yield dict(kind=1, mode=mode, name='actual-ppu.argb', full_ordinal=n, testcase=n+15), raw
    yield dict(kind=3, mode=0, name='diagnostic-CHR-0242.bin', full_ordinal=0, testcase=82), bytes(range(256))*4
    yield dict(kind=2, mode=1, name='different-named.argb', full_ordinal=0, testcase=83), solid
    yield dict(kind=1, mode=0, name='actual-ppu.argb', full_ordinal=67, testcase=84), noisy


def expected_aliases():
    return {1: 'first.argb', 2: 'reused-name.argb', 3: 'reused-name.argb',
            65: 'keyframe.argb', 66: 'last-delta.argb', 69: 'final.argb'}


def check(container, index, native):
    assert len(container) < 2_000_000 and container[:16] == MAGIC
    assert native['passed'] is True and native['lua_version'] == 'Lua 5.4'
    assert native['testcase_count'] == 85
    assert [q['name'] for q in native['encoder_cases']] == [q[0] for q in micro_cases()]
    for row, (name, raw, previous, keyframe, mode) in zip(native['encoder_cases'], micro_cases()):
        payload = bytes.fromhex(row['payload_hex'])
        assert row['name'] == name and row['mode'] == mode
        assert row['decoded_bytes'] == len(raw) and row['word_fnv1a32'] == checksum(raw)
        assert decode(mode, payload, previous, len(raw)) == raw, name
        assert not keyframe or mode != 2
    assert native['rejection_cases'] == [dict(name='unaligned-input', rejected=True),
                                         dict(name='wrong-previous-length', rejected=True)]
    frames = native['callback_frames']
    assert len(frames) == len(native['callback_cpu_seconds']) == 85
    assert all(type(n) is int for n in frames) and all(b > a for a, b in zip(frames, frames[1:]))
    assert all(type(n) in (int, float) and 0 <= n < 1 for n in native['callback_cpu_seconds'])
    assert native['registrations_at_startup'] == 1
    for key in ('runtime_registration_calls', 'emulated_writes', 'input_calls', 'screenshots'):
        assert native[key] == 0
    rows = [json.loads(line) for line in index.splitlines()]
    expected_index, p, previous = [], 16, None
    aliases = expected_aliases()
    decoded_hash = hashlib.sha256()
    modes = {0: 0, 1: 0, 2: 0}
    for seq, (want, raw) in enumerate(expected_records(), 1):
        start = p
        assert p + HEAD.size <= len(container), 'Missing record header'
        kind, mode, reserved, ordinal, mlen, plen, h = HEAD.unpack_from(container, p)
        p += HEAD.size
        assert (kind, mode, reserved, ordinal) == (want['kind'], want['mode'], 0, seq)
        assert 0 < mlen <= 4096 and 0 <= plen <= FRAME_BYTES and p+mlen+plen <= len(container)
        meta = json.loads(container[p:p+mlen])
        p += mlen
        payload = container[p:p+plen]
        p += plen
        stamp = dict(testcase=want['testcase'])
        assert meta == dict(name=want['name'], stamp=stamp, decoded_bytes=len(raw), full_ordinal=want['full_ordinal'])
        actual = decode(mode, payload, previous, len(raw))
        assert actual == raw and h == checksum(raw), f'Actual decoded bytes differ at record {seq}'
        if kind != 3:
            previous = actual
        if kind == 1:
            decoded_hash.update(actual)
        modes[mode] += 1
        expected_index.append(dict(type='record', record=seq, offset=start, bytes=p-start,
                                   kind=kind, mode=mode, name=want['name'], decoded_bytes=len(raw),
                                   stamp=stamp, full_ordinal=want['full_ordinal'], word_fnv1a32=h))
        if seq in aliases:
            expected_index.append(dict(type='alias', name=aliases[seq], record=seq,
                                       decoded_bytes=FRAME_BYTES, stamp=stamp))
    assert p == len(container), 'Unexpected extra/trailing records'
    assert rows == expected_index, 'Every physical/alias index field and event order must match'
    assert native['adapter_stats'] == dict(container_bytes=len(container), records=69, full_frames=67,
                                          open_virtual_files=0, full_closed=True, format='NESPPU01',
                                          per_frame_files=0, screenshots=0)
    return dict(passed=True, full_frames=67, physical_records=69, aliases=6, modes=modes,
                decoded_full_bytes=67*FRAME_BYTES, decoded_full_sha256=decoded_hash.hexdigest(),
                micro_codec_cases=13, adapter_rejection_cases=2, testcase_count=85,
                max_callback_cpu_seconds=max(native['callback_cpu_seconds']),
                container_sha256=sha(container), index_sha256=sha(index.encode()))


def source_check():
    text = LUA.read_text(encoding='utf-8')
    adapter = ADAPTER.read_text(encoding='utf-8')
    assert text.count('emu.addEventCallback(') == 1 and text.rstrip().endswith('end,emu.eventType.endFrame)')
    assert "dofile(TEST_DIR..'final_inventory_compact_capture_v1.lua')" in text
    for forbidden in ('addMemoryCallback', 'removeMemoryCallback', 'removeEventCallback', 'setInput',
                      'emu.write', 'setState', 'takeScreenshot', 'getScreenBuffer'):
        assert forbidden not in text and forbidden not in adapter
    assert text.count('oneTest()') == 2 and 'if step<=84 then oneTest()' in text
    assert 'container_bytes=2000000,records=70' in text
    assert 'local originalOpen=io.open' in text and "'lua-encoder-native.json'" in text
    return dict(passed=True, source_only=True, native_run=False, encoder_execution='UNRUN',
                one_startup_event_callback=True, one_test_per_endFrame=True,
                output_files=['captures.nesppuv1', 'captures-index.jsonl', 'lua-encoder-native.json'],
                capture_max_bytes=2_000_000, total_max_bytes=CAP_BYTES, total_max_files=CAP_FILES,
                screenshots=0, emulated_writes=0, input_calls=0, runtime_callback_mutations=0,
                scope='Only actual adapter encoder/container I/O. No old native74-callback/gameplay proof.')


def decoder_negatives():
    """No synthetic disk files: independent decoder boundary/corruption controls."""
    controls = []
    for n in (2, 127, 128):
        raw = repeated(n)
        payload = bytes([127+n]) + raw[:4]
        assert decode(1, payload, None, len(raw)) == raw
        assert decode(2, bytes([127+n])+b'\0'*4, raw, len(raw)) == raw
    samples = [
        ('bad-mode', lambda: decode(3, b'', None, 0)),
        ('truncated-repeat', lambda: decode(1, b'\x81\0', None, 8)),
        ('truncated-literal', lambda: decode(1, b'\x01\0'*2, None, 8)),
        ('overlong-run', lambda: decode(1, b'\xff'+b'\0'*4, None, 8)),
        ('wrong-raw-size', lambda: decode(0, b'123', None, 4)),
        ('missing-xor-predecessor', lambda: decode(2, b'\x81'+b'\0'*4, None, 8)),
        ('wrong-xor-size', lambda: decode(2, b'\x81'+b'\0'*4, b'\0'*4, 8)),
    ]
    for name, call in samples:
        try:
            call()
        except (AssertionError, ValueError):
            controls.append(dict(name=name, rejected=True))
        else:
            raise AssertionError(name)
    return controls


def reference_payload(raw, previous, mode):
    """Independent in-memory format fixture, never a substitute Lua encoder."""
    if mode == 0:
        return raw
    if mode == 2:
        raw = bytes(a ^ b for a, b in zip(raw, previous))
    words = [raw[i:i+4] for i in range(0, len(raw), 4)]
    output, literals = bytearray(), []
    def flush():
        while literals:
            take = literals[:128]
            del literals[:128]
            output.extend(bytes([len(take)-1])+b''.join(take))
    p = 0
    while p < len(words):
        end = p+1
        while end < len(words) and words[end] == words[p]:
            end += 1
        length = end-p
        if length == 1:
            literals.append(words[p])
            if len(literals) == 128:
                flush()
        else:
            flush()
            while length:
                take = min(128, length)
                output.extend(bytes([127+take])+words[p])
                length -= take
        p = end
    flush()
    return bytes(output)


def reader_reference_controls():
    container, rows, previous = bytearray(MAGIC), [], None
    micro = []
    for name, raw, prior, _, mode in micro_cases():
        micro.append(dict(name=name, mode=mode, decoded_bytes=len(raw),
                          payload_hex=reference_payload(raw, prior, mode).hex(),
                          word_fnv1a32=checksum(raw)))
    for seq, (want, raw) in enumerate(expected_records(), 1):
        offset = len(container)
        stamp = dict(testcase=want['testcase'])
        meta = dict(name=want['name'], stamp=stamp, decoded_bytes=len(raw), full_ordinal=want['full_ordinal'])
        mb = json.dumps(meta).encode()
        payload = reference_payload(raw, previous, want['mode'])
        h = checksum(raw)
        container.extend(HEAD.pack(want['kind'], want['mode'], 0, seq, len(mb), len(payload), h)+mb+payload)
        rows.append(dict(type='record', record=seq, offset=offset, bytes=len(container)-offset,
                         kind=want['kind'], mode=want['mode'], name=want['name'], decoded_bytes=len(raw),
                         stamp=stamp, full_ordinal=want['full_ordinal'], word_fnv1a32=h))
        if seq in expected_aliases():
            rows.append(dict(type='alias', name=expected_aliases()[seq], record=seq,
                             decoded_bytes=FRAME_BYTES, stamp=stamp))
        if want['kind'] != 3:
            previous = raw
    native = dict(passed=True, lua_version='Lua 5.4', testcase_count=85, encoder_cases=micro,
                  rejection_cases=[dict(name='unaligned-input', rejected=True), dict(name='wrong-previous-length', rejected=True)],
                  callback_frames=list(range(85)), callback_cpu_seconds=[0]*85,
                  registrations_at_startup=1, runtime_registration_calls=0, emulated_writes=0, input_calls=0, screenshots=0,
                  adapter_stats=dict(container_bytes=len(container), records=69, full_frames=67,
                                     open_virtual_files=0, full_closed=True, format='NESPPU01', per_frame_files=0, screenshots=0))
    index = ''.join(json.dumps(q)+'\n' for q in rows)
    result = check(bytes(container), index, native)
    negative = native_negatives(bytes(container), index, native)
    return dict(passed=True, full_reader_positive=True, full_reader_corruption_controls=negative,
                synthetic_encoded_bytes=len(container), decoded_full_sha256=result['decoded_full_sha256'],
                disk_files_created=0, Lua_executed=False,
                scope='Independent in-memory format fixture qualifies this reader, not the actual Lua encoder.')


def native_negatives(container, index, native):
    checks = []
    def reject(name, data=container, idx=index, receipt=native):
        try:
            check(data, idx, receipt)
        except (AssertionError, ValueError, UnicodeError, struct.error, KeyError, TypeError):
            checks.append(dict(name=name, rejected=True))
        else:
            raise AssertionError('Corruption accepted: '+name)
    reject('truncated-record', container[:-1])
    reject('changed-decoded-pixel', container[:-1]+bytes([container[-1]^1]))
    b = bytearray(container); b[20:24] = (99).to_bytes(4, 'little')
    reject('wrong-record-sequence', bytes(b))
    b = bytearray(container); b[16+16] ^= 1
    reject('changed-word-checksum', bytes(b))
    rows = [json.loads(s) for s in index.splitlines()]
    def encode(z):
        return ''.join(json.dumps(q)+'\n' for q in z)
    reject('missing-physical-index', idx=encode(rows[1:]))
    bad = copy.deepcopy(rows); next(q for q in bad if q['type']=='alias')['record'] = 999
    reject('wrong-alias-target', idx=encode(bad))
    bad = copy.deepcopy(rows); bad[0]['stamp']['testcase'] = 999
    reject('changed-index-stamp', idx=encode(bad))
    bad = copy.deepcopy(native); bad['encoder_cases'][0]['payload_hex'] = '00000000'
    reject('changed-micro-payload', receipt=bad)
    bad = copy.deepcopy(native); bad['callback_frames'][1] = bad['callback_frames'][0]
    reject('two-tests-same-endFrame', receipt=bad)
    return checks


def critical_settings(path):
    cfg = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    names = dict(Nes=dict(Region='Auto', DisableSprites=False, DisableBackground=False,
                         RemoveSpriteLimit=False, AdaptiveSpriteLimit=False,
                         RandomizeMapperPowerOnState=False, RandomizeCpuPpuAlignment=False,
                         PpuExtraScanlinesBeforeNmi=0, PpuExtraScanlinesAfterNmi=0),
                 Emulation=dict(RunAheadFrames=0, EmulationSpeed=100))
    assert {group: {name: cfg[group][name] for name in values} for group, values in names.items()} == names
    return names


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-check', action='store_true')
    p.add_argument('--review', type=Path)
    p.add_argument('--receipt', type=Path, help='Optional source-only JSON; existing tools/audit only')
    a = p.parse_args()
    assert a.source_check != bool(a.review), 'Choose source-check or review'
    if a.source_check:
        report = source_check()
        report['independent_decoder_controls'] = decoder_negatives()
        report['independent_reader_reference_controls'] = reader_reference_controls()
        report['bindings'] = [bind(q) for q in (LUA, ADAPTER, Path(__file__),
                              R/'tools/audit/run_mesen_isolated.py', R/'tools/run_mesen.py',
                              R/'tools/audit/capture_budget.py')]
        settings = Path('C:/Mesen2/settings.json')
        report['runtime_context_observed'] = dict(
            bindings=[bind(q) for q in (Path('C:/Mesen2/Mesen.exe'), Path('C:/Mesen2/MesenCore.dll'),
                      settings, Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes'))],
            critical_profile=critical_settings(settings), human_settings_written=False,
            note='Observed only, no runtime copied/launched. ROOT must verify actual critical profile/settings pre/post; command uses doNotSaveSettings and AllZeros override.')
        output = LUA.parent/'compact-lua-encoder-run-v1'
        assert not output.exists(), 'Prepared one-shot output must be absent; do not overwrite a previous run'
        report['prepared_commands_not_executed'] = dict(
            native=['python', '-B', str(R/'tools/audit/run_mesen_isolated.py'),
                    '--output', str(output), '--emulator', 'C:/Mesen2/Mesen.exe',
                    str(LUA), 'C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes',
                    '--timeout', '30', '--option=--doNotSaveSettings',
                    '--option=--nes.removeSpriteLimit=false', '--option=--nes.ramPowerOnState=AllZeros',
                    '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false'],
            review=['python', '-B', str(Path(__file__).resolve()), '--review', str(output)],
            expected_run_files=6, maximum_run_files=8, maximum_run_bytes=CAP_BYTES,
            no_run_output_directory_created=True, no_native_grant_inferred=True)
        if a.receipt:
            assert a.receipt.resolve().parent == LUA.parent and not a.receipt.exists()
            a.receipt.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    else:
        assert a.receipt is None
        out = a.review.resolve()
        files = [q for q in out.iterdir() if q.is_file()]
        assert all(not q.is_dir() for q in out.iterdir()), 'No output subtrees permitted'
        target = out/'lua-encoder-review.json'
        assert not target.exists() and len(files)+1 <= CAP_FILES
        assert sum(q.stat().st_size for q in files) < CAP_BYTES-100_000
        for q in files:
            assert q.suffix.lower() not in ('.png', '.argb', '.bmp', '.jpg'), 'No screenshots/frame dumps'
        container = (out/'captures.nesppuv1').read_bytes()
        index = (out/'captures-index.jsonl').read_text(encoding='utf-8')
        raw_proof = (out/'lua-encoder-native.json').read_bytes()
        native = json.loads(raw_proof)
        report = check(container, index, native)
        report.update(source_check())
        report.update(passed=True, source_only=False, native_run=True,
                      encoder_execution='Actual Mesen Lua 5.4; encoder/container only',
                      negative_controls=native_negatives(container, index, native)+decoder_negatives(),
                      output_bindings=[bind(q) for q in files],
                      source_bindings=[bind(q) for q in (LUA, ADAPTER, Path(__file__))],
                      native_proof_sha256=sha(raw_proof), no_gameplay_or_74callback_qualification=True)
        report['critical_profile_after'] = critical_settings('C:/Mesen2/settings.json')
        report['human_settings_sha256_after_informational'] = sha(Path('C:/Mesen2/settings.json').read_bytes())
        target.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        assert len(files)+1 <= CAP_FILES and sum(q.stat().st_size for q in out.iterdir()) <= CAP_BYTES
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
