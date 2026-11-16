"""Candidate ordinary life route/full cold transport, zero files/native."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_bowser_life_gain_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

def inspect(parent):
    raw,compose=F.C.proposal(parent);assert F.C.inverse(raw)==parent;rows=[]
    for key in('smb3','smb1'):
        m,q=F.Current.cold(raw,key,report=True);rows.append(q)
    rejects=[];wrong=bytearray(raw);wrong[16+8192]^=1
    for label,image in(('parent',parent),('truncated',raw[:-1]),('unowned-byte',bytes(wrong))):
        try:F.C.inverse(image)
        except AssertionError:rejects.append(label)
        else:raise AssertionError('Candidate inverse accepted wrong image')
    q=dict(passed=True,composition=compose,cold=rows,inverse_portable=True,strict_rejections=rejects,outputs=0,Mesen=False)
    q['receipt_SHA256']=F.C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1),default=0);p.add_argument('--kind',choices=('oneup','star'),default='oneup');p.add_argument('--cold',action='store_true');p.add_argument('--metadata',action='store_true');a=p.parse_args()
    parent=F.ROM.read_bytes();raw,_=F.C.proposal(parent);key='smb1'if a.identity else'smb3';family=F.family(a.identity,a.kind)
    def deny(*args,**kw):raise AssertionError('Candidate source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):
        q=inspect(parent)if a.cold else family.metadata(raw,key)if a.metadata else Model.run(raw,key,2600)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Candidate stated source scope did not qualify'
