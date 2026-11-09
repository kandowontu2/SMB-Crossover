"""Verify the native manual controls and combine their exact edits with the title footer."""

import argparse
import hashlib
import json
from pathlib import Path

from prepare_manual_platform_native_1110 import BASE, PIN, R
from prepare_selected_native_packet_v1 import sha
from prepare_title_credit_1110 import apply_credit, encode


MANUAL = R / 'build/manual-vertical-platform-1110/proof.json'
MANUAL_NATIVE = R / 'build/manual-platform-native-1110'
TITLE = R / 'build/title-credit-1110/proof.json'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
MANUAL_PIN = '00cf5481231239967994bd3ad69ea65fe9f02c7dc74560a997d3722ad6a4566c'
TITLE_PIN = '37d63ad56d02f70bb47cbbbc9f46a1fa3e289f25fe1878b74ae5e31774c04997'
CREDIT = '   BY KANDOWONTU  '


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def apply(parent, rows):
    result = bytearray(parent)
    end = 16
    for row in sorted(rows, key=lambda p: p['file_offset']):
        at = row['file_offset']
        before, after = (bytes.fromhex(row[k]) for k in ('old_hex', 'new_hex'))
        assert before and len(before) == len(after) and end <= at <= len(parent) - len(before), at
        end = at + len(before)
        assert result[at:end] == before, at
        result[at:end] = after
    return bytes(result)


def check_paths(bindings):
    for name, value in bindings.items():
        assert sha(R / name) == value, name


def native_result(packet, rom, pin):
    ready_path, capture = packet / 'ready.json', packet / 'capture'
    ready, bound, result = (read(p) for p in (ready_path, capture/'binding.json', capture/'result.json'))
    assert Path(ready['ROM']).resolve() == rom.resolve()
    assert ready['ROM_sha256'] == bound['ROM_sha256'] == result['ROM_sha256'] == pin
    assert not ready['emulated_writes'] and bound['exit_code'] == 0 and bound['ready_sha256'] == sha(ready_path)
    assert result['passed'] and result['controller_only'] and not result['script_RAM_writes']
    check_paths(ready['bindings'])
    return result


def manual_result(packet, rom, pin, owner):
    result = native_result(packet, rom, pin)
    assert result['owner'] == owner and result['terminal']['lives'] == 2
    births = result['birth_events']
    assert [b['births'] for b in births] == [1, 2]
    center = {41: 4, 34: 8}[owner]
    for birth in births:
        actor, = birth['actors']
        assert abs(actor['x'] + 16 - (birth['x'] + center)) <= 1 and actor['y'] == birth['y'] + 32
    samples = {p['phase']: p for p in result['samples']}
    assert all(not samples[phase]['actors'] for phase in ('idle', 'select_only', 'up_only'))
    assert samples['held_combo']['births'] == 1 and samples['replacement_held']['births'] == 2
    assert len(samples['held_combo']['actors']) == len(samples['replacement_held']['actors']) == 1
    return result


def compose():
    parent = BASE.read_bytes()
    manual, title = read(MANUAL), read(TITLE)
    assert digest(parent) == manual['parent_SHA256'] == title['parent_SHA256'] == PIN
    assert manual['passed'] and title['passed'] and len(manual['patches']) == 10 and len(title['patches']) == 1
    check_paths(manual['bindings'])
    # The title source was compiled against Downloads. Bind the identical
    # frozen parent so delivery verification remains usable after replacement.
    check_paths({str(BASE) if Path(p).resolve() == NIGHTLY.resolve() else p: h
                 for p, h in title['bindings'].items()})
    platform = apply(parent, manual['patches'])
    footer = apply(parent, title['patches'])
    assert digest(platform) == manual['expected_memory_only_SHA256'] == MANUAL_PIN
    assert platform == (MANUAL_NATIVE/'candidate.nes').read_bytes()
    assert digest(footer) == title['candidate_SHA256'] == TITLE_PIN
    assert apply_credit(parent, encode(CREDIT)) == (footer, title['patches'][0])
    for name, owner in (('mini', 41), ('karnov', 34)):
        manual_result(MANUAL_NATIVE/name, MANUAL_NATIVE/'candidate.nes', MANUAL_PIN, owner)
    rows = sorted(manual['patches'] + title['patches'], key=lambda p: p['file_offset'])
    combined = apply(parent, rows)
    assert combined == apply(platform, title['patches']) == apply(footer, manual['patches'])
    return combined, rows


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build' and not out.exists()
    combined, patches = compose()
    refs = [Path(__file__), BASE, MANUAL, TITLE]
    for owner in ('mini', 'karnov'):
        refs.extend(MANUAL_NATIVE/owner/name for name in ('ready.json', 'capture/binding.json', 'capture/result.json'))
    q = dict(passed=True, ROM_written=False, parent_SHA256=PIN, expected_memory_only_SHA256=digest(combined),
             component_SHA256={'manual_platform': MANUAL_PIN, 'title_only': TITLE_PIN}, patches=patches,
             title_text=CREDIT.strip(), title_ppu_address=0x22c6,
             bindings={p.relative_to(R).as_posix(): sha(p) for p in refs})
    out.mkdir()
    (out/'proof.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')
    print(q['expected_memory_only_SHA256'], flush=True)


if __name__ == '__main__':
    main()
