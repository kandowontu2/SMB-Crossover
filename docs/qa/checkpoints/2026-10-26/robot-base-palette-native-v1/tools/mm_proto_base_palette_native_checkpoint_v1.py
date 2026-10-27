"""Small additive native FALSE checkpoint; preserve the earlier source packet."""
from pathlib import Path
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C=D/'robot-base-palette-candidate-v2';V=C/'native-review-v1';B=C/'ready-v1'
T=R/'docs/qa/checkpoints/2026-10-26/robot-base-palette-native-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    assert not T.exists();T.mkdir(parents=True)
    assert sha(V/'proof.json')=='049b33ebd569b90851fdd7c21160053fc6fb7a144b934e923feebabfadecf4b7'
    for f,h in json.loads((V/'external-raw-manifest.json').read_text()).items():assert sha(f)==h,f
    copied={}
    def copy(f,rel):
        dst=T/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
        assert sha(dst)==sha(f);copied[rel]=dict(source=str(f),sha256=sha(f),bytes=f.stat().st_size)
    for name in['proof.json','samples.json','native-evidence.json','external-raw-manifest.json']:
        copy(V/name,'evidence/'+name)
    images=['primary-actual-whole-images.png','support-actual-whole-images.png','rush-consecutive-actual-whole-images.png','startup-actual-whole-images.png']
    for name in images:copy(V/name,'images/'+name)
    for name in['ROOT-grant.json','launch-binding-v1.json','launch-outcome-v1.json']:
        copy(B/name,'launch/'+name)
    tools=['mm_proto_base_palette_run_v1.py','mm_proto_base_palette_native_review_v1.py',Path(__file__).name]
    for name in tools:copy(R/'tools/audit'/name,'tools/'+name)
    report=R/'docs/qa/mm-proto-base-palette-native-2026-10-26.txt';copy(report,'report.txt')
    source=R/'docs/qa/checkpoints/2026-10-26/robot-base-palette-source-v1'
    links={str(f):dict(sha256=sha(f),bytes=f.stat().st_size)for f in[source/'checkpoint-proof.json',source/'catalog.json',source/'review-files.json',C/'source-manifest.json',B/'readiness.json',B/'bindings.json']}
    put(T/'source-and-runtime-links.json',links)
    put(T/'visual-review.json',dict(agent_viewed=True,source_native_proof_unchanged=True,
        actual_placements=dict(primary=20,support=13,Rush_consecutive=36,startup=8),total_placements=77,
        image_hashes={name:sha(V/name)for name in images},
        observations='StartupProto/HUD/scenery coherent inselectedsamples; no newscenerycorruptionidentified. Rush beam/cloud/arrival forms match prior authenticatedforms. Native8sprite body/shot/Rush omissions remain in charged/crowded samples. Not universally graphicsclean.',
        strict_profile_pass=False,actual993_packet_not_recorded=True,no_retry=True))
    (T/'README.txt').write_text('''PRIVATE/HELD native followup; strict six-case profile FALSE.
This additive packet supersedes neither the immutable source UNRUN checkpoint nor older0ba negatives.
df fixes startup376/378, then completes five staged cases and fails993 during case6Balancer.
Actual962full256DMA pages are independently exact; this does not waive the late render enable.
See report.txt and source-and-runtime-links.json for exact source/CPU/readiness ownership.
No ROM/audio/referenceart/settings/rawPPU/sourceZIP payload is included. External raw files are hash-only.
Three exact versioned tools and existing linked prerequisites are supplied; not a turnkey fresh-clone
QA claim. ROOT stages/pushes and decides any later composition/native work. This builder does none.
''')
    put(T/'copied-origin-map.json',copied)
    files={f.relative_to(T).as_posix():dict(sha256=sha(f),bytes=f.stat().st_size)for f in T.rglob('*')if f.is_file()}
    put(T/'catalog.json',files)
    review={str(T/rel):x['sha256']for rel,x in files.items()};review[str(T/'catalog.json')]=sha(T/'catalog.json')
    review.update({str(R/'tools/audit'/name):sha(R/'tools/audit'/name)for name in tools});review[str(report)]=sha(report)
    put(T/'review-files.json',review)
    put(T/'checkpoint-proof.json',dict(checkpoint_complete=True,native_profile_pass=False,production_changed=False,
        candidate_ROM_sha256='dfbdca24019776262c4388e3ea782fb989e24b8fc0e3cf0bfe0bbb84a9f480ad',
        native_launches=1,retries=0,native_worker_released=True,source_checkpoint_proof_sha256=sha(source/'checkpoint-proof.json'),
        native_proof_sha256=sha(V/'proof.json'),payload_files=len(files),catalog_sha256=sha(T/'catalog.json'),
        review_files_sha256=sha(T/'review-files.json'),no_git_or_install=True,tool_sha256=sha(__file__)))
    size=sum(f.stat().st_size for f in T.rglob('*')if f.is_file());assert size<=1_000_000,size
    print(json.dumps(dict(path=str(T),bytes=size,payloads=len(files),proof_sha256=sha(T/'checkpoint-proof.json'),
        catalog_sha256=sha(T/'catalog.json'),review_files_sha256=sha(T/'review-files.json')),indent=2))


if __name__=='__main__':main()
