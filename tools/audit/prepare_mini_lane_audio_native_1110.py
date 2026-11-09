"""Rebase qualified Mini lane and shared audio changes for the current route."""

import argparse
import json
from pathlib import Path
import re
import shutil

from compose_mini_frame_budget_1108 import check_full_cpu, compose, digest, load
from prepare_selected_native_packet_v1 import R, prepare, sha
from qualify_mini_busy_1109 import bind_kernel


BUILD = R/'build'
CURRENT = BUILD/'mini-sweep-seam-native-1110/candidate.nes'
CURRENT_SHA = 'ddd6e71b42aaed99645a54b64b766b4fb3a32aee5c3b55bfe9b7c552000c94b3'
PREVIOUS = BUILD/'mini-combined-camera-native-1110/candidate.nes'
PREVIOUS_SHA = '56c4135e3edd7421c207fd4cd623ad8f58cd263353342d0af54202cd790cbcbc'
EARLIER = BUILD/'mini-box-terrain-visible-1110/candidate.nes'
EARLIER_SHA = '6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
RETENTION_HISTORY = (
    BUILD/'mini-camera-lifts-v2-1110/proof.json',
    BUILD/'mini-lift-retention-1110/proof-v2.json',
    BUILD/'mini-sweep-center-1110/proof.json',
)
LANE = BUILD/'mini-jump-lane-reuse-1110/proof.json'
LANE_IRQ = LANE.with_name('irq.json')
AUDIO = BUILD/'guest-expansion-sweep-1110/proof.json'
AUDIO_IRQ = AUDIO.with_name('vectors.json')
OLD_KERNEL = BUILD/'mini-sweep-center-1110/kernel.bin'
KERNEL = LANE.with_name('kernel.bin')
CONTROLLER = CURRENT.parent/'route/controller.lua'
READY = CONTROLLER.with_name('ready.json')
CODE, COOKIE = 1048592+962*1024, 16+65*8192+0x1003
RAM_EXCLUSIONS = {2: [(0x1fe3,0x1ff0)], 3: [(0,5120), (0x1fe3,0x1ff0)]}


def bound_rom(path, expected):
    data = path.read_bytes()
    assert digest(data)==expected,path
    return data


def ranges(proof, length):
    assert proof['patches']
    spans = []
    for row in proof['patches']:
        start = row['file_offset']
        old, new = (bytes.fromhex(row[key]) for key in ('old_hex','new_hex'))
        assert old and len(old)==len(new) and 16<=start<=length-len(old),row
        end = start+len(old)
        assert all(end<=lo or start>=hi for lo,hi,_,_ in spans),row
        spans.append((start,end,old,new))
    return spans


def verify_parent(parent, path):
    proof = load(path)
    assert proof['passed'] is True and not proof.get('ROM_written',False),path
    declared = proof.get('parent_SHA256',proof.get('base_ROM_SHA256'))
    assert declared==digest(parent),path
    proof['parent_SHA256'] = declared
    spans = ranges(proof,len(parent))
    isolated = bytearray(parent)
    compose(parent,isolated,proof,parent=declared)
    return bytes(isolated),proof,spans


def verify_interrupts(path, irq_path, proof):
    irq = load(irq_path)
    assert irq['passed'] is True and not irq.get('ROM_written',False),irq_path
    result_keys = ('memory_image_SHA256','memory_only_SHA256','expected_memory_only_SHA256')
    results = [irq[key] for key in result_keys if key in irq]
    assert results and all(h==proof['expected_memory_only_SHA256'] for h in results),irq_path
    for key in ('parent_SHA256','base_ROM_SHA256'):
        if key in irq:
            assert irq[key]==proof['parent_SHA256'],(irq_path,key)
    bindings = { (R/Path(p)).resolve(): h for p,h in irq['bindings'].items() }
    assert bindings[path.resolve()]==sha(path),irq_path
    for p,h in bindings.items():
        assert sha(p)==h,p


def verify_payload(raw,kernel):
    body = kernel.read_bytes()
    assert len(body)==5120 and raw[CODE:CODE+5120]==body,kernel
    assert raw[COOKIE:COOKIE+16]==bytes((167,41,1))+bytes.fromhex(digest(raw[CODE:CODE+7168]))[:13]


