"""Offline every-row/remaining-slot body-pixel dominance, no emulator/ROM edits."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json
from check_parodius_body_pixels_v1 import pixels,signed
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['original-manifest','sorted-manifest','rom','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old=json.loads(a.original_manifest.read_text());new=json.loads(a.sorted_manifest.read_text());chrdata=a.rom.read_bytes()[1048592:]
    records=[];all_cases=0;aggregate_regressions=0
    for left,right in zip(old['pools'],new['pools'],strict=True):
        for frame in left['body_frames']:
            parts=[list(reversed(p['records'][str(frame)]))for p in [left,right]]
            pointmaps=[[pixels(chrdata,left,[part])for part in pp]for pp in parts]
            assert pixels(chrdata,left,left['records'][str(frame)])==pixels(chrdata,right,right['records'][str(frame)])
            failures=[];budgets=[]
            for budget in range(9):
                totals=[Counter(),Counter()]
                for y in range(-32,64):
                    counts=[]
                    for side,(pp,pm)in enumerate(zip(parts,pointmaps,strict=True)):
                        eligible=[i for i,p in enumerate(pp)if signed(p[2])<=y<signed(p[2])+16]
                        output={pt:v for i in eligible[:budget]for pt,v in pm[i].items()if pt[1]==y}
                        counts.append(dict(body=len(output),core=sum(v[0]==0 for v in output.values())))
                        totals[side].update(counts[-1])
                    if counts[1]['body']<counts[0]['body']or counts[1]['core']<counts[0]['core']:
                        failures.append(dict(relative_y=y,remaining_body_slots=budget,baseline=counts[0],sorted=counts[1]))
                    all_cases+=1
                budgets.append(dict(remaining_body_slots=budget,baseline=dict(totals[0]),sorted=dict(totals[1])))
                if totals[1]['body']<totals[0]['body']:aggregate_regressions+=1
            records.append(dict(pool=left['index'],frame=frame,body_record_parts=len(parts[0]),row_dominates=not failures,first_failures=failures[:8],failing_rows_budgets=len(failures),aggregate_budgets=budgets))
    assert len(records)==131
    safe=[dict(pool=r['pool'],frame=r['frame'])for r in records if r['row_dominates']]
    (a.output/'records.json').write_text(json.dumps(records,indent=2)+'\n')
    (a.output/'row-dominating-poses.json').write_text(json.dumps(safe,indent=2)+'\n')
    q=dict(analysis_complete=True,native_run=False,ROM_changed=False,model_only=True,body_records=131,row_budget_cases=all_cases,body_and_core_row_dominating_poses=len(safe),original_fallback_poses=131-len(safe),safe_pools=dict(Counter(r['pool']for r in safe)),aggregate_fullbody_budget_regressions=aggregate_regressions,CHR_sha256=hashlib.sha256(chrdata).hexdigest(),ROM_sha256=sha(a.rom),original_manifest_sha256=sha(a.original_manifest),sorted_manifest_sha256=sha(a.sorted_manifest),tool_sha256=sha(Path(__file__)),record_data_sha256=sha(a.output/'records.json'),safe_pose_data_sha256=sha(a.output/'row-dominating-poses.json'),passed=False,limits='This is a disclosed negative for unconditional119pose nonwrap admission, not a new game/native verdict. Remaining0..8 body slots are modeled independently on every relative row, using exact linked CHR/palette-index pixels and real reverse-emission order. Global OAM wrap/clipping must separately retain original. Core-first can trade total secondary-plane pixels for core;32 poses avoid both losses on every modeled row/budget. All original colors/shapes remain equal without sprite limit. No audio/cadence/lifecycle/other-mode qualification.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
