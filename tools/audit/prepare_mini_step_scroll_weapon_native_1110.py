"""Compose the qualified Mini arithmetic, scroll and weapon optimizations."""

import argparse
import importlib
import json
from pathlib import Path
import re
import shutil

import check_mini_inactive_weapon_gate_1110_v1 as Weapon
import check_mini_step_alu_1110 as Alu
import check_mini_step_alu_irq_1110 as AluIRQ
import check_native_platform_box_reuse_1110_v1 as Platform
import check_native_post_scroll_offscreen_1110 as Scroll
import check_native_post_scroll_offscreen_irq_1110 as ScrollIRQ
import prepare_helper_camera_6bd5_native_1110 as Camera
import prepare_mini_platform_firebar_native_1110 as Previous
from prepare_mini_empty_projectile_draw_1108 import DRAW_RUN, DRAW_SOURCE, FIRE_BANK
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import CODE, COOKIE, bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha
from qualify_mini_busy_1109 import bind_kernel


BASE = Alu.BASE
PIN = Alu.PIN
PACKET = BASE.parent/'mini'
ALU_ROOT = R/'build/mini-step-alu-1110'
SCROLL_ROOT = R/'build/native-post-scroll-offscreen-1110'
WEAPON_ROOT = R/'build/mini-inactive-weapon-gate-1110'
OLD_KERNEL = Previous.NEW_KERNEL
KERNEL = ALU_ROOT/'kernel.bin'
ROOTS = {'alu': ALU_ROOT, 'scroll': SCROLL_ROOT, 'weapon': WEAPON_ROOT}
PRG_END = 1048592


def verify_layout(proofs, spans):
    alu = proofs['alu']
    assert alu['Mini_kernel_bytes'] == 5120
    assert alu['labels'] == load(Previous.PROJECTION)['labels']
    assert KERNEL.with_suffix('.lbl').read_bytes() == OLD_KERNEL.with_suffix('.lbl').read_bytes()
    expected = [(CODE+lo-0xa000,CODE+hi-0xa000) for lo,hi in alu['code_spans']]
    assert [(lo,hi) for lo,hi,_,_ in spans['alu']] == expected+[(COOKIE+3,COOKIE+16)]
    Previous.verify_layout(proofs['weapon'],0,((Weapon.START,Weapon.END-Weapon.START),))
    for row,(_,bank,lo,hi) in zip(proofs['scroll']['patches'],Scroll.SPANS,strict=True):
        assert row['physical_PRG'] == bank and row['CPU_half_open'] == [lo,hi]
        assert row['file_offset'] == Scroll.offset(bank,lo)
        assert len(bytes.fromhex(row['old_hex'])) == hi-lo


def build_image():
    parent = bound_rom(BASE,PIN)
    candidate = bytearray(parent)
    prior = load(BASE.with_name('proof.json'))
    assert prior['passed'] and prior['candidate_SHA256'] == PIN
    refs = {BASE,BASE.with_name('proof.json'),OLD_KERNEL,KERNEL,OLD_KERNEL.with_suffix('.lbl'),
            KERNEL.with_suffix('.lbl'),Previous.Audio.RUNTIME,Previous.Audio.OBSERVER}
    all_paths = {root/name for root in ROOTS.values() for name in ('proof.json','irq.json')}
    missing = sorted(str(path) for path in all_paths if not path.is_file())
    assert not missing,('Wait for all three standalone qualification receipts',missing)
    spans, proofs = {}, {}
    for role,root in ROOTS.items():
        path, irq = root/'proof.json',root/'irq.json'
        isolated,proof,parts = verify_parent(parent,path)
        verify_interrupts(path,irq,proof)
        assert digest(isolated) == proof['expected_memory_only_SHA256']
        for lo,hi,old,new in parts:
            assert all(hi<=a or lo>=b for rows in spans.values() for a,b,_,_ in rows),(role,lo,hi)
            assert candidate[lo:hi] == parent[lo:hi] == old,(role,lo,hi)
            candidate[lo:hi] = new
        spans[role],proofs[role] = parts,proof
        refs.update((path,irq))

    verify_layout(proofs,spans)
    assert candidate[:16] == parent[:16]
    assert candidate[PRG_END:CODE] == parent[PRG_END:CODE]
    assert candidate[CODE+5120:] == parent[CODE+5120:]
    for image,kernel in ((parent,OLD_KERNEL),(candidate,KERNEL)):
        verify_payload(image,kernel)
    verify_immutable_ranges(parent,candidate,proofs['alu'])
    return parent,bytes(candidate),proofs,spans,refs


