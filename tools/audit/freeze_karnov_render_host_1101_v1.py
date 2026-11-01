"""Freeze exact explicit inputs and compact evidence for Karnov rendering."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-host-resource-base-1101-v1';D=O/'render-checkpoint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    proof_names=['terrain-assembly.json','render-art.json','render-CPU-controls.json','shot-motion-CPU-controls.json','terrain-CPU-controls.json','terrain-vectors.json']
    proofs={n:json.loads((O/n).read_text())for n in proof_names};candidate=sha(O/'candidate.nes')
    for n,q in proofs.items():
        assert q['passed']and(n=='render-art.json'or q['ROM_sha256']==candidate)
        for p,h in q['bindings'].items():assert sha(p)==h,p
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(installed)=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
    D.mkdir(exist_ok=True);files={}
    for n in ['build_karnov_cache_host_1101_v1.py','build_karnov_gameplay_host_1101_v1.py','prepare_karnov_host_art_1101_v1.py','check_karnov_host_render_1101_v1.py','check_karnov_shot_motion_1101_v1.py','check_karnov_terrain_host_1101_v1.py','check_karnov_terrain_vectors_1101_v1.py','freeze_karnov_render_host_1101_v1.py']:files['tools/audit/'+n]=R/'tools/audit'/n
    for n in ['karnov_cache_kernel_1101_v1.s','karnov_cache_resident_1101_v1.inc','karnov_host_terrain_1101_v1.inc','karnov_host_render_1101_v1.inc']:files['tools/reference/'+n]=R/'tools/reference'/n
    for n in ['entrypoint.s','character_select.s','cf_menu_body.inc','kr-kernel.s','kr-resident.inc','kr-terrain.inc','kr-render.inc','kr-host-actor.inc','kr-images.s','kr-cookie.bin','kr-pose-meta.bin','kr-body.chr','kr-shot-tiles.bin','candidate.cfg','main-build.json','link.json','terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json',*proof_names]:files['host/'+n]=O/n
    for root,names in [('karnov-original-source-1101-v1',['portable_actor.inc','portable_dispatch.inc']),('karnov-original-weapons-1101-v1',['portable_weapon.inc','portable_clear.inc'])]:
        for n in names:files['original-source/'+n]=R/'build'/root/'source'/n
    for n in ['art-controls.json','body.chr']:files['original-art/'+n]=R/'build/karnov-original-art-1101-v1'/n
    manifest={n:dict(sha256=sha(p),bytes=p.stat().st_size,original=str(p.resolve()))for n,p in files.items()}
    with zipfile.ZipFile(D/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in files.items():z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert(D/'source-proof.zip').stat().st_size<200000
    (D/'sprite-preview.png').write_bytes((O/'render-preview.png').read_bytes())
    a,art,r,s,t,v=[proofs[n]for n in proof_names]
    result=dict(passed=True,progress_only=True,installed=False,admitted=False,native=False,private_candidate=candidate,installed_nightly=sha(installed),playable=85,total_menu_identities=90,source_proof=dict(file='source-proof.zip',sha256=sha(D/'source-proof.zip'),bytes=(D/'source-proof.zip').stat().st_size,members=len(files)+1),preview=dict(file='sprite-preview.png',sha256=sha(D/'sprite-preview.png'),kind='CPU-rendered source-pixel preview; not an emulator capture'),resident_bytes=a['resident_bytes'],kernel_bytes=a['kernel_bytes'],services=a['implemented_services'],body_cases=r['body_cases'],shot_cases=r['shot_cases'],OAM_capacity_rotation_cases=r['capacity_rotation_cases'],native_palette_NMI=r['actual_native_palette_NMI'],source_actor_projectile_updates=s['actor_projectile_updates'],source_engine_executions=s['source_engine_executions'],native_camera_updates=t['native_camera_updates'],real_interrupt_cuts=v['real_interrupt_cuts'],minimum_SP=v['minimum_SP'],draw_cycle_range=r['draw_cycle_range'],
        next=['Fund the real shared dispatch and scene/menu hooks without changing any85 legal existing identities.','Connect original projectiles to native enemies, destructible blocks, effects and score.','Recover source health, earned upgrades/options and original audio.','Use native controller playtests for1-1/shortcut/powerups before admission or nightly replacement.'],
        limits=['No shared Main/terrain/menu hook is enabled; Karnov remains COMING SOON in the installed85 build.','Body/shot contexts and upgrades are CPU fixtures, not earned gameplay progression.','Normal native NMI palette writing executes in a model with NES palette mirroring; no raster/video claim.','Contact support and source sound/scene/terrain callbacks remain declared unit boundaries.','The mutable root contains historical receipts for older hashes. Use the current six receipt names in this packet.'],
        retained_baseline='docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1',previous_component='docs/qa/checkpoints/2026-11-01/karnov-terrain-component-v1')
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (D/'README.md').write_text(f'''# Karnov rendering and projectile motion — private progress

Karnov is still COMING SOON in the installed 85-character nightly. This component
adds real body/shot rendering and original actor-to-weapon updates. It is not a
native stage clear, combat/upgrade completion, or release admission.

The {a['kernel_bytes']}-byte kernel includes all 64 original facing/pose packets,
kept in their native OAM priority order. Five CHR pages remain sufficient: seven
original projectile patterns occupy verified unused pairs in body page 3.
Even projectile tiles use P0 window 3; world windows 4..7 are preserved.
The 1345-byte pose metadata is copied to conditional C2/D000, so native farcalls
can read it while A3 is unmapped. Hurt blinking keeps the actual source CHR page.

Original single/double/triple/boomerang updates run after the source actor.
Existing shots rebase before spawning at a new camera, and drawing accounts for
the native scroll that occurs after movement. Left-edge underflow never wraps a
projectile to the right. Palette commands write only 3F11..13, preserving the
NES universal background color at mirrored 3F00/10.

Evidence: 256 exact original body contexts, 768 shot contexts, 24 OAM capacity/
rotation cases, 644 coherent actor/projectile comparisons, 840 native block-query
comparisons, 420 native camera updates, and {v['real_interrupt_cuts']} real host
interrupt cuts. Two executions of the real normal-NMI palette writer verify
default/injured sprite colors and an unchanged universal background color.

Draw cost in these CPU fixtures ranges from {r['draw_cycle_range'][0]} to
{r['draw_cycle_range'][1]} cycles. That is not a whole-game 60Hz claim.
sprite-preview.png is one bounded CPU-rendered pixel preview, not native footage.

The ZIP lists exact source/assets and compact receipts; it contains no ROM,
object/debug images, video or capture forest. Existing game linker objects and
the original donor are retained external inputs, not recursively archived here.
''',encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__':main()
