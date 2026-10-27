"""Small current-Mega6 review packet; retain raw data externally."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'robot-primary-combined-mega-ready-v2'
V=D/'robot-primary-combined-mega-review-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    assert sha(V/'proof.json')=='0cd218f60cf71014270b0ef5af147dd108c10718e7c4808d8cfd4639c588c6d9'
    for f,h in json.loads((B/'bindings.json').read_text()).items():assert sha(f)==h,f
    for f,h in json.loads((V/'external-raw-manifest.json').read_text()).items():assert sha(f)==h,f
    copies={}
    def copy(src,dst):
        q=a.output/dst;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,q);copies[dst]=dict(source=str(src),sha256=sha(q))
    for name in ['readiness.json','exact-profile-delta.json','fresh-assembled-controls.json','environment.json','launch-binding-v1.json','launch-outcome-v1.json']:
        copy(B/name,'preparation/'+name)
    copy(B/'native/native-mm-weapon-profile.json','actual-native-six-components.json')
    for name in ['proof.json','samples.json','native-evidence.json','old0a-comparison.json','external-raw-manifest.json']:
        copy(V/name,'actual-native/'+name)
    for f in sorted(V.glob('*.png')):copy(f,'images/'+f.name)
    tools=['mm_proto_primary_combined_mega_prepare_v2.py','mm_proto_primary_combined_mega_review_v1.py','mm_proto_primary_combined_mega_checkpoint_v1.py']
    for name in tools:copy(R/'tools/audit'/name,'tools/'+name)
    reports=[R/'docs/qa/mm-proto-primary-combined-mega-2026-10-26.txt',R/'docs/qa/mm-proto-primary-combined-mega-native-2026-10-26.txt']
    for f in reports:copy(f,'reports/'+f.name)
    put(a.output/'external-prerequisites.json',dict(
        combined_source_manifest=dict(path=str(D/'root-render-audio-palette-hud-union-v2/source-manifest.json'),sha256=sha(D/'root-render-audio-palette-hud-union-v2/source-manifest.json')),
        native_binding_manifest=dict(path=str(B/'bindings.json'),sha256=sha(B/'bindings.json'),count=4631),
        source_ready=dict(path=str(D/'robot-primary-combined-mega-final-v1/proof.json'),sha256=sha(D/'robot-primary-combined-mega-final-v1/proof.json')),
        helper_prerequisite='tools/audit/mm_proto_color_rotation_native_review_v1.py sheet() and its original imports; source/ROM/reference/runtime assets remain external. No turnkey fresh-clone QA claim.'))
    put(a.output/'visual-review.json',dict(viewed=True,actual_wholeimage_placements=88,sheets=6,
        selected_frame_scope_only=True,full_stream_comparison='1029/1030 exact old0a, retained71pixel menu183 difference',
        no_whole1030frame_manual_review=True,residual_8sprite_charge_Rush_body_omissions=True,
        no_full_fairness_art_clean_waveform_FPS_or_adoption_claim=True))
    (a.output/'README.txt').write_text('Freshce635 MegaHard6 PASS; one launch, no retry, worker released.\n'
        'Only identity.variant0 differs from qualifiedProto executable body.\n'
        '997full256DMAs/669scoped safe enables/0late/656updates.\n'
        'Actual34stage images and88selected wholeframe placements; sprite omissions retained.\n'
        'Old0a is a separate scope:1029wholeframes exact, menu18371px difference retained.\n'
        'No product/source/ROM/settings/default/Git changes; raw/ROM/audio/settings external.\n')
    catalog={f.relative_to(a.output).as_posix():dict(bytes=f.stat().st_size,sha256=sha(f))for f in a.output.rglob('*')if f.is_file()}
    assert sum(x['bytes']for x in catalog.values())<1024*1024
    put(a.output/'catalog.json',catalog)
    owned=sorted((R/'tools/audit').glob('mm_proto_primary_combined_mega_*.py'))+reports
    put(a.output/'review-files.json',dict(owned_files=[dict(path=f.relative_to(R).as_posix(),sha256=sha(f))for f in owned],
        checkpoint=str(a.output),no_Git_mutation=True,retained_v1='Preparation predecessor only; runtimeDB binding addedv2, neverlaunchedv1.'))
    put(a.output/'proof.json',dict(checkpoint_verified=True,native_profile_pass=True,native_launches=1,retries=0,worker_released=True,
        actual_owner=1,actual_variant=0,numeric_Hard=1,ROM_sha256='ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111',
        catalog_sha256=sha(a.output/'catalog.json'),review_files_sha256=sha(a.output/'review-files.json'),
        payloads=len(catalog),bytes=sum(x['bytes']for x in catalog.values()),copies=copies,tool_sha256=sha(__file__),
        no_raw_ROM_audio_settings_copied=True,source_default_unchanged=True,limits='Compact actualMega6 review only. Scopes/one menu difference/remaining sprite omissions explicit; no full-roster, acquisition, waveform, matchedFPS or adoption.'))
    print(json.dumps(dict(checkpoint=str(a.output),proof_sha256=sha(a.output/'proof.json'),review_files_sha256=sha(a.output/'review-files.json'),payloads=len(catalog),bytes=sum(x['bytes']for x in catalog.values())),indent=2))


if __name__=='__main__':main()
