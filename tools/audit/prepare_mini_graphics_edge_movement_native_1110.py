"""Compose exact delivered Mini performance successors and bind a native replay."""

import argparse
import json
from pathlib import Path
import re
import shutil

import check_mini_player_graphics_visibility_1110 as Graphics
import check_mini_player_graphics_visibility_irq_1110 as GraphicsIRQ
import check_native_box_core_1110 as Box
import check_native_enemy_offscreen_edge_1110 as Edge
import check_native_enemy_offscreen_edge_irq_1110 as EdgeIRQ
import prepare_mini_lift_afterbg_audio_bounds_native_1110 as Prior
import prepare_mini_step_scroll_weapon_native_1110 as Route
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import CODE, COOKIE, bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha


BASE,PIN,KERNEL = EdgeIRQ.ROM,EdgeIRQ.PIN,EdgeIRQ.KERNEL
BASE_PROOF = BASE.with_name('proof.json')
DELIVERY = R/'build/mini-lift-afterbg-audio-bounds-delivery-1110/verified-delivery.json'
GRAPHICS = R/'build/mini-player-graphics-visibility-1110/proof.json'
EDGE = R/'build/native-enemy-offscreen-edge-1110/current-proof.json'
BOX = R/'build/native-box-core-1110/proof.json'
PACKET = BASE.parent/'mini'
PRG_END = 16+128*8192


def range_set(rows):
    return {at for row in rows
            for at in range(row['file_offset'],row['file_offset']+len(bytes.fromhex(row['new_hex'])))}


def exact_extent(proof,bank,lo,hi):
    row, = proof['patches']
    assert row['physical_PRG']==bank and row['CPU_half_open']==[lo,hi],row
    assert row['file_offset']==16+bank*8192+(lo&8191)
    assert len(bytes.fromhex(row['new_hex']))==hi-lo


def compose(groups):
    assert set(groups)=={'graphics_visibility','enemy_edge','box_core'}
    parent = bound_rom(BASE,PIN)
    incumbent,delivery = load(BASE_PROOF),load(DELIVERY)
    assert incumbent['passed'] and incumbent['candidate_SHA256']==PIN
    assert delivery['installed'] and delivery['Downloads_launch_verified'] and delivery['IPS_roundtrip']
    assert delivery['ROM_SHA256']==PIN and delivery['composed_proof_SHA256']==sha(BASE_PROOF)
    assert delivery['kernel_SHA256']==incumbent['kernel_SHA256']==sha(KERNEL)==EdgeIRQ.KERNEL_PIN
    assert delivery['native_audio_matches_candidate'] and delivery['active_11_cadence']['no_controller_read']==49
    declared90a8 = bound_rom(Graphics.ROM,Graphics.PIN)
    image = bytearray(parent)
    refs = {BASE,BASE_PROOF,DELIVERY,KERNEL,KERNEL.with_suffix('.lbl'),Graphics.ROM,
            Prior.AUDIO.RUNTIME,Prior.AUDIO.OBSERVER}
    for path,digest_expected in incumbent['bindings'].items():
        assert sha(R/Path(path))==digest_expected,path
    current_rows = [row for rows in incumbent['groups'].values() for row in rows]
    current_bytes = range_set(current_rows)
    for row in current_rows:
        at,data = row['file_offset'],bytes.fromhex(row['new_hex'])
        assert parent[at:at+len(data)]==data,row
    proofs,spans = {},{}
    for role,(path,irq) in groups.items():
        declared = declared90a8 if role=='graphics_visibility' else parent
        isolated,proof,parts = verify_parent(declared,path)
        assert digest(isolated)==proof['expected_memory_only_SHA256']
        if irq is not None:
            verify_interrupts(path,irq,proof)
            refs.add(irq)
        else:
            assert proof['vectors'],(role,path)
        refs.add(path)
        for lo,hi,old,new in parts:
            assert all(hi<=a or lo>=b for existing in spans.values() for a,b,_,_ in existing),(role,lo,hi)
            assert not current_bytes.intersection(range(lo,hi)),(role,lo,hi)
            assert hi<=PRG_END and image[lo:hi]==parent[lo:hi]==old,(role,lo,hi)
            image[lo:hi] = new
        proofs[role],spans[role] = proof,parts
    exact_extent(proofs['graphics_visibility'],1,Graphics.ENTRY,Graphics.END)
    exact_extent(proofs['enemy_edge'],0,Edge.ENTRY,Edge.END)
    assert Graphics.ingress(parent)==Graphics.ingress(declared90a8)
    assert json.loads(json.dumps(Edge.census(parent)))==proofs['enemy_edge']['ingress']
    exact_extent(proofs['box_core'],126,0x9f4e,0x9f90)
    final = bytes(image)
    for parts in spans.values():
        image = Route.remove(image,parts)
    assert image==parent
    assert final[:16]==parent[:16] and final[PRG_END:]==parent[PRG_END:]
    assert final[COOKIE:COOKIE+16]==parent[COOKIE:COOKIE+16]
    for raw in (parent,final):
        verify_payload(raw,KERNEL)
    return parent,final,incumbent,proofs,spans,refs


