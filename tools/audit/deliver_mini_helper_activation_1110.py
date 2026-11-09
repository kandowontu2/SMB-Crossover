"""Deliver the qualified offscreen-only Mini helper activation build."""

import argparse
import json
from pathlib import Path

import deliver_mini_nightly_root_1103_v30 as nightly
import prepare_mini_helper_activation_native_1110 as activation
from compose_mini_frame_budget_1108 import digest
from deliver_helper_camera_render_1110 import bindings, mini_evidence, read, run
from prepare_selected_native_packet_v1 import sha


R = activation.R
PREVIOUS = activation.H.PIN
PIN = activation.TARGET
PUBLISHED = R/'build/mini-contact-lag-delivery-1110/verified-delivery.json'
LIFTS = tuple((left,left+16,192,32) for left in activation.H.LEFTS)
CAPACITY_STREAMS = {
    'E_GroundArea6':(19023,30,'f091a27d7278196232a796c0fab0f7e44cfea0181b8d0bf69f827655463891da'),
    'L_GroundArea6':(20956,101,'162fc0bf0e2e7bd2ecda0ac1bf3551ee5f45a3f116fa6343badda72005c0b4ec'),
}


def source_capacity(parent,final):
    streams = {}
    for name,(offset,length,h) in CAPACITY_STREAMS.items():
        assert parent[offset:offset+length]==final[offset:offset+length]
        assert digest(final[offset:offset+length])==h
        streams[name] = dict(file_offset=offset,bytes=length,SHA256=h)
    return dict(streams=streams,native_slots=6,max_occupied_before_birth=[2,4,5],
                scope='Source audit of natural Mini 1-1 actor and pickup admissions in both difficulty modes, '
                      'including earlier native lifts, the native left-edge cull and no slot-forcing stage objects.',
                synthetic_full_pool='The CPU proof covers a full pool. If no slot frees while the camera is '
                                    'inside the eight-pixel offscreen window, the lift is skipped.')


def route_evidence(packet):
    route = mini_evidence(packet,PIN)
    capture = packet/'capture'
    result = read(capture/'result.json')
    last = result['terminal_native']
    assert tuple(last[key] for key in ('SelectedCharacter','WorldNumber','LevelNumber',
                                       'GameEngineSubroutine','OperMode','OperMode_Task','NumberofLives')) == (
                                           41,0,1,8,1,3,2)
    assert result['helpers_added'] and result['phases']['fullstage']['wall_restarts']==0
    assert tuple((row['left'],row['center'],row['spawn_top'],row['width']) for row in route['lifts'])==LIFTS
    for row in route['lifts']:
        assert row['stage']=='1-1' and row['initial_top']==192
        assert row['boarded'] and row['departed'] and row['boarding_press'] and row['departure_press']
        assert row['spawn_frame']<row['board_frame']<row['departure_frame']
    spawns = read(capture/'camera-lifts.json')
    assert spawns==[dict(frame=row['spawn_frame'],left=row['left'],relative_x=row['spawn_relative_x'],
                         slot=row['slot'],top=row['spawn_top']) for row in route['lifts']]
    assert all(256<=row['relative_x']<=263 for row in spawns)
    assert route['audio']['terminal_tokens']>0 and route['audio']['ordered_music_image_writes']>0
    return dict(route,camera_edge_spawns=spawns)


