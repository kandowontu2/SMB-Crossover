"""Source qualify role-scoped ordinary late-edge WWF Star controls in memory."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_wwf_late_edge_star_7a80_1115 as F
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold
import wwf_stock_source_model_1115 as Model


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--roles',nargs='+',choices=tuple(F.IDENTITIES),default=['savage','andre']);a=p.parse_args()
    raw=F.ROM.read_bytes();factory=F.family();rows=[]
    def forbid(*args,**kwargs):raise AssertionError('Late-edge source attempted output/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid),patch.object(Runner,'Factory',factory),patch.object(Cold,'Factory',factory),patch.object(Runner,'cold',Cold.cold):
        for key in a.roles:
            q=Model.run(raw,key,4700);r=q['receipt'];row=dict(key=key,passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],Main=r.get('Main_returns'),Wf=r.get('WfMovement_calls'),reason=r.get('reason'),
                stock=r.get('natural_stock'),items=r.get('items'),events=r.get('events'),power_changes=r.get('power_changes'),terminal=r.get('terminal'),seconds=q['seconds'])
            rows.append(row);print('CASE '+json.dumps(row,separators=(',',':')),flush=True)
    print('RESULT '+json.dumps(dict(passed=all(q['passed']for q in rows),cases=[dict(key=q['key'],passed=q['passed'],receipt_SHA256=q['receipt_SHA256'])for q in rows],outputs=0,Mesen_run=False),separators=(',',':')),flush=True)
    assert all(q['passed']for q in rows),'Late-edge WWF stock route remains source-unqualified'