def native_inputs(parent,final,incumbent):
    meta_path = BASE.with_suffix('.json')
    meta = load(meta_path)
    assert meta['passed'] and meta['candidate_SHA256']==PIN and meta['kernel_SHA256']==sha(KERNEL)
    assert meta['composed_proof_SHA256']==sha(BASE_PROOF)
    assert meta['platform_spawn'] and meta['camera_lifts'] and set(meta['frames'])==set('ABCD')
    art = incumbent['assets']
    assert digest(final[CODE+5120:CODE+7168])==art['metadata_and_art_carrier_SHA256']
    for frame in meta['frames'].values():
        at = CODE+5120+frame['CHR_offset']
        assert final[at:at+32]==bytes.fromhex(frame['bytes'])
    draw = bytes.fromhex(meta['native_draw_bytes'])
    at = Prior.AfterBg.offset(Route.FIRE_BANK,Route.DRAW_SOURCE)
    assert parent[at:at+len(draw)]==final[at:at+len(draw)]==draw
    assert digest(draw)==art['projectile_staged_draw_SHA256']
    # The delivered codec reuses part of the original seven frame-token
    # ranges. Compare current bytes, retaining that exact latest index.
    for row in load(Prior.AUDIO.RUNTIME)['patches']:
        at = row['file_offset']
        end = at+len(bytes.fromhex(row['new_hex']))
        assert final[at:end]==parent[at:end],row
    route,ready_path = PACKET/'controller.lua',PACKET/'ready.json'
    ready = load(ready_path)
    assert ready['prepared'] and not ready['emulated_writes'] and ready['ROM_sha256']==PIN
    assert Path(ready['ROM']).resolve()==BASE.resolve()
    refs = {Path(path).resolve() for path in ready['bindings']}
    assert {route.resolve(),BASE.resolve(),KERNEL.resolve()}<=refs
    for path,h in ready['bindings'].items():
        assert sha(Path(path))==h,path
    text = route.read_text(encoding='utf-8')
    assert text.count(PIN)==text.count(sha(KERNEL))==1
    assert all(token not in text for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                       r'\["bytes"\]=\{([\d,]+)\}',text)
    assert hooks
    for physical,data in hooks:
        off = 16+int(physical)
        expected = bytes(map(int,data.split(',')))
        assert parent[off:off+len(expected)]==final[off:off+len(expected)]==expected,physical
    audio = load(Prior.AUDIO.RUNTIME)
    cfg = Prior.AUDIO.audio_config(final,audio)
    assert Prior.AUDIO.audio_config(parent,audio)==cfg
    assert text.endswith('\n'+cfg+Prior.AUDIO.OBSERVER.read_text(encoding='utf-8'))
    assert text.count("shot('mini-active-1-2');audioAssertFinished();result(true)")==1
    return text.replace(PIN,digest(final)),ready,meta,refs|{ready_path,meta_path}


