"""Make one compact explicit-file source/proof packet for Karnov's host cache."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'build/karnov-host-resource-base-1101-v1';D=O/'guarded-checkpoint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    names=['cache-assembly.json','cache-CPU-controls.json','cache-vectors.json','kernel-CPU-controls.json']
    proofs={n:json.loads((O/n).read_text())for n in names}
    candidate=sha(O/'candidate.nes');assert all(q['passed']and q['ROM_sha256']==candidate for q in proofs.values())
    for q in proofs.values():
        for p,h in q['bindings'].items():assert sha(p)==h,p
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(installed)=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
    D.mkdir(exist_ok=True)
    files={}
    for prefix,names2 in {
        'tools/audit/':['build_karnov_cache_host_1101_v1.py','check_karnov_cache_host_1101_v1.py','check_karnov_cache_vectors_1101_v1.py','check_karnov_host_kernel_1101_v1.py','freeze_karnov_cache_host_1101_v1.py'],
        'tools/reference/':['karnov_cache_kernel_1101_v1.s','karnov_cache_resident_1101_v1.inc'],
    }.items():
        for n in names2:files[prefix+n]=R/prefix/n
    for n in ['entrypoint.s','character_select.s','cf_menu_body.inc','kr-kernel.s','kr-resident.inc','kr-images.s','kr-cookie.bin','candidate.cfg','cache-main-build.json','cache-kernel-build.json','cache-first-link.json','cache-images-build.json','cache-final-link.json',*names]:files['host/'+n]=O/n
    for directory,names2 in [
        ('karnov-original-source-1101-v1',['portable_actor.inc','portable_dispatch.inc']),
        ('karnov-original-weapons-1101-v1',['portable_weapon.inc','portable_clear.inc'])]:
        for n in names2:files['original-source/'+n]=R/'build'/directory/'source'/n
    files['art/body.chr']=R/'build/karnov-original-art-1101-v1/body.chr'
    manifest={n:dict(sha256=sha(p),bytes=p.stat().st_size,original=str(p.resolve()))for n,p in files.items()}
    with zipfile.ZipFile(D/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in files.items():z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert(D/'source-proof.zip').stat().st_size<200000
    result=dict(passed=True,progress_only=True,installed=False,menu_admitted=False,private_candidate=candidate,
        installed_nightly=sha(installed),playable=85,total_menu_identities=90,
        source_proof=dict(file='source-proof.zip',sha256=sha(D/'source-proof.zip'),bytes=(D/'source-proof.zip').stat().st_size,members=len(files)+1),
        resident_bytes=proofs[names[0]]['resident_bytes'],kernel_bytes=proofs[names[0]]['kernel_bytes'],
        cookie_checks=proofs[names[1]]['cookie_checks'],dispatch_cases=proofs[names[1]]['dispatch_cases'],
        real_vector_cuts=proofs[names[2]]['real_vector_cuts'],normal_paused_NMI=proofs[names[2]]['normal_paused_NMI'],
        source_engine_executions=proofs[names[3]]['engine_executions'],
        next=['Implement real SMB terrain/camera adapters and reconcile source viewport clamps.','Render source body/projectile packets with actual CHR/palette publication.','Recover native injury, options/pickups and audio; connect host enemies and powerups.','Fund selected-only shared ingress and cold scene lifecycle, preserve85foreign routes.','Cold native controller playtests before menu admission or nightly installation.'],
        scope='Original source routines linked at A000 in conditional RAM3, private state C000 in RAM2, pointer at actual R0/R1=3/4. ROM resident loader reads original code from CHR399..406 and verifies both full 16-byte headers. All 36 unimplemented gameplay rows reject. No playable 86th character, native gameplay or nightly replacement.',
        original_component='docs/qa/checkpoints/2026-11-01/karnov-original-component-v1',
        retained_baseline='docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1')
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (D/'README.md').write_text(f'''# Karnov guarded host cache — source checkpoint

Progress only. The Downloads nightly remains the tested 85-character build.
The private candidate does not admit Karnov from the menu; all 36 cache service
rows explicitly reject until actual gameplay adapters exist.

The source/proof ZIP contains only the explicit current inputs and compact
receipts listed in files.json. It contains no ROM, object/debug image, capture
forest, or recursively restored dependency tree. The full game linker still
uses current 85-character objects from the retained baseline; this is a component packet,
not a standalone clean-build release.

The loader occupies {proofs[names[0]]['resident_bytes']} bytes of real bank 29 menu padding.
Its {proofs[names[0]]['kernel_bytes']}-byte original actor/weapon kernel runs from
conditional RAM3/A000 with conditional RAM2/C000 state and the real foreground
R0/R1 at 3/4. It leaves NMI scratch 0..2 alone. CHR399..406 stores the 8KB
kernel; 407..411 holds the five original body pages.
All existing runtime symbols and ROM bytes outside the granted ranges remain
unchanged. Compile-time anonymous repeat names/farcall count may differ.

Verification: 12 forced-blank load combinations, 13 negative cases, 2112 full-cookie
checks, 148 typed dispatch cases, 33 retirement cases, {proofs[names[2]]['real_vector_cuts']} real host NMI/IRQ cuts,
12 normal/paused NMI cases, and 7808 donor-versus-linked CPU executions. Raster IRQ
intentionally changes the HUD CHR window; those actual ISR writes are recorded.
No native raster, terrain, earned powerup, sound or full-stage claim is made.

Active private output is build/karnov-host-resource-base-1101-v1. It remains
unqualified/mutable for the gameplay integration; this compact snapshot is
the immutable evidence for this stage. See handoff.json for the next work.
''',encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__':main()
