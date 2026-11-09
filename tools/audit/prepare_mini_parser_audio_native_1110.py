"""Stage the exact local column, negative sweep, and quiet tick composition."""

import argparse
import json
from pathlib import Path
import shutil

import check_guest_audio_quiet_tick_1110 as Quiet
import check_guest_expansion_negate4_1110 as Sweep
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
from prepare_mini_lane_audio_native_1110 import verify_parent, verify_payload
import prepare_mini_local_column_parser_native_1110 as Local
from prepare_selected_native_packet_v1 import prepare, sha


R, BASE, PIN = Local.R,Local.BASE,Local.PIN
PARSER_ROOT = R/'build/mini-local-column-parser-native-1110'
PARSER_PIN = '37aa4380ebf544ac40f1c66f85d02417e9b69198f4de35cc3c16b433bcb9ab28'
PARSER_PROOF_SHA = '8beb8cce76a5bde3e27bc20f182569b61c1748abd12c84fb4294b2297148967a'
SWEEP_ROLE, QUIET_ROLE = 'guest_expansion_negate4','guest_audio_quiet_tick'
ROLES = (Local.ROLE,SWEEP_ROLE,QUIET_ROLE)
RECEIPTS = {
    SWEEP_ROLE:(R/'build/guest-expansion-negate4-1110/proof.json',
                '42be68813e079c1b6185c190333cb93f0189befa3a490f2c33f3da4f519ff690'),
    QUIET_ROLE:(R/'build/guest-audio-quiet-tick-1110/proof.json',
                'a4f614d454c5a3284499e8cdf0a00a8d51ab112a8c04ce0461eb19c3b4740903'),
}


def census():
    before,local,patches,component,irq,parent,refs,source,ready = Local.census()
    parser_rom,parser_proof = PARSER_ROOT/'candidate.nes',PARSER_ROOT/'proof.json'
    parser_manifest = PARSER_ROOT/'candidate.json'
    published = read(parser_proof)
    assert sha(parser_rom)==PARSER_PIN and parser_rom.read_bytes()==local
    assert sha(parser_proof)==PARSER_PROOF_SHA==read(parser_manifest)['composed_proof_SHA256']
    assert published['passed'] and published['parent_SHA256']==PIN and published['candidate_SHA256']==PARSER_PIN
    assert published['groups']=={Local.ROLE:patches} and published['kernel_SHA256']==Local.Parser.M.KERNEL_PIN
    bindings(published['bindings'])
    parser_packet = PARSER_ROOT/'mini'
    parent_route = Local.MarginDelivery.Prior.Five
    with parent_route.exact_native_validators(PARSER_PIN):
        native = parent_route.Earlier.route_evidence(parser_packet)
    cadence = native['cadence']
    assert cadence['no_controller_read']==cadence['zero_update']==6
    assert cadence['physical']==cadence['updates']==3500
    assert (parser_packet/'controller.lua').read_text(encoding='utf-8')==source
    refs.update({Path(__file__),parser_rom,parser_proof,parser_manifest,parser_packet/'controller.lua',parser_packet/'ready.json',
                 parser_packet/'capture/result.json',parser_packet/'capture/binding.json',parser_packet/'capture/timing.json',
                 *map(Path,published['bindings']),*map(Path,read(parser_packet/'ready.json')['bindings'])})

    groups = {Local.ROLE:patches}
    qualified = {}
    for role,(path,digest) in RECEIPTS.items():
        assert sha(path)==digest
        _,receipt,_ = verify_parent(before,path)
        assert receipt['parent_SHA256']==PIN and not receipt['ROM_written']
        groups[role],qualified[role] = receipt['patches'],receipt
        refs.update({path,*map(Path,receipt['bindings'])})
    parts = sorted((row['file_offset'],row['file_offset']+len(bytes.fromhex(row['new_hex'])))
                   for rows in groups.values() for row in rows)
    assert len(parts)==6 and all(b<=c for (_,b),(c,_) in zip(parts,parts[1:]))
    for path in (Local.PARENT_MANIFEST,Local.Margin.PARENT/'proof.json',Local.Margin.Box.BASE.with_name('proof.json')):
        for rows in read(path)['groups'].values():
            for row in rows:
                lo = row['file_offset']
                hi = lo+len(bytes.fromhex(row['new_hex']))
                assert all(end<=lo or hi<=start for start,end in parts),row
    final = install(before,[row for rows in groups.values() for row in rows])
    assert final==install(local,groups[SWEEP_ROLE]+groups[QUIET_ROLE]) and final[1048592:]==before[1048592:]
    verify_payload(final,Local.Margin.Seven.KERNEL)
    minus = {role:install(before,[row for other,rows in groups.items() if other!=role for row in rows]) for role in ROLES}
    assert all(install(minus[role],groups[role])==final for role in ROLES)
    pin = Local.Parser.P.sha(final)
    assert source.count(PARSER_PIN)==1 and pin not in source
    rebound = source.replace(PARSER_PIN,pin,1)
    assert rebound.replace(pin,PIN,1)==(Local.PARENT_PACKETS/'mini/controller.lua').read_text(encoding='utf-8')
    return final,minus,groups,component,irq,qualified,parent,refs,rebound,ready


