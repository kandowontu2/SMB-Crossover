"""Combine the seven actual old-image identity/settings observations."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=V/'root49-parent-modes-review-ay.json';assert not out.exists()
    cases=[]
    for suffix,count in [('ay',2),('az',5)]:
        h=V/f'root49-parent-modes-{suffix}';progress=json.loads((h/'progress.json').read_text());assert len(progress['results'])==count
        if suffix=='az':assert progress['status']=='ALL_OBSERVATIONS_TERMINAL'
        else:assert (h/'batch-host-negative.json').exists()
        for q in progress['results']:
            p=R/f"build/roster-through-2-2/root49-parent-mode-{suffix}-{q['character']}-v0-mmc3"
            for n,item in q['files'].items():assert sha(p/n)==item['sha256'],n
            assert q['old_650_trace_rows_literal']and int(q['last_active']['selected'])==q['character']
            if q['character']==4:assert q['observed_behavior']==-1
            else:assert q['observed_behavior']==0
            cases.append(q)
    assert {q['character']for q in cases}=={1,4,5,6,7,9,10}
    result=dict(status='PASS_SEVEN_ACTUAL_PARENT_IDENTITIES_AND_650_LITERAL_TRACE_ROWS_EACH',script_sha256=sha(__file__),cases=cases,
      interpretation=['Link old image lacks the behavior-setting symbol; -1 means unavailable, not a menu setting. Current D actual Easy0 and old Link are not interchangeable behavior references.',
       'The other six old images actually use raw setting0, so a blanket mode-mismatch explanation is contradicted.',
       'Movement/input timing at completed native updates still needs inspection; NMI count differences alone do not prove unchanged physics.',
       'AY missing Simon local ROM copy is a retained host-reference failure; AZ uses exact original ROM hashes and does not repeat completed observations.'],
      main_changed=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=sha(out))))
if __name__=='__main__':main()