def verify_immutable_ranges(before,after,proof):
    old = before[CODE:CODE+5120]
    new = after[CODE:CODE+5120]
    difference = {i for i,(a,b) in enumerate(zip(old,new,strict=True)) if a!=b}
    expected = {i for lo,hi in proof['exact_changed_code'] for i in range(lo,hi)}
    assert difference == expected and difference
    header = (0x1fe3,0x1ff0)
    return {2:[header],3:[*proof['exact_changed_code'],header]}


def remove(final,spans):
    result = bytearray(final)
    for lo,hi,old,new in spans:
        assert result[lo:hi] == new
        result[lo:hi] = old
    return bytes(result)


def whole_loop(before,after,masks):
    if not masks:
        return Platform.whole(before,after)
    adapter = Platform.Direct.D
    memory = adapter.memory

    def normalized(bus):
        image = bus.bundle['raw']
        cookie = image[COOKIE:COOKIE+16]
        assert bytes(bus.ram[3][:5120]) == image[CODE:CODE+5120]
        assert all(bytes(bus.ram[b][0x1fe0:0x1ff0]) == cookie for b in (2,3))
        state = memory(bus)
        banks = list(state[5])
        for bank,ranges in masks.items():
            block = bytearray(banks[bank])
            for lo,hi in ranges:
                block[lo:hi] = bytes(hi-lo)
            banks[bank] = bytes(block)
        return (*state[:5],tuple(banks),*state[6:])

    adapter.memory = normalized
    try:
        return Platform.whole(before,after)
    finally:
        adapter.memory = memory


def assets(parent,final,meta):
    assert meta['passed'] and meta['candidate_SHA256'] == PIN and meta['kernel_SHA256'] == sha(OLD_KERNEL)
    assert meta['platform_spawn'] and meta['camera_lifts']
    metadata = CODE+5120
    assert set(meta['frames']) == set('ABCD') and meta['palette'] == [0x16,0x30,0x27]
    assert meta['live_art_extent'] == [6,6] and meta['native_collision_extent'] == [4,4]
    for frame in meta['frames'].values():
        start = metadata+frame['CHR_offset']
        expected = bytes.fromhex(frame['bytes'])
        assert len(expected)==32 and final[start:start+32] == parent[start:start+32] == expected
    draw = bytes.fromhex(meta['native_draw_bytes'])
    draw_at = 16+8192*FIRE_BANK+(DRAW_SOURCE&8191)
    assert meta['native_draw_address']==DRAW_RUN
    assert final[draw_at:draw_at+len(draw)] == parent[draw_at:draw_at+len(draw)] == draw
    # The Mini renderer, palette publisher, staged CHR pages and audio
    # transport all retain their original payload and entry points.
    labels = load(ALU_ROOT/'proof.json')['labels']
    for name,next_name in (('MiniHostDraw','MiniHostPortrait'),('MiniNativeDraw','MiniNativeDrawEnd'),
                           ('MiniHostColors','MiniHostName')):
        start,end = (CODE+labels[n]-0xa000 for n in (name,next_name))
        assert parent[start:end] == final[start:end]
    audio = load(Previous.Audio.RUNTIME)
    for row in audio['patches']:
        start = row['file_offset']
        data = bytes.fromhex(row['new_hex'])
        assert final[start:start+len(data)] == parent[start:start+len(data)] == data
    return dict(code_carriers=5,code_bytes=5120,metadata_and_art_carrier_SHA256=digest(final[metadata:metadata+2048]),
                authenticated_cookie=final[COOKIE:COOKIE+16].hex(),verified_projectile_frames=list(meta['frames']),
                projectile_palette=meta['palette'],projectile_staged_draw_SHA256=digest(draw))


def controller_for(parent,final):
    text,refs,ready = Camera.packet_input(PACKET,BASE,final,None,'mini')
    old_sha,new_sha = sha(OLD_KERNEL),sha(KERNEL)
    assert text.count(old_sha)==1 and new_sha not in text
    text = bind_kernel(text,KERNEL).replace(old_sha,new_sha)
    assert text.count(digest(final))==text.count(new_sha)==1 and old_sha not in text
    memory_hooks = re.findall(r'\["name"\]="(Mini\w+)",\["pc"\]=(\d+),'
                             r'\["physical"\]=(\d+),\["memory"\]="nesWorkRam",'
                             r'\["bytes"\]=\{([\d,]+)\}',text)
    assert {'MiniStep','MiniHostMain','MiniNativeDraw'} <= {row[0] for row in memory_hooks}
    labels = load(ALU_ROOT/'proof.json')['labels']
    for name,pc,physical,data in memory_hooks:
        pc,physical = int(pc),int(physical)
        assert labels[name]==pc and physical==pc-0x4000
        offset = CODE+pc-0xa000
        expected = bytes(map(int,data.split(',')))
        assert final[offset:offset+len(expected)]==expected
    audio = Previous.Audio
    passive = audio.OBSERVER.read_text(encoding='utf-8')
    config = load(audio.RUNTIME)
    assert audio.audio_config(parent,config)==audio.audio_config(final,config)
    assert text.endswith('\n'+audio.audio_config(final,config)+passive)
    assert text.count("shot('mini-active-1-2');audioAssertFinished();result(true)")==1
    return text,refs,ready


