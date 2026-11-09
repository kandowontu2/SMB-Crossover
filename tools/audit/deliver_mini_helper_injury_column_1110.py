"""Deliver the five verified Mini helper and shared terrain groups."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path

import deliver_mini_helper_injury_pair_1110 as Earlier
import deliver_mini_nightly_root_1103_v30 as nightly
import prepare_mini_helper_injury_native_1110_v3 as Batch
from deliver_helper_camera_render_1110 import bindings, read, run
from prepare_selected_native_packet_v1 import sha


R = Batch.R
PIN = 'bca98ddef87633c4d2e83cfc188115572803b4fc58962108abf3ed505aa4af2f'
PREVIOUS = Batch.H.PIN
WITNESS = R/'build/mini-injury-helper-v4-native-1110'
SCOPE = R/'build/mini-helper-injury-scope-1110/proof.json'


@contextmanager
def exact_native_validators(pin):
    # Keep the frozen earlier delivery recipe intact. Its verifiers consume
    # the same strict kernel and native schemas with this exact ROM digest.
    previous = Earlier.PIN
    Earlier.PIN = pin
    try:
        yield
    finally:
        Earlier.PIN = previous


def verify_scope(path,pin):
    proof = read(path)
    assert proof['passed'] and not proof['ROM_written'] and proof['parent_SHA256']==PREVIOUS
    assert proof['five_group_SHA256']==pin
    assert ['native_mode10_context',False,1087] in proof['foreground']
    assert ['native_mode10_context',True,1] in proof['foreground']
    bindings(proof['bindings'])


def candidate_evidence(root,rom):
    with exact_native_validators(PIN):
        Earlier.native_suite(root,rom)
        route = Earlier.route_evidence(root/'mini')
        injury = Earlier.injury_evidence(WITNESS,rom)
    proof = read(WITNESS/'capture/result.json')['injury_helper']
    assert proof['native_status_anomaly']==dict(before=1,during=41,expected=0)
    assert proof['jump_request'] and proof['jump_ack']['engine']==10
    assert proof['jump_ack']['counter']<injury['visible']['counter']
    assert injury['visible']['sprite_chr4']==968
    return route,injury


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--check-only',action='store_true',help='Check the exact native receipts without writing or launching.')
    args = parser.parse_args()
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    rom,path = root/'candidate.nes',root/'proof.json'
    parent,_,final,_,_,_,groups = Batch.components()
    assert rom.read_bytes()==final and sha(rom)==PIN
    proof = read(path)
    assert proof['passed'] and proof['parent_SHA256']==PREVIOUS and proof['candidate_SHA256']==PIN
    assert proof['groups']==groups and set(groups)==set(proof['final_minus_SHA256'])==set(Batch.GROUPS)
    assert proof['kernel_SHA256']==sha(Batch.Four.Strict.KERNEL) and proof['birth_relative_left']==[256,263]
    for suffix in ('.dbg','.lbl'):
        assert sha(rom.with_suffix(suffix))==sha(Batch.H.BASE.with_suffix(suffix))
    bindings(proof['bindings'])
    meta = read(rom.with_suffix('.json'))
    assert meta['candidate_SHA256']==PIN and meta['composed_proof_SHA256']==sha(path)
    previous_path = Earlier.Earlier.PUBLISHED
    published = read(previous_path)
    assert published['ROM_SHA256']==PREVIOUS and published['Downloads_launch_verified'] and published['IPS_roundtrip']
    assert published['native_audio_matches_candidate'] and not published['backup_created']
    assert Path(published['destination']).resolve()==nightly.D.resolve()
    assert nightly.check(nightly.D)['ROM_sha256']==PREVIOUS
    previous = published['active_11_cadence']
    assert previous['no_controller_read']==35
    capacity = Earlier.Earlier.source_capacity(parent,final)
    verify_scope(SCOPE,PIN)
    candidate,injury = candidate_evidence(root,rom)
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
    with exact_native_validators(PIN):
        downloads = Earlier.route_evidence(installed)
    assert downloads==candidate,'Downloads route, audio, cadence or lift evidence differs from the candidate'
    run([installer,'finalize',*common])

    receipt_path = out/'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256']==nightly.check(nightly.D)['ROM_sha256']==PIN
    assert receipt['IPS_SHA256']==sha(out/'SMB-Crossover-Latest-WIP-MMC5.ips')
    cadence = downloads['cadence']
    receipt.update(composed_proof_SHA256=sha(path),published_parent_receipt_SHA256=sha(previous_path),
                   kernel_SHA256=sha(Batch.Four.Strict.KERNEL),native_audio=downloads['audio'],
                   native_audio_matches_candidate=True,camera_edge_spawns=downloads['camera_edge_spawns'],
                   camera_edge_spawns_match_candidate=True,natural_11_source_capacity=capacity,
                   native_injury_helper=injury,injury_scope_proof_SHA256=sha(SCOPE),
                   prior_native_powered_status_note_SHA256=sha(Earlier.NATIVE_STATUS),
                   previous_comparable_missed_reads=previous['no_controller_read'],
                   lag_free=cadence['no_controller_read']==0)
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    with (out/'release-notes.txt').open('a',encoding='utf-8') as notes:
        notes.write('\nMini’s three native 1-1 lifts start 256–263 pixels from the camera’s left edge. '
                    'The Downloads replay verified all three crossings and retained both lives. '
                    'A separate native replay verified the third lift appearing offscreen during injury. '
                    'Shared native actor and terrain rendering work takes fewer CPU cycles. '
                    f'The route recorded {cadence["no_controller_read"]} missed reads over '
                    f'{cadence["physical"]} physical frames, compared with {previous["no_controller_read"]} '
                    f'over {previous["physical"]} on the prior route.\n')
    print(json.dumps(dict(delivered=True,ROM_SHA256=PIN,IPS_SHA256=receipt['IPS_SHA256'],cadence=cadence)),flush=True)


if __name__=='__main__':
    main()
