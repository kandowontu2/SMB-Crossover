"""Audit exact Mini contact-lag successors over the a1c28 graphics/geometry image."""

import argparse
import json
from pathlib import Path
import re
import shutil

import check_mini_direct_frame_stack_1110 as Movement
import check_mini_direct_frame_stack_irq_1110 as MovementIRQ
import check_mini_native_contact_1110 as Contact
import check_mini_native_contact_irq_1110 as ContactIRQ
import check_mini_stomp_drop_1110 as StompDrop
import check_mini_stomp_drop_irq_1110 as StompDropIRQ
import check_shared_palette_reset_1110 as Palette
import check_shared_palette_reset_irq_1110 as PaletteIRQ
import prepare_mini_graphics_edge_movement_native_1110 as GraphicsBatch
from compose_mini_frame_budget_1108 import digest, load
from prepare_mini_lane_audio_native_1110 import CODE, COOKIE, bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha


BASE = R/'build/mini-graphics-edge-movement-native-1110/candidate.nes'
PIN = 'a1c28fdf0b03bbc652e989083a74fc8365b7a875b821bcb92d63f7cd7144180d'
DELIVERY = R/'build/mini-graphics-edge-movement-delivery-1110/verified-delivery.json'
KERNEL = GraphicsBatch.KERNEL
BASE_GROUPS = {'graphics_visibility','enemy_edge','box_core'}
NEXT_GROUPS = {'movement_stack','palette_reset','mini_stomp_drop','native_body_contact'}
MOVEMENT = R/'build/mini-direct-frame-stack-1110/proof.json'
PALETTE = R/'build/shared-palette-reset-1110/proof.json'
STOMP = R/'build/mini-stomp-drop-1110/proof.json'
CONTACT = R/'build/mini-native-contact-1110/proof.json'
PRG_END = 16+128*8192


def parent_image():
    parent = bound_rom(BASE,PIN)
    evidence = load(BASE.with_name('proof.json'))
    assert evidence['passed'] and evidence['candidate_SHA256']==PIN
    assert evidence['parent_SHA256']==Movement.PIN
    assert set(evidence['groups'])==set(evidence['component_checks'])==BASE_GROUPS
    assert evidence['kernel_SHA256']==sha(KERNEL)
    for path,h in evidence['bindings'].items():
        assert sha(R/Path(path))==h,path
    previous = bound_rom(Movement.BASE,Movement.PIN)
    rows = [row for group in evidence['groups'].values() for row in group]
    linked = bytearray(previous)
    for row in rows:
        at = row['file_offset']
        old,new = (bytes.fromhex(row[k]) for k in ('old_hex','new_hex'))
        assert linked[at:at+len(old)]==old
        linked[at:at+len(new)] = new
    assert linked==parent
    delivery_parent = load(Movement.BASE.with_name('proof.json'))
    assert delivery_parent['passed'] and delivery_parent['candidate_SHA256']==Movement.PIN
    preserved = [row for group in delivery_parent['groups'].values() for row in group]
    for row in preserved:
        at,data = row['file_offset'],bytes.fromhex(row['new_hex'])
        assert previous[at:at+len(data)]==parent[at:at+len(data)]==data,row
    return parent,previous,evidence,rows+preserved


def group_inputs():
    return {'movement_stack':(MOVEMENT,MOVEMENT.with_name('irq.json')),
            'palette_reset':(PALETTE,PALETTE.with_name('irq.json')),
            'mini_stomp_drop':(STOMP,STOMP.with_name('irq.json')),
            'native_body_contact':(CONTACT,CONTACT.with_name('irq.json'))}