def qualify(parent,final,spans):
    g_before = Route.remove(final,spans['graphics_visibility'])
    e_before = Route.remove(final,spans['enemy_edge'])
    b_before = Route.remove(final,spans['box_core'])
    assert Graphics.ingress(g_before)==Graphics.ingress(Graphics.ROM.read_bytes())
    assert Edge.census(e_before)==Edge.census(BASE.read_bytes())
    cold,masks = Prior.Lift.A.exact_cold(parent,final,[])
    assert all(all(lo==0x1fe3 and hi==0x1ff0 for lo,hi in row) for row in masks.values())
    # Identical payload and cookie permit the strict full-loop oracle without
    # using any of the old immutable WRAM comparison masks.
    core = check_full_cpu(parent,final,{})
    loop = EdgeIRQ.whole(parent,final)
    assert all(row['min_saved']>0 for row in core)
    print('Exact combined cold, GameCore and multi-owner GameLoop passed.',flush=True)
    checks = {'graphics_visibility':dict(final_minus_SHA256=digest(g_before),
              foreground=Graphics.foreground(g_before,final),vectors=GraphicsIRQ.vectors(g_before,final))}
    print('Exact graphics vector rebind passed.',flush=True)
    checks['enemy_edge'] = dict(final_minus_SHA256=digest(e_before),
        whole_GameLoop=EdgeIRQ.whole(e_before,final),vectors=EdgeIRQ.vectors(e_before,final))
    print('Exact enemy-edge vector rebind passed.',flush=True)
    checks['box_core'] = dict(final_minus_SHA256=digest(b_before),whole_GameLoop=EdgeIRQ.whole(b_before,final),
                             vectors=Box.vectors(b_before,final))
    print('Exact bounding-box vector rebind passed.',flush=True)
    return checks,core,loop,cold


def emit(output,parent,final,incumbent,proofs,refs,checks,core,loop,cold):
    text,ready,meta,packet_refs = native_inputs(parent,final,incumbent)
    pin = digest(final)
    refs.update(Path(mod.__file__).resolve() for mod in (Graphics,GraphicsIRQ,Edge,EdgeIRQ,Box,Prior,Route))
    refs.add(Path(__file__).resolve())
    assert output.is_relative_to(R/'build') and not output.exists()
    output.mkdir()
    proof_path = output/'proof.json'
    report = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=PIN,candidate_SHA256=pin,
                  kernel_SHA256=sha(KERNEL),assets=incumbent['assets'],
                  groups={role:proof['patches'] for role,proof in proofs.items()},component_checks=checks,
                  changed_bytes=sum(a!=b for a,b in zip(parent,final,strict=True)),
                  whole_GameCore=core,whole_GameLoop=loop,cold_Mini=cold,
                  bindings={str(p.resolve()):sha(p) for p in sorted(refs)})
    proof_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    rom = output/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(BASE.with_suffix(suffix))
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=PIN,candidate_SHA256=pin,actual_MiniScene=cold,
                composed_proof_SHA256=sha(proof_path),verification='Private Mini performance replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'mini',rom,text,refs|packet_refs|{proof_path,manifest},expected=pin,
            timeout=ready['timeout'],scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,candidate_SHA256=pin,groups=sorted(proofs),
                          whole_GameCore=core,whole_GameLoop=loop,native_pending=True)),flush=True)


def known_groups():
    return {'graphics_visibility':(GRAPHICS,GRAPHICS.with_name('irq.json')),
            'enemy_edge':(EDGE,None),'box_core':(BOX,None)}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    mode = cli.add_mutually_exclusive_group(required=True)
    mode.add_argument('--census',action='store_true',help='Validate current inputs in memory and write no candidate.')
    mode.add_argument('--qualify-known',action='store_true',help='Run three known groups in memory. Do not emit a candidate.')
    mode.add_argument('--emit',action='store_true',help='Qualify and stage all three declared groups.')
    args = cli.parse_args()
    parent,final,incumbent,proofs,spans,refs = compose(known_groups())
    native_inputs(parent,final,incumbent)
    receipt = dict(passed=True,ROM_written=False,parent_SHA256=PIN,memory_SHA256=digest(final),
                   groups={role:[(lo,hi) for lo,hi,_,_ in parts] for role,parts in spans.items()})
    if not args.census:
        checks,core,loop,cold = qualify(parent,final,spans)
        if args.emit:
            emit(args.output.resolve(),parent,final,incumbent,proofs,refs,checks,core,loop,cold)
            return
        receipt.update(whole_GameCore=core,loop_savings={f"{row['owner']}/{row['scene']}":
                       [sample[0] for sample in row['updates']] for row in loop})
    print(json.dumps(receipt),flush=True)


if __name__=='__main__':
    main()
