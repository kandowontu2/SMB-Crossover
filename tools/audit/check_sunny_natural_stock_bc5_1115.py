"""Actual bc5 Sunny stock source CPU; no files/native/state seeds."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_sunny_natural_stock_bc5_1115 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

def metadata(raw,key):
    q=F.metadata(raw,key);rejects=[]
    changed=bytearray(raw);changed[16+81*8192+0x12d6]^=1
    for label,wrong in(('truncated',raw[:-1]),('changed_movement',bytes(changed)),('inverse_reference67',F.Current.reference(raw))):
        try:F.controller(wrong,key)
        except AssertionError:rejects.append(label)
        else:raise AssertionError(('Unknown image accepted',label))
    return dict(q,strict_rejections=rejects)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=F.KINDS,default='oneup');p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Sunny stock source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
         patch.object(Runner,'Factory',F),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',metadata):
        q=metadata(raw,a.kind)if a.metadata else Model.run(raw,a.kind,4550)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Sunny natural stock route remains unqualified'
