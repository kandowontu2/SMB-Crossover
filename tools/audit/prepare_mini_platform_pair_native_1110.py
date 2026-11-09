"""Compose the measured parser/mixer trial with native lift collision offsets."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_platform_pair_offset_1110 as Lift
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
import prepare_mini_paired_shadow_audio_native_1110 as Mix
from prepare_selected_native_packet_v1 import prepare, sha


R, PIN, Stage = Mix.R, Mix.PIN, Mix.Stage
LIFT_PROOF = R / 'build/native-platform-pair-offset-1110/proof.json'
LIFT_PROOF_SHA = 'ab3c692079ee127e0518ce6a96cdbe6754a093e6db5cb9bf5100961949840dce'
ROLE = 'native_platform_pair_offset'
MIX_ROOT = R / 'build/mini-paired-shadow-audio-native-1110'
MIX_PIN = 'dea5674a5bffa8f1316486d7ef4aaf28bee782ce3b2410c004a4b7518612a54b'
MIX_PROOF_SHA = '8d49fb0650386035e9ae2ee00bfc62b039ec5b282ec1ae4ad2b97d194ef87d04'


def census():
    mix, minus, groups, parser, audio, parent, published, refs = Mix.census()
    assert sha(MIX_ROOT / 'candidate.nes') == Lift.P.sha(mix) == MIX_PIN
    path = MIX_ROOT / 'proof.json'
    observed = read(path)
    assert sha(path) == MIX_PROOF_SHA and observed['passed'] and observed['groups'] == groups
    bindings(observed['bindings'])
    packet = MIX_ROOT / 'mini'
    with Stage.Delivery.validators(MIX_PIN) as validation:
        route = validation.route_evidence(packet)
    assert route['cadence']['no_controller_read'] == 4
    assert route['cadence']['physical'] == route['cadence']['updates'] == 3500

    assert sha(LIFT_PROOF) == LIFT_PROOF_SHA
    lift = read(LIFT_PROOF)
    assert lift['passed'] and lift['parent_SHA256'] == PIN and lift['sampled_1460_calls'] == 2
    bindings(lift['bindings'])
    standalone, row = Lift.linked(Stage.BASE.read_bytes())
    assert Lift.P.sha(standalone) == lift['expected_memory_only_SHA256'] and [row] == lift['patches']
    final, linked_row = Lift.linked(mix)
    assert row == linked_row
    groups = {**groups, ROLE: [row]}
    minus = {name: install(raw, [row]) for name, raw in minus.items()} | {ROLE: mix}
    assert all(install(minus[name], rows) == final for name, rows in groups.items())
    refs.update({Path(__file__), path, MIX_ROOT / 'candidate.nes', LIFT_PROOF, *map(Path, lift['bindings']),
                 *(packet / 'capture' / name for name in ('timing.json', 'binding.json', 'result.json', 'audio-order.json'))})
    return final, minus, groups, parser, audio, lift, parent, published, refs


def qualify(final, minus, parser, audio, lift):
    checks = Mix.qualify(final, minus, parser, audio)
    before = minus[ROLE]
    result = dict(foreground=Lift.foreground(before, final), vectors=Lift.vectors(before, final))
    assert Stage.stable(result) == {key: lift[key] for key in result}
    print('Final-minus lift offset foreground, balance pair and real vectors passed.', flush=True)
    return checks | {ROLE: result}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build') and out != R / 'build' and not out.exists()
    final, minus, groups, parser, audio, lift, parent, published, refs = census()
    pin = Lift.P.sha(final)
    source, ready, metrics, route_refs = Stage.route_plan(final, published)
    print('Candidate', pin, flush=True)
    checks = qualify(final, minus, parser, audio, lift)
    refs.update(route_refs)
    out.mkdir()
    rom = out / 'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom) == pin
    for suffix in ('.lbl', '.dbg'):
        shutil.copyfile(Stage.BASE.with_suffix(suffix), rom.with_suffix(suffix))
    proof = dict(passed=True, ROM_written=True, native_pending=True, parent_SHA256=PIN, candidate_SHA256=pin,
                 kernel_SHA256=sha(Stage.KERNEL), groups=groups, apply_order=[*parent['apply_order'], *groups],
                 final_minus_SHA256={name: Lift.P.sha(raw) for name, raw in minus.items()}, final_minus_checks=checks,
                 previous_native_metrics=metrics, bindings={str(path.resolve()): sha(path) for path in sorted(refs)})
    proof_path = out / 'proof.json'
    proof_path.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom), ROM_written=True, parent_SHA256=PIN, candidate_SHA256=pin,
                  composed_proof_SHA256=sha(proof_path), groups=groups, apply_order=proof['apply_order'],
                  final_minus_SHA256=proof['final_minus_SHA256'], ordinary_native_pending=True,
                  verification='Parser, audio, and lift offset final-minus tests passed. Native cadence pending.')
    manifest.write_text(json.dumps(parent, indent=2) + '\n', encoding='utf-8')
    prepare(out / 'mini', rom, source, refs | {manifest, proof_path}, expected=pin, timeout=ready['timeout'],
            scope=ready['scope'], allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*')) == 8


if __name__ == '__main__':
    main()
