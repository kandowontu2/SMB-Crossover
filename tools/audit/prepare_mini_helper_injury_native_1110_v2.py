"""Compose the four verified Mini helper and native actor groups from d998."""

import argparse
import json
from pathlib import Path
import shutil

import check_native_enemy_pair_offsets_1110 as Pair
import check_native_enemy_pair_offsets_irq_1110 as PairIRQ
import check_native_enemy_pair_offsets_readers_1110 as PairReaders
import prepare_mini_helper_injury_native_1110 as Prior
from check_mini_funded_actor_1108_v3 import install
from compose_mini_frame_budget_1108 import digest, load
from prepare_mini_lane_audio_native_1110 import verify_interrupts, verify_parent
from prepare_selected_native_packet_v1 import prepare, sha


R,H,Strict = Prior.R,Prior.H,Prior.Strict
PAIR = R/'build/native-enemy-pair-offsets-1110/proof-v2.json'
PAIR_IRQ = PAIR.with_name('irq-v2.json')
PAIR_READERS = PAIR.with_name('readers-v2.json')
PAIR_ROLE = 'enemy_pair_offsets'
GROUPS = (*Prior.GROUPS,PAIR_ROLE)


def pair_readers(image):
    prg = image[16:16+128*8192]
    modes = {'abs','abx','aby','ind'}
    ops = {op for op,(_,mode) in enumerate(PairReaders.MPU.disassemble) if mode in modes}
    return [[i//8192,i%8192,prg[i:i+3].hex()] for i in range(len(prg)-2)
            if prg[i] in ops and Pair.START<=prg[i+1]+256*prg[i+2]<Pair.ENTRY]


def components():
    published,strict,proofs,groups = Prior.components()
    isolated,proof,parts = verify_parent(published,PAIR)
    verify_interrupts(PAIR,PAIR_IRQ,proof)
    readers = load(PAIR_READERS)
    assert readers['passed'] and readers['parent_SHA256']==H.PIN
    assert readers['expected_memory_only_SHA256']==proof['expected_memory_only_SHA256']==digest(isolated)
    assert readers['bindings'][str(PAIR.resolve())]==sha(PAIR)
    assert readers['sole_code_consumer']==[126,0x9948] and readers['other_matches_source_confirmed_music_data']
    for inputs in (proof['bindings'],readers['bindings']):
        for path,h in inputs.items():
            assert sha(path)==h,path
    assert len(parts)==1 and parts[0][:2]==(H.offset(126,Pair.START),H.offset(126,Pair.END))
    assert proof['source_ingress']==Pair.census(published)
    assert len(groups)==3 and all(row['file_offset']+len(bytes.fromhex(row['new_hex']))<=parts[0][0] or
                                  row['file_offset']>=parts[0][1] for rows in groups.values() for row in rows)
    proofs[PAIR_ROLE],groups[PAIR_ROLE] = proof,proof['patches']
    before_pair = install(published,[row for role,rows in groups.items() if role!=PAIR_ROLE for row in rows])
    assert Pair.census(before_pair)==proof['source_ingress']
    assert pair_readers(before_pair)==readers['all_absolute_indexed_and_indirect_literal_matches']
    final = install(before_pair,proof['patches'])
    assert final==install(published,[row for role in GROUPS for row in groups[role]])
    return published,strict,final,before_pair,proofs,groups


def qualify(published,final,before_pair,proofs,groups):
    # Prior.qualify builds each final-minus image from all provided groups.
    # The pair change remains linked throughout all three original checks.
    checked = Prior.qualify(published,final,proofs,groups)
    proof = proofs[PAIR_ROLE]
    with Prior.strict_dispatch_kernel():
        direct = Pair.direct(before_pair,final)
        assert direct==proof['actual_caller_cases']
        game = Pair.whole(before_pair,final)
        vectors = PairIRQ.vectors(before_pair,final,proof['labels'])
    checked['final_minus_SHA256'][PAIR_ROLE] = digest(before_pair)
    assert set(checked['final_minus_SHA256'])==set(GROUPS)
    checked[PAIR_ROLE] = dict(actual_caller_cases=direct,whole_GameLoop=game,vectors=vectors)
    print('Final-minus native enemy pair GameLoop and vectors passed.',flush=True)
    return checked


def stage(output,final,groups,checks,packet):
    text,ready,refs = packet
    pin = digest(final)
    parent_meta = Prior.HISTORICAL_STRICT/'candidate.json'
    meta = load(parent_meta)
    assert meta['candidate_SHA256']==Strict.TARGET and meta['kernel_SHA256']==sha(Strict.KERNEL)
    assert meta['composed_proof_SHA256']==sha(parent_meta.with_name('proof.json'))
    refs.update((Path(__file__),Path(Prior.__file__),Path(Strict.__file__),Path(Prior.NormalIRQ.__file__),
                 Path(Prior.Injury.__file__),Path(Prior.InjuryIRQ.__file__),Path(Prior.Dispatch.__file__),
                 Path(Pair.__file__),Path(PairIRQ.__file__),Path(PairReaders.__file__),Strict.CPU,Strict.IRQ,
                 Strict.KERNEL,Strict.KERNEL.with_suffix('.lbl'),Prior.INJURY,Prior.INJURY_IRQ,Prior.DISPATCH,
                 PAIR,PAIR_IRQ,PAIR_READERS,Prior.QA,parent_meta,parent_meta.with_name('proof.json')))
    output.mkdir()
    rom = output/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(H.BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(H.BASE.with_suffix(suffix))
    proof = output/'proof.json'
    report = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=H.PIN,candidate_SHA256=pin,
                  kernel_SHA256=sha(Strict.KERNEL),groups=groups,birth_relative_left=[256,263],
                  helpers=[dict(stage='1-1',left=left,center=left+16,initial_top=192,width=32) for left in H.LEFTS],
                  native_injury_scope='Post-scroll admission only. Preexisting powered injury status recorded separately.',
                  bindings={str(path.resolve()):sha(path) for path in sorted(refs)},**checks)
    proof.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=H.PIN,candidate_SHA256=pin,actual_MiniScene=checks['cold_Mini'],
                composed_proof_SHA256=sha(proof),verification='Private Mini helper and native actor replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'mini',rom,text,refs|{proof,manifest},expected=pin,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,ROM_SHA256=pin,groups=GROUPS,native_pending=True)),flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--census',action='store_true',help='Check the exact preimages and controller without writing.')
    mode.add_argument('--qualify',action='store_true',help='Run all final-minus proofs in memory.')
    mode.add_argument('--emit',action='store_true',help='Run all final-minus proofs and stage one native packet.')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R/'build') and output!=R/'build' and not output.exists()
    published,strict,final,before_pair,proofs,groups = components()
    packet = Prior.route_controller(strict,final)
    print(json.dumps(dict(parent_SHA256=H.PIN,memory_SHA256=digest(final),groups=GROUPS)),flush=True)
    if args.census:
        return
    checks = qualify(published,final,before_pair,proofs,groups)
    if args.emit:
        stage(output,final,groups,checks,packet)


if __name__=='__main__':
    main()