def native_suite(root):
    for name in ('mini','native/idle','native/power','native/fire'):
        packet = root/name
        ready = read(packet/'ready.json')
        assert ready['ROM_sha256']==PIN and not ready['emulated_writes']
        assert Path(ready['ROM']).resolve()==root/'candidate.nes'
        if name!='native/fire':
            assert ready['bindings'][str(activation.KERNEL.resolve())]==sha(activation.KERNEL)
    idle,power,fire = (root/'native'/name for name in ('idle','power','fire'))
    nightly.proof(idle,PIN)
    timing = read(idle/'capture/timing.json')
    assert timing['ROM_sha256']==PIN
    for phase in ('idle','right','left','brake','jump','landing'):
        row = timing['cadence'][phase]
        assert row['physical']==row['updates'] and row['lag_nmi']==row.get('no_controller_read',0)==0
    assert timing['cadence']['idle']['updates']==180
    earned = nightly.proof(power,PIN)['earned_power']
    assert earned['completed'] and earned['mature'] and earned['item_lost']['status']==1
    ready = read(fire/'ready.json')
    bind,result = (read(fire/'capture'/name) for name in ('binding.json','result.json'))
    assert bind['exit_code']==0 and bind['ready_sha256']==sha(fire/'ready.json')
    assert bind['ROM_sha256']==result['ROM_sha256']==PIN and result['passed']
    bindings(ready['bindings'])
    assert result['max_active_fireballs']==result['max_visible_fireballs']==2
    assert result['staged_goomba_hit'] and all(result['concurrent_DMA_by_direction'].values())
    assert result['moving_art_phases']=={str(i):True for i in range(4)}
    assert result['impact_art_frames']==dict(C=True,D=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--check-only',action='store_true',help='Check all receipts without writing or launching.')
    args = parser.parse_args()
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    rom = root/'candidate.nes'
    parent,final,component = activation.bound_image()
    assert rom.read_bytes()==final and sha(rom)==PIN
    for suffix in ('.dbg','.lbl'):
        assert sha(rom.with_suffix(suffix))==sha(activation.H.BASE.with_suffix(suffix))
    path = root/'proof.json'
    proof = read(path)
    assert proof['passed'] and proof['parent_SHA256']==PREVIOUS and proof['candidate_SHA256']==PIN
    assert proof['patches']==component['patches'] and len(proof['patches'])==4
    assert proof['kernel_SHA256']==sha(activation.KERNEL) and proof['birth_relative_left']==[256,263]
    bindings(proof['bindings'])
    manifest = read(rom.with_suffix('.json'))
    assert manifest['candidate_SHA256']==PIN and manifest['composed_proof_SHA256']==sha(path)
    published = read(PUBLISHED)
    assert published['ROM_SHA256']==PREVIOUS and published['Downloads_launch_verified'] and published['IPS_roundtrip']
    assert published['native_audio_matches_candidate'] and not published['backup_created']
    assert Path(published['destination']).resolve()==nightly.D.resolve()
    assert nightly.check(nightly.D)['ROM_sha256']==PREVIOUS
    previous_cadence = published['active_11_cadence']
    assert previous_cadence['no_controller_read']==35
    capacity = source_capacity(parent,final)
    native_suite(root)
    candidate = route_evidence(root/'mini')
    if args.check_only:
        print(json.dumps(dict(ready=True,ROM_SHA256=PIN,cadence=candidate['cadence'])),flush=True)
        return

    common = ['--candidate',str(root),'--route',str(root/'mini'),
              '--idle',str(root/'native/idle'),'--power',str(root/'native/power'),
              '--fire',str(root/'native/fire'),'--output',str(out),'--previous',PREVIOUS]
    installer = 'tools/audit/deliver_mini_lifts_art_1108.py'
    run([installer,'install',*common])
    installed = out/'downloads-smoke'
    assert Path(read(installed/'ready.json')['ROM']).resolve()==nightly.D.resolve()
    assert sha(installed/'controller.lua')==sha(root/'mini/controller.lua')
    run([str(installed/'run.py')])
    downloads = route_evidence(installed)
    assert downloads==candidate,'Downloads route, audio, cadence or camera-lift evidence differs from the candidate'
    run([installer,'finalize',*common])

    receipt_path = out/'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256']==nightly.check(nightly.D)['ROM_sha256']==PIN
    assert receipt['IPS_SHA256']==sha(out/'SMB-Crossover-Latest-WIP-MMC5.ips')
    cadence = downloads['cadence']
    receipt.update(composed_proof_SHA256=sha(path),published_parent_receipt_SHA256=sha(PUBLISHED),
                   kernel_SHA256=sha(activation.KERNEL),native_audio=downloads['audio'],
                   native_audio_matches_candidate=True,camera_edge_spawns=downloads['camera_edge_spawns'],
                   camera_edge_spawns_match_candidate=True,natural_11_source_capacity=capacity,
                   previous_comparable_missed_reads=previous_cadence['no_controller_read'],
                   lag_free=cadence['no_controller_read']==0)
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    notes = out/'release-notes.txt'
    with notes.open('a',encoding='utf-8') as f:
        f.write('\nMini’s three 1-1 lifts start 256–263 pixels from the camera’s left edge and scroll into view. '
                'The exact Downloads replay verified all three crossings and retained both lives. '
                f'The replay recorded {cadence["no_controller_read"]} missed reads in {cadence["physical"]} '
                f'physical frames, compared with {previous_cadence["no_controller_read"]} in '
                f'{previous_cadence["physical"]} on the prior route.\n')
    print(json.dumps(dict(delivered=True,ROM_SHA256=PIN,IPS_SHA256=receipt['IPS_SHA256'],cadence=cadence)),flush=True)


if __name__=='__main__':
    main()
