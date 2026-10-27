"""Publish a small review checkpoint, excluding cartridge/audio/raw captures."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C=D/'robot-base-palette-candidate-v2';P=D/'robot-cold-palette-candidate-v2'
T=R/'docs/qa/checkpoints/2026-10-26/robot-base-palette-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    assert not T.exists();T.mkdir(parents=True)
    ready=C/'ready-v1'
    assert sha(ready/'readiness.json')=='d48e101f291439971146878107832bab23bdbc1fc534c2138ef9460e5406bb0d'
    for f,h in json.loads((ready/'bindings.json').read_text()).items():assert sha(f)==h,f
    copied={}
    def copy(f,rel):
        dst=T/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
        assert sha(dst)==sha(f);copied[rel]=dict(source=str(f),sha256=sha(f),bytes=f.stat().st_size)
    baseline=D/'root-current-roster-composition-v1/source'
    changed=['smb1base-mmc5-expanded.cfg','src/entrypoint.s','src/x5_palette.s','src/robot_cold_palette_cache.s']
    patch=[]
    for rel in changed:
        f=C/'source'/rel;copy(f,'source/'+rel)
        prior=baseline/rel
        patch+=list(difflib.unified_diff(prior.read_text().splitlines(True)if prior.exists()else[],f.read_text().splitlines(True),fromfile='3b/'+rel,tofile='proposed/'+rel))
    (T/'source-vs-installed3b.patch').write_text(''.join(patch))
    for f,rel in[
        (P/'proof.json','proofs/cold0ba-layout.json'),(P/'cpu-v1/proof.json','proofs/cold0ba-cpu.json'),
        (P/'lifecycle-v2/proof.json','proofs/cold0ba-lifecycle.json'),(P/'build-controls-v1/proof.json','proofs/cold0ba-builds.json'),
        (P/'native-review-v1/proof.json','proofs/cold0ba-native-STRICT-FALSE.json'),
        (D/'robot-cold-palette-budget-review-v1/proof.json','proofs/cold0ba-378-diagnostic-STRICT-FALSE.json'),
        (C/'proof.json','proofs/base-df-layout.json'),(C/'cpu-v2/proof.json','proofs/base-df-cpu.json'),
        (C/'lifecycle-v2/proof.json','proofs/base-df-lifecycle.json'),(C/'build-controls-v1/proof.json','proofs/base-df-builds.json'),
        (C/'lifecycle-v2/scratch-read-ownership.json','proofs/base-df-scratch-read-ownership.json'),
        (ready/'readiness.json','native-preparation/UNLAUNCHED-readiness.json'),
        (ready/'source-profile-proof.json','native-preparation/source-profile-proof.json'),
        (ready/'command.json','native-preparation/command.json'),
        (P/'native-review-v1/actual-startup-whole-images.png','images/actual0ba-startup-versus3b.png'),
        (P/'native-review-v1/samples.json','images/actual0ba-startup-samples.json'),
        (D/'robot-cold-palette-candidate-v1/failure.json','negatives/invalid-A748-pool-before-edit.json'),
        (C/'lifecycle-v1/failure.json','negatives/lifecycle-v1-Windows-slash-review.json'),
        (D/'robot-base-palette-candidate-v1/failure.json','negatives/builder-v1-tuple-symbol-review.json'),
        (D/'robot-cold-palette-budget-ready-v1/prelaunch-failure-v1.json','negatives/diagnostic-grant-schema-zero-launches.json')]:copy(f,rel)
    reports=['mm-proto-cold-palette-2026-10-26.txt','mm-proto-cold-palette-native-2026-10-26.txt','mm-proto-base-palette-2026-10-26.txt']
    for name in reports:copy(R/'docs/qa'/name,'reports/'+name)
    names=['mm_proto_cold_palette_candidate_v1.py','mm_proto_cold_palette_candidate_v2.py','mm_proto_cold_palette_cpu_v1.py',
        'mm_proto_cold_palette_lifecycle_v1.py','mm_proto_cold_palette_lifecycle_v2.py','mm_proto_cold_palette_freeze_v1.py',
        'mm_proto_cold_palette_freeze_v2.py','mm_proto_cold_palette_run_v1.py','mm_proto_cold_palette_native_review_v1.py',
        'mm_proto_cold_palette_diagnostic_prepare_v1.py','mm_proto_cold_palette_diagnostic_run_v1.py','mm_proto_cold_palette_budget_review_v1.py',
        'mm_proto_base_palette_candidate_v1.py','mm_proto_base_palette_candidate_v2.py','mm_proto_base_palette_cpu_v1.py',
        'mm_proto_base_palette_cpu_v2.py','mm_proto_base_palette_lifecycle_v1.py','mm_proto_base_palette_lifecycle_v2.py',
        'mm_proto_base_palette_freeze_v1.py',Path(__file__).name]
    for name in names:copy(R/'tools/audit'/name,'tools/'+name)
    ext={}
    for f in[P/'source-manifest.json',C/'source-manifest.json',ready/'bindings.json',
              P/'native-review-v1/external-raw-manifest.json',D/'robot-cold-palette-budget-review-v1/external-manifest.json',
              C/'cpu-v2/direct.json',C/'cpu-v2/flows.json',C/'lifecycle-v2/cases.json']:
        ext[str(f)]=dict(sha256=sha(f),bytes=f.stat().st_size)
    put(T/'external-immutable-bindings.json',ext)
    (T/'README.txt').write_text('''HELD/private review checkpoint; no production adoption.
Installed parent3b112; firstcold-cache donor0ba fixes startup376 but strictgallerystillfails378.
Source successor dfbdca24 only122Bbase-cache helper in verified bank78 tail; native UNRUN.
See reports and explicit FALSE proof files. No allweapons/graphics/FPS/wholegoal completion claim.

The four full source overlays and source-vs-installed3b.patch reconstruct the proposed source on
the exact frozen3b source baseline. All other source/ROM/RAM/CHR ownership remains bound externally.
Source-only build and CPU proofs are distinct from native acceptance. No ROM/NSF/reference art,
settings, rawPPU/captures or sourceZIP is copied into this checkpoint.

Frozen tools retain exact versions and error history. Their imported QA tools and original local
assets remain prerequisites bound in the external ready/bindings.json; this is NOT a turnkey
fresh-clone QA reproduction claim. Existing parent3b/source inputs are required. Paths D/... are
C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/...

Metadata-only diagnostic had one unused-grant schema failure before any subprocess; corrected
grant produced exactlyone native launch, expected378FALSE. No native retry. All old negatives
remain immutable. ROOT handles explicit staging/commit/push/install; this builder does none.
''')
    put(T/'copied-origin-map.json',copied)
    payloads={str(f.relative_to(T).as_posix()):dict(sha256=sha(f),bytes=f.stat().st_size)for f in T.rglob('*')if f.is_file()}
    put(T/'catalog.json',payloads)
    review={str(R/'tools/audit'/n):sha(R/'tools/audit'/n)for n in names}
    review.update({str(R/'docs/qa'/n):sha(R/'docs/qa'/n)for n in reports})
    review.update({str(T/rel):q['sha256']for rel,q in payloads.items()})
    review[str(T/'catalog.json')]=sha(T/'catalog.json')
    put(T/'review-files.json',review)
    put(T/'checkpoint-proof.json',dict(checkpoint_complete=True,production_changed=False,native_successor_run=False,
        parent_current3b='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287',
        held_native0ba='0ba628a76f02d4610c2608acd63cdd2a877e6e9a9eb667496a3efa1c655c1927',
        source_successor_df='dfbdca24019776262c4388e3ea782fb989e24b8fc0e3cf0bfe0bbb84a9f480ad',
        exact_source_overlay_files=changed,payload_files=len(payloads),
        catalog_sha256=sha(T/'catalog.json'),review_files_sha256=sha(T/'review-files.json'),
        readiness_sha256=sha(ready/'readiness.json'),source_manifest_sha256=sha(C/'source-manifest.json'),
        all_payload_origins_rehashed=True,all2747_readiness_bindings_rehashed=True,
        no_ROM_audio_settings_raw_capture_or_sourceZIP_payloads=True,no_git_actions=True,
        tool_sha256=sha(__file__)))
    size=sum(f.stat().st_size for f in T.rglob('*')if f.is_file());assert size<=1_000_000,size
    print(json.dumps(dict(path=str(T),bytes=size,payloads=len(payloads),proof_sha256=sha(T/'checkpoint-proof.json'),
        review_files_sha256=sha(T/'review-files.json'),catalog_sha256=sha(T/'catalog.json')),indent=2))


if __name__=='__main__':main()
