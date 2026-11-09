"""Compose the qualified camera and three performance groups, then bind four native routes."""

import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import check_helper_camera_admission_1110_v1 as Camera
import check_helper_camera_irq_1110_v1 as CameraIRQ
import check_native_goomba_edge_1110_v1 as Goomba
import check_native_goomba_edge_irq_1110_v1 as GoombaIRQ
import check_native_relative_offscreen_irq_1110 as RelativeIRQ
import prepare_helper_camera_6bd5_native_1110 as Stage
import prepare_mini_platform_firebar_native_1110 as Mini
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha


BUILD=R/'build'
CURRENT=Stage.CURRENT
PIN=Stage.PIN
CAMERA_BASE=BUILD/'helper-camera-6bd5-native-1110/candidate.nes'
CAMERA_PIN='eef90e7a271131d04428645fda168867a58eb347707a40d6f5ce6f5e09ac6c75'
CAMERA_PROOF=CAMERA_BASE.with_name('camera-rebase-proof.json')
GOOMBA=BUILD/'native-goomba-edge-1110/proof.json'
RELATIVE=BUILD/'native-relative-offscreen-1110/proof.json'
BOX=BUILD/'native-platform-box-reuse-1110/proof.json'
COMPONENTS={'camera':CAMERA_PROOF,'goomba':GOOMBA,'relative':RELATIVE,'platform_box':BOX}
IRQ_RECEIPTS={'goomba':GOOMBA.with_name('irq.json'),'relative':RELATIVE.with_name('irq.json')}
PLATFORM_BOX_SOURCE='check_native_platform_box_reuse_1110_v1'
ROUTES={'mini':(CURRENT.parent/'route',CURRENT),'thomas':(Stage.THOMAS,Stage.HISTORICAL),
        'goku':(Stage.GOKU,Stage.HISTORICAL),'karnov':(Stage.KARNOV,Stage.HISTORICAL)}
PRG_END=1048592


def source_bindings(path):
    entries={(R/Path(file)).resolve():h for file,h in load(path)['bindings'].items()}
    assert entries
    for file,h in entries.items():
        assert sha(file)==h,file
    return {str(file):h for file,h in entries.items()}


def extent(proof):
    result=[]
    for row in proof['patches']:
        bank=row['physical_PRG']
        lo,hi=row.get('CPU_half_open',[row.get('start'),row.get('end_exclusive')])
        assert isinstance(lo,int) and isinstance(hi,int),row
        assert 0x8000<=lo<hi<=0x10000 and (lo&0xe000)==((hi-1)&0xe000),row
        assert row['file_offset']==16+bank*8192+(lo&8191),row
        assert len(bytes.fromhex(row['old_hex']))==hi-lo,row
        result.append((bank,lo,hi))
    return sorted(result)


def checked_box(proof):
    # The platform proof's vector result is embedded in the same immutable receipt.
    vectors=proof['vectors']
    keys=('lag_FF','IRQ','nested_IRQ','poisoned_lag_FF','poisoned_IRQ','poisoned_nested_IRQ',
          'audio_shadow_transports')
    assert all(vectors['cuts'].get(k,0)>0 for k in keys)
    return vectors


