"""Rebind qualified platform motion and world draw to the delivered Mini audio build."""

import argparse
import json
from pathlib import Path
import re
import shutil

import check_native_platform_direct_1110_v1 as Direct
import prepare_mini_audio_frame_token_native_1110 as Audio
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import (
    BUILD, CODE, COOKIE, KERNEL, bound_rom, verify_interrupts, verify_parent, verify_payload,
)
from prepare_selected_native_packet_v1 import R, prepare, sha
from qualify_mini_busy_1109 import bind_kernel


DECLARED = Direct.ROM
DECLARED_SHA = Direct.PIN
CURRENT = BUILD/'mini-audio-token-native-1110/candidate.nes'
PIN = Audio.EXPECTED
CONTROLLER = CURRENT.parent/'route/controller.lua'
READY = CONTROLLER.with_name('ready.json')
PLATFORM = BUILD/'native-platform-direct-1110/proof.json'
FIREBAR = BUILD/'native-firebar-admission-1110/proof.json'
FIREBAR_IRQ = FIREBAR.with_name('irq.json')
PROJECTION = BUILD/'mini-projection-reuse-1110/proof.json'
PROJECTION_IRQ = PROJECTION.with_name('irq.json')
NEW_KERNEL = PROJECTION.with_name('kernel.bin')
COMPONENTS = (PLATFORM, FIREBAR, PROJECTION)
RECEIPTS = (*COMPONENTS, FIREBAR_IRQ, PROJECTION_IRQ)


def verify_layout(proof, bank, expected):
    rows = proof['patches']
    assert len(rows) == len(expected)
    for row, (cpu, count) in zip(rows, expected, strict=True):
        extent = row.get('CPU_half_open', [row.get('start'), row.get('end_exclusive')])
        assert extent == [cpu, cpu+count] and 0xa000 <= cpu < cpu+count <= 0xc000, row
        assert row['physical_PRG'] == bank and row['file_offset'] == 16+8192*bank+cpu-0xa000, row
        assert len(bytes.fromhex(row['old_hex'])) == len(bytes.fromhex(row['new_hex'])) == count, row


def validate_direct_vectors(proof):
    vectors = proof['vectors']
    keys = ('lag_FF', 'IRQ', 'nested_IRQ', 'poisoned_lag_FF', 'poisoned_IRQ', 'poisoned_nested')
    assert all(vectors['cuts'][key] > 0 for key in keys)
    assert vectors['minimum_SP'][1] > 0x7a and vectors['actual_lag_PC'] != vectors['forbidden_regular_PC']
    assert proof['actor']['kinds']['rider'] > 0 and not proof['actor']['reads']
    assert not proof['game_loop']['reads'] and not proof['game_loop']['residual_at_GameLoop_return']
    assert {(r['vector'], r['secondary_queue'], r['catchup_skips']) for r in proof['actual_idle_loop']['cases']} == {
        ('lag_FF', False, 1), ('lag_FF', True, 0), ('IRQ', False, 0),
    }


def projection_exclusions():
    spans = load(PROJECTION)['Mini_sweep_CPU_spans']
    assert len(spans) == 2 and all(0xa000 <= lo < hi <= 0xb400 and hi-lo == 21 for lo, hi in spans)
    digest_bytes = (0x1fe3, 0x1ff0)
    return {2: [digest_bytes], 3: [(lo-0xa000, hi-0xa000) for lo, hi in spans]+[digest_bytes]}


