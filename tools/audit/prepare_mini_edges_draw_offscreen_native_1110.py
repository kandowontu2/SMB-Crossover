"""Rebind qualified Mini edge, shared draw and offscreen changes to delivered 991b."""

import argparse
import json
from pathlib import Path
import re
import shutil

import check_mini_step_alu_irq_1110 as AluIRQ
import check_mini_step_edges_1110 as Edges
import check_mini_step_edges_irq_1110 as EdgesIRQ
import check_native_raw_offscreen_tail_1110 as Raw
import check_native_raw_offscreen_tail_irq_1110 as RawIRQ
import check_shared_draw_retarget_1110 as Draw
import check_shared_draw_retarget_irq_1110 as DrawIRQ
import prepare_mini_step_scroll_weapon_native_1110 as Prior
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import CODE, COOKIE, bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha
from qualify_mini_busy_1109 import bind_kernel


BASE, PIN = Edges.BASE, Edges.PIN
PACKET = BASE.parent/'mini'
DELIVERY = R/'build/mini-step-scroll-weapon-delivery-1110/verified-delivery.json'
ROOTS = {'edges':R/'build/mini-step-edges-1110',
         'draw':R/'build/shared-draw-retarget-1110',
         'offscreen':R/'build/native-raw-offscreen-tail-1110'}
OLD_KERNEL = Prior.KERNEL
KERNEL = ROOTS['edges']/'kernel.bin'
AUDIO = Prior.Previous.Audio


def layout(proofs,spans):
    edges = proofs['edges']
    assert edges['Mini_kernel_bytes']==5120
    assert edges['labels']==load(Prior.ALU_ROOT/'proof.json')['labels']
    assert KERNEL.with_suffix('.lbl').read_bytes()==OLD_KERNEL.with_suffix('.lbl').read_bytes()
    assert [tuple(pair) for pair in edges['code_spans']]==list(Edges.SPANS)
    expected = [(CODE+lo-0xa000,CODE+hi-0xa000) for lo,hi in Edges.SPANS]
    assert [(lo,hi) for lo,hi,_,_ in spans['edges']]==expected+[(COOKIE+3,COOKIE+16)]
    Prior.Previous.verify_layout(proofs['draw'],79,((Draw.PATCH_PC,len(Draw.PREIMAGE)),))
    for row,(_,lo,hi,preimage) in zip(proofs['offscreen']['patches'],Raw.SPANS,strict=True):
        assert row['physical_PRG']==126 and row['CPU_half_open']==[lo,hi]
        assert row['file_offset']==Raw.offset(lo) and row['old_hex']==preimage
        assert len(bytes.fromhex(row['new_hex']))==hi-lo


def build_image():
    refs = {BASE,BASE.with_name('proof.json'),DELIVERY,OLD_KERNEL,KERNEL,
            OLD_KERNEL.with_suffix('.lbl'),KERNEL.with_suffix('.lbl'),AUDIO.RUNTIME,AUDIO.OBSERVER}
    required = {root/name for root in ROOTS.values() for name in ('proof.json','irq.json')}
    missing = sorted(str(path) for path in required if not path.is_file())
    assert not missing,('Await complete standalone IRQ receipts',missing)
    parent = bound_rom(BASE,PIN)
    delivery = load(DELIVERY)
    assert delivery['ROM_SHA256']==PIN and delivery['Downloads_launch_verified'] and delivery['IPS_roundtrip']
    incumbent = load(BASE.with_name('proof.json'))
    assert incumbent['passed'] and incumbent['candidate_SHA256']==PIN
    assert delivery['composed_proof_SHA256']==sha(BASE.with_name('proof.json'))
    assert delivery['kernel_SHA256']==incumbent['kernel_SHA256']==sha(OLD_KERNEL)
    image = bytearray(parent)
    proofs,spans = {},{}
    for role,root in ROOTS.items():
        proof_path,irq_path = root/'proof.json',root/'irq.json'
        isolated,proof,parts = verify_parent(parent,proof_path)
        verify_interrupts(proof_path,irq_path,proof)
        assert digest(isolated)==proof['expected_memory_only_SHA256']
        for lo,hi,old,new in parts:
            assert all(hi<=a or lo>=b for rows in spans.values() for a,b,_,_ in rows),(role,lo,hi)
            assert image[lo:hi]==parent[lo:hi]==old,(role,lo,hi)
            image[lo:hi] = new
        proofs[role],spans[role] = proof,parts
        refs.update((proof_path,irq_path))
    layout(proofs,spans)
    final = bytes(image)
    assert final[:16]==parent[:16]
    assert final[Prior.PRG_END:CODE]==parent[Prior.PRG_END:CODE]
    assert final[CODE+5120:]==parent[CODE+5120:]
    for image,kernel in ((parent,OLD_KERNEL),(final,KERNEL)):
        verify_payload(image,kernel)
    Prior.verify_immutable_ranges(parent,final,proofs['edges'])
    return parent,final,proofs,spans,refs


