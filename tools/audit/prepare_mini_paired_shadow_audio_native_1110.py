"""Stage the paired parser and two-clock mixer over the installed 29aa ROM."""

import argparse
import json
from pathlib import Path
import shutil

import check_guest_expansion_clock_pair_1110 as Audio
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
from prepare_mini_lane_audio_native_1110 import verify_parent, verify_payload, without_component
import prepare_mini_paired_shadow_native_1110 as Stage
from prepare_selected_native_packet_v1 import prepare, sha


R, PIN = Stage.R,Stage.PIN
AUDIO_PROOF = R/'build/guest-expansion-grouped-1110/proof.json'
AUDIO_PROOF_SHA = 'f6cd2058ebf61d09b4ebc4e60666c468641a321866b532e4fc071ccafd8d3912'
AUDIO_PIN = '778a95d7cb91d5b04ca38ea222eb24f7218af6cbaa58ed0ecc8e0c7b656454aa'
PARSER_ROOT = R/'build/mini-paired-shadow-native-1110'
PARSER_PROOF_SHA = '85c160b460c5a6d6b0cdcfd7cfd573c6b7d2a5fad042b0262fa456b7f1207d31'
PARSER_PIN = 'ce9b87168c87517f8b47aea89ff6abc91c4b86aa7f49dd73049bba51c24ba320'
AUDIO_ROLE = 'guest_expansion_clock_pair'
ROLES = (Stage.ROLE,AUDIO_ROLE)


def census():
    before,parser_only,parser_rows,parser_receipts,parent,published,refs = Stage.census()
    rom,receipt_path = PARSER_ROOT/'candidate.nes',PARSER_ROOT/'proof.json'
    manifest = rom.with_suffix('.json')
    receipt = read(receipt_path)
    assert sha(rom)==receipt['candidate_SHA256']==PARSER_PIN and rom.read_bytes()==parser_only
    assert sha(receipt_path)==read(manifest)['composed_proof_SHA256']==PARSER_PROOF_SHA
    assert receipt['parent_SHA256']==PIN and receipt['passed']
    assert receipt['groups']=={Stage.ROLE:parser_rows} and receipt['kernel_SHA256']==sha(Stage.KERNEL)
    bindings(receipt['bindings'])

    assert Audio.PIN==PIN and sha(AUDIO_PROOF)==AUDIO_PROOF_SHA
    audio_only,audio_receipt,spans = verify_parent(before,AUDIO_PROOF)
    assert Audio.M.sha(audio_only)==audio_receipt['expected_memory_only_SHA256']==AUDIO_PIN
    bindings(audio_receipt['bindings'])
    audio_rows = audio_receipt['patches']
    assert [(p['physical_PRG'],p['CPU_half_open'],p['file_offset']) for p in audio_rows]==[
        (29,[0xab1c,0xab29],240428),(29,[0xac12,0xac28],240674)]
    linked,source_rows = Audio.linked(before)
    assert linked==audio_only and source_rows==audio_rows
    for patch in parser_rows:
        lo = patch['file_offset']
        hi = lo+len(bytes.fromhex(patch['new_hex']))
        assert all(end<=lo or hi<=start for start,end,_,_ in spans)
    final = install(parser_only,audio_rows)
    assert final==install(audio_only,parser_rows)
    assert without_component(final,AUDIO_PROOF)==parser_only
    assert without_component(final,Stage.SOURCE_ROOT/'proof.json')==audio_only
    assert final[:16]==before[:16] and final[1048592:]==before[1048592:]
    for image in (before,parser_only,audio_only,final):
        verify_payload(image,Stage.KERNEL)
    groups = {Stage.ROLE:parser_rows,AUDIO_ROLE:audio_rows}
    minus = {Stage.ROLE:audio_only,AUDIO_ROLE:parser_only}
    refs.update({Path(__file__),rom,receipt_path,manifest,AUDIO_PROOF,
                 *map(Path,receipt['bindings']),*map(Path,audio_receipt['bindings'])})
    return final,minus,groups,parser_receipts,audio_receipt,parent,published,refs


def qualify(final,minus,parser_receipts,audio_receipt):
    parser = Stage.qualify(minus[Stage.ROLE],final,parser_receipts)
    before = minus[AUDIO_ROLE]
    mixer = Audio.mixer(before,final)
    assert Stage.stable(mixer)==audio_receipt['foreground']
    print('Final-minus 55,296 mixer cases and ordered hardware writes passed.',flush=True)
    lifecycle = Audio.Prior.lifecycle(before,final)
    assert Stage.stable(lifecycle)==audio_receipt['lifecycle']
    vectors = Audio.vectors(before,final)
    assert Stage.stable(vectors)==audio_receipt['vectors']
    print('Final-minus all mixer owner transitions and real nested vectors passed.',flush=True)
    return {Stage.ROLE:parser,AUDIO_ROLE:dict(foreground=mixer,lifecycle=lifecycle,vectors=vectors)}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    final,minus,groups,parser_receipts,audio_receipt,parent,published,refs = census()
    pin = Audio.M.sha(final)
    minus_pins = {role:Audio.M.sha(raw) for role,raw in minus.items()}
    source,ready,metrics,route_refs = Stage.route_plan(final,published)
    print(json.dumps(dict(candidate_SHA256=pin,final_minus_SHA256=minus_pins)),flush=True)
    checks = qualify(final,minus,parser_receipts,audio_receipt)

    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.dbg','.lbl'):
        sidecar = Stage.BASE.with_suffix(suffix)
        shutil.copyfile(sidecar,rom.with_suffix(suffix))
        assert sha(sidecar)==sha(rom.with_suffix(suffix))
    refs.update(route_refs)
    proof_path = out/'proof.json'
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PIN,candidate_SHA256=pin,
                 kernel_SHA256=sha(Stage.KERNEL),apply_order=[*parent['apply_order'],*ROLES],groups=groups,
                 final_minus_SHA256=minus_pins,final_minus_checks=checks,parser_interrupt_trace_exact=True,
                 parser_standalone_proof_SHA256=PARSER_PROOF_SHA,audio_proof_SHA256=AUDIO_PROOF_SHA,
                 published_parent_receipt_SHA256=Stage.PUBLISHED_SHA,previous_native_metrics=metrics,
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom),ROM_written=True,parent_SHA256=PIN,candidate_SHA256=pin,
                  parent_composed_proof_SHA256=Stage.PARENT_PROOF_SHA,composed_proof_SHA256=sha(proof_path),
                  groups=groups,apply_order=proof['apply_order'],final_minus_SHA256=minus_pins,
                  final_minus_checks=checks,ordinary_native_pending=True,
                  verification='Exact paired shadow parser and two-clock expansion mixer proof. Ordinary native route pending.')
    manifest.write_text(json.dumps(parent,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,source,refs|{manifest,proof_path},expected=pin,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==8


if __name__=='__main__':
    main()
