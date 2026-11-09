"""Stage the four shared contact, lift, parser and mixer changes over 29aa."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_player_contact_ingress_1110 as Ingress
import check_native_player_contact_offset_1110 as Contact
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
from prepare_mini_lane_audio_native_1110 import verify_interrupts, verify_parent, verify_payload, without_component
import prepare_mini_platform_pair_native_1110 as Platform
from prepare_selected_native_packet_v1 import prepare, sha


R, PIN, Stage = Platform.R,Platform.PIN,Platform.Stage
TRIPLE = R/'build/mini-platform-pair-native-1110'
TRIPLE_PIN = 'df03fc35ebdc516a8df0b501bbe2008e52836aa8fcfad5c34e4df76783e9f331'
TRIPLE_PROOF_SHA = '6c741480a17ce38e70977ef123052eaa7160b0f7a2c87de10d7dd60564d41245'
TRIPLE_TIMING_SHA = 'b4f1f155707ee62aca0319ab5b6a3ef8fa6791556821120c18700fcb5c4af0ca'
CONTACT_ROOT = R/'build/native-player-contact-offset-1110'
CONTACT_PROOF_SHA = '134c1a925a89db2f41b5a779b0d72c9b5414a39053dc62e22bc07734eb2fd881'
CONTACT_INGRESS_SHA = 'af4b60a267c80cc5dd64471e8d0b5f6426322e9616c0f3d86365464415a0b9e8'
CONTACT_PIN = '4741094695cc7b5218448273df9727e148f090ecc7268cd684df78fe55d75f04'
ROLE = 'native_player_contact_offset'


def census():
    triple,minus,groups,parser,audio,lift,parent,published,refs = Platform.census()
    rom,proof_path = TRIPLE/'candidate.nes',TRIPLE/'proof.json'
    manifest = rom.with_suffix('.json')
    meta,proof = read(manifest),read(proof_path)
    assert sha(rom)==meta['candidate_SHA256']==proof['candidate_SHA256']==TRIPLE_PIN
    assert rom.read_bytes()==triple and sha(proof_path)==meta['composed_proof_SHA256']==TRIPLE_PROOF_SHA
    assert proof['passed'] and proof['parent_SHA256']==PIN
    assert proof['groups']==meta['groups']==groups and proof['kernel_SHA256']==sha(Stage.KERNEL)
    assert proof['final_minus_SHA256']=={role:Contact.P.sha(raw) for role,raw in minus.items()}
    bindings(proof['bindings'])
    packet = TRIPLE/'mini'
    with Stage.Delivery.validators(TRIPLE_PIN) as validation:
        route = validation.route_evidence(packet)
    with Stage.Delivery.validators(PIN) as validation:
        previous = validation.route_evidence(Stage.TEMPLATE)
    assert Stage.Delivery.same_audio(previous,route)
    assert route['lifts']==previous['lifts'] and route['camera_edge_spawns']==previous['camera_edge_spawns']
    timing = packet/'capture/timing.json'
    assert sha(timing)==TRIPLE_TIMING_SHA
    cadence = route['cadence']
    assert cadence['physical']==cadence['updates']==3500
    assert cadence['no_controller_read']==cadence['zero_update']==2
    metrics = Stage.Delivery.metrics(packet,TRIPLE_PIN,route)
    ready = read(packet/'ready.json')
    assert ready['ROM_sha256']==TRIPLE_PIN and not ready['emulated_writes']
    bindings(ready['bindings'])
    source,_,_,_ = Stage.route_plan(triple,published)
    assert (packet/'controller.lua').read_text(encoding='utf-8')==source
    refs.update({Path(__file__),rom,proof_path,manifest,packet/'ready.json',packet/'controller.lua',
                 *map(Path,proof['bindings']),*map(Path,ready['bindings']),
                 *(packet/'capture'/name for name in ('timing.json','binding.json','result.json','audio-order.json','camera-lifts.json'))})

    contact_path,ingress_path = CONTACT_ROOT/'proof.json',CONTACT_ROOT/'ingress.json'
    assert sha(contact_path)==CONTACT_PROOF_SHA and sha(ingress_path)==CONTACT_INGRESS_SHA
    before = Stage.BASE.read_bytes()
    contact_only,contact,spans = verify_parent(before,contact_path)
    assert Contact.P.sha(contact_only)==contact['expected_memory_only_SHA256']==CONTACT_PIN
    verify_interrupts(contact_path,ingress_path,contact)
    ingress = read(ingress_path)
    bindings(contact['bindings'])
    rows = contact['patches']
    assert [(p['physical_PRG'],p['CPU_half_open'],p['file_offset']) for p in rows]==[(126,[0x9659,0x9690],1037929)]
    for patch in (p for group in groups.values() for p in group):
        lo = patch['file_offset']
        hi = lo+len(bytes.fromhex(patch['new_hex']))
        assert all(end<=lo or hi<=start for start,end,_,_ in spans)
    final = install(triple,rows)
    assert final==install(contact_only,[p for group in groups.values() for p in group])
    assert without_component(final,contact_path)==triple
    assert final[:16]==before[:16] and final[1048592:]==before[1048592:]
    verify_payload(final,Stage.KERNEL)
    groups = groups | {ROLE:rows}
    minus = {name:install(raw,rows) for name,raw in minus.items()} | {ROLE:triple}
    assert all(install(minus[name],patches)==final for name,patches in groups.items())
    refs.update({contact_path,ingress_path,*map(Path,contact['bindings']),*map(Path,ingress['bindings'])})
    return final,minus,groups,parser,audio,lift,contact,ingress,parent,published,metrics,refs


def qualify(final,minus,parser,audio,lift,contact,ingress):
    checks = Platform.qualify(final,minus,parser,audio,lift)
    before,labels = minus[ROLE],contact['labels']
    result = dict(foreground=Contact.foreground(before,final,labels),rejected_callers=Contact.rejected(before,final),
                  vectors=Contact.vectors(before,final))
    assert Stage.stable(result)=={name:contact[name] for name in result}
    live = dict(ingress=Ingress.ingress(before,final),whole_GameLoop=Ingress.whole(before,final,labels))
    assert Stage.stable(live)=={name:ingress[name] for name in live}
    print('Final-minus ordinary contact, full index range, native caller convergence and real vectors passed.',flush=True)
    return checks | {ROLE:result | live}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    final,minus,groups,parser,audio,lift,contact,ingress,parent,published,triple_metrics,refs = census()
    pin = Contact.P.sha(final)
    minus_pins = {name:Contact.P.sha(raw) for name,raw in minus.items()}
    source,ready,metrics,route_refs = Stage.route_plan(final,published)
    print(json.dumps(dict(candidate_SHA256=pin,final_minus_SHA256=minus_pins)),flush=True)
    checks = qualify(final,minus,parser,audio,lift,contact,ingress)

    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.lbl','.dbg'):
        sidecar = Stage.BASE.with_suffix(suffix)
        shutil.copyfile(sidecar,rom.with_suffix(suffix))
        assert sha(sidecar)==sha(rom.with_suffix(suffix))
    refs.update(route_refs)
    proof_path = out/'proof.json'
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PIN,candidate_SHA256=pin,
                 kernel_SHA256=sha(Stage.KERNEL),groups=groups,apply_order=[*parent['apply_order'],*groups],
                 final_minus_SHA256=minus_pins,final_minus_checks=checks,
                 previous_native_metrics=metrics,intermediate_native_metrics=triple_metrics,
                 intermediate_native_SHA256=TRIPLE_PIN,intermediate_proof_SHA256=TRIPLE_PROOF_SHA,
                 intermediate_timing_SHA256=TRIPLE_TIMING_SHA,source_contact_proof_SHA256=CONTACT_PROOF_SHA,
                 source_contact_ingress_SHA256=CONTACT_INGRESS_SHA,ordered_audio_matches_parent=True,
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom),ROM_written=True,parent_SHA256=PIN,candidate_SHA256=pin,
                  parent_composed_proof_SHA256=Stage.PARENT_PROOF_SHA,composed_proof_SHA256=sha(proof_path),
                  groups=groups,apply_order=proof['apply_order'],final_minus_SHA256=minus_pins,
                  final_minus_checks=checks,ordinary_native_pending=True,
                  verification='Exact four-way parser, mixer, lift and ordinary contact proof. Native cadence pending.')
    manifest.write_text(json.dumps(parent,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,source,refs|{manifest,proof_path},expected=pin,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==8


if __name__=='__main__':
    main()
