"""Replay the proven Kirby inputs against the current installed MMC5 bytes."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from prepare_selected_native_packet_v1 import R, prepare, sha
from prepare_kirby_contacts_current_1108_v1 import LUA_DEPS


CASES = {
    'inhale': ('kirby-first-inhale-1110-v2',
               '328b51bc98adce0c30fc29b3dc08bd648d871883ccfbeef8203a646c279ef6b8'),
    'green': ('kirby-green-shell-1110-v3',
              '7f084c5e986179f51d10a12dd709920be5007a3a4b90758f1161f708444496d0'),
}
GREEN_APPROACH = R / 'tools/playthroughs/kirby_green_approach_1110.lua'
CURRENT = R / 'build/mini-contact-platform-combo-native-1110'
PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
PROOF = '9bb145df9aff1a33107d5e49bfc4fad1935df8f29fea3cf01f5baddebf556916'
DOWNLOADS = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=(*CASES, 'green-grounded', 'inhale-close'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    grounded = args.case == 'green-grounded'
    close = args.case == 'inhale-close'
    base_case = {'green-grounded': 'green', 'inhale-close': 'inhale'}.get(args.case, args.case)
    prior_name, ready_hash = CASES[base_case]
    prior = R / 'build' / prior_name
    prior_ready = prior / 'ready.json'
    binding = prior / 'capture/binding.json'
    result = prior / 'capture/result.json'
    controller = prior / 'controller.lua'
    proof_path = CURRENT / 'proof.json'
    rom = CURRENT / 'candidate.nes'
    assert sha(prior_ready) == ready_hash and sha(proof_path) == PROOF
    assert sha(rom) == sha(DOWNLOADS) == PIN
    proof = json.loads(proof_path.read_text())
    q = json.loads(prior_ready.read_text())
    old_pin = q['ROM_sha256']
    assert proof['parent_SHA256'] == old_pin and proof['candidate_SHA256'] == PIN
    assert json.loads(binding.read_text()) == dict(ROM_sha256=old_pin, ready_sha256=ready_hash, exit_code=0)
    old_result = json.loads(result.read_text())
    assert old_result['passed'] and old_result['controller_only'] and old_result['ROM_sha256'] == old_pin
    assert sha(controller) == q['bindings'][str(controller.resolve())]
    prior_rom = Path(q['ROM'])
    assert sha(prior_rom) == old_pin

    reconstructed = bytearray(prior_rom.read_bytes())
    span_count = 0
    new_groups = proof['apply_order'][-len(proof['groups']):]
    assert set(new_groups) == set(proof['groups'])
    for group in new_groups:
        for span in proof['groups'][group]:
            old, new = bytes.fromhex(span['old_hex']), bytes.fromhex(span['new_hex'])
            start = span['file_offset']
            end = start + len(old)
            assert len(old) == len(new) and reconstructed[start:end] == old
            reconstructed[start:end] = new
            span_count += 1
    assert reconstructed == rom.read_bytes()

    for hook in q['hooks'].values():
        start = 16 + hook['offset']
        data = bytes(hook['bytes'])
        assert reconstructed[start:start + len(data)] == data
    for owner in q.get('exact_owners', {}).values():
        start, size = owner['offset'], owner['size']
        assert hashlib.sha256(reconstructed[start:start + size]).hexdigest() == owner['sha256']
    for span in q.get('linked_shell_spans', {}).values():
        data = bytes.fromhex(span['bytes'])
        start = span['physical_offset']
        assert reconstructed[start:start + len(data)] == data

    text = controller.read_text(encoding='utf-8')
    assert text.count(old_pin) == 1 and old_pin in text.splitlines()[0]
    text = text.replace(old_pin, PIN)
    refs = [Path(__file__), proof_path, prior_ready, binding, result, controller]
    if grounded:
        start = text.index("  if koopa then\n", text.index('local function naturalControls()'))
        end = text.index("\n end\n if r('KbCopy')~=2", start)
        text = text[:start] + GREEN_APPROACH.read_text().rstrip('\n') + text[end:]
        refs.append(GREEN_APPROACH)
    elif close:
        old_range = 'gap>=34 and gap<=56'
        assert text.count(old_range) == 1
        text = text.replace(old_range, 'gap>=10 and gap<=16')
        # The linked early-suction leaf calls Suction while the opening
        # pose timer is live. Require that early capture in this replay.
        pull_offset = 0x9422a
        assert reconstructed[pull_offset:pull_offset + 14] == bytes.fromhex('2055a24c37a2eaeaeaeaeaeaeaea')
        old_guard = "or r('KbActionAge')~=0 or"
        assert text.count(old_guard) == 1
        text = text.replace(old_guard, "or r('KbActionAge')==0 or r('KbActionAge')>8 or\n    frame-fresh.player.frame>2 or")
        old_capture = "capture={player=player(),target=a,gap=gap,input=r('SavedJoypadBits')}"
        assert text.count(old_capture) == 1
        text = text.replace(old_capture, old_capture[:-1] + ",action_age=r('KbActionAge'),\n          frames_since_fresh=frame-fresh.player.frame}")
    text = text.replace("print('Kirby 29aa green-shell '", "print('Kirby current green-shell '")
    text = text.replace("print('Kirby 29aa first inhale '", "print('Kirby current first inhale '")
    sys.path.insert(0, str(LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    approach_scope = {
        'green-grounded': ' Settles on the ground early to meet the moving Koopa.',
        'inhale-close': ' Keeps walking until the first Goomba is 10–16 world pixels ahead before pressing B.',
    }.get(args.case, ' Controller inputs are unchanged.')
    prepare(args.output, rom, text, refs,
            expected=PIN, timeout=q['timeout'], allow_interactive=True,
            scope=q['scope'] + ' Exact current Downloads-equivalent ROM.' + approach_scope)
    ready = args.output / 'ready.json'
    current = json.loads(ready.read_text())
    current.update(previous_pass_SHA256=sha(result), compared_ROM_SHA256=old_pin,
                   compared_shared_patch_spans=span_count, hooks=q['hooks'],
                   controller_inputs_unchanged=not (grounded or close))
    ready.write_text(json.dumps(current, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