def build_image():
    required={CURRENT,CAMERA_BASE,Stage.CURRENT_VECTORS,*COMPONENTS.values(),*IRQ_RECEIPTS.values()}
    missing=sorted(str(path) for path in required if not path.is_file())
    assert not missing,('Wait for the final component proof set',missing)
    raw=bound_rom(CURRENT,PIN)
    incumbent=load(Stage.CURRENT_VECTORS)
    assert incumbent['passed'] and incumbent['candidate_SHA256']==PIN
    source_bindings(Stage.CURRENT_VECTORS)
    candidate=bytearray(raw)
    spans={}
    proofs={}
    for role,path in COMPONENTS.items():
        isolated,proof,parts=verify_parent(raw,path)
        if role=='camera':
            assert isolated==bound_rom(CAMERA_BASE,CAMERA_PIN)
            syms=Camera.P.bundle(raw)
            assert [(lo,hi-lo) for lo,hi,_,_ in parts]==[
                (Camera.TH_CHR+Camera.TH_GATE-0xa000,Camera.TH_END-Camera.TH_GATE),
                (Camera.P.location(syms,'ThCookie'),16),
                (Camera.bank_at(26,Camera.DP_TICK),Camera.DP_END-Camera.DP_TICK),
                (Camera.bank_at(26,Camera.HP_CONFIGURE_RELEASE),3),
            ]
            assert proof['vectors']['owners']==[10,24,34]
            assert proof['Mini_kernel_SHA256']==sha(Mini.NEW_KERNEL)
        elif role=='goomba':
            assert extent(proof)==[(4,0xbead,0xbf33)]
            verify_interrupts(path,IRQ_RECEIPTS[role],proof)
        elif role=='relative':
            assert extent(proof)==[(126,0x8a8c,0x8ace),(126,0x8b1a,0x8b73)]
            verify_interrupts(path,IRQ_RECEIPTS[role],proof)
        else:
            assert extent(proof)==[(0,0xbe83,0xbe84),(26,0xaee9,0xaeeb),(26,0xb04b,0xb07c)]
            checked_box(proof)
        for lo,hi,old,new in parts:
            assert all(hi<=a or lo>=b for prior in spans.values() for a,b,_,_ in prior),(role,lo,hi)
            assert bytes(candidate[lo:hi])==old==raw[lo:hi],(role,lo,hi)
            candidate[lo:hi]=new
        spans[role]=parts
        proofs[role]=proof

    final=bytes(candidate)
    assert raw[:16]==final[:16]
    camera_chr=[(lo,hi) for lo,hi,_,_ in spans['camera'] if lo>=PRG_END]
    assert camera_chr==[(Camera.TH_CHR+Camera.TH_GATE-0xa000,Camera.TH_CHR+Camera.TH_END-0xa000)]
    lo,hi=camera_chr[0]
    assert final[PRG_END:lo]==raw[PRG_END:lo] and final[hi:]==raw[hi:]
    assert final[Mini.CODE:Mini.CODE+7168]==raw[Mini.CODE:Mini.CODE+7168]
    assert final[Mini.COOKIE:Mini.COOKIE+16]==raw[Mini.COOKIE:Mini.COOKIE+16]
    for im in (raw,final):
        verify_payload(im,Mini.NEW_KERNEL)
    return raw,final,proofs,spans


def remove(image,parts):
    before=bytearray(image)
    for lo,hi,old,new in parts:
        assert image[lo:hi]==new,(lo,hi)
        before[lo:hi]=old
    return bytes(before)


def camera_controls(before,after,proof):
    old,new=[Camera.P.bundle(im) for im in (before,after)]
    kernel=after[Camera.TH_CHR:Camera.TH_CHR+6144]+Camera.TH_KERNEL.read_bytes()[6144:]
    state=Camera.TH_STATE.read_bytes()
    offset=Camera.P.location(new,'ThCookie')
    cookie=after[offset:offset+16]
    assert cookie==bytes.fromhex('a70a4001')+sha256(kernel+state).digest()[:12]
    # The frozen source helper needs an old cartridge reader for the old
    # cookie and foreign comparisons. Supply the exact final-minus image.
    saved=Camera.ROM
    Camera.ROM=SimpleNamespace(read_bytes=lambda:before)
    try:
        seed,loader=Camera.thomas_seed(new,kernel,state,cookie)
        cpu=Camera.qualify(new,seed)
        vectors=CameraIRQ.vectors(old,new,kernel,state,cookie)
    finally:
        Camera.ROM=saved
    assert cpu['CPU']==proof['CPU'] and cpu['spawn_relative_range']==[256,287]
    assert loader['previous_cookie_rejected'] and vectors['owners']==[10,24,34]
    return dict(CPU=cpu['CPU'],thomas_loader=loader,vectors=vectors)