def build_image():
    declared = bound_rom(DECLARED, DECLARED_SHA)
    raw = bound_rom(CURRENT, PIN)
    audio = load(Audio.RUNTIME)
    assert audio['passed'] and audio['parent_SHA256'] == Audio.F.PIN
    # Prove the entire difference between the qualification parent and the
    # installed base consists of the seven already delivered audio extents.
    rebound = bytearray(declared)
    audio_spans = []
    for row in audio['patches']:
        at = row['file_offset']
        old, new = (bytes.fromhex(row[k]) for k in ('old_hex', 'new_hex'))
        end = at+len(old)
        assert old and len(old) == len(new) and rebound[at:end] == old
        assert all(end <= lo or at >= hi for lo, hi in audio_spans)
        rebound[at:end] = new
        audio_spans.append((at, end))
    assert len(audio_spans) == 7 and rebound == raw

    candidate, occupied = bytearray(raw), audio_spans[:]
    for path in COMPONENTS:
        parent = raw if path == PROJECTION else declared
        isolated, proof, spans = verify_parent(parent, path)
        if path == PLATFORM:
            verify_layout(proof, 0, ((0xb489,22), (0xbe6f,47)))
            validate_direct_vectors(proof)
        elif path == FIREBAR:
            verify_layout(proof, 4, ((0xa261,21), (0xba23,20), (0xbea4,9)))
            verify_interrupts(path, FIREBAR_IRQ, proof)
        else:
            offsets = [(CODE+lo, CODE+hi) for lo, hi in projection_exclusions()[3][:-1]]
            assert [(lo,hi) for lo,hi,_,_ in spans] == offsets+[(COOKIE+3, COOKIE+16)]
            assert proof['source_preimage_reproduced'] and proof['Mini_kernel_bytes'] == 5120
            assert KERNEL.with_suffix('.lbl').read_bytes() == NEW_KERNEL.with_suffix('.lbl').read_bytes()
            verify_interrupts(path, PROJECTION_IRQ, proof)
            verify_payload(isolated, NEW_KERNEL)
        for start, end, old, new in spans:
            assert all(end <= lo or start >= hi for lo, hi in occupied), (path, start, end)
            assert raw[start:end] == old == candidate[start:end], (path, start, end)
            candidate[start:end] = new
            occupied.append((start, end))

    assert candidate[:16] == raw[:16]
    assert candidate[1048592:CODE] == raw[1048592:CODE] and candidate[CODE+5120:] == raw[CODE+5120:]
    assert all(candidate[lo:hi] == raw[lo:hi] for lo, hi in audio_spans)
    verify_payload(raw, KERNEL)
    verify_payload(candidate, NEW_KERNEL)
    return raw, bytes(candidate)


def controller_for(raw, candidate):
    ready = load(READY)
    assert ready['prepared'] and not ready['emulated_writes'] and ready['ROM_sha256'] == digest(raw) == PIN
    assert Path(ready['ROM']).resolve() == CURRENT.resolve()
    bindings = {Path(p).resolve(): h for p, h in ready['bindings'].items()}
    for p in (CONTROLLER, CURRENT, CURRENT.with_suffix('.json'), CURRENT.with_suffix('.dbg'),
              CURRENT.with_suffix('.lbl'), KERNEL, KERNEL.with_suffix('.lbl'), Audio.OBSERVER, Audio.RUNTIME):
        assert bindings[p.resolve()] == sha(p), p
    text = CONTROLLER.read_text(encoding='utf-8')
    assert text.count(PIN) == text.count(sha(KERNEL)) == 1
    assert all(token not in text for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                       r'\["bytes"\]=\{([\d,]+)\}', text)
    assert hooks
    for address, data in hooks:
        at, expected = 16+int(address), bytes(map(int, data.split(',')))
        assert raw[at:at+len(expected)] == candidate[at:at+len(expected)] == expected, address
    proof = load(Audio.RUNTIME)
    passive = Audio.OBSERVER.read_text(encoding='utf-8')
    assert text.endswith('\n'+Audio.audio_config(raw, proof)+passive)
    assert Audio.audio_config(raw, proof) == Audio.audio_config(candidate, proof)
    assert text.count("shot('mini-active-1-2');audioAssertFinished();result(true)") == 1
    text = bind_kernel(text.replace(PIN, digest(candidate)), NEW_KERNEL)
    text = text.replace(sha(KERNEL), sha(NEW_KERNEL))
    assert text.count(digest(candidate)) == text.count(sha(NEW_KERNEL)) == 1
    assert text.endswith('\n'+Audio.audio_config(candidate, proof)+passive)
    return text


