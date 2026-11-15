"""Current seven-a-eighty WWF Star normal controller source; zero artifacts."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_wwf_natural_star_7a80_1115 as F
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold
import wwf_stock_source_model_1115 as Model


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--roles',nargs='+',choices=tuple(F.IDENTITIES),default=['hogan']);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes();factory=F.family();rows=[]
    def forbid(*args,**kwargs):raise AssertionError('WWF Star source attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid),patch.object(Runner,'Factory',factory),patch.object(Cold,'Factory',factory),patch.object(Runner,'cold',Cold.cold):
        for key in a.roles:
            q=Runner.strict_metadata(raw,key)if a.metadata else Model.run(raw,key,4700)
            if a.metadata:row=dict(key=key,passed=True,metadata=q)
            else:
                r=q['receipt'];row=dict(key=key,passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],Main=r.get('Main_returns'),Wf=r.get('WfMovement_calls'),
                    reason=r.get('reason'),stock=r.get('natural_stock'),items=r.get('items'),events=r.get('events'),power_changes=r.get('power_changes'),terminal=r.get('terminal'),seconds=q['seconds'])
            rows.append(row);print('CASE '+json.dumps(row,separators=(',',':')),flush=True)
    result=dict(passed=all(q['passed']for q in rows),rows=rows,outputs=0,Mesen_run=False)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
    assert result['passed'],'WWF Star route remains source-unqualified'
