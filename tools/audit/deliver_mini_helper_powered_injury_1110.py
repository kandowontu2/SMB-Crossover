"""Deliver the seven-group Mini composition after native injury qualification."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path

import deliver_mini_helper_injury_column_1110 as Five
import deliver_mini_nightly_root_1103_v30 as nightly
import prepare_mini_helper_injury_native_1110_v5 as Batch
from compose_mini_frame_budget_1108 import digest
from deliver_helper_camera_render_1110 import bindings, read, run
from prepare_selected_native_packet_v1 import sha


R = Batch.R
PIN = 'f003b378b0e5bd862403eae71f267d8c33a3b06e9270548ae20b1d9f6b2f9979'
PREVIOUS = Five.PIN
PUBLISHED = R/'build/mini-helper-injury-column-delivery-1110/verified-delivery.json'
PREVIOUS_IPS = '25e0e351fd57b5c2407dee477ab23dc04b805a291849f924fc575841c737a6b3'


@contextmanager
def native_validators():
    # The shared idle/power/fire and full-stage schemas stay the same.
    strict = Five.Earlier.Batch.Strict
    previous = strict.KERNEL
    strict.KERNEL = Batch.KERNEL
    try:
        with Five.exact_native_validators(PIN):
            yield Five.Earlier
    finally:
        strict.KERNEL = previous


def corrected_injury(packet,rom):
    result = nightly.proof(packet,PIN)
    ready = read(packet/'ready.json')
    assert Path(ready['ROM']).resolve()==rom.resolve() and not ready['emulated_writes']
    assert ready['bindings'][str(Batch.KERNEL.resolve())]==sha(Batch.KERNEL)
    assert ready['bindings'][str(Batch.KERNEL.with_suffix('.lbl').resolve())]==sha(Batch.KERNEL.with_suffix('.lbl'))
    earned = result['earned_power']
    assert earned['completed'] and earned['mature'] and earned['item_lost']['status']==1
    witness = result['injury_helper']
    assert witness['completed'] and witness['native_status_transition']==dict(before=1,during=0)
    force,start,birth,visible = (witness[key] for key in ('force','start','constructor','visible'))
    assert force['status']==1 and force['engine']==8 and force['right']<856
    assert force['enemy']['flag']==1 and force['enemy']['id'] in (2,6)
    assert start['engine']==10 and start['timer']==0xef and start['status']==0
    fallback,store = (witness[key] for key in ('fallback','status_store'))
    assert fallback==dict(frame=force['frame'],pc=Batch.Status.LEAF,old=1)
    assert store==dict(frame=force['frame'],pc=Batch.Status.STORE,old=1,value=0,carry=0)
    assert witness['jump_request'] and witness['jump_ack']['engine']==10 and witness['airborne']
    assert birth['engine']==10 and 0xc9<=birth['timer']<=0xef
    assert 856<=birth['right']<=863 and birth['relative_x']==864-birth['right']+255
    assert birth['top']==192 and 0<=birth['slot']<6
    assert visible['engine']==10 and visible['right']>=864 and visible['seen']&4 and visible['status']==0
    assert visible['sprite_chr4']==968 and birth['frame']<=visible['frame']
    actor = visible['actor']
    assert tuple(actor[key] for key in ('slot','flag','id','state','x','y_high','box'))==(
        birth['slot'],1,0x25,0x40,864,1,5)
    steps = witness['native_steps']
    assert len(steps)==39 and [row['timer'] for row in steps]==list(range(0xef,0xc8,-1))
    assert all(row['engine']==10 and row['status']==0 and row['source_tier']==1 and row['source_top']==0xf9
               for row in steps)
    step,box,draw,update,dma = (witness[key] for key in ('first_source_step','first_source_box','first_source_draw',
                                                        'first_source_update','first_small_dma'))
    assert step['tier']==update['tier']==0 and step['top']==update['top']==1
    assert step['counter']==box['counter']==draw['counter']==update['counter']
    assert update['source']==step['source']+1 and update['pose']==draw['pose']
    assert (box['width'],box['height'])==(6,7)
    assert tuple((hi-lo)&255 for lo,hi in zip(box['upper_left'],box['lower_right'],strict=True))==(5,6)
    assert 0<=draw['pose']<39 and 0<draw['tile']<=31 and 0<=dma['pose']<39 and 0<dma['tile']<=31
    assert dma['chr4']==968 and dma['frame']>=draw['frame']
    assert result['last']['lives']==update['lives']==2
    return dict(packet=str(packet),ready_SHA256=sha(packet/'ready.json'),
                result_SHA256=sha(packet/'capture/result.json'),fallback=fallback,status_store=store,
                constructor=birth,visible=visible,native_movement_updates=len(steps),lives=2,
                first_source_update=update,first_source_box=box,first_source_draw=draw,first_small_dma=dma)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--injury-packet',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--check-only',action='store_true',help='Check the exact native receipts without writing or launching.')
    args = parser.parse_args()
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    rom,path = root/'candidate.nes',root/'proof.json'
    parent,_,six,final,_,groups = Batch.components()
    assert rom.read_bytes()==final and sha(rom)==PIN
    proof = read(path)
    assert proof['passed'] and proof['parent_SHA256']==Batch.H.PIN and proof['candidate_SHA256']==PIN
    assert proof['immediate_six_group_SHA256']==digest(six)
    assert proof['groups']==groups and tuple(proof['apply_order'])==Batch.GROUPS
    assert set(groups)==set(proof['final_minus_SHA256'])==set(Batch.GROUPS)
    assert proof['kernel_SHA256']==sha(Batch.KERNEL) and proof['birth_relative_left']==[256,263]
    for suffix in ('.dbg','.lbl'):
        assert sha(rom.with_suffix(suffix))==sha(Batch.H.BASE.with_suffix(suffix))
    bindings(proof['bindings'])
    meta = read(rom.with_suffix('.json'))
    assert meta['candidate_SHA256']==PIN and meta['composed_proof_SHA256']==sha(path)
    assert meta['kernel_SHA256']==proof['kernel_SHA256'] and meta['parent_SHA256']==digest(six)

    published = read(PUBLISHED)
    assert published['ROM_SHA256']==PREVIOUS and published['IPS_SHA256']==PREVIOUS_IPS
    assert published['Downloads_launch_verified'] and published['IPS_roundtrip'] and not published['backup_created']
    assert published['native_audio_matches_candidate'] and published['camera_edge_spawns_match_candidate']
    assert Path(published['destination']).resolve()==nightly.D.resolve()
    assert nightly.check(nightly.D)['ROM_sha256']==PREVIOUS
    previous = published['active_11_cadence']
    assert previous['no_controller_read']==12
    capacity = Five.Earlier.Earlier.source_capacity(parent,final)
    Five.verify_scope(Five.SCOPE,PREVIOUS)
    injury = corrected_injury(args.injury_packet.resolve(),rom)
    with native_validators() as validation:
        validation.native_suite(root,rom)
        candidate = validation.route_evidence(root/'mini')
    if args.check_only:
        print(json.dumps(dict(ready=True,ROM_SHA256=PIN,cadence=candidate['cadence'],native_injury_helper=injury)),flush=True)
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
    with native_validators() as validation:
        downloads = validation.route_evidence(installed)
    assert downloads==candidate,'Downloads route, audio, cadence or lift evidence differs from the candidate'
    run([installer,'finalize',*common])

    receipt_path = out/'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256']==nightly.check(nightly.D)['ROM_sha256']==PIN
    assert receipt['IPS_SHA256']==sha(out/'SMB-Crossover-Latest-WIP-MMC5.ips')
    cadence = downloads['cadence']
    receipt.update(composed_proof_SHA256=sha(path),published_parent_receipt_SHA256=sha(PUBLISHED),
                   source_composition_parent_SHA256=Batch.H.PIN,immediate_six_group_SHA256=digest(six),
                   kernel_SHA256=sha(Batch.KERNEL),native_audio=downloads['audio'],
                   native_audio_matches_candidate=True,camera_edge_spawns=downloads['camera_edge_spawns'],
                   camera_edge_spawns_match_candidate=True,natural_11_source_capacity=capacity,
                   native_corrected_injury=injury,injury_scope_proof_SHA256=sha(Five.SCOPE),
                   previous_comparable_missed_reads=previous['no_controller_read'],
                   lag_free=cadence['no_controller_read']==0)
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    with (out/'release-notes.txt').open('a',encoding='utf-8') as notes:
        notes.write('\nPowered Mini now returns to small status after a native hit. An earned-mushroom '
                    'replay verifies the small collision box and sprite after injury, with the third lift '
                    'entering view during the native injury sequence. All three Downloads crossings retain both lives. '
                    f'The route recorded {cadence["no_controller_read"]} missed reads over '
                    f'{cadence["physical"]} physical frames, compared with {previous["no_controller_read"]} '
                    f'over {previous["physical"]} on the prior route.\n')
    print(json.dumps(dict(delivered=True,ROM_SHA256=PIN,IPS_SHA256=receipt['IPS_SHA256'],cadence=cadence)),flush=True)


if __name__=='__main__':
    main()