def apply_frozen(parent,previous,current_rows,groups):
    assert groups and set(groups)<=NEXT_GROUPS
    refs = {BASE,BASE.with_name('proof.json'),Movement.BASE,Movement.BASE.with_name('proof.json'),
            KERNEL,KERNEL.with_suffix('.lbl'),
            GraphicsBatch.Prior.AUDIO.RUNTIME,GraphicsBatch.Prior.AUDIO.OBSERVER}
    occupied = GraphicsBatch.range_set(current_rows)
    frozen,spans = {},{}
    image = bytearray(parent)
    parents = {Movement.PIN:previous,PIN:parent}
    for role,(path,irq_path) in groups.items():
        header = load(path)
        declared = header.get('parent_SHA256',header.get('base_ROM_SHA256'))
        assert declared in parents,(role,declared)
        isolated,proof,parts = verify_parent(parents[declared],path)
        assert digest(isolated)==proof['expected_memory_only_SHA256']
        verify_interrupts(path,irq_path,proof)
        if role=='movement_stack':
            GraphicsBatch.exact_extent(proof,84,Movement.ENTRY,Movement.END)
        if role=='palette_reset':
            GraphicsBatch.exact_extent(proof,79,Palette.ENTRY,Palette.END)
        if role=='mini_stomp_drop':
            expected = ((StompDrop.WORKER,StompDrop.END),(StompDrop.CALLER,StompDrop.JOIN))
            for row,(lo,hi) in zip(proof['patches'],expected,strict=True):
                GraphicsBatch.exact_extent({'patches':[row]},66,lo,hi)
            assert proof['allocation']['old_EA_preimage_accepted']
            assert proof['allocation']['new_guard_preimage_rejected']
        if role=='native_body_contact':
            expected = ((Contact.GATE,0xbf34),(Contact.HELPER,0xb180))
            for row,(lo,hi) in zip(proof['patches'],expected,strict=True):
                GraphicsBatch.exact_extent({'patches':[row]},74,lo,hi)
        for lo,hi,old,new in parts:
            extent = set(range(lo,hi))
            assert hi<=PRG_END and not occupied.intersection(extent),(role,lo,hi)
            assert image[lo:hi]==parent[lo:hi]==old,(role,lo,hi)
            occupied.update(extent)
            image[lo:hi] = new
        refs.update((path,irq_path))
        frozen[role],spans[role] = proof,parts
    final = bytes(image)
    assert final[:16]==parent[:16] and final[PRG_END:]==parent[PRG_END:]
    assert final[COOKIE:COOKIE+16]==parent[COOKIE:COOKIE+16]
    for raw in (parent,final):
        verify_payload(raw,KERNEL)
    for parts in spans.values():
        image = GraphicsBatch.Route.remove(image,parts)
    assert image==parent
    return final,frozen,spans,refs


def replay_inputs(parent,final,evidence):
    manifest = BASE.with_suffix('.json')
    meta = load(manifest)
    assert meta['passed'] and meta['candidate_SHA256']==PIN and meta['kernel_SHA256']==sha(KERNEL)
    assert meta['composed_proof_SHA256']==sha(BASE.with_name('proof.json'))
    assert meta['platform_spawn'] and meta['camera_lifts'] and set(meta['frames'])==set('ABCD')
    art = evidence['assets']
    assert digest(final[CODE+5120:CODE+7168])==art['metadata_and_art_carrier_SHA256']
    assert final[COOKIE:COOKIE+16].hex()==art['authenticated_cookie']
    for frame in meta['frames'].values():
        at = CODE+5120+frame['CHR_offset']
        assert final[at:at+32]==bytes.fromhex(frame['bytes'])
    draw = bytes.fromhex(meta['native_draw_bytes'])
    route = GraphicsBatch.Route
    at = 16+route.FIRE_BANK*8192+(route.DRAW_SOURCE&8191)
    assert parent[at:at+len(draw)]==final[at:at+len(draw)]==draw
    assert digest(draw)==art['projectile_staged_draw_SHA256']
    audio = GraphicsBatch.Prior.AUDIO
    runtime = load(audio.RUNTIME)
    for row in runtime['patches']:
        off = row['file_offset']
        end = off+len(bytes.fromhex(row['new_hex']))
        assert final[off:end]==parent[off:end],row
    packet = BASE.parent/'mini'
    lua,ready_path = packet/'controller.lua',packet/'ready.json'
    ready = load(ready_path)
    assert ready['prepared'] and not ready['emulated_writes'] and ready['ROM_sha256']==PIN
    assert Path(ready['ROM']).resolve()==BASE.resolve()
    refs = {Path(path).resolve() for path in ready['bindings']}
    assert {lua.resolve(),BASE.resolve(),KERNEL.resolve()}<=refs
    for path,h in ready['bindings'].items():
        assert sha(path)==h,path
    text = lua.read_text(encoding='utf-8')
    assert text.count(PIN)==text.count(sha(KERNEL))==1
    assert all(token not in text for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                       r'\["bytes"\]=\{([\d,]+)\}',text)
    assert hooks
    for address,data in hooks:
        off = 16+int(address)
        expected = bytes(map(int,data.split(',')))
        assert parent[off:off+len(expected)]==final[off:off+len(expected)]==expected,address
    cfg = audio.audio_config(final,runtime)
    assert audio.audio_config(parent,runtime)==cfg
    assert text.endswith('\n'+cfg+audio.OBSERVER.read_text(encoding='utf-8'))
    assert text.count("shot('mini-active-1-2');audioAssertFinished();result(true)")==1
    return text.replace(PIN,digest(final)),ready,meta,refs|{ready_path,manifest}


