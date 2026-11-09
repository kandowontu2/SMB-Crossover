"""Prepare the current Mini body and platform box changes for native replay."""

import argparse
import json
from pathlib import Path
import re
import shutil

from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import (
    BUILD, KERNEL, bound_rom, verify_interrupts, verify_parent, verify_payload,
    without_component,
)
from prepare_selected_native_packet_v1 import prepare, sha


CURRENT = BUILD/'mini-lane-audio-native-1110/candidate.nes'
PIN = 'a226894c4f6b97f1b9df248cf1465f1a36037fcc256d8ec703e05d0f077d6746'
CONTROLLER = CURRENT.parent/'route/controller.lua'
READY = CONTROLLER.with_name('ready.json')
BODY = BUILD/'mini-bodybox-dispatch-1110/proof.json'
PLATFORM = BUILD/'native-platform-box-1110/proof.json'
GIRDER = BUILD/'native-girder-draw-1110/proof.json'


def build_image(with_girder=False):
    raw = bound_rom(CURRENT,PIN)
    components = [(BODY,BODY.with_name('irq.json')),
                  (PLATFORM,PLATFORM.with_name('vectors.json'))]
    if with_girder:
        components.append((GIRDER,GIRDER.with_name('irq.json')))

    candidate, occupied = bytearray(raw), []
    for proof_path, irq_path in components:
        _,proof,spans = verify_parent(raw,proof_path)
        verify_interrupts(proof_path,irq_path,proof)
        for start,end,old,new in spans:
            assert all(end<=lo or start>=hi for lo,hi in occupied),(proof_path,start,end)
            assert candidate[start:end]==old,(proof_path,start,end)
            candidate[start:end] = new
            occupied.append((start,end))

    assert candidate[:16]==raw[:16] and candidate[1048592:]==raw[1048592:]
    verify_payload(raw,KERNEL)
    verify_payload(candidate,KERNEL)
    return raw,bytes(candidate),components


def controller_for(raw,candidate):
    ready = load(READY)
    assert ready['prepared'] and not ready['emulated_writes']
    assert ready['ROM_sha256']==digest(raw)==PIN
    assert Path(ready['ROM']).resolve()==CURRENT.resolve()
    bindings = {Path(p).resolve():h for p,h in ready['bindings'].items()}
    for path in (CONTROLLER,CURRENT,CURRENT.with_suffix('.json'),CURRENT.with_suffix('.dbg'),
                 CURRENT.with_suffix('.lbl'),KERNEL,KERNEL.with_suffix('.lbl')):
        assert bindings[path.resolve()]==sha(path),path

    text = CONTROLLER.read_text(encoding='utf-8')
    assert text.count(PIN)==text.count(sha(KERNEL))==1
    assert all(token not in text for token in ('emu.write(','emu.reset(','emu.loadSavestate('))
    hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                       r'\["bytes"\]=\{([\d,]+)\}',text)
    assert hooks
    for address,data in hooks:
        at,expected = 16+int(address),bytes(map(int,data.split(',')))
        assert raw[at:at+len(expected)]==candidate[at:at+len(expected)]==expected,address
    return text.replace(PIN,digest(candidate))


def verify_cpu(raw,candidate):
    whole = check_full_cpu(raw,candidate,{})
    body_only = check_full_cpu(without_component(candidate,BODY),candidate,{})
    assert all(r['min_saved']==r['max_saved']==451 for r in body_only),body_only
    assert all(r['min_saved']>0 for r in whole),whole
    return whole,body_only


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--with-girder',action='store_true')
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(BUILD) and output!=BUILD and not output.exists()
    raw,candidate,components = build_image(args.with_girder)
    controller = controller_for(raw,candidate)
    whole,body_only = verify_cpu(raw,candidate)
    candidate_sha = digest(candidate)

    output.mkdir()
    rom = output/'candidate.nes'
    rom.write_bytes(candidate)
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(CURRENT.with_suffix(suffix),rom.with_suffix(suffix))
    metadata = rom.with_suffix('.json')
    parent_meta = load(CURRENT.with_suffix('.json'))
    assert parent_meta['candidate_SHA256']==PIN
    proofs = {path for pair in components for path in pair}
    parent_meta.update(parent_SHA256=PIN,candidate_SHA256=candidate_sha,
        whole_GameCore=whole,composed_body_only_GameCore=body_only,
        body_platform_proofs={str(p.resolve()):sha(p) for p in sorted(proofs)},
        girder_included=args.with_girder,kernel_SHA256=sha(KERNEL),
        private_pending_current_interrupt_proof=True,verification='Private replay pending')
    metadata.write_text(json.dumps(parent_meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'route',rom,controller,
        {CONTROLLER,READY,metadata,KERNEL,KERNEL.with_suffix('.lbl'),Path(__file__),*proofs},
        expected=candidate_sha,timeout=180,allow_interactive=True,
        scope='Same Mini 1-1 controller and lift route as a226. Both lives and active 1-2 required.')
    print(json.dumps(dict(candidate_SHA256=candidate_sha,whole_GameCore=whole,
                          composed_body_only_GameCore=body_only)),flush=True)


if __name__=='__main__':
    main()