def assets(parent,final,meta):
    assert meta['passed'] and meta['candidate_SHA256']==PIN and meta['kernel_SHA256']==sha(OLD_KERNEL)
    old = load(BASE.with_name('proof.json'))['assets']
    start = CODE+5120
    assert digest(parent[start:start+2048])==digest(final[start:start+2048])==old['metadata_and_art_carrier_SHA256']
    assert set(meta['frames'])==set(old['verified_projectile_frames'])==set('ABCD')
    for frame in meta['frames'].values():
        at = start+frame['CHR_offset']
        assert parent[at:at+32]==final[at:at+32]==bytes.fromhex(frame['bytes'])
    assert meta['palette']==old['projectile_palette']==[0x16,0x30,0x27]
    assert meta['platform_spawn'] and meta['camera_lifts']
    assert meta['live_art_extent']==[6,6] and meta['native_collision_extent']==[4,4]
    assert meta['native_draw_address']==Prior.DRAW_RUN
    draw = bytes.fromhex(meta['native_draw_bytes'])
    at = 16+8192*Prior.FIRE_BANK+(Prior.DRAW_SOURCE&8191)
    assert parent[at:at+len(draw)]==final[at:at+len(draw)]==draw
    assert digest(draw)==old['projectile_staged_draw_SHA256']
    for row in load(AUDIO.RUNTIME)['patches']:
        at = row['file_offset']
        code = bytes.fromhex(row['new_hex'])
        assert final[at:at+len(code)]==parent[at:at+len(code)]==code
    labels = load(ROOTS['edges']/'proof.json')['labels']
    for entry,end in (('MiniNativeDraw','MiniNativeDrawEnd'),('MiniHostColors','MiniHostName')):
        lo,hi = (CODE+labels[name]-0xa000 for name in (entry,end))
        assert final[lo:hi]==parent[lo:hi]
    return old|dict(authenticated_cookie=final[COOKIE:COOKIE+16].hex())


def controller_for(parent,final):
    controller,ready_path = PACKET/'controller.lua',PACKET/'ready.json'
    ready = load(ready_path)
    assert ready['prepared'] and not ready['emulated_writes'] and ready['ROM_sha256']==PIN
    assert Path(ready['ROM']).resolve()==BASE.resolve()
    refs = {Path(p).resolve() for p in ready['bindings']}
    assert {controller.resolve(),BASE.resolve(),OLD_KERNEL.resolve()} <= refs
    for p,h in ready['bindings'].items():
        assert sha(Path(p))==h,p
    text = controller.read_text(encoding='utf-8')
    assert all(token not in text for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    old_kernel,new_kernel = sha(OLD_KERNEL),sha(KERNEL)
    pin = digest(final)
    assert text.count(PIN)==text.count(old_kernel)==1 and new_kernel not in text
    hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                       r'\["bytes"\]=\{([\d,]+)\}',text)
    assert hooks
    for physical,data in hooks:
        at = 16+int(physical)
        expected = bytes(map(int,data.split(',')))
        assert parent[at:at+len(expected)]==final[at:at+len(expected)]==expected,physical
    text = bind_kernel(text.replace(PIN,pin),KERNEL).replace(old_kernel,new_kernel)
    assert text.count(pin)==text.count(new_kernel)==1 and old_kernel not in text
    hooks = re.findall(r'\["name"\]="(Mini\w+)",\["pc"\]=(\d+),\["physical"\]=(\d+),'
                       r'\["memory"\]="nesWorkRam",\["bytes"\]=\{([\d,]+)\}',text)
    assert {'MiniStep','MiniHostMain','MiniNativeDraw'} <= {name for name,*_ in hooks}
    labels = load(ROOTS['edges']/'proof.json')['labels']
    for name,pc,physical,data in hooks:
        pc = int(pc)
        at = CODE+pc-0xa000
        expected = bytes(map(int,data.split(',')))
        assert pc==labels[name] and int(physical)==pc-0x4000 and final[at:at+len(expected)]==expected
    audio = load(AUDIO.RUNTIME)
    assert AUDIO.audio_config(parent,audio)==AUDIO.audio_config(final,audio)
    assert text.endswith('\n'+AUDIO.audio_config(final,audio)+AUDIO.OBSERVER.read_text(encoding='utf-8'))
    assert text.count("shot('mini-active-1-2');audioAssertFinished();result(true)")==1
    return text,refs|{ready_path},ready


