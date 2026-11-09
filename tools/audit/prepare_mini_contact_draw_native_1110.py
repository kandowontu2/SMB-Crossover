"""Stage the exact Tank contact and shared native draw-scan composition."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_helper_draw_scan_1110 as Draw
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
from prepare_mini_lane_audio_native_1110 import verify_payload
import prepare_mini_contact_tank_precheck_native_1110 as Contact
from prepare_selected_native_packet_v1 import prepare, sha


R = Contact.R
PRIOR = Contact.Prior
SUITES = PRIOR.Suites
STANDALONE = R/'build/mini-contact-tank-precheck-native-1110'
STANDALONE_PROOF_PIN = '8fa5d4a5e0771a08c78f248cb3f628d8e4daf4b1328bda8d0a776cd1e8f8a932'
DRAW = R/'build/native-helper-draw-scan-1110/proof.json'
DRAW_PIN = 'd1d498443cb525280680556330a64013c79385f319526a332eed4bb03a669ede'
DRAW_ROLE = 'native_helper_draw_scan'
ROLES = (Contact.ROLE,DRAW_ROLE)


def census():
    rom,before,parent_proof,parent_manifest = SUITES.bind_candidate(SUITES.ROOT)
    delivery = read(Contact.PARENT_DELIVERY)
    assert delivery['ROM_SHA256']==Contact.PARENT and delivery['Downloads_launch_verified']
    assert delivery['native_audio_matches_candidate'] and delivery['camera_edge_spawns_match_candidate']

    components,groups = {},{}
    refs = {Path(__file__),rom,parent_proof,parent_manifest,Contact.PARENT_DELIVERY}
    for role,path,digest in ((Contact.ROLE,Contact.COMPONENT,Contact.COMPONENT_PIN),(DRAW_ROLE,DRAW,DRAW_PIN)):
        assert sha(path)==digest
        component = read(path)
        assert component['passed'] and component['ROM_written'] is False and component['parent_SHA256']==Contact.PARENT
        bindings(component['bindings'])
        groups[role] = component['patches']
        assert len(groups[role])==1
        components[role] = component
        refs.update({path,*map(Path,component['bindings'])})
    contact,draw = (groups[role][0] for role in ROLES)
    assert (contact['file_offset'],contact['CPU_half_open'],contact['physical_PRG'])==(642982,[0xaf96,0xafd6],78)
    assert (draw['file_offset'],draw['CPU_half_open'],draw['physical_PRG'])==(217228,[0xb07c,0xb0f0],26)
    assert len(bytes.fromhex(contact['old_hex']))==64 and len(bytes.fromhex(draw['old_hex']))==116

    isolated = {role:install(before,groups[role]) for role in ROLES}
    assert all(Draw.C.M.sha(raw)==components[role]['expected_memory_only_SHA256'] for role,raw in isolated.items())
    contact_rom,contact_proof = STANDALONE/'candidate.nes',STANDALONE/'proof.json'
    contact_manifest = contact_rom.with_suffix('.json')
    stage,stage_meta = read(contact_proof),read(contact_manifest)
    assert sha(contact_proof)==STANDALONE_PROOF_PIN==stage_meta['composed_proof_SHA256']
    assert stage['passed'] and stage['parent_SHA256']==Contact.PARENT
    assert stage['candidate_SHA256']==stage_meta['candidate_SHA256']==sha(contact_rom)==Contact.PIN
    assert stage['groups']=={Contact.ROLE:[contact]} and contact_rom.read_bytes()==isolated[Contact.ROLE]
    bindings(stage['bindings'])
    refs.update({contact_rom,contact_proof,contact_manifest})

    final = install(isolated[Contact.ROLE],[draw])
    assert final==install(isolated[DRAW_ROLE],[contact])
    assert final[:16]==before[:16] and final[1048592:]==before[1048592:]
    verify_payload(final,SUITES.KERNEL)
    return final,{Contact.ROLE:isolated[DRAW_ROLE],DRAW_ROLE:isolated[Contact.ROLE]},components,groups,refs


def qualify(final,minus,components):
    checks = {}
    for role,module,names in ((Contact.ROLE,Contact.Contact,('foreground','vectors','handoff')),
                              (DRAW_ROLE,Draw,('foreground','vectors'))):
        result = {name:getattr(module,name)(minus[role],final) for name in names}
        assert json.loads(json.dumps(result))=={name:components[role][name] for name in names}
        checks[role] = result
        print(f'{role} final-minus PASS',flush=True)
    return checks


def plan(final,pin):
    parent = SUITES.ROOT
    with PRIOR.validators() as validation:
        route = validation.route_evidence(parent/'mini')
        validation.native_suite(parent,Contact.BASE)
        PRIOR.Prior.corrected_injury(parent/'native/injury',Contact.BASE)
    metrics = PRIOR.native_metrics(parent/'mini',Contact.PARENT,route)
    assert route['cadence']==read(Contact.PARENT_DELIVERY)['active_11_cadence']

    packets = {}
    for name in ('mini',*SUITES.PACKETS):
        path = Path('mini') if name=='mini' else Path('native')/name
        old = parent/path
        ready_path,source_path = old/'ready.json',old/'controller.lua'
        ready,source = read(ready_path),source_path.read_text(encoding='utf-8')
        assert ready['ROM_sha256']==Contact.PARENT and Path(ready['ROM']).resolve()==Contact.BASE.resolve()
        assert ready['emulated_writes'] is False
        bindings(ready['bindings'])
        refs = {ready_path,source_path,old/'capture/binding.json',old/'capture/result.json',*map(Path,ready['bindings'])}
        if name=='mini':
            refs.update(old/'capture'/file for file in ('audio-order.json','camera-lifts.json','timing.json'))
        else:
            expected,planned,_ = SUITES.plan(final,name)
            assert source==expected
            refs.update(planned)
        assert source.count(Contact.PARENT)==1 and pin not in source
        rebound = source.replace(Contact.PARENT,pin,1)
        assert rebound.replace(pin,Contact.PARENT,1)==source
        packets[path] = rebound,refs,ready
    return packets,metrics


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    final,minus,components,groups,refs = census()
    pin = Draw.C.M.sha(final)
    minus_pins = {role:Draw.C.M.sha(raw) for role,raw in minus.items()}
    assert all(install(minus[role],groups[role])==final for role in ROLES)
    packets,metrics = plan(final,pin)
    print(json.dumps(dict(candidate_SHA256=pin,final_minus_SHA256=minus_pins)),flush=True)
    checks = qualify(final,minus,components)

    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(Contact.BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(Contact.BASE.with_suffix(suffix))
    proof_path = out/'proof.json'
    parent = read(Contact.BASE.with_suffix('.json'))
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=Contact.PARENT,candidate_SHA256=pin,
                 kernel_SHA256=parent['kernel_SHA256'],apply_order=[*parent['apply_order'],*ROLES],groups=groups,
                 final_minus_SHA256=minus_pins,final_minus_checks=checks,previous_native_metrics=metrics,
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom),ROM_written=True,parent_SHA256=Contact.PARENT,candidate_SHA256=pin,
                  parent_composed_proof_SHA256=Contact.PARENT_PROOF_PIN,composed_proof_SHA256=sha(proof_path),
                  groups=groups,apply_order=proof['apply_order'],final_minus_SHA256=minus_pins,
                  final_minus_checks=checks,ordinary_native_pending=True,
                  verification='Exact Tank contact V2 and native draw scan CPU and interrupt proof. Five native replays pending.')
    manifest.write_text(json.dumps(parent,indent=2)+'\n',encoding='utf-8')
    (out/'native').mkdir()
    for path,(source,packet_refs,ready) in packets.items():
        prepare(out/path,rom,source,refs|packet_refs|{manifest,proof_path},expected=pin,timeout=ready['timeout'],
                scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==20


if __name__=='__main__':
    main()
