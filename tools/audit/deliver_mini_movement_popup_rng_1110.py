"""Deliver exact f518 after native movement, power, fire and injury checks."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path

import deliver_mini_helper_powered_injury_1110 as Prior
import deliver_mini_nightly_root_1103_v30 as Nightly
import prepare_mini_movement_popup_rng_suites_1110 as Suites
from deliver_helper_camera_render_1110 import bindings, read, run
from prepare_selected_native_packet_v1 import sha


R, ROOT, PIN, PREVIOUS = Suites.R,Suites.ROOT,Suites.PIN,Suites.PREVIOUS
PARENT_DELIVERY = R/'build/mini-helper-powered-injury-delivery-1110/verified-delivery.json'
PARENT_RECEIPT_SHA = 'b280939fbb8679f5fa012b4ebe96e3a195602d7684faefc60edf8aeb3c182166'
INSTALLER = 'tools/audit/deliver_mini_lifts_art_1108.py'


@contextmanager
def validators():
    pin = Prior.PIN
    Prior.PIN = PIN
    try:
        with Prior.native_validators() as validation:
            yield validation
    finally:
        Prior.PIN = pin


def exact_candidate(root):
    rom,path = root/'candidate.nes',root/'proof.json'
    proof,meta = read(path),read(rom.with_suffix('.json'))
    assert proof['passed'] and proof['ROM_written'] and proof['native_pending']
    assert proof['parent_SHA256']==meta['parent_SHA256']==PREVIOUS
    assert proof['candidate_SHA256']==meta['candidate_SHA256']==sha(rom)==PIN
    assert meta['composed_proof_SHA256']==sha(path)==Suites.PROOF_SHA
    assert proof['kernel_SHA256']==meta['kernel_SHA256']==Suites.Batch.Movement.KERNEL_PIN
    assert set(proof['groups'])==set(proof['final_minus_SHA256'])==set(Suites.Batch.ROLES)
    assert sum(len(row['cycles_saved']) for row in proof['combined_GameLoop'])==160
    bindings(proof['bindings'])
    parent,final,_,groups,_,_,_,_,controller,_ = Suites.Batch.census()
    assert rom.read_bytes()==final and proof['groups']==groups
    assert (root/'mini/controller.lua').read_text(encoding='utf-8')==controller
    for ext in ('.dbg','.lbl'):
        assert sha(rom.with_suffix(ext))==sha(Suites.PARENT.with_suffix(ext))
    assert sha(PARENT_DELIVERY)==PARENT_RECEIPT_SHA
    delivered = read(PARENT_DELIVERY)
    assert delivered['ROM_SHA256']==PREVIOUS and delivered['Downloads_launch_verified']
    assert delivered['IPS_roundtrip'] and not delivered['backup_created']
    assert delivered['native_audio_matches_candidate'] and delivered['camera_edge_spawns_match_candidate']
    assert Path(delivered['destination']).resolve()==Nightly.D.resolve()
    assert Nightly.check(Nightly.D)['ROM_sha256']==PREVIOUS
    previous = delivered['active_11_cadence']
    assert previous['no_controller_read']==9
    capacity = Prior.Five.Earlier.Earlier.source_capacity(parent,final)
    return rom,path,previous,capacity


def candidate_evidence(root, rom, previous):
    for name,template in Suites.PACKETS.items():
        old = (template/'controller.lua').read_text(encoding='utf-8')
        new = (root/'native'/name/'controller.lua').read_text(encoding='utf-8')
        assert old.count(PREVIOUS)==new.count(PIN)==1 and new==old.replace(PREVIOUS,PIN,1)
    with validators() as validation:
        validation.native_suite(root,rom)
        candidate = validation.route_evidence(root/'mini')
        injury = Prior.corrected_injury(root/'native/injury',rom)
    witness = read(root/'native/injury/capture/result.json')['injury_helper']
    handoff = witness['handoff_dma']
    assert handoff['page']==2 and handoff['draw_engine']==10
    assert handoff['actual']==handoff['expected'] and handoff['stale_actual']!=handoff['stale_expected']
    assert handoff['counter']==(handoff['draw_counter']+1)&255
    assert witness['oam_clears']>0 and witness['observed_injury_dmas']>0
    cadence = candidate['cadence']
    assert cadence['physical']==previous['physical']==3500 and cadence['updates']==previous['updates']==3500
    assert cadence['no_controller_read']==7 and cadence['zero_update']==7
    return candidate,dict(injury,handoff_dma=handoff)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--candidate',type=Path,default=ROOT)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--check-only',action='store_true')
    args = cli.parse_args()
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    rom,path,previous,capacity = exact_candidate(root)
    candidate,injury = candidate_evidence(root,rom,previous)
    if args.check_only:
        print(json.dumps(dict(ready=True,ROM_SHA256=PIN,cadence=candidate['cadence'],native_corrected_injury=injury)),flush=True)
        return

    common = ['--candidate',str(root),'--route',str(root/'mini'),
              '--idle',str(root/'native/idle'),'--power',str(root/'native/power'),
              '--fire',str(root/'native/fire'),'--output',str(out),'--previous',PREVIOUS]
    run([INSTALLER,'install',*common])
    installed = out/'downloads-smoke'
    assert Path(read(installed/'ready.json')['ROM']).resolve()==Nightly.D.resolve()
    assert sha(installed/'controller.lua')==sha(root/'mini/controller.lua')
    run([str(installed/'run.py')])
    with validators() as validation:
        downloads = validation.route_evidence(installed)
    assert downloads==candidate,'Downloads route, audio, cadence or lifts differ from the candidate'
    run([INSTALLER,'finalize',*common])

    receipt_path = out/'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256']==Nightly.check(Nightly.D)['ROM_sha256']==PIN
    assert receipt['IPS_SHA256']==sha(out/'SMB-Crossover-Latest-WIP-MMC5.ips')
    cadence = downloads['cadence']
    receipt.update(composed_proof_SHA256=sha(path),published_parent_receipt_SHA256=PARENT_RECEIPT_SHA,
                   kernel_SHA256=Suites.Batch.Movement.KERNEL_PIN,native_audio=downloads['audio'],
                   native_audio_matches_candidate=True,camera_edge_spawns=downloads['camera_edge_spawns'],
                   camera_edge_spawns_match_candidate=True,natural_11_source_capacity=capacity,
                   native_corrected_injury=injury,previous_comparable_missed_reads=previous['no_controller_read'],
                   lag_free=cadence['no_controller_read']==0)
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    with (out/'release-notes.txt').open('a',encoding='utf-8') as notes:
        notes.write('\nMini movement and shared popup and random-number updates use fewer CPU cycles. '
                    'The Downloads 1-1 replay recorded seven missed controller reads over 3,500 frames, '
                    'compared with nine on the prior nightly. The corrected native injury replay retained '
                    'both lives and verified the small collision box and sprite through actual DMA.\n')
    print(json.dumps(dict(delivered=True,ROM_SHA256=PIN,IPS_SHA256=receipt['IPS_SHA256'],cadence=cadence)),flush=True)


if __name__=='__main__':
    main()
