"""Actual captured owner M/F, unchanged callbacks, new ordinary clear-side input."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_gb_pit_right_clear_stock_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('mushroom','flower'),default='mushroom');p.add_argument('--metadata',action='store_true');p.add_argument('--owning',choices=('a2','9826','cb95'));a=p.parse_args();raw=F.ROM.read_bytes();opening=[]
    if a.owning:assert F.Current.OWNERS.get(F.H(raw))==a.owning,'Captured owning image differs from required source scope'
    def deny(*a,**kw):raise AssertionError('GB Pit right-clear source attempted files/native')
    def cold(image,key):m,q=F.Current.cold(image,True);opening.append(q);return m
    family=F.family(a.kind)
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):q=F.metadata(raw,a.kind)if a.metadata else Model.run(raw,'gb_pit',2400 if a.kind=='mushroom'else 5700)
    if opening:q['actual_cold']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Actual GB Pit right-clear stock route remains unqualified'
