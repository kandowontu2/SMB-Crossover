"""Rebase the qualified Mini body transport and prepare one native replay."""

import argparse
import json
from pathlib import Path
import shutil

import check_mini_box_transport_1110 as Transport
import check_mini_box_transport_irq_1110 as IRQ
import check_native_platform_box_reuse_1110_v1 as PlatformBox
import prepare_helper_camera_render_composite_1110 as Camera
from check_mini_funded_actor_1108_v3 import install
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha


BASE = R/'build/helper-camera-render-composite-1110/candidate.nes'
PIN = 'f2050c1964b53b4bd3dc2e5f24c2ed688d47ad79a8aef6bb2cfd55e28b3e7e42'
EXPECTED = '03c0cfe6d4562f6b7970199ce2d6ffa6f2f0f905a8cb8425945add6fcb71585d'
BASE_PROOF = BASE.with_name('proof.json')
TRANSPORT_PROOF = R/'build/mini-box-transport-1110/proof.json'
TRANSPORT_IRQ = TRANSPORT_PROOF.with_name('irq.json')
SOURCE_PACKET = BASE.parent/'mini'


def image_pair():
    declared = bound_rom(Transport.BASE,Transport.PIN)
    before = bound_rom(BASE,PIN)
    qualified = load(BASE_PROOF)
    assert qualified['passed'] and qualified['candidate_SHA256']==PIN
    assert qualified['parent_SHA256']==Transport.PIN
    assert set(qualified['groups'])=={'camera','goomba','relative','platform_box'}
    grouped = [patch for rows in qualified['groups'].values() for patch in rows]
    assert install(declared,grouped)==before
    assert Camera.source_bindings(BASE_PROOF)

    isolated,proof,parts = verify_parent(declared,TRANSPORT_PROOF)
    assert digest(isolated)==proof['expected_memory_only_SHA256']
    verify_interrupts(TRANSPORT_PROOF,TRANSPORT_IRQ,proof)
    assert Camera.source_bindings(TRANSPORT_PROOF)
    assert Camera.extent(proof)==[(86,lo,hi) for lo,hi in Transport.PATCH_SPANS]
    occupied = [(row['file_offset'],row['file_offset']+len(bytes.fromhex(row['old_hex']))) for row in grouped]
    for lo,hi,old,_ in parts:
        assert declared[lo:hi]==before[lo:hi]==old
        assert all(hi<=a or lo>=b for a,b in occupied),(lo,hi)
    assert Transport.census(before)==Transport.census(declared)
    final = install(before,proof['patches'])
    assert digest(final)==EXPECTED and Camera.remove(final,parts)==before
    assert final[:16]==before[:16] and final[Camera.PRG_END:]==before[Camera.PRG_END:]
    assert final[Camera.Mini.COOKIE:Camera.Mini.COOKIE+16]==before[Camera.Mini.COOKIE:Camera.Mini.COOKIE+16]
    audio = Camera.Mini.Audio
    audio_spans = audio.load(audio.RUNTIME)['patches']
    assert len(audio_spans)==7
    for row in audio_spans:
        at = row['file_offset']
        data = bytes.fromhex(row['new_hex'])
        assert before[at:at+len(data)]==final[at:at+len(data)]==data
    for image in (before,final):
        verify_payload(image,Camera.Mini.NEW_KERNEL)
    return before,final,proof


def qualify(before,final,proof):
    body = Transport.box_cases(before,final)
    life = Transport.lifecycle_cases(before,final)
    assert body==proof['body_box'] and life==proof['lifecycle']
    cold = Camera.cold_mini(before,final)
    core = check_full_cpu(before,final,{})
    assert core==proof['whole_GameCore']
    loop = PlatformBox.whole(before,final)
    print(json.dumps(dict(whole_GameCore=core,whole_GameLoop=loop)),flush=True)
    vectors = IRQ.vectors(before,final)
    assert all(vectors['cuts'][name]>0 for name in ('lag_FF','IRQ','nested_IRQ','resumed'))
    return dict(body_box=body,lifecycle=life,cold_Mini=cold,whole_GameCore=core,
                whole_GameLoop=loop,vectors=vectors)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R/'build') and not output.exists()
    before,final,proof = image_pair()
    text,refs,ready = Camera.Stage.packet_input(SOURCE_PACKET,BASE,final,None,'mini')
    original = (SOURCE_PACKET/'controller.lua').read_text(encoding='utf-8')
    assert original.count(PIN)==1 and text==original.replace(PIN,EXPECTED)
    meta = load(BASE.with_suffix('.json'))
    assert meta['candidate_SHA256']==PIN and meta['kernel_SHA256']==sha(Camera.Mini.NEW_KERNEL)
    result = qualify(before,final,proof)
    print(json.dumps(dict(vectors=result['vectors']['cuts'],min_ISR_SP=result['vectors']['minimum_ISR_SP'])),flush=True)

    output.mkdir()
    report = output/'proof.json'
    refs.update((Path(__file__),Path(Transport.__file__),Path(IRQ.__file__),Path(PlatformBox.__file__),
                 Path(Camera.__file__),BASE_PROOF,TRANSPORT_PROOF,TRANSPORT_IRQ,
                 Transport.SOURCE,Camera.Mini.NEW_KERNEL,Camera.Mini.Audio.RUNTIME))
    receipt = dict(passed=True,source_CPU_only=True,native_route_pending=True,ROM_written=True,
                   parent_SHA256=PIN,final_minus_body_SHA256=digest(before),candidate_SHA256=EXPECTED,
                   declared_parent_SHA256=Transport.PIN,patches=proof['patches'],
                   changed_bytes=sum(a!=b for a,b in zip(before,final,strict=True)),
                   exact_header_CHR_code_metadata_cookie_and_audio=True,
                   controller_change='Exact f205 controller with only its bound ROM digest replaced.',
                   bindings={str(path.resolve()):sha(path) for path in sorted(refs)},**result)
    assert receipt['changed_bytes']==245
    report.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    rom = output/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==EXPECTED
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(BASE.with_suffix(suffix))
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=PIN,candidate_SHA256=EXPECTED,
                verification='Private Mini body transport native replay pending',
                body_transport_proof_SHA256=sha(report),body_transport_source_SHA256=sha(TRANSPORT_PROOF))
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'mini',rom,text,refs | {report,manifest},expected=EXPECTED,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,candidate_SHA256=EXPECTED,native_route_pending=True)),flush=True)


if __name__=='__main__':
    main()
