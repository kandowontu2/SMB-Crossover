"""Stage the exact DD Mini successor with the shared GameLoop tail patch."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_game_loop_tail_1110 as Tail
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
import deliver_mini_contact_draw_1110 as Previous
import prepare_mini_contact_draw_native_1110 as DD
from prepare_mini_lane_audio_native_1110 import verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R = Previous.R
BASE = Previous.ROOT/'candidate.nes'
PARENT = 'dd805e86b5d22cd7b7b3222915b821a92bc882ef63a139e5e3b6def7186e8a13'
PARENT_PROOF_PIN = '268b284a85f7295bafbc6311db864e9006571f6435096d0b8b9a731cae82f94a'
PARENT_DELIVERY = R/'build/mini-contact-draw-delivery-1110/verified-delivery.json'
PARENT_DELIVERY_PIN = '6c3989921eccdfd149267b90de7de5a0a64a5b57b46fcb4ccc71ae610fe10282'
COMPONENT = R/'build/native-game-loop-tail-1110/proof.json'
COMPONENT_PIN = 'abcc9575beb262d91858fe071403b099a2624b34740ae870e8dd4774cc62176c'
ROLE = 'native_game_loop_tail'


def census():
    manifest_path,proof_path = BASE.with_suffix('.json'),BASE.with_name('proof.json')
    parent,proof = read(manifest_path),read(proof_path)
    before = BASE.read_bytes()
    assert Tail.P.sha(before)==parent['candidate_SHA256']==proof['candidate_SHA256']==PARENT
    assert sha(proof_path)==parent['composed_proof_SHA256']==PARENT_PROOF_PIN and proof['passed']
    assert parent['parent_SHA256']==proof['parent_SHA256']==Tail.PIN
    assert parent['kernel_SHA256']==proof['kernel_SHA256']==sha(DD.SUITES.KERNEL)
    bindings(proof['bindings'])

    prior = Tail.BASE.read_bytes()
    assert Tail.P.sha(prior)==Tail.PIN
    groups = proof['groups']
    assert groups==parent['groups'] and set(groups)==set(DD.ROLES)
    inherited = [patch for role in DD.ROLES for patch in groups[role]]
    assert install(prior,inherited)==before

    assert sha(PARENT_DELIVERY)==PARENT_DELIVERY_PIN
    delivery = read(PARENT_DELIVERY)
    assert delivery['ROM_SHA256']==PARENT and delivery['Downloads_launch_verified'] and delivery['IPS_roundtrip']
    assert delivery['native_audio_matches_candidate'] and delivery['camera_edge_spawns_match_candidate']
    assert not delivery['backup_created']

    assert sha(COMPONENT)==COMPONENT_PIN
    component = read(COMPONENT)
    assert component['passed'] and component['ROM_written'] is False and component['parent_SHA256']==Tail.PIN
    bindings(component['bindings'])
    patches = component['patches']
    assert [(p['physical_PRG'],p['CPU_half_open'],p['file_offset'],len(bytes.fromhex(p['old_hex']))) for p in patches]==[
        (126,[0x8352,0x8355],1033058,3),(126,[0x8365,0x8369],1033077,4)]
    isolated = install(prior,patches)
    assert Tail.P.sha(isolated)==component['expected_memory_only_SHA256']
    final = install(before,patches)
    reverse = [dict(p,old_hex=p['new_hex'],new_hex=p['old_hex']) for p in patches]
    assert final==install(isolated,inherited) and install(final,reverse)==before
    assert final[:16]==before[:16] and final[1048592:]==before[1048592:]
    verify_payload(final,DD.SUITES.KERNEL)
    refs = {Path(__file__),BASE,manifest_path,proof_path,PARENT_DELIVERY,COMPONENT,
            *map(Path,component['bindings']),*map(Path,proof['bindings'])}
    return before,final,patches,component,parent,delivery,refs


def plan(final,pin,delivery):
    root = BASE.parent
    with Previous.validators(PARENT) as validation:
        route = validation.route_evidence(root/'mini')
        validation.native_suite(root,BASE)
        Previous.Parent.Prior.corrected_injury(root/'native/injury',BASE)
    metrics = Previous.metrics(root/'mini',PARENT,route)
    cadence = route['cadence']
    assert cadence==delivery['active_11_cadence']
    assert cadence['physical']==cadence['updates']==3500 and cadence['no_controller_read']==cadence['zero_update']==4

    packets = {}
    for name in ('mini',*DD.SUITES.PACKETS):
        path = Path('mini') if name=='mini' else Path('native')/name
        old = root/path
        ready_path,source_path = old/'ready.json',old/'controller.lua'
        ready,source = read(ready_path),source_path.read_text(encoding='utf-8')
        assert ready['ROM_sha256']==PARENT and Path(ready['ROM']).resolve()==BASE.resolve()
        assert ready['emulated_writes'] is False
        bindings(ready['bindings'])
        refs = {ready_path,source_path,old/'capture/binding.json',old/'capture/result.json',*map(Path,ready['bindings'])}
        if name=='mini':
            refs.update(old/'capture'/file for file in ('audio-order.json','camera-lifts.json','timing.json'))
        else:
            expected,planned,_ = DD.SUITES.plan(final,name)
            assert source==expected.replace(DD.SUITES.PIN,PARENT,1)
            refs.update(planned)
        assert source.count(PARENT)==1 and pin not in source
        packets[path] = source.replace(PARENT,pin,1),refs,ready
    return packets,metrics


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    before,final,patches,component,parent,delivery,refs = census()
    pin = Tail.P.sha(final)
    packets,metrics = plan(final,pin,delivery)
    print(json.dumps(dict(candidate_SHA256=pin,final_minus_SHA256={ROLE:PARENT})),flush=True)
    checks = dict(whole_GameLoop=Tail.whole(before,final),vectors=Tail.vectors(before,final))
    assert json.loads(json.dumps(checks))=={name:component[name] for name in checks}
    print('Shared GameLoop tail final-minus whole and vectors passed.',flush=True)

    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(BASE.with_suffix(suffix))
    proof_path = out/'proof.json'
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PARENT,candidate_SHA256=pin,
                 kernel_SHA256=parent['kernel_SHA256'],apply_order=[*parent['apply_order'],ROLE],groups={ROLE:patches},
                 final_minus_SHA256={ROLE:PARENT},final_minus_checks={ROLE:checks},previous_native_metrics=metrics,
                 published_parent_receipt_SHA256=PARENT_DELIVERY_PIN,source_component_SHA256=COMPONENT_PIN,
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom),ROM_written=True,parent_SHA256=PARENT,candidate_SHA256=pin,
                  parent_composed_proof_SHA256=PARENT_PROOF_PIN,composed_proof_SHA256=sha(proof_path),
                  groups=proof['groups'],apply_order=proof['apply_order'],final_minus_SHA256=proof['final_minus_SHA256'],
                  final_minus_checks=proof['final_minus_checks'],ordinary_native_pending=True,
                  verification='Exact shared GameLoop tail CPU and interrupt proof. Five native replays pending.')
    manifest.write_text(json.dumps(parent,indent=2)+'\n',encoding='utf-8')
    (out/'native').mkdir()
    for path,(source,packet_refs,ready) in packets.items():
        prepare(out/path,rom,source,refs|packet_refs|{manifest,proof_path},expected=pin,timeout=ready['timeout'],
                scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==20


if __name__=='__main__':
    main()
