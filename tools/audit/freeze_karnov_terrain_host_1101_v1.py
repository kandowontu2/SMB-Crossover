"""Save the explicit current Karnov terrain component and bounded CPU proofs."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-host-resource-base-1101-v1';D=O/'terrain-checkpoint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    proofs={n:json.loads((O/n).read_text())for n in ['terrain-assembly.json','terrain-CPU-controls.json','terrain-vectors.json']}
    candidate=sha(O/'candidate.nes')
    for q in proofs.values():
        assert q['passed']and q['ROM_sha256']==candidate
        for p,h in q['bindings'].items():assert sha(p)==h,p
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(installed)=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
    D.mkdir(exist_ok=True);files={}
    for n in ['build_karnov_cache_host_1101_v1.py','build_karnov_gameplay_host_1101_v1.py','check_karnov_terrain_host_1101_v1.py','check_karnov_terrain_vectors_1101_v1.py','freeze_karnov_terrain_host_1101_v1.py']:files['tools/audit/'+n]=R/'tools/audit'/n
    for n in ['karnov_cache_kernel_1101_v1.s','karnov_cache_resident_1101_v1.inc','karnov_host_terrain_1101_v1.inc']:files['tools/reference/'+n]=R/'tools/reference'/n
    for n in ['entrypoint.s','character_select.s','cf_menu_body.inc','kr-kernel.s','kr-resident.inc','kr-terrain.inc','kr-host-actor.inc','kr-images.s','kr-cookie.bin','candidate.cfg','main-build.json','link.json','terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json',*proofs]:files['host/'+n]=O/n
    for root,names in [('karnov-original-source-1101-v1',['portable_dispatch.inc','portable_actor.inc']),('karnov-original-weapons-1101-v1',['portable_weapon.inc','portable_clear.inc'])]:
        for n in names:files['original-source/'+n]=R/'build'/root/'source'/n
    files['art/body.chr']=R/'build/karnov-original-art-1101-v1/body.chr'
    manifest={n:dict(sha256=sha(p),bytes=p.stat().st_size,original=str(p.resolve()))for n,p in files.items()}
    with zipfile.ZipFile(D/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in files.items():z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert(D/'source-proof.zip').stat().st_size<200000
    a,t,v=[proofs[n]for n in ['terrain-assembly.json','terrain-CPU-controls.json','terrain-vectors.json']]
    result=dict(passed=True,progress_only=True,installed=False,admitted=False,native=False,private_candidate=candidate,installed_nightly=sha(installed),playable=85,total_menu_identities=90,source_proof=dict(file='source-proof.zip',sha256=sha(D/'source-proof.zip'),bytes=(D/'source-proof.zip').stat().st_size,members=len(files)+1),resident_bytes=a['resident_bytes'],kernel_bytes=a['kernel_bytes'],services=a['implemented_services'],cookie_checks=t['cookie_checks'],corrupt_or_foreign_route_rejections=t['corrupt_or_foreign_route_rejections'],query_differentials=t['query_differentials'],source_step_comparisons=t['source_step_comparisons'],contact_boundaries=t['landing_ceiling_ledge_boundaries'],native_camera_updates=t['native_camera_updates'],maximum_camera=t['maximum_camera'],real_interrupt_cuts=v['real_interrupt_cuts'],minimum_SP=v['minimum_SP'],
        next=['Implement body/projectile CHR publication and original six-cell body packets.','Connect original nine projectile slots to native blocks/enemies, camera rebasing, hit counts and effects.','Recover damage, health, earned options/upgrades and original audio.','Fund selected-only shared ingress and scene/menu hooks; do not change legal existing character routes.','Verify native 1-1, shortcut, pickups, stomps/bounces, pipes/flagpole and camera before admission.'],
        limits=['No shared Main/terrain ingress or character-menu admission exists yet.','Support and post-collision inputs in the CPU tests are declared fixtures. Actual ScrollHandler and ordinary SMB block-query routines execute.','Only source FA06 viewport clamps redirect to FA5C facing update; original land movement/jump/fall instructions and tables are retained.','Native enemy bounce, full collision worker, weapons, health/options, music and rendering remain unfinished.','The active output is mutable. Older cache receipts there refer to previous hashes; use immutable checkpoint packets for those stages.'],
        retained_baseline='docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1',original_component='docs/qa/checkpoints/2026-11-01/karnov-original-component-v1',prior_cache='docs/qa/checkpoints/2026-11-01/karnov-guarded-cache-v1')
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (D/'README.md').write_text(f'''# Karnov terrain component — private progress

The installed nightly remains the tested 85-character build. Karnov is still
COMING SOON. This packet does not claim a native stage clear or playable admission.

The {a['kernel_bytes']}-byte kernel adds cold construction, source movement export,
head/side queries, body geometry, easy/hard stomp policy, landing/ceiling/ledge
reconciliation and the native collision profile selector. The {a['resident_bytes']}-byte
ROM resident now has genuine 36 JMP rows: caller Y is the terrain probe coordinate,
not the service index. Child A/X/Y/flags and scratch return live through the
guarded dispatcher, while mapper and SMC operands are restored.

The native Mega profile supplies the same (2,32)/(13,32) foot probes. Custom
standing/crouching probes query block buffers without moving the player anchor.
Source FA06 screen clamps redirect to the original FA5C facing update because
SMB owns screen bounds. Original land physics instructions/tables remain intact.

Evidence: 2112 cookie checks, 1188 corrupt/foreign route rejections, 840 comparisons
with actual SMB queries, 64 HUD head-extent cases, 11 declared contact boundaries,
1140 original source-step comparisons, 420 updates through the real ScrollHandler
without horizontal drift, and {v['real_interrupt_cuts']} actual host NMI/IRQ cuts.
Ordinary and boot jump rises remain 48 and 88 pixels across world-page wraps.

Terrain support/contact inputs are explicit unit fixtures. Shared gameplay/menu
hooks, full native BG collision, rendering, combat, health, options/pickups,
original music and controller playthroughs remain required. See handoff.json.

The ZIP contains only listed source inputs and compact receipts, without ROM,
objects, debug images or captures. It is a component packet using retained
current-game linker inputs, not a standalone clean-build release.
''',encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__':main()