def qualify(parent,final,proofs,spans):
    minus = {role:Prior.remove(final,parts) for role,parts in spans.items()}
    masks = Prior.verify_immutable_ranges(parent,final,proofs['edges'])
    cold,cold_masks = Edges.Alu.exact_cold(minus['edges'],final,proofs['edges']['exact_changed_code'])
    assert cold==proofs['edges']['exact_cold'] and cold_masks==masks
    core = check_full_cpu(parent,final,masks)
    assert all(row['min_saved']>0 for row in core)
    loop = Prior.whole_loop(parent,final,masks)
    checks = {}
    for role,previous in minus.items():
        mask = masks if role=='edges' else {}
        checks[role] = dict(final_minus_SHA256=digest(previous),whole_GameCore=check_full_cpu(previous,final,mask),
                            whole_GameLoop=Prior.whole_loop(previous,final,mask))
    checks['edges']['vectors'] = EdgesIRQ.qualify(final)
    checks['edges']['final_minus_vectors'] = AluIRQ.qualify(minus['edges'],load(Prior.ALU_ROOT/'proof.json')['code_spans'])
    print('Mini edge vectors',checks['edges']['vectors']['cuts'],flush=True)
    checks['offscreen']['vectors'] = RawIRQ.vectors(minus['offscreen'],final)
    print('Raw offscreen vectors',checks['offscreen']['vectors']['cuts'],flush=True)
    assert DrawIRQ.Draw is Draw and Draw.KERNEL==OLD_KERNEL
    Draw.KERNEL = KERNEL
    try:
        checks['draw']['independent_cold_GameLoop'] = Draw.whole(minus['draw'],final)
        checks['draw']['vectors'] = DrawIRQ.vectors(minus['draw'],final)
    finally:
        Draw.KERNEL = OLD_KERNEL
    print('Shared draw vectors',checks['draw']['vectors']['cuts'],flush=True)
    return dict(component_checks=checks,cold_Mini=cold,whole_GameCore=core,whole_GameLoop=loop,
                immutable_WRAM_comparison_masks=masks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    parent,final,proofs,spans,refs = build_image()
    pin = digest(final)
    text,route_refs,ready = controller_for(parent,final)
    meta = load(BASE.with_suffix('.json'))
    art = assets(parent,final,meta)
    result = qualify(parent,final,proofs,spans)
    refs.update((Path(__file__),Path(EdgesIRQ.__file__),Path(AluIRQ.__file__),Path(RawIRQ.__file__),
                 Path(DrawIRQ.__file__),Path(Prior.__file__)))
    report = dict(passed=True,parent_SHA256=PIN,candidate_SHA256=pin,ROM_written=True,native_pending=True,
                  groups={role:proof['patches'] for role,proof in proofs.items()},kernel_SHA256=sha(KERNEL),
                  assets=art,bindings={str(p.resolve()):sha(p) for p in sorted(refs)},**result)
    out.mkdir()
    proof_path = out/'proof.json'
    proof_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    rom = out/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for ext in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(ext),rom.with_suffix(ext))
        assert sha(rom.with_suffix(ext))==sha(BASE.with_suffix(ext))
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=PIN,candidate_SHA256=pin,kernel_SHA256=sha(KERNEL),
                actual_MiniScene=result['cold_Mini'],composed_proof_SHA256=sha(proof_path),
                verification='Private Mini edge, draw and offscreen replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,text,refs|route_refs|{proof_path,manifest},expected=pin,
            timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,candidate_SHA256=pin,whole_GameCore=result['whole_GameCore'],
                          native_pending=True)),flush=True)


if __name__=='__main__':
    main()
