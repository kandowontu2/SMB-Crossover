"""Derive current-build native Kirby tests without relabelling parent CPU results."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import sys

from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address as compiled_address, location as compiled_location
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]
PARENT = 'ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
CURRENT = 'bdf9ca2bfe69ee93ca85f1b5e5319e474d9f01aa641c79a58cd9bd602253c40e'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', choices=['basics', 'copies-low', 'copies-high', 'meta'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(ROOT / 'build') and not out.exists()
    handoff = ROOT / 'build/current-ab221e-kirby-meta-earned-handoff-v1.json'
    assert sha(handoff) == '8f068636399cb7f0f5fd240566d5f0a2a3ae58f5563c587f67c81b02a04a814c'
    profile = next(q for q in json.loads(handoff.read_text())['profiles'] if q['unit'] == args.unit)
    old_ready = Path(profile['path'])
    assert sha(old_ready) == profile['sha256']
    original = json.loads(old_ready.read_text())
    for binding in original['bindings']:
        assert sha(Path(binding['path'])) == binding['sha256'], binding['path']
    old_rom = ROOT / 'build/mega_proto_body_palette_9ea.nes'
    new_rom = ROOT / 'build/cv3-life-watch-bdf9-production.nes'
    assert sha(old_rom) == PARENT and sha(new_rom) == CURRENT
    before, after = old_rom.read_bytes(), new_rom.read_bytes()
    assert len(before) == len(after)
    changes = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    counts = {bank: sum((i - 16) // 8192 == bank for i in changes) for bank in [82, 84]}
    assert len(changes) == 31 and counts == {82: 23, 84: 8}
    assert all((i - 16) // 8192 in counts for i in changes)
    built = scoped_load(new_rom)
    raw = built['raw']
    address = lambda name: compiled_address(built, name)
    location = lambda name: compiled_location(built, name)
    cfg = json.loads((old_ready.parent / 'config.json').read_text())
    assert cfg['ROM_sha256'] == PARENT
    for name, value in cfg['ram'].items():
        assert address(name) == value, name
    for hook in cfg['hooks'].values():
        at = location(hook['source_symbol']) + hook['source_delta']
        assert address(hook['source_symbol']) + hook['source_delta'] == hook['pc']
        assert list(raw[at:at + len(hook['bytes'])]) == hook['bytes']
        bank = (at - 16) // 8192
        assert bank in hook['banks']
        for other in hook['banks']:
            clone = 16 + other * 8192 + (at - 16) % 8192
            assert raw[clone:clone + len(hook['bytes'])] == bytes(hook['bytes'])
    for name, table in cfg['metatiles'].items():
        at = location(name)
        assert ((at - 16) // 8192, (at - 16) % 8192) == (table['bank'], table['offset'])
    cfg['ROM_sha256'] = CURRENT
    out.mkdir(parents=True)
    put(out / 'config.json', cfg)
    fixture = ROOT / 'tools/audit/current_kirby_meta_earned_v1.lua'
    (out / 'run.lua').write_text('CURRENT_KIRBY_META_EARNED=' + lua(cfg) +
                               '\ndofile([=[' + fixture.as_posix() + ']=])\n', newline='\n')
    command = json.loads((old_ready.parent / 'command.json').read_text())
    replacements = {str(old_ready.parent / 'run.lua'): str(out / 'run.lua'),
                    str(old_ready.parent / 'native'): str(out / 'native'),
                    str(old_rom): str(new_rom)}
    assert all(command['argv'].count(key) == 1 for key in replacements)
    command['argv'] = [replacements.get(arg, arg) for arg in command['argv']]
    put(out / 'command.json', command)
    proof = dict(passed=True, parent_ROM_sha256=PARENT, actual_native_target_sha256=CURRENT,
                 changed_ROM_bytes=31, changed_banks=counts, actual_ram_and_hooks_checked=True,
                 actual_mirrored_hook_bytes_checked=True, literal_fixture_unchanged=True,
                 original_CPU_campaign_not_rerun=True,
                 parent_CPU_proof=str(old_ready.parent / 'source-controls.json'),
                 parent_CPU_proof_sha256=sha(old_ready.parent / 'source-controls.json'),
                 limits='The original CPU campaign remains labelled ab221e. Current compiled '
                 'RAM/hook/mirror/table preflight and the sparse CV3-only ROM delta qualify '
                 'this native launch. They are not a current CPU campaign, native, graphics, '
                 'sound, timing, or full-route pass.')
    put(out / 'candidate-preflight.json', proof)
    ready = copy.deepcopy(original)
    ready.update(ROM_sha256=CURRENT, source_CPU_passed=False,
                 parent_source_CPU_passed=True, parent_source_CPU_ROM_sha256=PARENT,
                 current_compiled_preflight_passed=True,
                 source_CPU_campaign_rerun=False, predecessor_ready=str(old_ready),
                 predecessor_ready_sha256=profile['sha256'])
    files = [Path(q['path']) for q in original['bindings']]
    files += [old_ready, handoff, Path(__file__), new_rom, new_rom.with_suffix('.dbg'),
              new_rom.with_suffix('.lbl')] + [out / n for n in
              ['config.json', 'run.lua', 'command.json', 'candidate-preflight.json']]
    ready['bindings'] = [dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p))
                         for p in dict.fromkeys(files)]
    put(out / 'prepared-not-run.json', ready)
    print(json.dumps(dict(prepared=True, native_run=False, unit=args.unit,
                          ready=str(out / 'prepared-not-run.json'),
                          sha256=sha(out / 'prepared-not-run.json'), bindings=len(ready['bindings']))))


if __name__ == '__main__':
    main()
