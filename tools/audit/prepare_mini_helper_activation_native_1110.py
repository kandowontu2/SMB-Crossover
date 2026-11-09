"""Stage the frozen strict-offscreen Mini lift experiment for native replay."""

import argparse
import json
from pathlib import Path
import re
import shutil

import check_mini_helper_activation_1110 as H
import prepare_mini_contact_lag_native_1110 as Contact
from compose_mini_frame_budget_1108 import digest, load
from prepare_mini_lane_audio_native_1110 import bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R,L = H.R,H.L
CPU = R/'build/mini-helper-activation-offscreen-1110/proof.json'
IRQ = CPU.with_name('irq.json')
KERNEL = CPU.with_name('kernel.bin')
TARGET = '9debe5a9cb8046be06a3ed9adef95b3fc1909935f52a5421720ea4400c71a5e8'


def bound_image():
    parent = bound_rom(H.BASE,H.PIN)
    final,proof,spans = verify_parent(parent,CPU)
    verify_interrupts(CPU,IRQ,proof)
    assert digest(final)==proof['expected_memory_only_SHA256']==TARGET
    assert proof['width']==8 and proof['strict_offscreen_retry']
    assert tuple(proof['native_left_edges'])==H.LEFTS and proof['initial_top']==192
    assert tuple(proof['camera_right_minima'])==H.MINIMA
    assert all(left-minimum==8 for left,minimum in zip(H.LEFTS,H.MINIMA,strict=True))
    assert len(spans)==4
    scan = H.offset(24,H.WORKER)
    assert spans[0][:2]==(scan,scan+H.END-H.WORKER)
    assert spans[-1][:2]==(L.COOKIE+3,L.COOKIE+16)
    assert {i-L.CODE for lo,hi,_,_ in spans[1:3] for i in range(lo,hi)}=={
        lo for lo,hi in proof['exact_changed_code'] if hi-lo==1}
    for image,kernel in ((parent,Contact.KERNEL),(final,KERNEL)):
        verify_payload(image,kernel)
    assert KERNEL.with_suffix('.lbl').read_bytes()==Contact.KERNEL.with_suffix('.lbl').read_bytes()
    assert final[L.CODE+5120:L.CODE+7168]==parent[L.CODE+5120:L.CODE+7168]
    for path,h in proof['bindings'].items():
        assert sha(path)==h,path
    return parent,final,proof


def bound_controller(parent,final):
    original = H.BASE.parent/'mini'
    ready_path,controller_path = original/'ready.json',original/'controller.lua'
    ready,meta = load(ready_path),load(H.BASE.with_suffix('.json'))
    assert ready['prepared'] and not ready['emulated_writes'] and ready['ROM_sha256']==H.PIN
    assert Path(ready['ROM']).resolve()==H.BASE.resolve()
    for path,h in ready['bindings'].items():
        assert sha(path)==h,path
    assert meta['passed'] and meta['candidate_SHA256']==H.PIN and meta['platform_spawn'] and meta['camera_lifts']
    parent_proof = H.BASE.with_name('proof.json')
    assert sha(parent_proof)==meta['composed_proof_SHA256']
    assert meta['kernel_SHA256']==sha(Contact.KERNEL)
    for frame in meta['frames'].values():
        offset = L.CODE+5120+frame['CHR_offset']
        assert final[offset:offset+32]==bytes.fromhex(frame['bytes'])
    text = controller_path.read_text(encoding='utf-8')
    hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                       r'\["bytes"\]=\{([\d,]+)\}',text)
    assert hooks
    for address,data in hooks:
        offset = 16+int(address)
        expected = bytes(map(int,data.split(',')))
        assert parent[offset:offset+len(expected)]==final[offset:offset+len(expected)]==expected,address
    audio = Contact.GraphicsBatch.Prior.AUDIO
    runtime = load(audio.RUNTIME)
    cfg = audio.audio_config(final,runtime)
    assert audio.audio_config(parent,runtime)==cfg
    assert text.endswith('\n'+cfg+audio.OBSERVER.read_text(encoding='utf-8'))
    assert all(token not in text for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    edits = {H.PIN:TARGET,sha(Contact.KERNEL):sha(KERNEL),'relative>=256 and relative<=288':
             'relative>=256 and relative<=263'}
    for old,new in edits.items():
        assert text.count(old)==1,old
        text = text.replace(old,new)
    return text,ready,meta,{ready_path,controller_path,parent_proof,H.BASE,H.BASE.with_suffix('.json'),
                            audio.RUNTIME,audio.OBSERVER,Contact.KERNEL}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    output = cli.parse_args().output.resolve()
    assert output.is_relative_to(R/'build') and not output.exists()
    parent,final,proof = bound_image()
    text,ready,meta,refs = bound_controller(parent,final)
    output.mkdir()
    rom = output/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==TARGET
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(H.BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(H.BASE.with_suffix(suffix))
    refs.update((Path(__file__),Path(H.__file__),CPU,IRQ,KERNEL,KERNEL.with_suffix('.lbl')))
    receipt = output/'proof.json'
    assets = dict(load(H.BASE.with_name('proof.json'))['assets'],
                  authenticated_cookie=final[L.COOKIE:L.COOKIE+16].hex())
    report = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=H.PIN,
                  candidate_SHA256=TARGET,kernel_SHA256=sha(KERNEL),assets=assets,
                  patches=proof['patches'],camera_right_minima=H.MINIMA,birth_relative_left=[256,263],
                  full_slot_behavior='Retry while offscreen inside the eight-pixel window; then skip the lift.',
                  initial_top=192,helpers=[dict(stage='1-1',left=left,center=left+16) for left in H.LEFTS],
                  bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=H.PIN,candidate_SHA256=TARGET,kernel_SHA256=sha(KERNEL),
                actual_MiniScene=proof['exact_cold'],composed_proof_SHA256=sha(receipt),
                verification='Private native replay pending for strict offscreen helper activation')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'mini',rom,text,refs|{receipt,manifest},expected=TARGET,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])


if __name__=='__main__':
    main()
