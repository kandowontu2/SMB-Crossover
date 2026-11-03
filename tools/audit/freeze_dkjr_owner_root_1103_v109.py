"""Freeze current DK Jr's private four-owner source model, without admission."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/dkjr-owner-root-freeze-1103-v109'
D=R/'docs/qa/checkpoints/2026-11-03/dkjr-current-owner-v87'
def main():
    O.mkdir(exist_ok=True);p=R/'build/dkjr-native-source-1102-v2';manifest=p/'native-current-owner-v87.json';q=json.loads(manifest.read_text());archive=R/q['archive']
    assert q['passed']and not q['qualified']and not q['installed']and not q['resident_grant']and not q['menu_grant']
    assert sha(archive)==q['archive_SHA256']and archive.stat().st_size==q['archive_bytes']==135309
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(q['members'])==51
        for row in q['members']:
            blob=z.read(row['path'].replace('\\','/'));assert len(blob)==row['bytes']and hashlib.sha256(blob).hexdigest()==row['SHA256']
            assert(R/row['path']).read_bytes()==blob,row['path']
    assert len(q['source_files'])==17
    D.mkdir(parents=True);(D/'inputs.zip').write_bytes(archive.read_bytes());(D/'helper-manifest.json').write_bytes(manifest.read_bytes())
    sources=[r['path']for r in q['source_files']]+[Path(__file__).relative_to(R).as_posix()]
    out=dict(passed=True,installed=False,native_gameplay_qualified=False,checkpoint=D.relative_to(R).as_posix(),archive_SHA256=sha(D/'inputs.zip'),archive_bytes=q['archive_bytes'],members=51,source_files=sources,scope='Private DK current130/cf7 four-owner resident proposal only. Complete cold/readback/16ordered transitions/128header-byte rejects and888 constructed foreign37-row calls pass. Actual native classifier/stomp/source-reset, native pickup and280flatworldMain epochs pass in the CPU model; original15px jump retained. Body8127/metadataD7D3;531Bmanager+92extra+176selector. No menu/ROM/native scene entry or helper crossing is proved. Reference Prince130 exact source is preserved in durable prince-strike-v141; its real native144 spawn defect requires eventual DK rebase, not silent scope reuse. Empty-area CPU cost is unresolved; no frame-rate claim. Source reset counter wording in86 is corrected by87.',bindings={f.relative_to(R).as_posix():sha(f)for f in[Path(__file__),manifest,D/'inputs.zip',D/'helper-manifest.json',R/'docs/qa/checkpoints/2026-11-03/prince-strike-v141/helper-manifest.json']})
    (D/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    a=R/'docs/qa/continuation-current.json';h=json.loads(a.read_text());h['dkjr_current_source_1102'].update(current_owner_checkpoint=D.relative_to(R).as_posix(),current_owner_status='FOUR_OWNER_CURRENT130_CPU_PROPOSAL_FROZEN_NO_MENU_OR_NATIVE',current_owner_scope=out['scope'],remaining='Complete populatedretire/currentrowservices/ISR; actualworldentrancegeometry/palette/statusauthority; rebasefinalPrincefix/cookie, exactresident/menu source grant, nativeMesen andhelper-assisted1-1. No newhelper grantedorverified.')
    a.write_text(json.dumps(h,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='bindings'}))
if __name__=='__main__':main()