def verify_delivery(path):
    q = load(path)
    assert q['installed'] and q['Downloads_launch_verified'] and q['IPS_roundtrip']
    assert q['ROM_SHA256']==PIN and q['previous_ROM_SHA256']==Movement.PIN
    assert q['composed_proof_SHA256']==sha(BASE.with_name('proof.json'))
    assert q['kernel_SHA256']==sha(KERNEL) and q['native_audio_matches_candidate']
    assert q['active_11_cadence']['no_controller_read']==39
    assert q['post_guard']['passed'] and q['post_guard']['ROM_sha256']==PIN
    assert not q['post_guard']['matching_patch_files']
    assert sha(Path(q['destination']))==PIN
    return q


def qualify_movement(final,proof,parts):
    before = GraphicsBatch.Route.remove(final,parts)
    direct = Movement.qualify(before,final)
    assert direct==proof['direct']
    core = Movement.A.P.check_full_cpu(before,final,{})
    loop = Movement.Q.Lift.Edges.Composed.whole_loop(before,final,{})
    vectors = MovementIRQ.vectors(before,final)
    return dict(final_minus_SHA256=digest(before),direct=direct,whole_GameCore=core,
                whole_GameLoop=loop,vectors=vectors)


def qualify_palette(final,proof,parts):
    before = GraphicsBatch.Route.remove(final,parts)
    loops = Palette.whole(before,final,kernel=KERNEL,kernel_sha=sha(KERNEL))
    assert loops==proof['whole_GameLoop']
    vectors = PaletteIRQ.vectors(before,final,kernel=KERNEL,kernel_sha=sha(KERNEL))
    return dict(final_minus_SHA256=digest(before),whole_GameLoop=loops,vectors=vectors)


def qualify_stomp(final,parts):
    before = GraphicsBatch.Route.remove(final,parts)
    loops = StompDrop.whole(before,final,kernel=KERNEL,kernel_sha=sha(KERNEL))
    assert all(row['savings']>=1300 and row['final_packet_exact'] for row in loops)
    vectors = StompDropIRQ.vectors(before,final,kernel=KERNEL,kernel_sha=sha(KERNEL))
    return dict(final_minus_SHA256=digest(before),whole_contact_GameLoop=loops,vectors=vectors)


def qualify_contact(final,proof,parts):
    before = GraphicsBatch.Route.remove(final,parts)
    foreground = Contact.foreground(before,final)
    assert foreground==proof['foreground']
    vectors = ContactIRQ.vectors(before,final)
    return dict(final_minus_SHA256=digest(before),foreground=foreground,vectors=vectors)


