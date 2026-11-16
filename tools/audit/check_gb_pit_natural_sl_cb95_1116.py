"""Strict owning cb95 production callbacks for ordinary natural Pit Star/1UP."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_gb_pit_natural_sl_cb95_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('oneup','star'),default='oneup');p.add_argument('--metadata',action='store_true');a=p.parse_args();raw=F.ROM.read_bytes();assert F.H(raw)==F.PIN;opening=[]
    def deny(*a,**kw):raise AssertionError('GB Pit stock source attempted files/native')
    def cold(image,key):m,q=F.Current.cold(image,True);opening.append(q);return m
    family=F.family(a.kind)
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):q=F.metadata(raw,a.kind)if a.metadata else Model.run(raw,'gb_pit',5800)
    if opening:q['actual_cold']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Actual GB Pit natural stock remains unqualified'
