"""Preserve compact exact-source evidence for the shared Karnov ingress."""
from pathlib import Path
import hashlib,json,zipfile
from build_storage_guard_v1 import preflight
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-host-resource-base-1101-v1';D=O/'ingress-checkpoint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    preflight(private_root=O,reserved_bytes=300000,reserved_files=4,fresh=True)
    names=['terrain-assembly.json','ingress-CPU-controls.json','render-art.json','terrain-CPU-controls.json','render-CPU-controls.json','shot-motion-CPU-controls.json','terrain-vectors.json']
    proofs={n:json.loads((O/n).read_text())for n in names};candidate=sha(O/'candidate.nes')
    for n,q in proofs.items():
        assert q['passed']and(n=='render-art.json'or q['ROM_sha256']==candidate)
        for p,h in q['bindings'].items():assert sha(p)==h,p
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(nightly)=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
    files={}
    for n in ['build_karnov_cache_host_1101_v1.py','build_karnov_gameplay_host_1101_v1.py','prepare_karnov_host_art_1101_v1.py','prepare_karnov_ingress_1101_v1.py','check_karnov_ingress_1101_v1.py','check_karnov_terrain_host_1101_v1.py','check_karnov_host_render_1101_v1.py','check_karnov_shot_motion_1101_v1.py','check_karnov_terrain_vectors_1101_v1.py','freeze_karnov_ingress_1101_v1.py']:
        files['tools/audit/'+n]=R/'tools/audit'/n
    for n in ['karnov_cache_kernel_1101_v1.s','karnov_cache_resident_1101_v1.inc','karnov_host_terrain_1101_v1.inc','karnov_host_render_1101_v1.inc']:files['tools/reference/'+n]=R/'tools/reference'/n
    for n in ['entrypoint.s','character_select.s','cf_menu_body.inc','kr-kernel.s','kr-resident.inc','kr-terrain.inc','kr-render.inc','kr-host-actor.inc','kr-images.s','kr-cookie.bin','kr-pose-meta.bin','kr-body.chr','kr-shot-tiles.bin','megaman_physics.s','union.s','candidate.cfg','main-build.json','link.json','terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json','ingress-union-build.json',*names]:files['host/'+n]=O/n
    for root,part in [('karnov-original-source-1101-v1',['portable_actor.inc','portable_dispatch.inc']),('karnov-original-weapons-1101-v1',['portable_weapon.inc','portable_clear.inc'])]:
        for n in part:files['original-source/'+n]=R/'build'/root/'source'/n
    for n,p in [('megaman_physics.s',R/'build/bt-ready-menu-1031-v2/joint/src/megaman_physics.s'),('union.s',R/'build/hogan-thomas-current/union.s'),('union-build.json',R/'build/hogan-thomas-current/union-build.json')]:files['parent-source/'+n]=p
    manifest={n:dict(sha256=sha(p),bytes=p.stat().st_size,original=str(p.resolve()))for n,p in files.items()}
    D.mkdir(exist_ok=True)
    with zipfile.ZipFile(D/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in files.items():z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert(D/'source-proof.zip').stat().st_size<250000
    a,i,r,t,v=[proofs[n]for n in ['terrain-assembly.json','ingress-CPU-controls.json','render-CPU-controls.json','terrain-CPU-controls.json','terrain-vectors.json']]
    result=dict(passed=True,progress_only=True,native=False,installed=False,menu_admitted=False,private_candidate=candidate,installed_nightly=sha(nightly),playable=85,total_menu_identities=90,source_proof=dict(file='source-proof.zip',sha256=sha(D/'source-proof.zip'),bytes=(D/'source-proof.zip').stat().st_size,members=len(files)+1),resident_bytes=a['resident_bytes'],kernel_bytes=a['kernel_bytes'],implemented_services=a['implemented_services'],runtime_character_ID=34,service_veneer_address='B400',original_water_table='B38E',relocated_water_table=i['relocated_table_address'],exact_table_consumers=i['exact_indexed_consumers'],indexed_read_pairs=i['indexed_read_pairs'],full_math_pairs=i['full_math_pairs'],unchanged_public_union_exports=i['legacy_union_exports_unchanged'],route_pairs=i['route_pairs'],admitted_existing_identities=i['admitted_menu_identities'],ingress_ISR_cuts=i['real_ISR_cuts'],component_ISR_cuts=v['real_interrupt_cuts'],minimum_component_SP=v['minimum_SP'],body_cases=r['body_cases'],shot_cases=r['shot_cases'],source_step_comparisons=t['source_step_comparisons'],native_camera_updates=t['native_camera_updates'],storage=preflight(fresh=True),previous_component='docs/qa/checkpoints/2026-11-01/karnov-render-component-v1',next=['Wire the original real InitScreen consumer (screen_render.s) through a ROM-resident Karnov scene wrapper, preserving the whole old Wf/Bw/S2/Th scene chain.','Split new-life construction from area reconciliation to preserve earned options; verify actual Main with raw34.','Add ROM-only cold portrait/colors/names and menu remap; audit every direct-ID table before enabling Start.','Implement native combat/stomp reconciliation, health, earned upgrades/options and original audio.','Use bounded native controller playtests before menu admission or nightly replacement.'],limits=['Actual shared36-entry ingress is now present, but the menu and scene loader do not call it for Karnov yet.','No actual new-character Main/gameplay/menu qualification or native raster/playthrough claim.','Existing component scripts still use their deliberate raw7+alt1 private fixtures; their older no-shared-ingress wording describes the unexercised boundary, not removal of the new ingress.','No combat, earned-upgrade, health, native audio or nightly change is claimed.'])
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (D/'README.md').write_text('''# Karnov shared ingress — private progress

The genuine 36-entry shared dispatch can now route runtime character 34 to
Karnov's guarded services at bank 29/B400. All 54 old public union entry addresses
remain exact. The installed nightly remains the tested 85-character build.

This is an assembled source integration, with 51,408 route comparisons including
all 256 raw IDs and all 85 actual admitted menu identities. The new route keeps
the original caller registers, flags and real query Y. No existing ID is aliased
or removed. Existing public endpoints and all final-object imports are checked.

Space comes from relocating MarioWaterCoast's exact 256-byte ProductHi table
within the same physical bank, from B38E to BA8E. The three genuine indexed-read
operands are the only arithmetic-code changes. All 256 indices through each
consumer preserve their ABI and page-crossing cycles. 2,056 full 24-bit multiply
pairs match the original output, flags, registers, stack and cycles.
The genuine B400 JMP rows occupy the old table extent; no arbitrary free-space
claim or replacement of the arithmetic/MMC5 multiplier is involved.

254 real IRQ/NMI cuts cover the shared transport and relocated consumers. The
same candidate also repeats the movement, native queries, body/shot pixels,
original projectile motion, camera and 436 component interrupt checks.
These are CPU/mapper unit checks; native raster cadence is not simulated.

Menu resolution, ROM-only cold portraits, scene loading, combat, health, earned
upgrades/options, original audio and native controller tests remain. Karnov is
still COMING SOON in Downloads. The exact source ZIP excludes ROMs, objects,
debug images and capture forests; retained linker inputs remain external.
''',encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__':main()
