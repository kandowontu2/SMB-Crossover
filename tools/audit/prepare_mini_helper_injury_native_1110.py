"""Compose strict lift timing, its injury repair and ordinary actor dispatch."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re
import shutil

import check_mini_helper_activation_irq_1110 as NormalIRQ
import check_mini_helper_injury_1110 as Injury
import check_mini_helper_injury_irq_1110 as InjuryIRQ
import check_native_enemy_ordinary_dispatch_1110_v2 as Dispatch
import prepare_mini_helper_activation_native_1110 as Strict
from check_mini_funded_actor_1108_v3 import install
from compose_mini_frame_budget_1108 import digest, load
from prepare_mini_lane_audio_native_1110 import verify_interrupts, verify_parent
from prepare_selected_native_packet_v1 import prepare, sha


R,H,L = Strict.R,Strict.H,Strict.L
INJURY = R/'build/mini-helper-injury-1110/proof.json'
INJURY_IRQ = INJURY.with_name('irq.json')
DISPATCH = R/'build/native-enemy-ordinary-dispatch-1110/proof-v2.json'
QA = R/'docs/qa/mini-injury-native-status-1110.md'
GROUPS = ('strict_offscreen','injury_admission','ordinary_enemy_dispatch')
HISTORICAL_STRICT = R/'build/mini-helper-activation-native-1110'
WATCHDOG = R/'tools/audit/run_bounded_build_v1.py'
OLD_WATCHDOG = 'eb331ec122dd933d83eb2e0b217e0ca7be7ccf16e9c35d7e22231ce076d8b643'


def components():
    published,strict,normal_proof = Strict.bound_image()
    injured,injury_proof,_ = verify_parent(strict,INJURY)
    verify_interrupts(INJURY,INJURY_IRQ,injury_proof)
    assert digest(injured)==injury_proof['expected_memory_only_SHA256']
    assert injury_proof['combined_patches']==normal_proof['patches']+injury_proof['patches']
    dispatched,dispatch_proof,_ = verify_parent(published,DISPATCH)
    assert digest(dispatched)==dispatch_proof['expected_memory_only_SHA256']
    assert dispatch_proof['vectors']['paired_GameLoop_resumes']
    assert dispatch_proof['patches']==Dispatch.patches(published)
    proofs = dict(zip(GROUPS,(normal_proof,injury_proof,dispatch_proof),strict=True))
    groups = {name:proof['patches'] for name,proof in proofs.items()}
    assert [len(groups[key]) for key in GROUPS]==[4,6,2]
    occupied = set()
    for patch in (row for rows in groups.values() for row in rows):
        lo = patch['file_offset']
        current = set(range(lo,lo+len(bytes.fromhex(patch['old_hex']))))
        assert not occupied.intersection(current),patch
        occupied.update(current)
    assert install(published,groups['strict_offscreen']+groups['injury_admission'])==injured
    for name in ('injury_admission','ordinary_enemy_dispatch'):
        for source,h in proofs[name]['bindings'].items():
            assert sha(source)==h,source
    return published,strict,proofs,groups


@contextmanager
def strict_dispatch_kernel():
    edge = Dispatch.Edge
    previous = edge.KERNEL,edge.KERNEL_PIN
    edge.KERNEL,edge.KERNEL_PIN = Strict.KERNEL,sha(Strict.KERNEL)
    try:
        yield
    finally:
        edge.KERNEL,edge.KERNEL_PIN = previous


def qualify(published,final,proofs,groups):
    baselines = {remove:install(published,[row for name,rows in groups.items() if name!=remove for row in rows])
                 for remove in GROUPS}
    normal = NormalIRQ.qualify(baselines['strict_offscreen'],final,proofs['strict_offscreen'])
    print('Final-minus strict offscreen GameCore and vectors passed.',flush=True)
    without_injury = baselines['injury_admission']
    injury_cpu = Injury.foreground(without_injury,final)
    assert json.loads(json.dumps(injury_cpu))==proofs['injury_admission']['foreground']
    injury_lifecycle = InjuryIRQ.lifecycle(without_injury,final)
    assert injury_lifecycle==load(INJURY_IRQ)['native_injury_sequence']
    injury_vectors = InjuryIRQ.vectors(without_injury,final)
    print('Final-minus real injury sequence, foreground and vectors passed.',flush=True)
    with strict_dispatch_kernel():
        before = baselines['ordinary_enemy_dispatch']
        finite = Dispatch.finite(before,final)
        assert finite==proofs['ordinary_enemy_dispatch']['all_8bit_dispatch']
        dispatch_cpu = Dispatch.whole(before,final)
        dispatch_vectors = Dispatch.vectors(before,final)
    print('Final-minus native ordinary actor GameLoop and vectors passed.',flush=True)
    cold,_ = H.A.exact_cold(published,final,proofs['strict_offscreen']['exact_changed_code'])
    return dict(cold_Mini=cold,final_minus_SHA256={name:digest(image) for name,image in baselines.items()},
                strict_offscreen=normal,injury_admission=dict(foreground=injury_cpu,
                native_injury_sequence=injury_lifecycle,vectors=injury_vectors),
                ordinary_enemy_dispatch=dict(finite=finite,whole_GameLoop=dispatch_cpu,vectors=dispatch_vectors))


def historical_route(root,pin):
    packet = root/'mini'
    ready_path,controller = packet/'ready.json',packet/'controller.lua'
    bind = packet/'capture/binding.json'
    ready,result = load(ready_path),load(bind)
    assert ready['ROM_sha256']==result['ROM_sha256']==pin
    assert ready['prepared'] and not ready['emulated_writes'] and result['exit_code']==0
    assert result['ready_sha256']==sha(ready_path)
    assert Path(ready['ROM']).resolve()==(root/'candidate.nes').resolve()
    for name,h in ready['bindings'].items():
        if Path(name).resolve()==WATCHDOG:
            # Root's replacement only allows a caller to lower the cap.
            # Historical runs stay frozen against the then-current wrapper.
            assert h==OLD_WATCHDOG
        else:
            assert sha(name)==h,name
    return controller.read_text(encoding='utf-8'),ready,{ready_path,controller,bind,root/'candidate.nes'}


def route_controller(strict,final):
    old,_,old_refs = historical_route(H.BASE.parent,H.PIN)
    text,ready,refs = historical_route(HISTORICAL_STRICT,Strict.TARGET)
    for source,target in ((H.PIN,Strict.TARGET),(sha(Strict.Contact.KERNEL),sha(Strict.KERNEL)),
                          ('relative>=256 and relative<=288','relative>=256 and relative<=263')):
        assert old.count(source)==1,source
        old = old.replace(source,target)
    assert old==text
    assert HISTORICAL_STRICT.joinpath('candidate.nes').read_bytes()==strict
    hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                       r'\["bytes"\]=\{([\d,]+)\}',text)
    assert hooks
    for address,data in hooks:
        offset = 16+int(address)
        expected = bytes(map(int,data.split(',')))
        assert strict[offset:offset+len(expected)]==final[offset:offset+len(expected)]==expected,address
    audio = Strict.Contact.GraphicsBatch.Prior.AUDIO
    runtime = load(audio.RUNTIME)
    assert audio.audio_config(strict,runtime)==audio.audio_config(final,runtime)
    assert all(token not in text for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    assert text.count(Strict.TARGET)==1
    return text.replace(Strict.TARGET,digest(final)),ready,old_refs|refs|{audio.RUNTIME,audio.OBSERVER,WATCHDOG}


def stage(output,final,groups,checks,packet):
    text,ready,refs = packet
    pin = digest(final)
    meta = load(HISTORICAL_STRICT/'candidate.json')
    assert meta['candidate_SHA256']==Strict.TARGET and meta['kernel_SHA256']==sha(Strict.KERNEL)
    assert meta['composed_proof_SHA256']==sha(HISTORICAL_STRICT/'proof.json')
    output.mkdir()
    rom = output/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(H.BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(H.BASE.with_suffix(suffix))
    refs.update((Path(__file__),Path(Strict.__file__),Path(NormalIRQ.__file__),Path(Injury.__file__),
                 Path(InjuryIRQ.__file__),Path(Dispatch.__file__),Strict.CPU,Strict.IRQ,Strict.KERNEL,
                 Strict.KERNEL.with_suffix('.lbl'),INJURY,INJURY_IRQ,DISPATCH,QA,
                 HISTORICAL_STRICT/'candidate.json',HISTORICAL_STRICT/'proof.json'))
    path = output/'proof.json'
    report = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=H.PIN,
                  candidate_SHA256=pin,kernel_SHA256=sha(Strict.KERNEL),groups=groups,
                  birth_relative_left=[256,263],
                  helpers=[dict(stage='1-1',left=left,center=left+16,initial_top=192,width=32) for left in H.LEFTS],
                  native_injury_scope='Post-scroll admission only. Preexisting powered injury status recorded separately.',
                  bindings={str(p.resolve()):sha(p) for p in sorted(refs)},**checks)
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=H.PIN,candidate_SHA256=pin,kernel_SHA256=sha(Strict.KERNEL),
                actual_MiniScene=checks['cold_Mini'],composed_proof_SHA256=sha(path),
                verification='Private Mini injury-safe offscreen helper and ordinary actor replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'mini',rom,text,refs|{path,manifest},expected=pin,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,ROM_SHA256=pin,groups=GROUPS,native_pending=True)),flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--census',action='store_true',help='Check exact preimages and print the memory-only target.')
    mode.add_argument('--emit',action='store_true',help='Run final-minus proofs and stage one private native packet.')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R/'build') and output!=R/'build' and not output.exists()
    published,strict,proofs,groups = components()
    final = install(published,[row for name in GROUPS for row in groups[name]])
    packet = route_controller(strict,final)
    print(json.dumps(dict(parent_SHA256=H.PIN,memory_SHA256=digest(final),groups=GROUPS)),flush=True)
    if args.emit:
        checks = qualify(published,final,proofs,groups)
        stage(output,final,groups,checks,packet)


if __name__=='__main__':
    main()