def qualify(parent,final,proofs,spans):
    minus = {role:remove(final,rows) for role,rows in spans.items()}
    masks = verify_immutable_ranges(parent,final,proofs['alu'])
    cold,cold_masks = Alu.exact_cold(minus['alu'],final,proofs['alu']['exact_changed_code'])
    assert masks==cold_masks and cold==proofs['alu']['exact_cold']
    core = check_full_cpu(parent,final,masks)
    loop = whole_loop(parent,final,masks)
    assert all(row['min_saved']>0 for row in core)
    result = {}
    for role,before in minus.items():
        compare_masks = masks if role=='alu' else {}
        result[role] = dict(final_minus_SHA256=digest(before),
                            whole_GameCore=check_full_cpu(before,final,compare_masks),
                            whole_GameLoop=whole_loop(before,final,compare_masks))
    result['alu']['vectors'] = AluIRQ.qualify(final,proofs['alu']['code_spans'])
    result['alu']['final_minus_vectors'] = AluIRQ.qualify(minus['alu'],proofs['alu']['code_spans'])
    print('Mini arithmetic vectors',result['alu']['vectors']['cuts'],flush=True)
    result['scroll']['vectors'] = ScrollIRQ.vectors(minus['scroll'],final)
    print('Post-scroll vectors',result['scroll']['vectors']['cuts'],flush=True)
    fire_irq = importlib.import_module('check_mini_inactive_weapon_gate_irq_1110_v1')
    # Both final-minus weapon images carry the same new authenticated Mini
    # kernel. The cold fixture still compares all 5120 decoded bytes and both
    # headers through the real menu/entrance before checking the live route.
    assert fire_irq.Match is Weapon.Match and Weapon.Match.KERNEL == OLD_KERNEL
    Weapon.Match.KERNEL = KERNEL
    try:
        result['weapon']['matched_GameLoop'] = Weapon.whole(minus['weapon'],final)
        result['weapon']['vectors'] = fire_irq.vectors(minus['weapon'],final)
    finally:
        Weapon.Match.KERNEL = OLD_KERNEL
    print('Inactive weapon vectors',result['weapon']['vectors']['cuts'],flush=True)
    return dict(component_checks=result,cold_Mini=cold,whole_GameCore=core,whole_GameLoop=loop,
                immutable_WRAM_comparison_masks=masks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--check-only',action='store_true',help='Write the proof without a ROM or native packet')
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    parent,final,proofs,spans,refs = build_image()
    text,route_refs,ready = controller_for(parent,final)
    meta = load(BASE.with_suffix('.json'))
    art = assets(parent,final,meta)
    result = qualify(parent,final,proofs,spans)
    pin = digest(final)
    fire_irq = importlib.import_module('check_mini_inactive_weapon_gate_irq_1110_v1')
    refs.update((Path(__file__),Path(AluIRQ.__file__),Path(ScrollIRQ.__file__),Path(fire_irq.__file__)))
    report = dict(passed=True,parent_SHA256=PIN,candidate_SHA256=pin,ROM_written=not args.check_only,
                  native_pending=True,groups={role:proof['patches'] for role,proof in proofs.items()},
                  kernel_SHA256=sha(KERNEL),assets=art,
                  bindings={str(p.resolve()):sha(p) for p in sorted(refs)},**result)
    out.mkdir()
    proof_path = out/'proof.json'
    proof_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if not args.check_only:
        rom = out/'candidate.nes'
        rom.write_bytes(final)
        assert sha(rom)==pin
        for ext in ('.lbl','.dbg'):
            shutil.copyfile(BASE.with_suffix(ext),rom.with_suffix(ext))
            assert sha(rom.with_suffix(ext))==sha(BASE.with_suffix(ext))
        manifest = rom.with_suffix('.json')
        meta.update(parent_SHA256=PIN,candidate_SHA256=pin,kernel_SHA256=sha(KERNEL),
                    actual_MiniScene=result['cold_Mini'],composed_proof_SHA256=sha(proof_path),
                    verification='Private Mini arithmetic, scroll and weapon replay pending')
        manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
        prepare(out/'mini',rom,text,refs|route_refs|{proof_path,manifest},expected=pin,
                timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,candidate_SHA256=pin,whole_GameCore=result['whole_GameCore'],
                          ROM_written=not args.check_only,native_pending=True)),flush=True)


if __name__=='__main__':
    main()
