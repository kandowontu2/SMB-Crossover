"""Stage one exact final-minus Mini movement, popup and RNG candidate."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_floatey_gate_1110 as Popup
import check_native_rng_step_1110 as Rng
from check_mini_funded_actor_1108_v3 import install
import prepare_mini_movement_prefix_native_1110 as Prefix
from prepare_mini_lane_audio_native_1110 import verify_parent, verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R, BASE, PIN, Movement = Prefix.R, Prefix.BASE, Prefix.PIN, Prefix.Movement
MOVEMENT_ROM = R/'build/mini-movement-prefix-native-1110/candidate.nes'
MOVEMENT_RECEIPT_SHA = '683148c7643af7f82fa7c08f39c066dcacfc7ccd54ad30d417ec6f2e2965495d'
POPUP = R/'build/native-floatey-gate-1110/proof.json'
POPUP_SHA = 'e2428a6a3c179e5ab8655da34a6e0818034f975255a75d7c3deb174bab1baa8e'
RNG = R/'build/native-rng-step-1110/proof.json'
RNG_SHA = '0fb84d79819dfc5f51c708894bfb07c3024bcbf08eebbe1eb9553fa97916b56a'
POPUP_ROLE, RNG_ROLE = 'native_floatey_update_gate', 'native_rng_step'
ROLES = (Prefix.ROLE, POPUP_ROLE, RNG_ROLE)


def stable(value):
    return json.loads(json.dumps(value))


def source_refs(receipt):
    refs = set()
    for key in ('bindings','source_bindings'):
        for path,want in receipt.get(key,{}).items():
            actual = (R/Path(path)).resolve()
            assert sha(actual)==want,actual
            refs.add(actual)
    return refs


def census():
    before,moved,movement,parent,meta,refs,movement_text,parent_ready = Prefix.census()
    assert sha(MOVEMENT_ROM)==Prefix.FINAL_PIN and MOVEMENT_ROM.read_bytes()==moved
    movement_manifest = MOVEMENT_ROM.with_suffix('.json')
    movement_receipt = MOVEMENT_ROM.with_name('proof.json')
    movement_packet = MOVEMENT_ROM.parent/'mini'
    movement_ready = movement_packet/'ready.json'
    movement_controller = movement_packet/'controller.lua'
    assert sha(movement_receipt)==MOVEMENT_RECEIPT_SHA
    assert Prefix.read(movement_manifest)['composed_proof_SHA256']==MOVEMENT_RECEIPT_SHA
    q = Prefix.read(movement_receipt)
    assert q['candidate_SHA256']==Prefix.FINAL_PIN and q['groups'][Prefix.ROLE]==movement['patches']
    assert Prefix.read(movement_ready)['bindings'][str(movement_controller.resolve())]==sha(movement_controller)
    assert movement_controller.read_text(encoding='utf-8')==movement_text

    refs.update({Path(__file__),MOVEMENT_ROM,movement_manifest,movement_receipt,movement_ready,movement_controller,POPUP,RNG})
    groups = {Prefix.ROLE:movement['patches']}
    receipts = {Prefix.ROLE:movement}
    for role,path,pin in ((POPUP_ROLE,POPUP,POPUP_SHA),(RNG_ROLE,RNG,RNG_SHA)):
        assert sha(path)==pin
        isolated,receipt,_ = verify_parent(before,path)
        assert Movement.P.sha(isolated)==receipt['expected_memory_only_SHA256']
        refs.update(source_refs(receipt))
        groups[role],receipts[role] = receipt['patches'],receipt

    spans = sorted((row['file_offset'],row['file_offset']+len(bytes.fromhex(row['new_hex'])),role)
                   for role in ROLES for row in groups[role])
    assert len(spans)==5 and all(hi<=right for (_,hi,_),(right,_,_) in zip(spans,spans[1:]))
    for rows in parent['groups'].values():
        for row in rows:
            old_start = row['file_offset']
            old_end = old_start+len(bytes.fromhex(row['new_hex']))
            assert all(hi<=old_start or old_end<=lo for lo,hi,_ in spans),row

    final = install(before,[row for role in ROLES for row in groups[role]])
    assert final==install(moved,groups[POPUP_ROLE]+groups[RNG_ROLE])
    assert final[1048592:]==before[1048592:]
    verify_payload(final,Movement.KERNEL)
    minus = {}
    for role in ROLES:
        without = install(before,[row for other in ROLES if other!=role for row in groups[other]])
        assert final==install(without,groups[role])
        minus[role] = without
    assert len({Movement.P.sha(raw) for raw in minus.values()})==3

    pin = Movement.P.sha(final)
    assert movement_text.count(Prefix.FINAL_PIN)==1 and pin not in movement_text
    controller = movement_text.replace(Prefix.FINAL_PIN,pin,1)
    assert controller.replace(pin,Prefix.FINAL_PIN,1)==movement_text
    assert controller.replace(pin,PIN,1)==(BASE.parent/'mini/controller.lua').read_text(encoding='utf-8')
    return before,final,minus,groups,receipts,parent,meta,refs,controller,parent_ready


def qualify(before, final, minus, receipts):
    movement = Movement.whole(minus[Prefix.ROLE],final)
    assert stable(movement)==receipts[Prefix.ROLE]['whole_GameLoop']
    movement_vectors = Movement.vectors(minus[Prefix.ROLE],final)
    original_irq = Prefix.read(Prefix.INTERRUPTS)
    assert all(original_irq[name]==value for name,value in stable(movement_vectors).items())
    print('Final-minus movement GameLoop and interrupts passed.',flush=True)

    popup = Popup.qualify(minus[POPUP_ROLE],final)
    popup_vectors = Popup.vectors(minus[POPUP_ROLE],final)
    assert stable(popup)==receipts[POPUP_ROLE]['foreground']
    assert stable(popup_vectors)==receipts[POPUP_ROLE]['vectors']
    popup_whole = Movement.whole(minus[POPUP_ROLE],final)
    assert all(-6<=value<=66 and (value+6)%12==0
               for row in popup_whole for value in row['cycles_saved'])
    print('Final-minus popup actor, score, flagpole, full GameLoop and interrupts passed.',flush=True)

    rng = Rng.finite(minus[RNG_ROLE],final)
    rng_vectors = Rng.vectors(minus[RNG_ROLE],final)
    rng_whole = Movement.whole(minus[RNG_ROLE],final)
    assert stable(rng)==receipts[RNG_ROLE]['feedback_cases']
    assert stable(rng_vectors)==receipts[RNG_ROLE]['vectors']
    assert stable(rng_whole)==receipts[RNG_ROLE]['whole_GameLoop']
    print('Final-minus RNG finite, full GameLoop and interrupts passed.',flush=True)

    combined = Movement.whole(before,final)
    for total,m,p,r in zip(combined,movement,popup_whole,rng_whole,strict=True):
        for key in ('owner','scene','version','joins'):
            assert total[key]==m[key]==p[key]==r[key],(key,total,m,p,r)
        assert total['cycles_saved']==[a+b+c for a,b,c in zip(
            m['cycles_saved'],p['cycles_saved'],r['cycles_saved'],strict=True)]
    return dict(combined_GameLoop=combined, final_minus_checks={
        Prefix.ROLE:dict(whole_GameLoop=movement,vectors=movement_vectors),
        POPUP_ROLE:dict(foreground=popup,whole_GameLoop=popup_whole,vectors=popup_vectors),
        RNG_ROLE:dict(feedback_cases=rng,whole_GameLoop=rng_whole,vectors=rng_vectors),
    })


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    before,final,minus,groups,receipts,parent,meta,refs,controller,ready = census()
    pin = Movement.P.sha(final)
    print(json.dumps(dict(candidate_SHA256=pin,final_minus={k:Movement.P.sha(v) for k,v in minus.items()})),flush=True)
    checks = qualify(before,final,minus,receipts)
    out.mkdir()
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.lbl','.dbg'):
        original = BASE.with_suffix(suffix)
        shutil.copyfile(original,rom.with_suffix(suffix))
        assert sha(original)==sha(rom.with_suffix(suffix))
    report = out/'proof.json'
    proof = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PIN,candidate_SHA256=pin,
                 kernel_SHA256=Movement.KERNEL_PIN,intermediate_movement_SHA256=Prefix.FINAL_PIN,
                 apply_order=[*parent['apply_order'],*ROLES],inherited_groups=parent['apply_order'],
                 groups=groups,final_minus_SHA256={k:Movement.P.sha(v) for k,v in minus.items()},
                 bindings={str(path.resolve()):sha(path) for path in sorted(refs)},**checks)
    report.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=PIN,candidate_SHA256=pin,composed_proof_SHA256=sha(report),
                verification='Private movement, popup and RNG native replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,controller,refs|{report,manifest},expected=pin,
            timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])


if __name__=='__main__':
    main()
