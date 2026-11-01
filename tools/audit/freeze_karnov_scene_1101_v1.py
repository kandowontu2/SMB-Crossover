"""Freeze bounded scene/Main integration evidence, without menu admission."""
from pathlib import Path
import hashlib,json,zipfile
from build_storage_guard_v1 import preflight
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-host-resource-base-1101-v1';D=O/'scene-checkpoint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    preflight(private_root=O,reserved_bytes=350000,reserved_files=4,fresh=True)
    names=['terrain-assembly.json','scene-CPU-controls.json','ingress-CPU-controls.json','render-art.json','terrain-CPU-controls.json','render-CPU-controls.json','shot-motion-CPU-controls.json','terrain-vectors.json']
    proofs={n:json.loads((O/n).read_text())for n in names};candidate=sha(O/'candidate.nes')
    for n,q in proofs.items():
        assert q['passed']and(n=='render-art.json'or q['ROM_sha256']==candidate)
        for p,h in q['bindings'].items():assert sha(p)==h,p
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(nightly)=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
    files={}
    for n in ['build_karnov_cache_host_1101_v1.py','build_karnov_gameplay_host_1101_v1.py','prepare_karnov_host_art_1101_v1.py','prepare_karnov_ingress_1101_v1.py','prepare_karnov_scene_1101_v1.py','check_karnov_scene_1101_v1.py','check_karnov_ingress_1101_v1.py','check_karnov_terrain_host_1101_v1.py','check_karnov_host_render_1101_v1.py','check_karnov_shot_motion_1101_v1.py','check_karnov_terrain_vectors_1101_v1.py','freeze_karnov_scene_1101_v1.py']:
        files['tools/audit/'+n]=R/'tools/audit'/n
    for n in ['karnov_cache_kernel_1101_v1.s','karnov_cache_resident_1101_v1.inc','karnov_host_terrain_1101_v1.inc','karnov_host_render_1101_v1.inc','karnov_host_scene_1101_v1.inc']:files['tools/reference/'+n]=R/'tools/reference'/n
    for n in ['entrypoint.s','character_select.s','cf_menu_body.inc','kr-kernel.s','kr-resident.inc','kr-terrain.inc','kr-render.inc','kr-host-actor.inc','kr-images.s','kr-cookie.bin','kr-pose-meta.bin','kr-body.chr','kr-shot-tiles.bin','megaman_physics.s','union.s','screen_render.s','hot_render_gate.s','candidate.cfg','main-build.json','link.json','terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json','ingress-union-build.json',*names]:files['host/'+n]=O/n
    for root,part in [('karnov-original-source-1101-v1',['portable_actor.inc','portable_dispatch.inc']),('karnov-original-weapons-1101-v1',['portable_weapon.inc','portable_clear.inc'])]:
        for n in part:files['original-source/'+n]=R/'build'/root/'source'/n
    for n,p in [('megaman_physics.s',R/'build/bt-ready-menu-1031-v2/joint/src/megaman_physics.s'),('union.s',R/'build/hogan-thomas-current/union.s'),('union-build.json',R/'build/hogan-thomas-current/union-build.json'),('screen_render.s',R/'build/hogan-thomas-current/src/screen_render.s'),('hot_render_gate.s',R/'build/hogan-thomas-current/src/hot_render_gate.s')]:files['parent-source/'+n]=p
    manifest={n:dict(sha256=sha(p),bytes=p.stat().st_size,original=str(p.resolve()))for n,p in files.items()};D.mkdir(exist_ok=True)
    with zipfile.ZipFile(D/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in files.items():z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert(D/'source-proof.zip').stat().st_size<300000
    a,s,i,r,t,v=[proofs[n]for n in ['terrain-assembly.json','scene-CPU-controls.json','ingress-CPU-controls.json','render-CPU-controls.json','terrain-CPU-controls.json','terrain-vectors.json']]
    assert s['actual_Main_updates']==120 and s['existing_identity_scene_pairs']==85 and s['foreign_post_BG_extra_cycles']==[4]
    result=dict(passed=True,progress_only=True,native=False,installed=False,menu_admitted=False,private_candidate=candidate,installed_nightly=sha(nightly),playable=85,total_menu_identities=90,source_proof=dict(file='source-proof.zip',sha256=sha(D/'source-proof.zip'),bytes=(D/'source-proof.zip').stat().st_size,members=len(files)+1),resident_bytes=a['resident_bytes'],kernel_bytes=a['kernel_bytes'],implemented_services=a['implemented_services'],runtime_ID=34,existing_identity_scene_pairs=s['existing_identity_scene_pairs'],existing_post_BG_pairs=s['existing_post_BG_pairs'],foreign_post_BG_extra_cycles=s['foreign_post_BG_extra_cycles'],actual_parser_updates=s['actual_parser_updates'],actual_Main_updates=s['actual_Main_updates'],completed_normal_NMIs=s['completed_normal_NMIs'],actual_Main_ISR_cuts=s['actual_Main_ISR_cuts'],minimum_Main_ISR_SP=s['minimum_Main_ISR_SP'],draw_cycle_range=r['draw_cycle_range'],Main_runtime_assignment_fixture=True,area_preserves_gear_stock_health=True,new_life_resets_gear=True,earned_extra_life_keeps_movement=True,apex_zero_step_fall_fixed=True,route_pairs=i['route_pairs'],unchanged_public_union_exports=i['legacy_union_exports_unchanged'],ingress_ISR_cuts=i['real_ISR_cuts'],component_ISR_cuts=v['real_interrupt_cuts'],minimum_component_SP=v['minimum_SP'],body_cases=r['body_cases'],shot_cases=r['shot_cases'],terrain_query_pairs=t['query_differentials'],landing_ceiling_ledge_boundaries=t['landing_ceiling_ledge_boundaries'],native_camera_updates=t['native_camera_updates'],previous_component='docs/qa/checkpoints/2026-11-01/karnov-ingress-component-v1',storage=preflight(fresh=True),next=['Add ROM-only cold menu portrait/colors/names and selected-alternate remap, audit every direct runtime-ID table before enabling Start.','Connect original projectiles to native blocks/enemies, injury/health, earned Super Fireball/options, original audio and native stomp bounce.','Run bounded native controller tests for normal1-1, shortcut and every powerup before user-facing admission/nightly replacement.'],limits=['Karnov is still COMING SOON in the installed85 build. No nightly update or playable86 claim.','The actual parser/Main test assigns raw34 once after starting old-menu Rygar; it does not prove normal menu admission.','Life/area stock and gear preservation uses explicit original-state fixtures; upgrades are not earned in this test.','All simulation is CPU/mapper/PPU queue modeling. No native emulator/controller/raster/full-stage/audio qualification.','Older component scopes describing absent shared hooks are historical or explicitly unexercised boundaries. Use these eight exact-hash receipts.'])
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (D/'README.md').write_text('''# Karnov scene/Main integration — private progress

The actual InitScreen consumer now calls a ROM29 wrapper. The complete old
Wf/Bw/S2/Th scene chain runs first, with exactly the same old-owner outputs.
Only selected Karnov then cold-loads the guarded code and constructs its source
state. All 85 admitted menu identities retain their old scene RAM, registers,
flags, maps, CHR latches and loader reads in the comparison cohort.

Source gear, option stock and health survive an area transfer in the same life;
input/action/flight counters and projectiles reset. A lost life or player change
constructs fresh state. An earned extra life no longer fails the movement guard.
These progression fields are explicit fixtures, not controller-earned items.

The real post-BG callback now routes runtime34 directly to its guarded service.
The selector consumes existing fixed-size HotRender padding. It adds four CPU
cycles for each existing owner, preserving their original child/AXYP/SP across
255 comparisons; it adds no extra old-owner farcall or RAM-cache load.

The first level-engine run exposed a jump-apex freeze: a zero-pixel falling step
was misclassified as a ceiling collision, resetting gravity indefinitely. The
fix excludes an already-falling source state from that reset. Four added contact
boundaries and the real 120-Main jump/landing test cover the correction.

For that test, Rygar starts through the real existing menu, then raw34 is assigned
once as an explicit integration fixture. The normal native parser, InitScreen,
entrance, player controller, source movement/weapon updates, PlayerBGCollision,
post-terrain reconciliation, draw and NMI run afterward. This is CPU/mapper
execution, not a native emulator replay, and Karnov is not yet selectable.

Live Main interrupt checks also exposed a tight stack margin. Drawing now calls
its shared graphics body without nesting a second complete register save. The
post-terrain and bounding-box leaves save only the registers they actually use.
Their external register/scratch contracts remain covered by the same checks;
the Main ISR test now requires twelve bytes of reserve above the SMC operands.
Movement saves A/X/Y/P and the foreground pointer pair, keeping R2..R7 untouched.
Future native combat/audio/terrain callback leaves must preserve those scratch
bytes and recheck the live Main stack; do not spend the reserve on nested saves.

Shared dispatch, exact water arithmetic, source body/shot pixels, projectile
motion, native block-query ABI and real interrupt cuts repeat on this candidate.
Cold portraits/names/menu resolution, direct-ID table closure, native combat,
health, earned options/upgrades, original audio and native controller tests remain.
The Downloads nightly stays at the tested 85-character build.

The ZIP contains exact sources/assets and compact receipts, excluding ROM,
object/debug binaries and videos/capture forests. Old linker objects and donor
ROMs remain external inputs. No recursive historical source graph was copied.
''',encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__':main()
