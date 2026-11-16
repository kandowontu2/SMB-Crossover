"""Single source-head query diagnostic on unchanged ordinary guarded inputs."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_mini_oneup_head_query_1327_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    raw=F.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Mini head diagnostic attempted artifacts/native')
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',lambda image,key:F.Current.cold(image)),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'mini',2000)
    q['diagnostic_only']=True;print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['receipt'].get('item',{}).get('source_head_min'),'No genuine upward source query observed'
