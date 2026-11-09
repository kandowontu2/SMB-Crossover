"""Compose five qualified performance components over the delivered 90a8 ROM."""

import argparse
import json
from pathlib import Path
import re
import shutil

import check_mini_after_bg_1110 as AfterBg
import check_mini_after_bg_irq_1110 as AfterBgIRQ
import check_mini_lift_seen_fast_1110 as Lift
import check_mini_lift_seen_fast_irq_1110 as LiftIRQ
import check_native_actor_bounds_1110 as Bounds
import check_native_actor_bounds_irq_1110 as BoundsIRQ
import check_native_audio_dirty_clear_1110 as Dirty
import check_native_audio_dirty_clear_irq_1110 as DirtyIRQ
import check_native_ground_token_index_1110 as Ground
import check_native_ground_token_index_irq_1110 as GroundIRQ
import prepare_mini_edges_draw_offscreen_native_1110 as Prior
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import CODE, COOKIE, bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha
from qualify_mini_busy_1109 import bind_kernel


BASE,PIN = Lift.BASE,Lift.PIN
DELIVERY = R/'build/mini-edges-draw-offscreen-delivery-1110/verified-delivery.json'
ROOTS = {'lift_seen':R/'build/mini-lift-seen-fast-1110',
         'after_bg':R/'build/mini-afterbg-1110',
         'ground_codec':R/'build/native-ground-token-index-1110',
         'dirty_clear':R/'build/native-audio-dirty-clear-1110',
         'actor_bounds':R/'build/native-actor-bounds-v2-1110'}
OLD_KERNEL = Prior.KERNEL
KERNEL = ROOTS['lift_seen']/'kernel.bin'
AUDIO = Prior.AUDIO


def layout(proofs,spans):
    lift = proofs['lift_seen']
    assert lift['Mini_kernel_bytes']==5120
    assert lift['labels']==load(Prior.ROOTS['edges']/'proof.json')['labels']
    assert KERNEL.with_suffix('.lbl').read_bytes()==OLD_KERNEL.with_suffix('.lbl').read_bytes()
    expected = [(CODE+lo,CODE+hi) for lo,hi in lift['exact_changed_code']]
    assert [(lo,hi) for lo,hi,_,_ in spans['lift_seen']]==expected+[(COOKIE+3,COOKIE+16)]
    fixed = {'after_bg':((66,0xb438,0xb48a),(66,0xb497,0xb4a4)),
             'ground_codec':((38,0xc217,0xc2f4),(57,0xbb9c,0xbbb8)),
             'dirty_clear':((29,0xa92d,0xaab5),),
             'actor_bounds':((0,0xba1e,0xba4e),(0,0xa493,0xa496),(0,0xb450,0xb453))}
    for role,expected in fixed.items():
        rows = proofs[role]['patches']
        for row,(bank,lo,hi) in zip(rows,expected,strict=True):
            assert row['physical_PRG']==bank and row['CPU_half_open']==[lo,hi],(role,row)
            assert row['file_offset']==AfterBg.offset(bank,lo)
    ret = ROOTS['actor_bounds']/'return.json'
    evidence = load(ret)
    assert evidence['passed'] and evidence['parent_SHA256']==PIN
    assert evidence['expected_memory_only_SHA256']==proofs['actor_bounds']['expected_memory_only_SHA256']
    for path,h in evidence['bindings'].items():
        assert sha(R/Path(path))==h,path
    return ret


