"""Preserve reviewed shared spans and the exact private Prince source packet."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/current-native-review-freeze-1103-v106'
D=R/'docs/qa/checkpoints/2026-11-03/prince-strike-v141'
W=R/'docs/qa/checkpoints/2026-11-03/current-native-review-v106'
def main():
    O.mkdir(exist_ok=True);p=R/'build/prince-actor-1101-v1';manifest=p/'strike-checkpoint-v141.json';q=json.loads(manifest.read_text());archive=R/q['archive']
    assert q['passed']and not q['installed']and not q['native_emulator']and q['archive_members']==92
    assert archive.stat().st_size==q['archive_bytes']==225037 and sha(archive)==q['archive_SHA256']
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==92
        for member,row in q['members'].items():
            name=member.replace('\\','/');blob=z.read(name)
            assert hashlib.sha256(blob).hexdigest()==row['SHA256']and(R/name).read_bytes()==blob,name
    D.mkdir(parents=True);(D/'inputs.zip').write_bytes(archive.read_bytes());(D/'helper-manifest.json').write_bytes(manifest.read_bytes())
    dkjr=R/'build/dkjr-native-source-1102-v2';sources=[Path(__file__),R/'tools/audit/grant_dkjr_shared_gates_root_1103_v104.py',R/'tools/audit/grant_prince_frontend_root_1103_v105.py',*(R/'tools/audit'/n for n in['check_dkjr_native_rare_gate_1103_v71.py','check_dkjr_native_bbox_foreign_1103_v72.py','check_dkjr_native_bbox_foreign_1103_v73.py'])]
    grants=[R/'docs/qa/allocations/dkjr-shared-gates-1103-v104.json',R/'docs/qa/allocations/prince-current-frontend-1103-v105.json'];files=sources+grants+[dkjr/'native-rare-gate-v71.json',dkjr/'native-bbox-current-foreign-v73.json',D/'helper-manifest.json']
    for grant in grants:
        g=json.loads(grant.read_text());assert g['granted']
        for name,h in g['bindings'].items():assert sha(R/name)==h,name
    # Preserve both actual failed observers, without calling a fixture failure
    # a gameplay defect or silently editing a completed controller.
    negatives=[]
    for version,reason in[(139,'Obsolete33slot standalone icon assertion before Prince selection.'),(142,'Fixed360frame menu-to-game assertion; actual handoff state not yet diagnosed.')]:
        a=p/f'native-first-controls-v{version}';binding=json.loads((a/'capture/binding.json').read_text());assert binding['exit_code']==1
        assert binding['ready_sha256']==sha(a/'ready.json')and binding['ROM_sha256']==q['ROM_SHA256']
        files.extend([a/'controller.lua',a/'ready.json',a/'run.py',a/'capture/binding.json',a/'capture/prince-private-v140-controller.log'])
        negatives.append(dict(version=version,passed=False,reason=reason))
    W.mkdir(parents=True);target=W/'inputs.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in files:z.writestr(f.relative_to(R).as_posix(),f.read_bytes())
    assert target.stat().st_size<256000
    with zipfile.ZipFile(target)as z:
        for f in files:assert z.read(f.relative_to(R).as_posix())==f.read_bytes()
    out=dict(passed=True,installed=False,native_gameplay_pass=False,private_ROM_SHA256=q['ROM_SHA256'],Prince_checkpoint=D.relative_to(R).as_posix(),Prince_archive_SHA256=sha(D/'inputs.zip'),Prince_archive_bytes=q['archive_bytes'],Prince_members=92,review_checkpoint=W.relative_to(R).as_posix(),archive_SHA256=sha(target),archive_bytes=target.stat().st_size,source_files=[f.relative_to(R).as_posix()for f in sources]+q['source_files_to_commit'],native_negatives=negatives,scope='Private current Prince122 runtime/cold129/source manifest130 plus fullcold/foreign/earnedstrike/lifecycle/IRQ/nested/front137 and actual item/contact ingress138 CPU milestones. Original strike/proxy ownership repaired without native/shared defeat mutation. All current cf7 body/cookie deltas retained; no new pages. This is not an emulator pass or nightly unlock. Two real observer negatives preserved; distinct143 will diagnose handoff. DK Jr exact37+1 shared spans and Prince exact9frontendspans26changedbytes approved only for private composition/native checks.',bindings={f.relative_to(R).as_posix():sha(f)for f in files})
    (W/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');(D/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    handoff=R/'docs/qa/continuation-current.json';h=json.loads(handoff.read_text());h['Prince_native_current_1103']=dict(status='PRIVATE_B684_CPU_QUALIFIED_NATIVE_OBSERVER_NEGATIVES',candidate='build/prince-actor-1101-v1/prince-private-v140.nes',ROM_SHA256=q['ROM_SHA256'],checkpoint=D.relative_to(R).as_posix(),review_checkpoint=W.relative_to(R).as_posix(),source='Final122 source-owned deferred strike/no-drop acknowledgement, actual fullcurrentcf7 cold130/131, original unarmed A jump and earned flower-to-sword policy. Exact frontend137 public Prince alternate enabled only in private candidate.',native_negatives=negatives,remaining='Actual native cold/menu/hardware/idle/walk/jump/contact/death and naturallyearned sword/strike; full1-1/helper need/audio. No nightly unlock yet.')
    h['dkjr_current_source_1102'].update(shared_gate_grant=grants[0].relative_to(R).as_posix(),current_positive_bbox='build/dkjr-native-source-1102-v2/native-bbox-current-foreign-v73.json',shared_scope='Exact37B bbox+1B rarethreshold privatelyapproved,144 actual currentauthenticated foreign pairs and131072classifiercases. No public40 admission/ROM/menu yet.')
    handoff.write_text(json.dumps(h,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in['bindings','source_files']}))
if __name__=='__main__':main()
