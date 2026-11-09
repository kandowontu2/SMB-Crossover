"""Stage the qualified Tank contact shortcut with the unchanged Mini route."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_contact_tank_precheck_v2_1110 as Contact
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
import deliver_mini_parser_audio_1110 as Prior
from prepare_mini_lane_audio_native_1110 import verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R, BASE, PARENT = Contact.C.R,Contact.C.BASE,Contact.C.PIN
PIN = '9b6e2582ae7f1263c0128590e287331301b1c97590c9a2500486f04083ca06b1'
COMPONENT = R/'build/native-contact-tank-precheck-v2-1110/proof.json'
COMPONENT_PIN = '6bf666fee8f20f6e0a078fb97db02c4a3c7b5c7be4d409c1e78f6df37ba1351b'
PARENT_PROOF_PIN = '3441db7e094d0aa5a843928f67a15fff2c92a740ad0ebf2b18e4e1cd5e2edf0c'
PARENT_DELIVERY = R/'build/mini-parser-audio-delivery-1110/verified-delivery.json'
ROLE = 'native_contact_tank_precheck_v2'


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()

    parent_manifest,parent_proof = BASE.with_suffix('.json'),BASE.with_name('proof.json')
    parent,published = read(parent_manifest),read(parent_proof)
    assert sha(BASE)==PARENT and sha(parent_proof)==PARENT_PROOF_PIN==parent['composed_proof_SHA256']
    assert parent['passed'] and published['passed'] and published['candidate_SHA256']==parent['candidate_SHA256']==PARENT
    assert published['kernel_SHA256']==parent['kernel_SHA256']==sha(Prior.Suites.KERNEL)
    bindings(published['bindings'])
    delivery = read(PARENT_DELIVERY)
    assert delivery['Downloads_launch_verified'] and delivery['ROM_SHA256']==PARENT
    assert delivery['native_audio_matches_candidate'] and delivery['camera_edge_spawns_match_candidate']

    packet = BASE.parent/'mini'
    ready,source = read(packet/'ready.json'),(packet/'controller.lua').read_text(encoding='utf-8')
    assert ready['ROM_sha256']==PARENT and Path(ready['ROM']).resolve()==BASE.resolve()
    assert ready['emulated_writes'] is False
    bindings(ready['bindings'])
    with Prior.validators() as validation:
        route = validation.route_evidence(packet)
    metrics = Prior.native_metrics(packet,PARENT,route)
    assert route['cadence']==delivery['active_11_cadence']
    assert source.count(PARENT)==1 and PIN not in source
    rebound = source.replace(PARENT,PIN,1)
    assert rebound.replace(PIN,PARENT,1)==source

    assert sha(COMPONENT)==COMPONENT_PIN
    component = read(COMPONENT)
    assert component['passed'] and component['ROM_written'] is False
    assert component['parent_SHA256']==PARENT and component['expected_memory_only_SHA256']==PIN
    bindings(component['bindings'])
    patch, = component['patches']
    assert patch['physical_PRG']==78 and patch['CPU_half_open']==[0xaf96,0xafd6]
    assert patch['file_offset']==642982 and len(bytes.fromhex(patch['old_hex']))==64
    before = BASE.read_bytes()
    final = install(before,[patch])
    reverse = dict(patch,old_hex=patch['new_hex'],new_hex=patch['old_hex'])
    minus = install(final,[reverse])
    assert minus==before and Contact.C.M.sha(final)==PIN
    verify_payload(final,Prior.Suites.KERNEL)
    checks = {name:check(minus,final) for name,check in (
        ('foreground',Contact.foreground),('vectors',Contact.vectors),('handoff',Contact.handoff))}
    # Normalize in-memory tuples and numeric JSON object keys before comparison.
    assert json.loads(json.dumps(checks))=={name:component[name] for name in checks}
    print('Contact V2 final-minus foreground, vectors and exact SMC handoff passed.',flush=True)

    refs = {Path(__file__),BASE,parent_manifest,parent_proof,PARENT_DELIVERY,COMPONENT,packet/'ready.json',
            *(packet/'capture'/name for name in ('binding.json','result.json','timing.json','audio-order.json','camera-lifts.json')),
            *map(Path,ready['bindings']),*map(Path,component['bindings'])}
    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==PIN
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(BASE.with_suffix(suffix))
    proof_path = out/'proof.json'
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PARENT,candidate_SHA256=PIN,
                 kernel_SHA256=parent['kernel_SHA256'],apply_order=[*parent['apply_order'],ROLE],
                 groups={ROLE:[patch]},final_minus_SHA256={ROLE:PARENT},final_minus_checks={ROLE:checks},
                 previous_native_metrics=metrics,bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom),ROM_written=True,parent_SHA256=PARENT,candidate_SHA256=PIN,
                  parent_composed_proof_SHA256=PARENT_PROOF_PIN,composed_proof_SHA256=sha(proof_path),
                  groups=proof['groups'],apply_order=proof['apply_order'],final_minus_SHA256=proof['final_minus_SHA256'],
                  final_minus_checks=proof['final_minus_checks'],ordinary_native_pending=True,
                  verification='Exact Tank contact V2 CPU and interrupt proof. Ordinary Mini native route pending.')
    manifest.write_text(json.dumps(parent,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,rebound,refs|{manifest,proof_path},expected=PIN,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==8


if __name__=='__main__':
    main()
