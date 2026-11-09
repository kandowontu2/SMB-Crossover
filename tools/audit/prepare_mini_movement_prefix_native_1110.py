"""Stage the frozen Mini movement prefix over the tested seven-group parent."""

import argparse
import json
from pathlib import Path
import shutil

import check_mini_movement_prefix_1110 as Movement
from deliver_mini_nightly_root_1103_v30 import proof as native_proof
from prepare_mini_lane_audio_native_1110 import verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R, BASE, PIN = Movement.R, Movement.BASE, Movement.PIN
COMPONENT = R/'build/mini-movement-prefix-1110/proof.json'
INTERRUPTS = COMPONENT.with_name('irq.json')
COMPONENT_PIN = '647d54830955a96623d8b474e864b0e7ab6e9c4cc918009440a7de395acfa10f'
INTERRUPTS_PIN = '4f7a26c605241a1ac8e452c60a5e71c2bbc5cf6331a81ba140932cadb65dd0ce'
FINAL_PIN = '4b06554d90ae643b7b259957bb5343618e181f0967cadd08776e55fab5271f02'
DELIVERED = R/'build/mini-helper-powered-injury-delivery-1110/verified-delivery.json'
ROLE = 'mini_movement_prefix_and_collision_branch'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def census():
    before = BASE.read_bytes()
    assert Movement.P.sha(before) == PIN
    assert sha(COMPONENT) == COMPONENT_PIN and sha(INTERRUPTS) == INTERRUPTS_PIN
    final, component, spans = verify_parent(before, COMPONENT)
    verify_interrupts(COMPONENT, INTERRUPTS, component)
    assert Movement.P.sha(final) == component['expected_memory_only_SHA256'] == FINAL_PIN
    assert [(lo,hi) for lo,hi,_,_ in spans] == [(706084,706133),(1037617,1037618)]

    parent_proof = BASE.with_name('proof.json')
    parent_meta = BASE.with_suffix('.json')
    parent_packet = BASE.parent/'mini'
    parent = read(parent_proof)
    meta, delivered = read(parent_meta), read(DELIVERED)
    assert parent['passed'] and parent['candidate_SHA256'] == meta['candidate_SHA256'] == PIN
    assert len(parent['apply_order']) == len(parent['groups']) == 7
    assert delivered['installed'] and delivered['Downloads_launch_verified'] and delivered['ROM_SHA256'] == PIN
    assert sha(parent_proof) == meta['composed_proof_SHA256'] == delivered['composed_proof_SHA256']
    for rows in parent['groups'].values():
        for row in rows:
            start = row['file_offset']
            end = start + len(bytes.fromhex(row['new_hex']))
            assert all(end <= lo or hi <= start for lo,hi,_,_ in spans), row

    restored = bytearray(final)
    for lo,hi,old,new in spans:
        assert final[lo:hi] == new
        restored[lo:hi] = old
    assert restored == before
    for rom in (before,final):
        verify_payload(rom, Movement.KERNEL)
    assert sha(Movement.KERNEL) == parent['kernel_SHA256'] == Movement.KERNEL_PIN

    result = native_proof(parent_packet, PIN)
    assert result['full_stage'] and result['last']['lives'] == 2
    controller = parent_packet/'controller.lua'
    ready = parent_packet/'ready.json'
    text = controller.read_text(encoding='utf-8')
    assert text.count(PIN) == 1 and text.count(Movement.KERNEL_PIN) == 1
    refs = {Path(__file__), COMPONENT, INTERRUPTS, DELIVERED, BASE, parent_proof, parent_meta,
            controller, ready, parent_packet/'capture/binding.json', parent_packet/'capture/result.json',
            Movement.KERNEL, Movement.KERNEL.with_suffix('.lbl')}
    for receipt in (component,read(INTERRUPTS)):
        for name,h in receipt['bindings'].items():
            path = Path(name)
            assert sha(path) == h,path
            refs.add(path)
    return bytes(restored), final, component, parent, meta, refs, text.replace(PIN, FINAL_PIN), read(ready)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build' and not out.exists()
    before, final, component, parent, meta, refs, controller, ready = census()
    whole = Movement.whole(before, final)
    assert json.loads(json.dumps(whole)) == component['whole_GameLoop']
    print('Exact final-minus GameLoop passed.',flush=True)
    vectors = Movement.vectors(before, final)
    irq = read(INTERRUPTS)
    assert all(irq[name] == value for name,value in json.loads(json.dumps(vectors)).items())
    print('Exact final-minus IRQ and NMI passed.',flush=True)

    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom) == FINAL_PIN
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(suffix), rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix)) == sha(BASE.with_suffix(suffix))
    report = out/'proof.json'
    proof = dict(passed=True, ROM_written=True, native_pending=True, candidate_SHA256=FINAL_PIN,
                 parent_SHA256=PIN, kernel_SHA256=Movement.KERNEL_PIN,
                 apply_order=[*parent['apply_order'],ROLE], inherited_groups=parent['apply_order'],
                 groups={ROLE:component['patches']}, final_minus_SHA256={ROLE:PIN},
                 whole_GameLoop=whole, vectors=vectors,
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    report.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=PIN, candidate_SHA256=FINAL_PIN, composed_proof_SHA256=sha(report),
                verification='Private movement-prefix replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,controller,refs|{report,manifest},expected=FINAL_PIN,
            timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])


if __name__ == '__main__':
    main()