def build_image():
    refs = {BASE,BASE.with_name('proof.json'),DELIVERY,OLD_KERNEL,KERNEL,
            OLD_KERNEL.with_suffix('.lbl'),KERNEL.with_suffix('.lbl'),AUDIO.RUNTIME,AUDIO.OBSERVER}
    required = {root/name for root in ROOTS.values() for name in ('proof.json','irq.json')}
    required.add(ROOTS['actor_bounds']/'return.json')
    missing = sorted(str(path) for path in required if not path.is_file())
    assert not missing,('Await complete standalone receipts',missing)
    parent = bound_rom(BASE,PIN)
    previous = bound_rom(Prior.BASE,Prior.PIN)
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
        declared = previous if role=='ground_codec' else parent
        isolated,proof,parts = verify_parent(declared,proof_path)
        verify_interrupts(proof_path,irq_path,proof)
        assert digest(isolated)==proof['expected_memory_only_SHA256']
        for lo,hi,old,new in parts:
            assert all(hi<=a or lo>=b for rows in spans.values() for a,b,_,_ in rows),(role,lo,hi)
            assert image[lo:hi]==parent[lo:hi]==old,(role,lo,hi)
            image[lo:hi] = new
        proofs[role],spans[role] = proof,parts
        refs.update((proof_path,irq_path))
    refs.update((layout(proofs,spans),Prior.BASE))
    final = bytes(image)
    assert final[:16]==parent[:16]
    assert final[Prior.Prior.PRG_END:CODE]==parent[Prior.Prior.PRG_END:CODE]
    assert final[CODE+5120:]==parent[CODE+5120:]
    for rom,kernel in ((parent,OLD_KERNEL),(final,KERNEL)):
        verify_payload(rom,kernel)
    return parent,final,proofs,spans,refs


def assets(parent,final,meta,spans):
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
    assert meta['native_draw_address']==Prior.Prior.DRAW_RUN
    draw = bytes.fromhex(meta['native_draw_bytes'])
    at = AfterBg.offset(Prior.Prior.FIRE_BANK,Prior.Prior.DRAW_SOURCE)
    assert parent[at:at+len(draw)]==final[at:at+len(draw)]==draw
    assert digest(draw)==old['projectile_staged_draw_SHA256']
    previous_audio = Prior.Prior.remove(final,spans['ground_codec'])
    for row in load(AUDIO.RUNTIME)['patches']:
        at = row['file_offset']
        code = bytes.fromhex(row['new_hex'])
        assert previous_audio[at:at+len(code)]==parent[at:at+len(code)]==code
    labels = load(ROOTS['lift_seen']/'proof.json')['labels']
    for entry,end in (('MiniNativeDraw','MiniNativeDrawEnd'),('MiniHostColors','MiniHostName')):
        lo,hi = (CODE+labels[name]-0xa000 for name in (entry,end))
        assert final[lo:hi]==parent[lo:hi]
    return old|dict(authenticated_cookie=final[COOKIE:COOKIE+16].hex())


def controller_for(parent,final):
    packet = BASE.parent/'mini'
    controller,ready_path = packet/'controller.lua',packet/'ready.json'
    ready = load(ready_path)
    assert ready['prepared'] and not ready['emulated_writes'] and ready['ROM_sha256']==PIN
    assert Path(ready['ROM']).resolve()==BASE.resolve()
    refs = {Path(p).resolve() for p in ready['bindings']}
    assert {controller.resolve(),BASE.resolve(),OLD_KERNEL.resolve()} <= refs
    for path,h in ready['bindings'].items():
        assert sha(Path(path))==h,path
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
    labels = load(ROOTS['lift_seen']/'proof.json')['labels']
    for name,pc,physical,data in hooks:
        pc = int(pc)
        at = CODE+pc-0xa000
        expected = bytes(map(int,data.split(',')))
        assert pc==labels[name] and int(physical)==pc-0x4000 and final[at:at+len(expected)]==expected
    audio = load(AUDIO.RUNTIME)
    cfg = AUDIO.audio_config(final,audio)
    assert AUDIO.audio_config(parent,audio)==cfg
    assert text.endswith('\n'+cfg+AUDIO.OBSERVER.read_text(encoding='utf-8'))
    assert text.count("shot('mini-active-1-2');audioAssertFinished();result(true)")==1
    return text,refs|{ready_path},ready