def cold_mini(before,after):
    pair=[]
    expected_kernel=Mini.NEW_KERNEL.read_bytes()
    attr=load(Mini.PROJECTION)['exact_runtime_attribute_SHA256']
    for im in (before,after):
        m=Camera.N.fresh(Camera.P.bundle(im))
        Camera.N.put(m,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,
                     DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
        result=Camera.N.invoke(m,'MiniScene')
        cookie=im[Mini.COOKIE:Mini.COOKIE+16]
        assert bytes(m.ram[3][:5120])==expected_kernel and m.ram[2][0x300]==1
        assert all(bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie for bank in (2,3))
        assert bytes(m.ram[2][0x1000:0x1300])==im[Mini.CODE+5120:Mini.CODE+5120+0x300]
        assert digest(m.ram[2][0x1300:0x1400])==attr
        pair.append((result,Stage.Platform.memory(m)))
    assert pair[0]==pair[1]
    return dict(MiniScene=pair[0][0],kernel_SHA256=sha(Mini.NEW_KERNEL),
                cookie=after[Mini.COOKIE:Mini.COOKIE+16].hex(),attribute_SHA256=attr)


def qualify(raw,final,proofs,spans):
    only_camera=bound_rom(CAMERA_BASE,CAMERA_PIN)
    minus={role:remove(final,parts) for role,parts in spans.items()}
    assert remove(remove(remove(final,spans['goomba']),spans['relative']),spans['platform_box'])==only_camera
    results={}
    results['camera']=camera_controls(minus['camera'],final,proofs['camera'])
    print('Camera final-minus vectors',results['camera']['vectors']['cuts'],flush=True)
    results['goomba']=GoombaIRQ.vectors(Goomba.P.bundle(minus['goomba']),Goomba.P.bundle(final))
    print('Goomba final-minus vectors',results['goomba']['cuts'],flush=True)
    results['relative']=RelativeIRQ.vectors(minus['relative'],final)
    print('Relative/offscreen final-minus vectors',results['relative']['cuts'],flush=True)
    box=importlib.import_module(PLATFORM_BOX_SOURCE)
    results['platform_box']=dict(vectors=box.qualify_vectors(minus['platform_box'],final),
                                 resumed_vectors=box.resumed_vectors(minus['platform_box'],final),
                                 whole=box.whole(minus['platform_box'],final))
    print('Platform box final-minus vectors',results['platform_box']['vectors']['cuts'],flush=True)
    for role in results:
        report=results[role].get('vectors',results[role])
        assert all(report['cuts'].get(k,0)>0 for k in ('lag_FF','IRQ','nested_IRQ')),role

    camera_core=check_full_cpu(minus['camera'],final,{})
    assert all(q['min_saved']==q['max_saved']==0 for q in camera_core)
    performance_core=check_full_cpu(only_camera,final,{})
    # Both cartridges already include the delivered direct platform gate.
    # The box whole-loop observer checks that shared baseline with strict
    # memory parity and follows prepared-box scratch lifetime across updates.
    parent_loop=box.whole(raw,final)
    peak=[row for row in parent_loop if row['ordinary']==3 and row['mode']=='normal']
    assert len(peak)==1 and peak[0]['savings'][0]>0,peak
    return dict(final_minus_component_SHA256={role:digest(im) for role,im in minus.items()},
                component_checks=results,cold_Mini=cold_mini(raw,final),
                camera_isolation_GameCore=camera_core,performance_GameCore=performance_core,
                full_parent_GameLoop=parent_loop)


def thomas_history():
    packet,_=ROUTES['thomas']
    ready=packet/'ready.json'
    binding,result,helper=[packet/'capture'/n for n in ('binding.json','result.json','helper-camera.json')]
    b,q,h=[load(path) for path in (binding,result,helper)]
    assert b['exit_code']==0 and b['ready_sha256']==sha(ready)
    assert b['ROM_sha256']==q['ROM_sha256']==h['ROM_sha256']==Stage.HISTORICAL_PIN
    assert q['passed'] and q['reason']=='Full1-1 active1-2' and h['passed']
    assert [row['left_x'] for row in h['placements']]==list(Camera.TH_LEFTS)
    assert all(row['crossed'] and 256<=row['relative_left']<=287 for row in h['placements'])
    gap=q['first_floor_gap']
    assert gap['readback']['input']&8 and gap['airborne']['x']==1374 and gap['landing']['x']==1412
    return {binding,result,helper}


def prepare_routes(output,rom,prepared,receipt,manifest):
    expected=sha(rom)
    for role,(text,refs,ready) in prepared.items():
        root=output/role
        timeout=ready['timeout']
        assert 1<=timeout<=450
        prepare(root,rom,text,refs|{receipt,manifest},expected=expected,timeout=min(timeout,240),
                scope=ready['scope'],allow_interactive=True)
        if timeout>240:
            path=root/'ready.json'
            data=load(path)
            data['timeout']=timeout
            path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')


def group_sources():
    receipts={role:[path] for role,path in COMPONENTS.items()}
    receipts['camera'] += [Stage.SOURCE,Stage.HISTORY]
    for role,path in IRQ_RECEIPTS.items():
        receipts[role].append(path)
    result={}
    for role,paths in receipts.items():
        checked={}
        for path in paths:
            checked.update(source_bindings(path))
        assert any(Path(path).suffix=='.s' for path in checked),role
        result[role]=checked
    return result


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    output=args.output.resolve()
    assert output.is_relative_to(BUILD) and output!=BUILD and not output.exists()
    raw,final,proofs,spans=build_image()
    group_source_bindings=group_sources()
    thomas_refs=thomas_history()
    prepared={}
    for role,(path,previous_rom) in ROUTES.items():
        text,refs,ready=Stage.packet_input(path,previous_rom,final,proofs['camera'],role)
        prepared[role]=(text,refs|({*thomas_refs} if role=='thomas' else set()),ready)
    result=qualify(raw,final,proofs,spans)
    sources={Path(__file__),Path(Camera.__file__),Path(CameraIRQ.__file__),Path(GoombaIRQ.__file__),
             Path(RelativeIRQ.__file__),Path(importlib.import_module(PLATFORM_BOX_SOURCE).__file__),
             Path(Stage.__file__),CURRENT,CAMERA_BASE,Stage.CURRENT_VECTORS,Mini.NEW_KERNEL,
             Camera.TH_KERNEL,Camera.TH_STATE,*COMPONENTS.values(),*IRQ_RECEIPTS.values(),*thomas_refs}
    expected=digest(final)
    receipt_data=dict(passed=True,source_CPU_only=True,native_route_pending=True,parent_SHA256=PIN,
                      camera_base_SHA256=CAMERA_PIN,candidate_SHA256=expected,
                      groups={role:proofs[role]['patches'] for role in proofs},
                      group_source_bindings=group_source_bindings,
                      bindings={str(path.resolve()):sha(path) for path in sources},**result)
    output.mkdir()
    receipt=output/'proof.json'
    receipt.write_text(json.dumps(receipt_data,indent=2)+'\n',encoding='utf-8')
    rom=output/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==expected
    for ext in ('.dbg','.lbl'):
        shutil.copyfile(CURRENT.with_suffix(ext),rom.with_suffix(ext))
    manifest=rom.with_suffix('.json')
    meta=load(CAMERA_BASE.with_suffix('.json'))
    assert meta['candidate_SHA256']==CAMERA_PIN and meta['kernel_SHA256']==sha(Mini.NEW_KERNEL)
    meta.update(parent_SHA256=PIN,candidate_SHA256=expected,camera_base_SHA256=CAMERA_PIN,
                composed_proof_SHA256=sha(receipt),verification='Private native qualification pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare_routes(output,rom,prepared,receipt,manifest)
    print(json.dumps(dict(passed=True,candidate_SHA256=expected,packets=list(prepared),
                          native_route_pending=True)),flush=True)


if __name__=='__main__':
    main()
