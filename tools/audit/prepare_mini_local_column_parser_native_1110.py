"""Requalify the local column parser over the installed 863e nightly."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_column_parser_local_1110 as Parser
import check_native_column_parser_local_irq_1110 as ParserIRQ
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
import deliver_mini_margin_native_1110 as MarginDelivery
import prepare_mini_margin_native_1110 as Margin
from prepare_mini_lane_audio_native_1110 import verify_interrupts, verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R, BASE, PIN = Margin.R,Margin.ROM,Margin.PIN
PARENT_PACKETS = MarginDelivery.ROOT
PARENT_MANIFEST = PARENT_PACKETS/'candidate.json'
PARENT_MANIFEST_SHA = '9b0b5ce2412b068491efac71a0562886ddee75bea4b2905e18ab3501840605bc'
PARENT_DELIVERY = R/'build/mini-margin-delivery-1110/verified-delivery.json'
PARENT_DELIVERY_SHA = 'b520fc9af7f82e8b29bf44ad93cb9b5f417657eb98863f599b2ca60ffd40de46'
FOREGROUND = R/'build/native-column-parser-local-1110/foreground.json'
FOREGROUND_SHA = 'f84c5a44442ed6393887538be154c489eacfd26c34641a0cf184b87054546a20'
INTERRUPTS = FOREGROUND.with_name('irq-v2.json')
INTERRUPTS_SHA = '6ed95b2559fdf6296ef20e54fd70b810cfdd318da3477ded5f05d58dd13e7fb4'
ROLE = 'native_column_parser_local'


def stable(value):
    return json.loads(json.dumps(value))


def census():
    assert sha(FOREGROUND)==FOREGROUND_SHA and sha(INTERRUPTS)==INTERRUPTS_SHA
    component,irq = read(FOREGROUND),read(INTERRUPTS)
    assert component['foreground_passed'] and not component['qualified'] and not component['ROM_written']
    assert irq['proved_exact_next_foreground_packet'] and irq['passed'] and not irq['ROM_written']
    verify_interrupts(FOREGROUND,INTERRUPTS,component)
    bindings(component['bindings'])
    refs = {Path(__file__),Path(Parser.__file__),Path(ParserIRQ.__file__),FOREGROUND,INTERRUPTS,
            *map(Path,component['bindings']),*map(Path,irq['bindings'])}

    older,before,_,margin_groups,_,_,_,margin_refs = Margin.census()
    assert BASE.read_bytes()==before and sha(BASE)==PIN
    assert sha(PARENT_MANIFEST)==PARENT_MANIFEST_SHA and sha(PARENT_DELIVERY)==PARENT_DELIVERY_SHA
    parent,installed = read(PARENT_MANIFEST),read(PARENT_DELIVERY)
    assert parent['passed'] and parent['candidate_SHA256']==PIN and parent['groups']==margin_groups
    assert installed['ROM_SHA256']==PIN and installed['composed_proof_SHA256']==PARENT_MANIFEST_SHA
    assert installed['Downloads_launch_verified'] and installed['IPS_roundtrip'] and not installed['backup_created']
    assert installed['active_11_cadence']['no_controller_read']==6
    assert MarginDelivery.Nightly.check(MarginDelivery.Nightly.D)['ROM_sha256']==PIN
    refs.update(margin_refs|{BASE,PARENT_MANIFEST,PARENT_DELIVERY})
    bindings(parent['bindings'])

    patches = component['patches']
    assert component['parent_SHA256']==Parser.PIN==Parser.P.sha(older)
    assert older==Parser.BASE.read_bytes()
    isolated = install(older,patches)
    assert Parser.P.sha(isolated)==component['expected_memory_only_SHA256']==irq['expected_memory_only_SHA256']
    assert [(row['physical_PRG'],row['CPU_half_open'],row['file_offset']) for row in patches]==[
        (2,[0xa2e4,0xa314],17140),(2,[0xbff0,0xbff1],24576)]
    parts = [(row['file_offset'],row['file_offset']+len(bytes.fromhex(row['new_hex']))) for row in patches]
    assert parts[0][1]<=parts[1][0]
    for path in (PARENT_MANIFEST,Margin.PARENT/'proof.json',Margin.Box.BASE.with_name('proof.json')):
        refs.add(path)
        for rows in read(path)['groups'].values():
            for row in rows:
                lo = row['file_offset']
                hi = lo+len(bytes.fromhex(row['new_hex']))
                assert all(end<=lo or hi<=start for start,end in parts),row
    final = install(before,patches)
    undo = [{**row,'old_hex':row['new_hex'],'new_hex':row['old_hex']} for row in patches]
    assert install(final,undo)==before and before[1048592:]==final[1048592:]
    for image in (before,final):
        verify_payload(image,Margin.Seven.KERNEL)
    assert parent['kernel_SHA256']==sha(Margin.Seven.KERNEL)==Parser.M.KERNEL_PIN

    packet = PARENT_PACKETS/'mini'
    with MarginDelivery.validators() as validation:
        route = validation.route_evidence(packet)
    assert route['cadence']==installed['active_11_cadence']
    route_ready = read(packet/'ready.json')
    controller = (packet/'controller.lua').read_text(encoding='utf-8')
    pin = Parser.P.sha(final)
    assert controller.count(PIN)==1 and pin not in controller
    source = controller.replace(PIN,pin,1)
    assert source.replace(pin,PIN,1)==controller
    refs.update({packet/'controller.lua',packet/'ready.json',packet/'capture/result.json',packet/'capture/binding.json',
                 packet/'capture/timing.json',*map(Path,route_ready['bindings'])})
    return before,final,patches,component,irq,parent,refs,source,route_ready


def qualify(before, final, component, irq):
    foreground = Parser.foreground(before,final)
    assert stable(foreground)==component['column_cases']
    whole = Parser.whole(before,final)
    assert stable(whole)==component['whole_GameLoop']
    print('Exact 863e parser final-minus foreground and next-GameLoop checks passed.',flush=True)
    vectors = ParserIRQ.vectors(before,final)
    assert all(irq[key]==value for key,value in stable(vectors).items())
    print('Exact 863e parser final-minus real IRQ, NMI, nested and catchup checks passed.',flush=True)
    return foreground,whole,vectors


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    before,final,patches,component,irq,parent,refs,source,ready = census()
    pin = Parser.P.sha(final)
    print(json.dumps(dict(candidate_SHA256=pin,final_minus_SHA256={ROLE:PIN})),flush=True)
    foreground,whole,vectors = qualify(before,final,component,irq)
    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for ext in ('.dbg','.lbl'):
        sidecar = BASE.with_suffix(ext)
        shutil.copyfile(sidecar,rom.with_suffix(ext))
        assert sha(sidecar)==sha(rom.with_suffix(ext))
    proof_path = out/'proof.json'
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PIN,candidate_SHA256=pin,
                 kernel_SHA256=Parser.M.KERNEL_PIN,groups={ROLE:patches},
                 apply_order=[*parent['apply_order'],ROLE],inherited_groups=parent['apply_order'],
                 final_minus_SHA256={ROLE:PIN},column_cases=foreground,whole_GameLoop=whole,vectors=vectors,
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    parent.update(ROM=str(rom),ROM_written=True,parent_SHA256=PIN,candidate_SHA256=pin,
                  parent_margin_manifest_SHA256=PARENT_MANIFEST_SHA,composed_proof_SHA256=sha(proof_path),
                  groups=proof['groups'],apply_order=proof['apply_order'],final_minus_SHA256=proof['final_minus_SHA256'],
                  ordinary_native_pending=True,verification='Exact local column parser over 863e. Ordinary route pending.')
    manifest.write_text(json.dumps(parent,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,source,refs|{manifest,proof_path},expected=pin,
            timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(p.is_file() for p in out.rglob('*'))==8


if __name__=='__main__':
    main()
