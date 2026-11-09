"""Deliver the retained exact 863e ROM after its ordinary native suite passes."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys

import deliver_mini_helper_powered_injury_1110 as Prior
import deliver_mini_nightly_root_1103_v30 as Nightly
from deliver_helper_camera_render_1110 import bindings, read, run
import prepare_mini_margin_native_1110 as Batch
from prepare_selected_native_packet_v1 import sha


R, ROM, PIN, PREVIOUS = Batch.R,Batch.ROM,Batch.PIN,Batch.PREVIOUS
ROOT = R/'build/mini-margin-native-1110'
PERFORMANCE = dict(cycle_savings=True,box_warm_mini=36,box_other_owners=0,
                   top_score_isolated_range=[-5,72],top_score_whole_fixture=72,
                   goomba_actor_range=[-127,343],goomba_whole_fixture_range=[-9,336],
                   combined_whole_fixture_range=[63,442],combined_mini_fixture_range=[99,442])


@contextmanager
def validators():
    old_pin = Prior.PIN
    Prior.PIN = PIN
    try:
        with Prior.native_validators() as validation:
            yield validation
    finally:
        Prior.PIN = old_pin


def evidence(root):
    parent,final,minus,groups,_,_,_,refs = Batch.census()
    trial,plans = Batch.route_plan(final,refs)
    manifest = root/'candidate.json'
    proof = read(manifest)
    assert proof['passed'] and not proof['ROM_written'] and proof['ordinary_native_pending']
    assert Path(proof['ROM']).resolve()==ROM.resolve() and sha(ROM)==proof['candidate_SHA256']==PIN
    assert proof['parent_SHA256']==PREVIOUS and proof['groups']==groups
    assert proof['final_minus_SHA256']=={role:Batch.Score.P.sha(raw) for role,raw in minus.items()}
    assert set(proof['final_minus_checks'])==set(groups)
    assert sum(len(row['cycles_saved']) for row in proof['combined_GameLoop'])==160
    assert proof['trial_composed_proof_SHA256']==Batch.TRIAL_PROOF_SHA
    assert proof['kernel_SHA256']==sha(Batch.Seven.KERNEL) and proof['cold_loader_exact_attribute_table']
    bindings(proof['bindings'])
    for name,source,_,_ in plans:
        packet = root/name
        ready = read(packet/'ready.json')
        assert ready['ROM_sha256']==PIN and Path(ready['ROM']).resolve()==ROM.resolve()
        assert ready['bindings'][str(manifest.resolve())]==sha(manifest)
        assert (packet/'controller.lua').read_text(encoding='utf-8')==source

    published = read(Batch.PUBLISHED)
    assert published['native_audio_matches_candidate'] and published['camera_edge_spawns_match_candidate']
    assert Path(published['destination']).resolve()==Nightly.D.resolve()
    assert Nightly.check(Nightly.D)['ROM_sha256']==PREVIOUS
    previous = published['active_11_cadence']
    with validators() as validation:
        validation.native_suite(root,ROM)
        candidate = validation.route_evidence(root/'mini')
        injury = Prior.corrected_injury(root/'native/injury',ROM)
    assert candidate==trial,'Ordinary route differs from the exact instrumented trial'
    cadence = candidate['cadence']
    assert cadence['physical']==previous['physical']==cadence['updates']==previous['updates']==3500
    assert cadence['no_controller_read']==cadence['zero_update']==6 and previous['no_controller_read']==7
    witness = read(root/'native/injury/capture/result.json')['injury_helper']
    handoff = witness['handoff_dma']
    assert handoff['page']==2 and handoff['draw_engine']==10
    assert handoff['actual']==handoff['expected'] and handoff['stale_actual']!=handoff['stale_expected']
    assert handoff['counter']==(handoff['draw_counter']+1)&255
    assert witness['oam_clears']>0 and witness['observed_injury_dmas']>0
    capacity = Prior.Five.Earlier.Earlier.source_capacity(parent,final)
    return manifest,candidate,dict(injury,handoff_dma=handoff),previous,capacity


def installer(action, output, packet, manifest):
    previous = Nightly.O,Nightly.PREVIOUS,sys.argv
    try:
        Nightly.O,Nightly.PREVIOUS = output,PREVIOUS
        sys.argv = [str(Path(Nightly.__file__)),action,'--rom',str(ROM),
                    '--packet',str(packet),'--candidate',str(manifest)]
        Nightly.main()
    finally:
        Nightly.O,Nightly.PREVIOUS,sys.argv = previous


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--candidate',type=Path,default=ROOT)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--check-only',action='store_true')
    args = cli.parse_args()
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    manifest,candidate,injury,previous,capacity = evidence(root)
    if args.check_only:
        print(json.dumps(dict(ready=True,ROM_SHA256=PIN,cadence=candidate['cadence'],native_corrected_injury=injury)),flush=True)
        return

    installer('install',out,root/'mini',manifest)
    installed = out/'downloads-smoke'
    assert Path(read(installed/'ready.json')['ROM']).resolve()==Nightly.D.resolve()
    assert sha(installed/'controller.lua')==sha(root/'mini/controller.lua')
    run([str(installed/'run.py')])
    with validators() as validation:
        downloads = validation.route_evidence(installed)
    assert downloads==candidate,'Downloads route, audio, cadence or lifts differ from the candidate'
    installer('finalize',out,root/'mini',manifest)

    receipt_path = out/'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256']==Nightly.check(Nightly.D)['ROM_sha256']==PIN
    assert receipt['IPS_SHA256']==sha(out/'SMB-Crossover-Latest-WIP-MMC5.ips')
    idle = read(root/'native/idle/capture/timing.json')['cadence']
    fire = read(root/'native/fire/capture/result.json')
    cadence = downloads['cadence']
    receipt.update(composed_proof_SHA256=sha(manifest),published_parent_receipt_SHA256=Batch.PUBLISHED_SHA,
                   kernel_SHA256=sha(Batch.Seven.KERNEL),native_audio=downloads['audio'],
                   native_audio_matches_candidate=True,camera_edge_spawns=downloads['camera_edge_spawns'],
                   camera_edge_spawns_match_candidate=True,natural_11_source_capacity=capacity,
                   native_corrected_injury=injury,native_lifts=downloads['lifts'],active_11_cadence=cadence,
                   idle_cadence=idle,earned_mushroom=True,moving_phases=fire['moving_art_phases'],
                   impact_frames=fire['impact_art_frames'],previous_comparable_missed_reads=previous['no_controller_read'],
                   lag_free=cadence['no_controller_read']==0,performance_tradeoffs=PERFORMANCE,
                   verification_scope='Exact Downloads controller-only 1-1 into 1-2 with three native lifts and both lives. '
                                      'Exact candidate idle/movement, earned mushroom, focused two-shot Goomba impact, '
                                      'and corrected native injury with actual DMA passed.')
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'release-notes.txt').write_text(
        'Current MMC5 work-in-progress nightly.\n\n'
        'Apply this IPS to clean, headered Super Mario Bros. (World).\n'
        f'Base SHA-256 {receipt["base_SHA256"]}\nPatched ROM SHA-256 {PIN}\n\n'
        'Mini clears 1-1 using the native lifts at left edges X560, X688 and X864. Each lift is '
        '32 pixels wide and begins at top Y192. The replay retained both lives.\n\n'
        'Mini’s box mapper and the common top-score path use fewer cycles. The Goomba terrain '
        'shortcut saves time on a successful left-edge check and adds work when that check falls back. '
        'The Downloads route recorded six missed controller reads over 3,500 frames, compared '
        'with seven on the prior nightly. Reopen the ROM and start a fresh game.\n',encoding='utf-8')
    print(json.dumps(dict(delivered=True,ROM_SHA256=PIN,IPS_SHA256=receipt['IPS_SHA256'],cadence=cadence)),flush=True)


if __name__=='__main__':
    main()