def build_image(brick_proof=None, brick_irq=None, platform_proof=None, platform_irq=None):
    assert (brick_proof is None)==(brick_irq is None)
    assert (platform_proof is None)==(platform_irq is None)
    raw = bound_rom(CURRENT,CURRENT_SHA)
    previous = bound_rom(PREVIOUS,PREVIOUS_SHA)
    hoist_parent = bound_rom(EARLIER,EARLIER_SHA)
    for history in RETENTION_HISTORY:
        hoist_parent,_,_ = verify_parent(hoist_parent,history)

    inputs = [(hoist_parent,LANE,LANE_IRQ),(previous,AUDIO,AUDIO_IRQ)]
    if brick_proof is not None:
        inputs.append((raw,brick_proof,brick_irq))
    if platform_proof is not None:
        inputs.append((raw,platform_proof,platform_irq))
    refs, occupied = [], []
    candidate = bytearray(raw)
    for declared_parent, path, irq_path in inputs:
        _,proof,spans = verify_parent(declared_parent,path)
        verify_interrupts(path,irq_path,proof)
        for start,end,old,new in spans:
            assert all(end<=lo or start>=hi for lo,hi in occupied),(path,start,end)
            assert candidate[start:end]==old,(path,start,end,'current ROM preimage')
            candidate[start:end] = new
            occupied.append((start,end))
        refs.extend((path,irq_path))
    assert candidate[CODE+5120:]==raw[CODE+5120:]
    verify_payload(raw,OLD_KERNEL)
    verify_payload(candidate,KERNEL)
    return raw,bytes(candidate),refs


def without_component(image, proof_path):
    """Remove one verified component while preserving every other patch."""
    parent = bytearray(image)
    for start,end,old,new in ranges(load(proof_path),len(image)):
        assert image[start:end]==new,(proof_path,start,end)
        parent[start:end] = old
    return bytes(parent)


def controller_for(raw,candidate):
    ready = load(READY)
    assert ready['prepared'] and not ready['emulated_writes']
    assert ready['ROM_sha256']==digest(raw)==CURRENT_SHA
    assert Path(ready['ROM']).resolve()==CURRENT.resolve()
    bindings = {Path(p).resolve():h for p,h in ready['bindings'].items()}
    for p in (CONTROLLER,OLD_KERNEL,OLD_KERNEL.with_suffix('.lbl'),CURRENT,
              CURRENT.with_suffix('.dbg'),CURRENT.with_suffix('.lbl')):
        assert bindings[p.resolve()]==sha(p),p

    text = CONTROLLER.read_text(encoding='utf-8')
    old_kernel_sha,new_kernel_sha = sha(OLD_KERNEL),sha(KERNEL)
    assert text.count(CURRENT_SHA)==text.count(old_kernel_sha)==1
    text = bind_kernel(text.replace(CURRENT_SHA,digest(candidate)),KERNEL)
    text = text.replace(old_kernel_sha,new_kernel_sha)
    assert text.count(digest(candidate))==text.count(new_kernel_sha)==1
    assert all(token not in text for token in ('emu.write(','emu.reset(','emu.loadSavestate('))

    # Shared renderer changes may use bank 4. Keep every existing ROM hook
    # anchored to its original instruction bytes in the combined image.
    rom_hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                           r'\["bytes"\]=\{([\d,]+)\}',text)
    assert rom_hooks
    for address,data in rom_hooks:
        offset,expected = 16+int(address),bytes(map(int,data.split(',')))
        assert raw[offset:offset+len(expected)]==candidate[offset:offset+len(expected)]==expected,address
    return text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--brick-coin-proof',type=Path)
    p.add_argument('--brick-coin-irq',type=Path)
    p.add_argument('--platform-proof',type=Path)
    p.add_argument('--platform-irq',type=Path)
    args = p.parse_args()
    if bool(args.brick_coin_proof)!=bool(args.brick_coin_irq):
        p.error('pass both --brick-coin-proof and --brick-coin-irq')
    if bool(args.platform_proof)!=bool(args.platform_irq):
        p.error('pass both --platform-proof and --platform-irq')
    output = args.output.resolve()
    assert output.is_relative_to(BUILD) and output!=BUILD and not output.exists()
    raw,candidate,proofs = build_image(args.brick_coin_proof,args.brick_coin_irq,
                                       args.platform_proof,args.platform_irq)
    text = controller_for(raw,candidate)
    whole = check_full_cpu(raw,candidate,RAM_EXCLUSIONS)
    assert all(row['average_saved']>0 for row in whole),whole

    output.mkdir()
    rom = output/'candidate.nes'
    rom.write_bytes(candidate)
    for ext in ('.dbg','.lbl'):
        shutil.copyfile(CURRENT.with_suffix(ext),rom.with_suffix(ext))
    parent_meta = load(CURRENT.with_suffix('.json'))
    assert parent_meta['candidate_SHA256']==CURRENT_SHA
    metadata = rom.with_suffix('.json')
    parent_meta.update(parent_SHA256=CURRENT_SHA,candidate_SHA256=digest(candidate),
        whole_GameCore=whole,added_proofs={str(f.resolve()):sha(f) for f in proofs},
        private_pending_current_interrupt_proof=True,verification='Private replay pending')
    metadata.write_text(json.dumps(parent_meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'route',rom,text,
            {CONTROLLER,READY,metadata,Path(__file__),KERNEL,KERNEL.with_suffix('.lbl'),*proofs},
            expected=digest(candidate),timeout=180,allow_interactive=True,
            scope='Current full Mini controller with all three early lift spawns, boarding and departure. Both lives and active 1-2 required.')
    print(json.dumps(dict(candidate_SHA256=digest(candidate),whole_GameCore=whole)),flush=True)


if __name__=='__main__':
    main()
