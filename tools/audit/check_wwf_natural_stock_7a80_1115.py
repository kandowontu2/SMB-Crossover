"""Actual current7a80 original CPU WWF natural stock sources, no outputs."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_wwf_natural_stock_7a80_1115 as F
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold
import wwf_stock_source_model_1115 as Model


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',choices=tuple(F.IDENTITIES)+('all',),default='hogan');p.add_argument('--roles',nargs='+',choices=tuple(F.IDENTITIES));p.add_argument('--kind',choices=tuple(F.KINDS),default='oneup');p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes();factory=F.family(a.kind);rows=[]
    def forbid(*args,**kwargs):raise AssertionError('WWF stock source attempted output/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid),patch.object(Runner,'Factory',factory),patch.object(Cold,'Factory',factory),patch.object(Runner,'cold',Cold.cold):
        for key in a.roles or(F.IDENTITIES if a.identity=='all'else(a.identity,)):
            q=Runner.strict_metadata(raw,key)if a.metadata else Model.run(raw,key,4700)
            if a.metadata:rows.append(dict(key=key,passed=True,metadata=q))
            else:
                r=q['receipt'];rows.append(dict(key=key,passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],Main=r.get('Main_returns'),Wf=r.get('WfMovement_calls'),
                    reason=r.get('reason'),stock=r.get('natural_stock'),items=r.get('items'),events=r.get('events'),terminal=r.get('terminal'),seconds=q['seconds']))
            print('CASE '+json.dumps(rows[-1],separators=(',',':')),flush=True)
    result=dict(passed=all(q['passed']for q in rows),kind=a.kind,rows=rows,outputs=0,Mesen_run=False)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
    assert result['passed'],'WWF stock route remains source-unqualified'
