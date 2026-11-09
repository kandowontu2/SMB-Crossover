"""Stage the exact 29aa successor with the shared paired-column parser."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_parser_paired_ingress_irq_1110 as Ingress
import check_native_parser_paired_shadow_1110 as Parser
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
import deliver_mini_contact_draw_1110 as Delivery
from prepare_mini_injury_helper_native_1110 import PRG_HOOK
from prepare_mini_lane_audio_native_1110 import verify_interrupts, verify_parent, verify_payload, without_component
import prepare_mini_shared_game_loop_tail_native_1110 as Tail
from prepare_selected_native_packet_v1 import prepare, sha


R, KERNEL = Parser.R,Parser.M.KERNEL
PARENT_ROOT = R/'build/mini-shared-game-loop-tail-native-1110'
BASE = PARENT_ROOT/'candidate.nes'
PIN = '29aa4f8df07425dfe6dcdaaa431421c78347adbca5979c332edce69c79367cf5'
PARENT_MANIFEST_SHA = '68de8667f551bff5d7449443abe64015532e87d078c3cadbfecd98e9fe8099cb'
PARENT_PROOF_SHA = 'e1fa5c21e0a6e9cf2e4b6222d3a85c1622b94fc86eb1aa677798de7a6704cf07'
PARENT_TIMING_SHA = 'a9b22f8e015f0fcb0381e4c892f0fc6ad59ce211c14a10ed468069485c88eda5'
PUBLISHED = R/'build/mini-shared-game-loop-tail-delivery-1110/verified-delivery.json'
PUBLISHED_SHA = 'ed3b32566d5ee1e9c39f146dd2f4e13099c7dd564a635b110d75bc68f866fe55'
SOURCE_ROOT = R/'build/native-parser-paired-shadow-1110'
SOURCES = {
    'proof.json':'512aee22c111c6bb076441cdb56f85920c570a38e153321a1aa60ba51b679d40',
    'irq.json':'492df4c1d3314ef473b88d9df13be3983609efc2f44c6735075ed507bce8ef0e',
    'ingress-irq.json':'89f3bb9c3c1bdd62703c8fd363689f518feeeb019544a638d93f9cdbe36f9d3f',
}
ROLE = 'native_parser_paired_shadow'
EXTENTS = [(2,[0xa2e4,0xa314],17140),(126,[0x9076,0x90d2],1036422),(2,[0xbfdd,0xc000],24557)]
TEMPLATE = PARENT_ROOT/'mini'


def stable(value):
    return json.loads(json.dumps(value))


def census():
    meta_path,proof_path = BASE.with_suffix('.json'),BASE.with_name('proof.json')
    assert sha(BASE)==PIN and sha(meta_path)==PARENT_MANIFEST_SHA and sha(proof_path)==PARENT_PROOF_SHA
    parent,parent_proof = read(meta_path),read(proof_path)
    assert parent_proof['passed'] and parent['composed_proof_SHA256']==PARENT_PROOF_SHA
    assert parent['candidate_SHA256']==parent_proof['candidate_SHA256']==PIN
    assert parent['parent_SHA256']==parent_proof['parent_SHA256']==Parser.PIN
    assert parent['kernel_SHA256']==parent_proof['kernel_SHA256']==sha(KERNEL)==Parser.M.KERNEL_PIN
    assert sha(PUBLISHED)==PUBLISHED_SHA
    published = read(PUBLISHED)
    assert published['ROM_SHA256']==PIN and published['IPS_roundtrip'] and published['Downloads_launch_verified']
    assert published['native_audio_matches_candidate'] and published['camera_edge_spawns_match_candidate']
    assert not published['backup_created'] and Path(published['destination']).resolve()==Delivery.NIGHTLY.D.resolve()
    assert Delivery.NIGHTLY.check(Delivery.NIGHTLY.D)['ROM_sha256']==PIN
    bindings(parent_proof['bindings'])

    refs = {Path(__file__),BASE,meta_path,proof_path,PUBLISHED,KERNEL,*map(Path,parent_proof['bindings'])}
    receipts = {}
    for name,digest in SOURCES.items():
        path = SOURCE_ROOT/name
        assert sha(path)==digest
        receipt = read(path)
        assert receipt['passed'] and receipt['ROM_written'] is False and receipt['parent_SHA256']==Parser.PIN
        bindings(receipt['bindings'])
        receipts[name] = receipt
        refs.update({path,*map(Path,receipt['bindings'])})

    before,dd = BASE.read_bytes(),Parser.BASE.read_bytes()
    assert Parser.P.sha(dd)==Parser.PIN
    isolated,component,spans = verify_parent(dd,SOURCE_ROOT/'proof.json')
    assert component==receipts['proof.json']
    for name in ('irq.json','ingress-irq.json'):
        verify_interrupts(SOURCE_ROOT/'proof.json',SOURCE_ROOT/name,component)
    rows = component['patches']
    assert [(p['physical_PRG'],p['CPU_half_open'],p['file_offset']) for p in rows]==EXTENTS
    assert parent['groups']==parent_proof['groups'] and set(parent['groups'])=={Tail.ROLE}
    inherited = parent['groups'][Tail.ROLE]
    for patch in inherited:
        lo = patch['file_offset']
        hi = lo+len(bytes.fromhex(patch['new_hex']))
        assert all(end<=lo or hi<=start for start,end,_,_ in spans)
    assert install(dd,inherited)==before
    final = install(before,rows)
    assert final==install(isolated,inherited)
    assert without_component(final,SOURCE_ROOT/'proof.json')==before
    assert final[:16]==before[:16] and final[1048592:]==before[1048592:]
    for image in (before,final):
        verify_payload(image,KERNEL)
    return before,final,rows,receipts,parent,published,refs


def route_plan(final,published):
    with Delivery.validators(PIN) as validation:
        route = validation.route_evidence(TEMPLATE)
    cadence = route['cadence']
    assert cadence==published['active_11_cadence']
    assert cadence['physical']==cadence['updates']==3500 and cadence['no_controller_read']==cadence['zero_update']==4
    timing = TEMPLATE/'capture/timing.json'
    assert sha(timing)==PARENT_TIMING_SHA
    metrics = Delivery.metrics(TEMPLATE,PIN,route)
    ready_path,controller = TEMPLATE/'ready.json',TEMPLATE/'controller.lua'
    ready,source = read(ready_path),controller.read_text(encoding='utf-8')
    assert ready['ROM_sha256']==PIN and Path(ready['ROM']).resolve()==BASE.resolve() and not ready['emulated_writes']
    bindings(ready['bindings'])
    pin = Parser.P.sha(final)
    assert source.count(PIN)==1 and pin not in source
    assert ready['bindings'][str(KERNEL.resolve())]==sha(KERNEL)
    for physical,values in PRG_HOOK.findall(source):
        at = 16+int(physical)
        want = bytes(map(int,values.split(',')))
        assert final[at:at+len(want)]==want,(hex(at),want.hex())
    refs = {ready_path,controller,*map(Path,ready['bindings']),
            *(TEMPLATE/'capture'/name for name in ('binding.json','result.json','audio-order.json','camera-lifts.json','timing.json'))}
    return source.replace(PIN,pin,1),ready,metrics,refs


def qualify(before,final,receipts,*,same_interrupt_trace=True):
    """Recheck final-minus byte images, including when an independent mixer is present."""
    proof = receipts['proof.json']
    assert install(before,proof['patches'])==final
    tails = Parser.tails(before,final)
    whole = Parser.whole(before,final)
    assert stable(tails)==proof['column_tails']
    assert stable(whole)=={name:proof[name] for name in ('loaded_columns','GameLoop')}
    print('Final-minus all buffer columns, native parser and full GameLoop passed.',flush=True)
    shadow = Parser.vectors(before,final,proof['labels'])
    if same_interrupt_trace:
        assert all(receipts['irq.json'][name]==value for name,value in stable(shadow).items())
    print('Final-minus shadow and actual vector guards passed.',flush=True)
    ingress = Ingress.paired(before,final)
    if same_interrupt_trace:
        assert all(receipts['ingress-irq.json'][name]==value for name,value in stable(ingress).items())
    print('Final-minus parser ingress, real nested interrupts and paired resumes passed.',flush=True)
    return dict(tails=tails,whole=whole,shadow_vectors=shadow,ingress_vectors=ingress)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    before,final,rows,receipts,parent,published,refs = census()
    pin = Parser.P.sha(final)
    source,ready,metrics,route_refs = route_plan(final,published)
    print(json.dumps(dict(candidate_SHA256=pin,final_minus_SHA256={ROLE:PIN})),flush=True)
    checks = qualify(before,final,receipts)

    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.dbg','.lbl'):
        sidecar = BASE.with_suffix(suffix)
        shutil.copyfile(sidecar,rom.with_suffix(suffix))
        assert sha(sidecar)==sha(rom.with_suffix(suffix))
    refs.update(route_refs)
    proof_path = out/'proof.json'
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PIN,candidate_SHA256=pin,
                 kernel_SHA256=sha(KERNEL),apply_order=[*parent['apply_order'],ROLE],groups={ROLE:rows},
                 final_minus_SHA256={ROLE:PIN},final_minus_checks={ROLE:checks},
                 source_component_SHA256=SOURCES['proof.json'],source_receipt_SHA256=SOURCES,
                 published_parent_receipt_SHA256=PUBLISHED_SHA,previous_native_metrics=metrics,
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom),ROM_written=True,parent_SHA256=PIN,candidate_SHA256=pin,
                  parent_composed_proof_SHA256=PARENT_PROOF_SHA,composed_proof_SHA256=sha(proof_path),
                  groups=proof['groups'],apply_order=proof['apply_order'],final_minus_SHA256=proof['final_minus_SHA256'],
                  final_minus_checks=proof['final_minus_checks'],
                  ordinary_native_pending=True,verification='Exact paired shadow and blank tile parser proof. Ordinary native route pending.')
    manifest.write_text(json.dumps(parent,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,source,refs|{proof_path,manifest},expected=pin,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==8


if __name__=='__main__':
    main()