def qualify(parent,final,proofs,spans):
    compare = Prior.Prior
    minus = {role:compare.remove(final,parts) for role,parts in spans.items()}
    lift = proofs['lift_seen']
    masks = compare.verify_immutable_ranges(parent,final,lift)
    cold,cold_masks = Lift.A.exact_cold(minus['lift_seen'],final,lift['exact_changed_code'])
    assert cold==lift['exact_cold'] and cold_masks==masks
    # The bounds worker leaves its source-proven unpublished scratch until
    # the next real writer. The strict generic checker has no consumer trace.
    # Check the other four together there, then use the bounds read guard
    # on both images with all the other changes in place.
    core = check_full_cpu(parent,minus['actor_bounds'],masks)
    loop = compare.whole_loop(parent,minus['actor_bounds'],masks)
    assert all(row['min_saved']>0 for row in core)
    print('Exact whole foreground before vector rebind',core,flush=True)
    checks = {role:dict(final_minus_SHA256=digest(before)) for role,before in minus.items()}
    checks['lift_seen']['vectors'] = LiftIRQ.qualify(minus['lift_seen'],final,lift)
    checks['after_bg']['vectors'] = AfterBgIRQ.vectors(minus['after_bg'],final)
    print('Exact lift and post-terrain vectors passed',flush=True)
    for role in ('lift_seen','after_bg'):
        mask = masks if role=='lift_seen' else {}
        checks[role]['whole_GameCore'] = check_full_cpu(minus[role],final,mask)
        checks[role]['whole_GameLoop'] = compare.whole_loop(minus[role],final,mask)
    ground = minus['ground_codec']
    checks['ground_codec']['whole_audio'] = Ground.whole_audio(ground,final,Ground.records(ground)[0])
    checks['ground_codec']['vectors'] = GroundIRQ.vectors(ground,final,proofs['ground_codec']['labels'])
    checks['dirty_clear']['whole_audio'] = Dirty.whole_audio(minus['dirty_clear'],final)
    checks['dirty_clear']['vectors'] = DirtyIRQ.vectors(minus['dirty_clear'],final)
    print('Exact ground codec and dirty clear vectors passed',flush=True)
    original = Bounds.KERNEL,Bounds.KERNEL_PIN
    assert original==(OLD_KERNEL,sha(OLD_KERNEL))
    Bounds.KERNEL,Bounds.KERNEL_PIN = KERNEL,sha(KERNEL)
    try:
        checks['actor_bounds']['whole_GameLoop'] = Bounds.whole(minus['actor_bounds'],final)
        checks['actor_bounds']['vectors'] = BoundsIRQ.vectors(minus['actor_bounds'],final)
    finally:
        Bounds.KERNEL,Bounds.KERNEL_PIN = original
    print('Exact actor bounds vectors passed',flush=True)
    return dict(component_checks=checks,cold_Mini=cold,whole_GameCore=core,whole_GameLoop=loop,
                whole_GameCore_and_GameLoop_exclude_actor_bounds=True,
                immutable_WRAM_comparison_masks=masks)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    parent,final,proofs,spans,refs = build_image()
    pin = digest(final)
    text,route_refs,ready = controller_for(parent,final)
    meta = load(BASE.with_suffix('.json'))
    art = assets(parent,final,meta,spans)
    result = qualify(parent,final,proofs,spans)
    modules = (LiftIRQ,AfterBgIRQ,GroundIRQ,DirtyIRQ,BoundsIRQ,Prior)
    refs.update((Path(__file__),*(Path(mod.__file__) for mod in modules)))
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
                verification='Private Mini lift, post-terrain, audio and bounds replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(out/'mini',rom,text,refs|route_refs|{proof_path,manifest},expected=pin,
            timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,candidate_SHA256=pin,whole_GameCore=result['whole_GameCore'],
                          native_pending=True)),flush=True)


if __name__=='__main__':
    main()
