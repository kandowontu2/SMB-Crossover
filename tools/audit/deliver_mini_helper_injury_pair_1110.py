"""Deliver the verified Mini injury-safe lifts and native actor composition."""

import argparse
import json
from pathlib import Path

import deliver_mini_nightly_root_1103_v30 as nightly
import deliver_mini_helper_activation_1110 as Earlier
import prepare_mini_helper_injury_native_1110_v2 as Batch
from deliver_helper_camera_render_1110 import bindings, mini_evidence, read, run
from prepare_selected_native_packet_v1 import sha


R = Batch.R
PIN = 'dad3943de199cb7bfd40e55183caf14419e29fb65faaca23a85d46f4f8f50a38'
PREVIOUS = Batch.H.PIN
NATIVE_STATUS = R/'docs/qa/mini-injury-native-status-native-witness-1110.md'


def route_evidence(packet):
    checked = mini_evidence(packet,PIN)
    capture = packet/'capture'
    result = read(capture/'result.json')
    last = result['terminal_native']
    fields = ('SelectedCharacter','WorldNumber','LevelNumber','GameEngineSubroutine',
              'OperMode','OperMode_Task','NumberofLives')
    assert tuple(last[key] for key in fields)==(41,0,1,8,1,3,2)
    assert result['helpers_added'] and result['phases']['fullstage']['wall_restarts']==0
    assert tuple((row['left'],row['center'],row['spawn_top'],row['width']) for row in checked['lifts'])==Earlier.LIFTS
    for row in checked['lifts']:
        assert row['stage']=='1-1' and row['initial_top']==192
        assert row['boarding_press'] and row['departure_press']
        assert row['spawn_frame']<row['board_frame']<row['departure_frame']
    spawns = read(capture/'camera-lifts.json')
    assert spawns==[dict(frame=row['spawn_frame'],left=row['left'],relative_x=row['spawn_relative_x'],
                         slot=row['slot'],top=row['spawn_top']) for row in checked['lifts']]
    assert all(256<=row['relative_x']<=263 for row in spawns)
    assert checked['audio']['terminal_tokens']>0 and checked['audio']['ordered_music_image_writes']>0
    return dict(checked,camera_edge_spawns=spawns)


def injury_evidence(packet,rom):
    result = nightly.proof(packet,PIN)
    ready = read(packet/'ready.json')
    assert Path(ready['ROM']).resolve()==rom.resolve() and not ready['emulated_writes']
    assert ready['bindings'][str(Batch.Strict.KERNEL.resolve())]==sha(Batch.Strict.KERNEL)
    earned = result['earned_power']
    assert earned['completed'] and earned['mature'] and earned['item_lost']['status']==1
    witness = result['injury_helper']
    assert witness['completed']
    force,start,birth,visible = (witness[key] for key in ('force','start','constructor','visible'))
    assert force['status']==1 and force['engine']==8 and force['right']<856
    assert force['enemy']['flag']==1 and force['enemy']['id'] in (2,6)
    assert start['engine']==10 and start['timer']==0xef and start['status']==41
    assert birth['engine']==10 and 0xc9<=birth['timer']<=0xef
    assert 856<=birth['right']<=863 and birth['relative_x']==864-birth['right']+255
    assert birth['top']==192 and 0<=birth['slot']<6
    actor = visible['actor']
    assert visible['engine']==10 and visible['right']>=864 and visible['seen']&4
    assert visible['status']==41 and result['last']['lives']==2
    assert tuple(actor[key] for key in ('slot','flag','id','state','x','y_high','box'))==(
        birth['slot'],1,0x25,0x40,864,1,5)
    assert 1<=len(witness['native_steps'])<=39
    assert all(row['engine']==10 and 0xc9<=row['timer']<=0xef for row in witness['native_steps'])
    return dict(packet=str(packet),ready_SHA256=sha(packet/'ready.json'),
                result_SHA256=sha(packet/'capture/result.json'),constructor=birth,
                visible=visible,native_movement_updates=len(witness['native_steps']),lives=2,
                preexisting_powered_status=41)


