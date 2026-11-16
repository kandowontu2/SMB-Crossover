"""Faithful actual native emerging-F gates/effect/60/resume, no game changes."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_supermaaa_flower_native6_91dc_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    raw=F.ROM.read_bytes();assert F.digest(raw)==F.PIN;opening=[]
    def deny(*args,**kw):raise AssertionError('SuperMaaa source attempted artifacts/native')
    def cold(image,key):
        m,q=F.Current.cold(image,key,True);opening.append(q);return m
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'supermaaa',3500)
    q['actual_cold_readback']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Actual native state6 Flower/credit/60/25 unqualified'
