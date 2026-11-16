"""One unchanged-input Star route with direct actual music64 witness."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_mini_star_music_1327_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    raw=F.ROM.read_bytes();opening=[]
    def deny(*args,**kw):raise AssertionError('Mini Star music observer attempted artifacts/native')
    def cold(image,key):m,q=F.Current.cold(image,True);opening.append(q);return m
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'mini',6100)
    q['actual_cold']=opening;print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Current Mini Star direct music witness remains unqualified'