def qualify(final,minus,component,irq,qualified):
    stable = Local.stable
    before = minus[Local.ROLE]
    foreground = Local.Parser.foreground(before,final)
    whole = Local.Parser.whole(before,final)
    assert stable(foreground)==component['column_cases'] and stable(whole)==component['whole_GameLoop']
    parser_vectors = Local.ParserIRQ.vectors(before,final)
    observed = stable(parser_vectors)
    assert all(irq[key]==value for key,value in observed.items())
    parser_nested = [row for row in observed['cuts'] if row[0]=='nested']
    print(json.dumps(dict(parser='final-minus PASS',nested=parser_nested,SP=observed['minimum_SP'])),flush=True)

    before,sweep = minus[SWEEP_ROLE],qualified[SWEEP_ROLE]
    assert stable(Sweep.source_callers(before))==sweep['source_callers']
    assert Sweep.profile_scope(before)==sweep['native_profile_projection']
    mixer = Sweep.direct_mixer(before,final)
    lifecycle = Sweep.lifecycle(before,final)
    sweep_vectors = Sweep.vectors(before,final)
    assert mixer==sweep['direct_mixer'] and lifecycle==sweep['lifecycle']
    assert stable(sweep_vectors)==sweep['vectors']
    print('Final-minus negate4 mixer, lifecycle and real interrupts passed.',flush=True)

    quiet = Quiet.vectors(minus[QUIET_ROLE],final)
    assert all(qualified[QUIET_ROLE][key]==value for key,value in stable(quiet).items())
    print('Final-minus quiet tick real NMI, ordered audio and nested IRQ passed.',flush=True)
    return {
        Local.ROLE:dict(foreground=foreground,whole_GameLoop=whole,vectors=parser_vectors,
                        source_proof_nested=[row for row in irq['cuts'] if row[0]=='nested']),
        SWEEP_ROLE:dict(direct_mixer=mixer,lifecycle=lifecycle,vectors=sweep_vectors),
        QUIET_ROLE:quiet,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    final,minus,groups,component,irq,qualified,parent,refs,source,ready = census()
    pin = Local.Parser.P.sha(final)
    minus_pins = {role:Local.Parser.P.sha(image) for role,image in minus.items()}
    print(json.dumps(dict(candidate_SHA256=pin,final_minus_SHA256=minus_pins)),flush=True)
    checks = qualify(final,minus,component,irq,qualified)
    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(BASE.with_suffix(suffix))
    proof_path = out/'proof.json'
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PIN,candidate_SHA256=pin,
                 intermediate_parser_SHA256=PARSER_PIN,kernel_SHA256=Local.Parser.M.KERNEL_PIN,
                 apply_order=[*parent['apply_order'],*ROLES],inherited_groups=parent['apply_order'],
                 groups=groups,final_minus_SHA256=minus_pins,final_minus_checks=checks,
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom),ROM_written=True,parent_SHA256=PIN,candidate_SHA256=pin,
                  parent_margin_manifest_SHA256=Local.PARENT_MANIFEST_SHA,composed_proof_SHA256=sha(proof_path),
                  groups=groups,apply_order=proof['apply_order'],final_minus_SHA256=minus_pins,
                  ordinary_native_pending=True,verification='Exact local parser and shared audio proof. Ordinary native route pending.')
    manifest.write_text(json.dumps(parent,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,source,refs|{manifest,proof_path},expected=pin,
            timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(p.is_file() for p in out.rglob('*'))==8


if __name__=='__main__':
    main()