def game_loop(before, after, *, projection_changed=False):
    images = [Direct.P.bundle(raw) for raw in (before, after)]
    bus, memory = Direct.N.Bus, Direct.D.memory
    masks = projection_exclusions()

    def normalize_immutable_payload(m):
        expected = m.bundle['raw']
        assert bytes(m.ram[3][:5120]) == expected[CODE:CODE+5120]
        assert all(bytes(m.ram[bank][0x1fe0:0x1ff0]) == expected[COOKIE:COOKIE+16] for bank in masks)
        state = memory(m)
        banks = list(state[5])
        for bank, spans in masks.items():
            image = bytearray(banks[bank])
            for lo, hi in spans:
                image[lo:hi] = bytes(hi-lo)
            banks[bank] = bytes(image)
        return state[:5]+(tuple(banks),)+state[6:]

    Direct.N.Bus = Direct.ObservedBus
    if projection_changed:
        Direct.D.memory = normalize_immutable_payload
    try:
        result = Direct.whole(images)
    finally:
        Direct.N.Bus = bus
        Direct.D.memory = memory
    assert not result['reads'] and not result['residual_at_GameLoop_return']
    return result


def verify_cpu(raw, candidate):
    cold = []
    attr_pin = load(PROJECTION)['exact_runtime_attribute_SHA256']
    for image in (raw, candidate):
        m = Direct.N.fresh(Direct.P.bundle(image))
        Direct.N.put(m, SelectedCharacter=41, OperMode=1, FamilyMainCommit=1,
                     DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
        cold.append(Direct.N.invoke(m,'MiniScene'))
        assert bytes(m.ram[3][:5120]) == image[CODE:CODE+5120] and m.ram[2][0x300] == 1
        # Cold boot replaces the final staging page with the native attributes.
        assert bytes(m.ram[2][0x1000:0x1300]) == image[CODE+5120:CODE+5120+0x300]
        assert digest(m.ram[2][0x1300:0x1400]) == attr_pin
        assert all(bytes(m.ram[bank][0x1fe0:0x1ff0]) == image[COOKIE:COOKIE+16] for bank in (2,3))
    assert cold[0] == cold[1], cold
    masks = projection_exclusions()
    whole = check_full_cpu(raw, candidate, masks)
    assert all(row['min_saved'] > 0 for row in whole), whole
    return dict(actual_MiniScene=cold[0], immutable_WRAM_comparison_masks=masks,
                whole_GameCore=whole, whole_GameLoop=game_loop(raw, candidate, projection_changed=True))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--check-only', action='store_true', help='Run all CPU checks in memory')
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(BUILD) and output != BUILD and not output.exists()
    raw, candidate = build_image()
    controller = controller_for(raw, candidate)
    cpu = verify_cpu(raw, candidate)
    candidate_sha = digest(candidate)
    summary = dict(parent_SHA256=PIN, candidate_SHA256=candidate_sha, **cpu)
    if not args.check_only:
        output.mkdir()
        rom = output/'candidate.nes'
        rom.write_bytes(candidate)
        for suffix in ('.dbg', '.lbl'):
            shutil.copyfile(CURRENT.with_suffix(suffix), rom.with_suffix(suffix))
        metadata = rom.with_suffix('.json')
        parent_meta = load(CURRENT.with_suffix('.json'))
        assert parent_meta['candidate_SHA256'] == PIN and parent_meta['kernel_SHA256'] == sha(KERNEL)
        parent_meta.update(summary, declared_component_parent_SHA256=DECLARED_SHA,
                           platform_firebar_proofs={str(p.resolve()):sha(p) for p in RECEIPTS},
                           kernel_SHA256=sha(NEW_KERNEL),
                           private_pending_current_interrupt_proof=True, verification='Private replay pending')
        metadata.write_text(json.dumps(parent_meta, indent=2)+'\n', encoding='utf-8')
        refs = {DECLARED, CURRENT, CONTROLLER, READY, metadata, KERNEL, KERNEL.with_suffix('.lbl'),
                NEW_KERNEL, NEW_KERNEL.with_suffix('.lbl'),
                Audio.OBSERVER, Audio.RUNTIME, Path(__file__), *RECEIPTS}
        prepare(output/'route', rom, controller, refs, expected=candidate_sha, timeout=180,
                allow_interactive=True, scope='Same delivered Mini full 1-1 route, lift contacts and passive audio observer.')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