def native_suite(root,rom):
    for name in ('mini','native/idle','native/power','native/fire'):
        ready = read(root/name/'ready.json')
        assert ready['ROM_sha256']==PIN and Path(ready['ROM']).resolve()==rom
        assert not ready['emulated_writes']
        if name!='native/fire':
            assert ready['bindings'][str(Batch.Strict.KERNEL.resolve())]==sha(Batch.Strict.KERNEL)
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
    ready_path = fire/'ready.json'
    bind,result = (read(fire/'capture'/name) for name in ('binding.json','result.json'))
    assert bind['ROM_sha256']==result['ROM_sha256']==PIN and bind['exit_code']==0 and result['passed']
    assert bind['ready_sha256']==sha(ready_path)
    bindings(read(ready_path)['bindings'])
    assert result['max_active_fireballs']==result['max_visible_fireballs']==2
    assert result['staged_goomba_hit'] and all(result['concurrent_DMA_by_direction'].values())
    assert result['moving_art_phases']=={str(i):True for i in range(4)}
    assert result['impact_art_frames']==dict(C=True,D=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--injury-packet',type=Path)
    parser.add_argument('--require-injury',action='store_true',help='Require the exact passing native injury witness.')
    parser.add_argument('--check-only',action='store_true',help='Check all supplied receipts without writing or launching.')
    args = parser.parse_args()
    assert not args.require_injury or args.injury_packet is not None
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    rom,path = root/'candidate.nes',root/'proof.json'
    parent,_,final,_,_,groups = Batch.components()
    assert rom.read_bytes()==final and sha(rom)==PIN
    proof = read(path)
    assert proof['passed'] and proof['parent_SHA256']==PREVIOUS and proof['candidate_SHA256']==PIN
    assert proof['groups']==groups and set(groups)==set(proof['final_minus_SHA256'])==set(Batch.GROUPS)
    assert proof['kernel_SHA256']==sha(Batch.Strict.KERNEL) and proof['birth_relative_left']==[256,263]
    for suffix in ('.dbg','.lbl'):
        assert sha(rom.with_suffix(suffix))==sha(Batch.H.BASE.with_suffix(suffix))
    bindings(proof['bindings'])
    meta = read(rom.with_suffix('.json'))
    assert meta['candidate_SHA256']==PIN and meta['composed_proof_SHA256']==sha(path)
    published = read(Earlier.PUBLISHED)
    assert published['ROM_SHA256']==PREVIOUS and published['Downloads_launch_verified'] and published['IPS_roundtrip']
    assert published['native_audio_matches_candidate'] and not published['backup_created']
    assert Path(published['destination']).resolve()==nightly.D.resolve()
    assert nightly.check(nightly.D)['ROM_sha256']==PREVIOUS
    previous = published['active_11_cadence']
    assert previous['no_controller_read']==35
    capacity = Earlier.source_capacity(parent,final)
    native_suite(root,rom)
    candidate = route_evidence(root/'mini')
    witness = injury_evidence(args.injury_packet.resolve(),rom) if args.injury_packet else None
    if args.check_only:
        print(json.dumps(dict(ready=True,ROM_SHA256=PIN,cadence=candidate['cadence'],
                              exact_native_injury_witness=bool(witness))),flush=True)
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
    assert downloads==candidate,'Downloads route, audio, cadence or lift evidence differs from the candidate'
    run([installer,'finalize',*common])

    receipt_path = out/'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256']==nightly.check(nightly.D)['ROM_sha256']==PIN
    assert receipt['IPS_SHA256']==sha(out/'SMB-Crossover-Latest-WIP-MMC5.ips')
    cadence = downloads['cadence']
    receipt.update(composed_proof_SHA256=sha(path),published_parent_receipt_SHA256=sha(Earlier.PUBLISHED),
                   kernel_SHA256=sha(Batch.Strict.KERNEL),native_audio=downloads['audio'],
                   native_audio_matches_candidate=True,camera_edge_spawns=downloads['camera_edge_spawns'],
                   camera_edge_spawns_match_candidate=True,natural_11_source_capacity=capacity,
                   native_injury_helper=witness,prior_native_powered_status_note_SHA256=sha(NATIVE_STATUS),
                   previous_comparable_missed_reads=previous['no_controller_read'],
                   lag_free=cadence['no_controller_read']==0)
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    with (out/'release-notes.txt').open('a',encoding='utf-8') as f:
        f.write('\nMini’s three native 1-1 lifts start 256–263 pixels from the camera’s left edge. '
                'The Downloads replay verified all three crossings and retained both lives. '
                f'The route recorded {cadence["no_controller_read"]} missed reads over '
                f'{cadence["physical"]} physical frames, compared with {previous["no_controller_read"]} '
                f'over {previous["physical"]} on the prior route. '
                'Shared native enemy dispatch and pair collision use fewer CPU cycles.\n')
    print(json.dumps(dict(delivered=True,ROM_SHA256=PIN,IPS_SHA256=receipt['IPS_SHA256'],cadence=cadence)),flush=True)


if __name__=='__main__':
    main()
