"""Small public rollback/review checkpoint of HELD a801; no game/native mutation."""
from pathlib import Path
import hashlib,json,shutil
from PIL import Image,ImageDraw
from mm_proto_priority450_review_v1 import load
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'mm-proto-publication-candidate-v3';N=D/'mm-proto-publication-native-ready-v1'
O=R/'docs/qa/checkpoints/2026-10-26/mm-proto-publication-held'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n')

def main():
    assert not O.exists();O.mkdir(parents=True)
    sr=B/'freeze-v1/receipt.json';nr=N/'freeze-v1/receipt.json'
    assert sha(sr)=='7d8aa2433f882e65718d1dccd845c63a60ce54656eaea79189f8918bf890cab6'
    assert sha(nr)=='957e04ad9bc8aa8126eada37f9d30cce4244406b379c16955562d10500e67302'
    source=json.loads(sr.read_text());native=json.loads(nr.read_text());assert not native['game_release_suitable']and native['physical_DMA_net_delta']==-3
    changed=source['changed_files'];manifest=json.loads((B/'source-manifest.json').read_text());changed_hashes={}
    for rel in changed:
        p=B/'source'/rel;assert sha(p)==manifest[rel];dst=O/'source-overlay'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);changed_hashes[rel]=dict(bytes=p.stat().st_size,sha256=sha(p))
    put(O/'seven-source-files.json',changed_hashes);shutil.copyfile(B/'source.patch',O/'source.patch')
    (O/'proofs').mkdir()
    refs={str(sr):sha(sr),str(nr):sha(nr)}
    for path,h in source['proofs'].items():
        p=Path(path);assert sha(p)==h;label=p.parent.name if p.parent!=B else'build-layout';shutil.copyfile(p,O/'proofs'/(label+'.json'));refs[str(p)]=h
    for p,label in[(N/'review-v2/proof.json','native-independent-review.json'),(N/'native-receipt.json','one-native-launch.json'),(B/'vine-chain-v3/proof.json','vine-partial-image.json'),(N/'freeze-v1/actual-visible-first8-record-runs.json','visible-first8-record-runs.json')]:shutil.copyfile(p,O/'proofs'/label);refs[str(p)]=sha(p)
    # Compact first-deferral metadata, without copying full hardware images.
    causal=json.loads((N/'freeze-v1/first-actual-deferral385.json').read_text())
    for k in['candidate_completed_Roster','candidate_Main_release','baseline_release','baseline_Roster']:
        z=causal[k];v=z['construction']if'construction'in z else z['main'];v.pop('source',None)
    put(O/'first-real-deferral385.json',causal)
    tools=['mm_proto_publication_candidate_v3.py','mm_proto_publication_render_cpu_v2.py','mm_proto_publication_nmi_cpu_v2.py','mm_proto_publication_records_cpu_v1.py','mm_proto_publication_callers_cpu_v1.py','mm_proto_publication_lifecycle_cpu_v1.py','mm_proto_publication_capacity_cpu_v1.py','mm_proto_publication_build_controls_v2.py','mm_proto_publication_source_freeze_v1.py','mm_proto_publication_native_prepare_v1.py','mm_proto_publication_candidate_observer_v1.lua','mm_proto_publication_candidate_mock_v1.py','mm_proto_publication_native_review_v2.py','mm_proto_publication_vine_chain_v3.py','mm_proto_publication_native_freeze_v1.py']
    (O/'tools').mkdir()
    for name in tools:
        p=R/'tools/audit'/name;shutil.copyfile(p,O/'tools'/name);refs[str(p)]=sha(p)
    deps=json.loads((B/'freeze-v1/bindings.json').read_text());prereq={p:z for p,z in deps.items()if'/tools/audit/'in p.replace('\\','/')and Path(p).name not in tools}
    put(O/'versioned-prerequisites.json',prereq)
    for p in[ B/'freeze-v1/source.zip',B/'source-manifest.json',B/'freeze-v1/bindings.json',N/'freeze-v1/bindings.json',N/'readiness.json',N/'ROOT-grant.json',N/'ownership.jsonl',N/'direct.argb',N/'timing.jsonl',N/'review-v2/actual-owned-publications.json',B/'vine-chain-v3/cases.json']:
        refs[str(p)]=sha(p)
    put(O/'external-artifact-links.json',refs)
    for p,label in[(R/'docs/qa/mm-proto-publication-source-2026-10-26.txt','source-report-original.txt'),(R/'docs/qa/mm-proto-publication-native-2026-10-26.txt','native-held-report.txt')]:shutil.copyfile(p,O/label)
    old,new=[load(p)for p in[D/'root-presentation450-731-v1',N]]
    (O/'images').mkdir()
    for label,chosen in [('first-deficit385',[385]),('body-shot-tradeoff403-404',[403,404])]:
        sheet=Image.new('RGB',(512,260*len(chosen)),'#202020');draw=ImageDraw.Draw(sheet)
        for row,f in enumerate(chosen):
            for col,(z,name)in enumerate([(old,'731baseline'),(new,'a801HELD')]):
                draw.text((col*256,row*260),f'{name} actual{f}',fill='white');sheet.paste(Image.fromarray(z['rgb'][f-176]),(col*256,row*260+20))
        sheet.save(O/'images'/f'{label}.png')
    (O/'README.txt').write_text('''HELD publication-aware body/shot priority -- never installed

Exact parent731; private candidatea801. source.patch plus seven complete
source-overlay files preserve the actual proposed bytes/line endings and
their hashes. Public fixed entries and other banks/CHR remain unchanged.
Use the already-published731 source as parent, not a newer unrelated build.
No full874-source ZIP, ROM, audio, raw PPU or settings is copied here;
external-artifact-links.json pins the immutable external evidence.

Read native-held-report.txt for the final result. The nine source/CPU/
canonical/ordinary proofs pass; these do not imply native performance.
The ONE same-controller450 pilot passes every original hardware guard,
but399vs402 real DMA transfers and63 cumulative prefix deficits fail
no-harm cadence. At385, completedRoster14 is274cycles later and Main369
misses its actual release deadline. Native state proves46 consumed priority
images alternate23body/23shots; first8 records favor the intended group.
Actual403 remains hair/face-only while404 has the body: the display
tradeoff is real, and opaque universal fairness is not established.
The real compiled Vine/no-draw chain additionally changes8/24 body bytes
in three configured shot-turn cases while retaining/consuming its tag.
That defeats an intact-body/whole-page guarantee. No native Vine campaign
or hardware timing is inferred from its source-only test.

Material costs: owned DrawAll+189..191, normal pending Mega/ProtoNMI+87..88,
no-pending+17 and commonMoveAll+18. Foreign fullNMI is cycle/state exact;
foreign DrawAll-24..-2. No next iteration or native retry is authorized
by this checkpoint. All earlier c5/00fb/source/native negatives remain.

Included versioned tools are frozen review/reproduction artifacts, with
existing prerequisite hashes in versioned-prerequisites.json. The earlier
failed renderer/NMI/build/Vine/reviewer attempts remain external and are
classified in the reports; none is relabeled as game acceptance.
review-files.json is the exact staging map. The builder does not stage,
commit, push, install, change settings, or launch an emulator.
''')
    stage={p.relative_to(R).as_posix():'Only this additive held experiment checkpoint; not production source.'for p in O.rglob('*')if p.is_file()};stage[Path(__file__).relative_to(R).as_posix()]='Checkpoint builder only.';put(O/'review-files.json',stage)
    catalog={p.relative_to(O).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(O.rglob('*'))if p.is_file()};put(O/'catalog.json',catalog)
    for rel,z in catalog.items():assert sha(O/rel)==z['sha256']
    proof=dict(passed=True,checkpoint_only=True,release_suitable=False,adopted=False,new_native_launch=False,ROM_sha256=source['ROM_sha256'],parent_ROM_sha256=source['parent_ROM_sha256'],seven_exact_source_files=True,native_net_transfer_deficit=-3,Vine_body_partial_counterexample_retained=True,catalog_files=len(catalog),bytes=sum(z['bytes']for z in catalog.values()),catalog_sha256=sha(O/'catalog.json'),review_map_sha256=sha(O/'review-files.json'),tool_sha256=sha(__file__))
    put(O/'proof.json',proof);print(json.dumps(dict(proof_sha256=sha(O/'proof.json'),**proof),indent=2))
if __name__=='__main__':main()
