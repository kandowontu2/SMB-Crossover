"""Keep measured bridge costs and the unadopted transport proposal compact."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-perf-root-freeze-1103-v108'
D=R/'docs/qa/checkpoints/2026-11-03/bub-bridge-profile-v72'
def main():
    O.mkdir(exist_ok=True);p=R/'build/bub-menu-candidate-1102-v2';manifest=p/'transport-proposals-v72.json';q=json.loads(manifest.read_text());a=q['archive'];archive=R/a['path']
    assert q['passed']and not q['ROM_written']and not q['private_candidate_allowed']and not q['cache_used']
    assert sha(archive)==a['SHA256']and archive.stat().st_size==a['bytes']==42356 and a['members']==32
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==32
        for name,row in q['members'].items():
            blob=z.read(name.replace('\\','/'));assert hashlib.sha256(blob).hexdigest()==row['SHA256']and len(blob)==row['bytes']
            assert(R/name).read_bytes()==blob,name
    for name,h in q['external_read_only_inputs'].items():assert sha(R/name)==h,name
    D.mkdir(parents=True);(D/'inputs.zip').write_bytes(archive.read_bytes());(D/'helper-manifest.json').write_bytes(manifest.read_bytes())
    out=dict(passed=True,installed_ROM_changed=False,candidate_admitted=False,checkpoint=D.relative_to(R).as_posix(),archive_SHA256=sha(D/'inputs.zip'),archive_bytes=a['bytes'],members=32,source_files=q['source_commit_files']+[Path(__file__).relative_to(R).as_posix()],scope=q['scope'],binding={f.relative_to(R).as_posix():sha(f)for f in[Path(__file__),manifest,D/'inputs.zip',D/'helper-manifest.json']})
    (D/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    hpath=R/'docs/qa/continuation-current.json';h=json.loads(hpath.read_text());h['bub_original_upgrades_current_1102'].update(performance_checkpoint=D.relative_to(R).as_posix(),performance_status='PROFILED_CURRENT_CF7_NO_PERFORMANCE_FIX_INSTALLED',performance_measurement='Emptyidle47380..47410CPU/Main,walk48036..48065; source2943..3217,13fullauth10088,dispatch5928,RAMfarcall6576,router2036. Full-auth Side proposal saves1939(~4%) only; noframebudgetcrossing/nativeFPSclaim. No cachedheader or currentPrince/DK manager rewrite adopted. Larger combinedsourceful savings stillunderstudy.')
    hpath.write_text(json.dumps(h,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
