"""Deliver exact 3a after the full native route and all four focused replays pass."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys

import deliver_mini_nightly_root_1103_v30 as Nightly
from deliver_helper_camera_render_1110 import bindings, read, run
import prepare_mini_parser_audio_suites_1110 as Suites
from prepare_selected_native_packet_v1 import sha


R, ROOT, PIN, PREVIOUS = Suites.R,Suites.ROOT,Suites.PIN,Suites.PREVIOUS
Prior = Suites.PARENT_VALIDATORS.Prior
Local = Suites.Batch.Local
EXPECTED_MISSES = {PREVIOUS:6,PIN:5}


@contextmanager
def validators():
    previous = Prior.PIN
    Prior.PIN = PIN
    try:
        with Prior.native_validators() as validation:
            yield validation
    finally:
        Prior.PIN = previous


def native_metrics(packet, pin, route):
    result = Nightly.proof(packet,pin)
    timing = read(packet/'capture/timing.json')
    assert timing['ROM_sha256']==pin and timing['open_calls']==timing['open_interrupts']==0
    assert result['physical_frames']==5300 and result['source_updates']==3501
    cadence = route['cadence']
    assert cadence==timing['cadence']['fullstage']
    assert cadence['physical']==cadence['updates']==3500
    assert cadence['no_controller_read']==cadence['zero_update']==cadence['lag_nmi']==EXPECTED_MISSES[pin]
    normal,lag,irq = (timing['interrupts'][name] for name in ('normal_nmi','lag_nmi','irq'))
    assert normal['calls']+lag['calls']==5292 and irq['calls']==4575
    game = timing['routines']['fullstage']['GameLoop']
    assert game['calls']==3500
    return dict(whole_replay_physical_frames=result['physical_frames'],active_11_cadence=cadence,
                normal_nmi=normal,lag_nmi=lag,irq=irq,nmi_cycles=normal['cycles']+lag['cycles'],
                active_GameLoop_foreground=game['foreground'],active_GameLoop_max_elapsed=game['max'])


def matched_performance(candidate_packet, candidate):
    parent_packet = Suites.PARENT/'mini'
    with Suites.PARENT_VALIDATORS.validators() as validation:
        parent = validation.route_evidence(parent_packet)
    previous = native_metrics(parent_packet,PREVIOUS,parent)
    current = native_metrics(candidate_packet,PIN,candidate)
    assert previous['irq']==current['irq']
    assert current['lag_nmi']['calls']<previous['lag_nmi']['calls']
    normal_saved = previous['normal_nmi']['cycles']-current['normal_nmi']['cycles']
    lag_saved = previous['lag_nmi']['cycles']-current['lag_nmi']['cycles']
    foreground_saved = previous['active_GameLoop_foreground']-current['active_GameLoop_foreground']
    assert (normal_saved,lag_saved,foreground_saved)==(392867,18542,12256)
    assert {k:v for k,v in parent['audio'].items() if k!='ROM_sha256'}=={
        k:v for k,v in candidate['audio'].items() if k!='ROM_sha256'}
    return dict(previous=previous,current=current,normal_nmi_cycles_saved=normal_saved,
                lag_nmi_cycles_saved=lag_saved,total_nmi_cycles_saved=normal_saved+lag_saved,
                active_GameLoop_foreground_cycles_saved=foreground_saved,ordered_audio_matches_parent=True,
                parent_timing_SHA256=sha(parent_packet/'capture/timing.json'),
                candidate_timing_SHA256=sha(candidate_packet/'capture/timing.json'))


def evidence(root):
    rom,raw,proof,manifest = Suites.bind_candidate(root)
    final,minus,groups,_,_,_,_,_,source,_ = Suites.Batch.census()
    assert final==raw
    meta,receipt = read(manifest),read(proof)
    final_minus = {role:Local.Parser.P.sha(image) for role,image in minus.items()}
    assert meta['groups']==receipt['groups']==groups
    assert meta['final_minus_SHA256']==receipt['final_minus_SHA256']==final_minus
    assert set(receipt['final_minus_checks'])==set(groups)
    assert sha(Local.PARENT_DELIVERY)==Local.PARENT_DELIVERY_SHA
    published = read(Local.PARENT_DELIVERY)
    assert published['native_audio_matches_candidate'] and published['camera_edge_spawns_match_candidate']
    assert Path(published['destination']).resolve()==Nightly.D.resolve()
    assert Nightly.check(Nightly.D)['ROM_sha256']==PREVIOUS

    for name in ('mini',*Suites.PACKETS):
        packet = root/('mini' if name=='mini' else f'native/{name}')
        text = source if name=='mini' else Suites.plan(raw,name)[0]
        ready = read(packet/'ready.json')
        assert ready['ROM_sha256']==PIN and Path(ready['ROM']).resolve()==rom.resolve()
        assert ready['emulated_writes'] is False
        for path in (proof,manifest,Suites.KERNEL,Suites.KERNEL.with_suffix('.lbl')):
            assert ready['bindings'][str(path.resolve())]==sha(path)
        bindings(ready['bindings'])
        assert (packet/'controller.lua').read_text(encoding='utf-8')==text

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
    performance = matched_performance(root/'mini',candidate)
    assert performance['previous']['active_11_cadence']==published['active_11_cadence']
    capacity = Prior.Five.Earlier.Earlier.source_capacity(Suites.BASE.read_bytes(),raw)
    return rom,proof,manifest,candidate,dict(injury,handoff_dma=handoff),capacity,performance


def installer(action, output, rom, packet, manifest):
    state = Nightly.O,Nightly.PREVIOUS,sys.argv
    try:
        Nightly.O,Nightly.PREVIOUS = output,PREVIOUS
        sys.argv = [str(Path(Nightly.__file__)),action,'--rom',str(rom),
                    '--packet',str(packet),'--candidate',str(manifest)]
        Nightly.main()
    finally:
        Nightly.O,Nightly.PREVIOUS,sys.argv = state


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--candidate',type=Path,default=ROOT)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--check-only',action='store_true')
    args = cli.parse_args()
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    rom,proof,manifest,candidate,injury,capacity,performance = evidence(root)
    cadence = candidate['cadence']
    if args.check_only:
        print(json.dumps(dict(ready=True,ROM_SHA256=PIN,cadence=cadence,
                              native_corrected_injury=injury,native_performance=performance)),flush=True)
        return

    installer('install',out,rom,root/'mini',manifest)
    installed = out/'downloads-smoke'
    assert Path(read(installed/'ready.json')['ROM']).resolve()==Nightly.D.resolve()
    assert sha(installed/'controller.lua')==sha(root/'mini/controller.lua')
    run([str(installed/'run.py')])
    with validators() as validation:
        downloads = validation.route_evidence(installed)
    assert downloads==candidate,'Downloads route, audio, cadence or lift evidence differs from the candidate'
    assert native_metrics(installed,PIN,downloads)==performance['current']
    assert read(installed/'capture/timing.json')==read(root/'mini/capture/timing.json')
    installer('finalize',out,rom,root/'mini',manifest)

    receipt_path = out/'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256']==Nightly.check(Nightly.D)['ROM_sha256']==PIN
    assert receipt['IPS_SHA256']==sha(out/'SMB-Crossover-Latest-WIP-MMC5.ips')
    fire = read(root/'native/fire/capture/result.json')
    receipt.update(composed_proof_SHA256=sha(proof),candidate_manifest_SHA256=sha(manifest),
                   published_parent_receipt_SHA256=Local.PARENT_DELIVERY_SHA,kernel_SHA256=sha(Suites.KERNEL),
                   native_audio=downloads['audio'],native_audio_matches_candidate=True,
                   camera_edge_spawns=downloads['camera_edge_spawns'],camera_edge_spawns_match_candidate=True,
                   natural_11_source_capacity=capacity,native_corrected_injury=injury,native_lifts=downloads['lifts'],
                   active_11_cadence=cadence,idle_cadence=read(root/'native/idle/capture/timing.json')['cadence'],
                   earned_mushroom=True,moving_phases=fire['moving_art_phases'],impact_frames=fire['impact_art_frames'],
                   previous_comparable_missed_reads=EXPECTED_MISSES[PREVIOUS],lag_free=False,
                   native_performance=dict(performance,downloads_matches_candidate=True,
                                           downloads_timing_SHA256=sha(installed/'capture/timing.json')),
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
        'The shared column parser and audio mixer use fewer cycles. The Downloads replay recorded '
        'five missed controller reads over 3,500 active frames, compared with six on the previous nightly. '
        'Across the complete replay, NMI used 411,409 fewer cycles and the ordered audio register writes '
        'matched. Reopen the ROM and start a fresh game.\n',encoding='utf-8')
    print(json.dumps(dict(delivered=True,ROM_SHA256=PIN,IPS_SHA256=receipt['IPS_SHA256'],cadence=cadence)),flush=True)


if __name__=='__main__':
    main()
