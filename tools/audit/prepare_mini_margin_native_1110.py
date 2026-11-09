"""Qualify the exact 863e margin trial and stage its ordinary native suite."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path

import check_native_goomba_left_high_x_1110 as Goomba
from check_mini_funded_actor_1108_v3 import install
from deliver_helper_camera_render_1110 import bindings, read
import deliver_mini_movement_popup_rng_1110 as Previous
import prepare_mini_helper_injury_native_1110_v5 as Seven
import prepare_mini_injury_helper_native_1110 as Hooks
import prepare_mini_margin_trial_1110 as Trial
from prepare_mini_lane_audio_native_1110 import verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R, Box, Score = Trial.R,Trial.Box,Trial.Score
PARENT, PREVIOUS = Trial.PARENT,Trial.PIN
TRIAL = R/'build/mini-margin-trial-1110'
ROM = TRIAL/'candidate.nes'
PIN = '863e1e3c536c3e6b8027e212a0a430356805886609fc2c264263d3cdb163fc9f'
TRIAL_PROOF_SHA = '318a6eff7e926def940f62872b0b403e5da8962433761b30a0213f85ecdfdbd5'
PUBLISHED = R/'build/mini-movement-popup-rng-delivery-1110/verified-delivery.json'
PUBLISHED_SHA = 'e148b497ab06012d96f2ffad70ac0a57cb82c0d151df6b64989ab78f213c7d08'
ROLES = tuple(Trial.COMPONENTS)
IRQ = {
    ROLES[0]:(Trial.BOX.with_name('irq.json'),'450f6f395f957c08bc3e7252d7a95ec3b6e5827e9a8af5a37463f6610d5a4d9b'),
    ROLES[2]:(Trial.Goomba.IRQ_PROOF,Trial.Goomba.IRQ_PIN),
}
PACKETS = {'mini':PARENT/'mini',**{f'native/{name}':PARENT/'native'/name for name in ('idle','power','fire','injury')}}


def stable(value):
    return json.loads(json.dumps(value))


@contextmanager
def status_goomba_kernel():
    old = Goomba.strict_dispatch_kernel
    Goomba.strict_dispatch_kernel = Seven.status_dispatch_kernel
    try:
        yield
    finally:
        Goomba.strict_dispatch_kernel = old


def census():
    parent_rom,parent_proof = PARENT/'candidate.nes',PARENT/'proof.json'
    trial_proof = TRIAL/'proof.json'
    parent,trial = read(parent_proof),read(trial_proof)
    assert sha(parent_rom)==parent['candidate_SHA256']==PREVIOUS
    assert sha(parent_proof)==Previous.Suites.PROOF_SHA
    assert sha(ROM)==trial['candidate_SHA256']==PIN and trial['parent_SHA256']==PREVIOUS
    assert sha(trial_proof)==TRIAL_PROOF_SHA and trial['private_trial'] and trial['passed']
    assert sha(PUBLISHED)==PUBLISHED_SHA
    installed = read(PUBLISHED)
    assert installed['ROM_SHA256']==PREVIOUS and installed['Downloads_launch_verified'] and installed['IPS_roundtrip']
    assert installed['active_11_cadence']['no_controller_read']==7 and not installed['backup_created']
    assert installed['composed_proof_SHA256']==sha(parent_proof)
    refs = {Path(__file__),Path(Trial.__file__),Path(Seven.__file__),parent_rom,parent_proof,trial_proof,
            PUBLISHED,Seven.KERNEL,Seven.KERNEL.with_suffix('.lbl')}
    groups,proofs,irq = {},{},{}
    for role,reference in zip(ROLES,(Box.BASE,Score.engine.BASE,Goomba.BASE),strict=True):
        path,digest = Trial.COMPONENTS[role]
        assert sha(path)==digest
        _,component,_ = verify_parent(reference.read_bytes(),path)
        groups[role],proofs[role] = component['patches'],component
        refs.update({path,reference,*map(Path,component['bindings'])})
        if role in IRQ:
            irq_path,irq_digest = IRQ[role]
            assert sha(irq_path)==irq_digest
            verify_interrupts(path,irq_path,component)
            irq[role] = read(irq_path)
            refs.update({irq_path,*map(Path,irq[role]['bindings'])})
    assert trial['groups']==groups
    parts = sorted((row['file_offset'],row['file_offset']+len(bytes.fromhex(row['new_hex'])))
                   for rows in groups.values() for row in rows)
    assert len(parts)==5 and all(b<=c for (_,b),(c,_) in zip(parts,parts[1:]))
    for report in (parent,read(Box.BASE.with_name('proof.json'))):
        for rows in report['groups'].values():
            for row in rows:
                start = row['file_offset']
                end = start+len(bytes.fromhex(row['new_hex']))
                assert all(hi<=start or end<=lo for lo,hi in parts),row
    before,final = parent_rom.read_bytes(),ROM.read_bytes()
    assert final==install(before,[row for rows in groups.values() for row in rows])
    assert final[1048592:]==before[1048592:]
    assert sha(Seven.KERNEL)==parent['kernel_SHA256']==Score.engine.KERNEL_PIN
    for image in (before,final):
        verify_payload(image,Seven.KERNEL)
    for suffix in ('.dbg','.lbl'):
        assert sha(ROM.with_suffix(suffix))==sha(parent_rom.with_suffix(suffix))
    minus = {role:install(before,[row for other,rows in groups.items() if other!=role for row in rows]) for role in ROLES}
    assert all(install(minus[role],groups[role])==final for role in ROLES)
    return before,final,minus,groups,proofs,irq,trial,refs


def qualify(before, final, minus, proofs, irq, trial):
    box,score,goomba = ROLES
    ingress = Box.ingress_cases(Box.M.cold_seeds(minus[box],final))
    assert ingress==proofs[box]['ingress']
    box_vectors = Box.vectors(minus[box],final)
    assert all(irq[box][key]==value for key,value in stable(box_vectors).items())
    box_whole = Box.whole(minus[box],final)
    assert stable(box_whole)==proofs[box]['whole_GameLoop']
    print('Final-minus box ingress, GameLoop and interrupts passed.',flush=True)

    score_finite = Score.finite(minus[score],final)
    score_vectors = Score.vectors(minus[score],final)
    score_whole = Score.engine.whole(minus[score],final)
    assert stable(score_finite)==proofs[score]['score_cases'] and score_vectors==proofs[score]['vectors']
    assert stable(score_whole)==proofs[score]['whole_GameLoop']
    print('Final-minus top score finite, GameLoop and interrupts passed.',flush=True)

    admission = Goomba.finite(minus[goomba],final)
    actors = Goomba.actor_cases(minus[goomba],final)
    assert admission==proofs[goomba]['all_low_direction_bytes'] and actors==proofs[goomba]['actor_cases']
    with status_goomba_kernel():
        goomba_vectors = Goomba.vectors(minus[goomba],final)
        goomba_whole = Goomba.whole(minus[goomba],final)
    assert all(irq[goomba][key]==value for key,value in stable(goomba_vectors).items())
    assert stable(goomba_whole)==proofs[goomba]['whole_GameLoop']
    print('Final-minus Goomba admission, actor, GameLoop and status-kernel interrupts passed.',flush=True)

    combined = Score.engine.whole(before,final)
    assert stable(combined)==trial['whole_GameLoop']
    for total,a,b,c in zip(combined,box_whole,score_whole,goomba_whole,strict=True):
        for key in ('owner','scene','version','joins'):
            assert total[key]==a[key]==b[key]==c[key],key
        assert total['cycles_saved']==[x+y+z for x,y,z in zip(a['cycles_saved'],b['cycles_saved'],c['cycles_saved'],strict=True)]
    return combined, {
        box:dict(ingress=ingress,vectors=box_vectors,whole_GameLoop=box_whole),
        score:dict(finite=score_finite,vectors=score_vectors,whole_GameLoop=score_whole),
        goomba:dict(admission=admission,actors=actors,vectors=goomba_vectors,whole_GameLoop=goomba_whole),
    }


def route_plan(final, refs):
    with Previous.validators() as validation:
        validation.native_suite(PARENT,PARENT/'candidate.nes')
        assert validation.route_evidence(PARENT/'mini')['cadence']['no_controller_read']==7
        Previous.Prior.corrected_injury(PARENT/'native/injury',PARENT/'candidate.nes')
    with Previous.Prior.Five.exact_native_validators(PIN):
        trial = Previous.Prior.Five.Earlier.route_evidence(TRIAL/'mini')
    assert trial['cadence']['no_controller_read']==trial['cadence']['zero_update']==6
    assert trial['cadence']['physical']==trial['cadence']['updates']==3500
    refs.update({TRIAL/'mini'/name for name in ('controller.lua','ready.json','capture/result.json','capture/binding.json','capture/timing.json')})
    plans = []
    for name,old in PACKETS.items():
        ready,controller = old/'ready.json',old/'controller.lua'
        meta = read(ready)
        assert meta['ROM_sha256']==PREVIOUS and Path(meta['ROM']).resolve()==PARENT/'candidate.nes'
        bindings(meta['bindings'])
        text = controller.read_text(encoding='utf-8')
        assert text.count(PREVIOUS)==1 and PIN not in text
        updated = text.replace(PREVIOUS,PIN,1)
        for physical,values in Hooks.PRG_HOOK.findall(updated):
            start = 16+int(physical)
            want = bytes(map(int,values.split(',')))
            assert final[start:start+len(want)]==want,(name,hex(start),want.hex())
        packet_refs = {controller,ready,old/'capture/result.json',old/'capture/binding.json',*map(Path,meta['bindings'])}
        plans.append((name,updated,meta,packet_refs))
    return trial,plans


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    before,final,minus,groups,proofs,irq,trial,refs = census()
    trial_native,plans = route_plan(final,refs)
    minus_pins = {role:Score.P.sha(raw) for role,raw in minus.items()}
    print(json.dumps(dict(ROM_SHA256=PIN,final_minus_SHA256=minus_pins)),flush=True)
    combined,checks = qualify(before,final,minus,proofs,irq,trial)
    out.mkdir()
    manifest = out/'candidate.json'
    meta = read(PARENT/'candidate.json')
    parent_proof = meta.pop('composed_proof_SHA256')
    meta.update(passed=True,parent_SHA256=PREVIOUS,candidate_SHA256=PIN,ROM=str(ROM),ROM_written=False,
                parent_composed_proof_SHA256=parent_proof,trial_composed_proof_SHA256=TRIAL_PROOF_SHA,
                apply_order=[*read(PARENT/'proof.json')['apply_order'],*ROLES],groups=groups,
                final_minus_SHA256=minus_pins,final_minus_checks=checks,combined_GameLoop=combined,
                native_trial_cadence=trial_native['cadence'],ordinary_native_pending=True,
                bindings={str(path.resolve()):sha(path) for path in sorted(refs)},
                verification='Exact final-minus qualification of retained native trial ROM. Ordinary native suite pending.')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    (out/'native').mkdir()
    for name,text,ready,packet_refs in plans:
        prepare(out/name,ROM,text,refs|packet_refs|{manifest},expected=PIN,timeout=ready['timeout'],
                scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==16


if __name__=='__main__':
    main()
