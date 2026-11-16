"""Single bounded same-controls writer diagnostic, no native/artifacts."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_celeste_flower_loss_probe_00bb_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    raw=F.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Celeste tier probe attempted artifacts/native')
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'celeste',2600)
    q['diagnostic_only']=True;print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert not q['passed']and q['receipt'].get('dash',{}).get('first_tier_loss'),'Actual first tier-loss evidence missing'