def qualify_combined(parent,final):
    cold,_ = GraphicsBatch.Prior.Lift.A.exact_cold(parent,final,[])
    core = GraphicsBatch.check_full_cpu(parent,final,{})
    loop = GraphicsBatch.EdgeIRQ.whole(parent,final)
    assert all(row['min_saved']>0 for row in core)
    return dict(cold_Mini=cold,whole_GameCore=core,whole_GameLoop=loop)


def stage(output,parent,final,evidence,proofs,checks,full,refs):
    assert set(proofs)==set(checks)==NEXT_GROUPS
    delivery = verify_delivery(DELIVERY)
    text,ready,meta,packet_refs = replay_inputs(parent,final,evidence)
    pin = digest(final)
    refs.update(Path(mod.__file__).resolve() for mod in
                (Movement,MovementIRQ,Palette,PaletteIRQ,StompDrop,StompDropIRQ,Contact,ContactIRQ,GraphicsBatch))
    refs.update((Path(__file__).resolve(),DELIVERY))
    assert output.is_relative_to(R/'build') and not output.exists()
    output.mkdir()
    proof_path = output/'proof.json'
    report = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PIN,candidate_SHA256=pin,
                  parent_cadence=delivery['active_11_cadence'],kernel_SHA256=sha(KERNEL),assets=evidence['assets'],
                  groups={role:proof['patches'] for role,proof in proofs.items()},component_checks=checks,
                  changed_bytes=sum(a!=b for a,b in zip(parent,final,strict=True)),
                  bindings={str(p.resolve()):sha(p) for p in sorted(refs)},**full)
    proof_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    rom = output/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(BASE.with_suffix(suffix))
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=PIN,candidate_SHA256=pin,actual_MiniScene=full['cold_Mini'],
                composed_proof_SHA256=sha(proof_path),verification='Private Mini contact-lag replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'mini',rom,text,refs|packet_refs|{proof_path,manifest},expected=pin,
            timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,candidate_SHA256=pin,groups=sorted(proofs),
                          whole_GameCore=full['whole_GameCore'],native_pending=True)),flush=True)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    mode = cli.add_mutually_exclusive_group(required=True)
    mode.add_argument('--census',action='store_true',help='Validate frozen spans and native bindings in memory only.')
    mode.add_argument('--emit',action='store_true',help='Qualify all four frozen groups and stage one native replay.')
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R/'build')
    parent,previous,evidence,rows = parent_image()
    delivered = DELIVERY.is_file()
    if delivered:
        verify_delivery(DELIVERY)
    groups = group_inputs()
    available = {name:paths for name,paths in groups.items() if all(path.is_file() for path in paths)}
    pending = NEXT_GROUPS-set(available)
    if args.emit:
        assert delivered and not pending,('Require exact installed parent and every frozen receipt',pending)
    final,proofs,spans,refs = apply_frozen(parent,previous,rows,available)
    replay_inputs(parent,final,evidence)
    if args.census:
        print(json.dumps(dict(passed=True,ROM_written=False,parent_SHA256=PIN,memory_SHA256=digest(final),
                              Downloads_parent_verified=delivered,
                              groups={role:[(lo,hi) for lo,hi,_,_ in parts] for role,parts in spans.items()},
                              pending=sorted(pending))))
        return
    full = qualify_combined(parent,final)
    print('Exact combined cold, GameCore and multi-owner GameLoop passed.',flush=True)
    checks = {'movement_stack':qualify_movement(final,proofs['movement_stack'],spans['movement_stack'])}
    print('Exact movement final-minus passed.',flush=True)
    checks['palette_reset'] = qualify_palette(final,proofs['palette_reset'],spans['palette_reset'])
    print('Exact palette final-minus passed.',flush=True)
    checks['mini_stomp_drop'] = qualify_stomp(final,spans['mini_stomp_drop'])
    print('Exact Mini stomp final-minus passed.',flush=True)
    checks['native_body_contact'] = qualify_contact(final,proofs['native_body_contact'],spans['native_body_contact'])
    print('Exact native body-contact final-minus passed.',flush=True)
    stage(output,parent,final,evidence,proofs,checks,full,refs)


if __name__=='__main__':
    main()
