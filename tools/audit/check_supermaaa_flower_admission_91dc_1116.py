"""Readonly first-admission diagnostic, no gameplay qualification claim."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_supermaaa_flower_admission_91dc_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    raw=F.ROM.read_bytes();assert F.digest(raw)==F.PIN
    def deny(*args,**kw):raise AssertionError('SuperMaaa trace attempted artifacts/native')
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'supermaaa',1800)
    q['diagnostic_only']=True
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert not q['passed']and q['receipt']['food']['stock'].get('first_admission'),'No actual admission captured'
