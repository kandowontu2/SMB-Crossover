"""Narrow actual9826 cold/metadata or frozen ordinary shot/full source replay."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_mini_weapon_owner_twoshot_a2_1116 as Shot
import replay_mini_weapon_owner_full11_a2_1116 as Full
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

def run(parent,scope):
    raw,composition=Shot.C.proposal(parent);opening=[]
    def deny(*a,**kw):raise AssertionError('Combined Mini source attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny):
        if scope=='cold':
            _,cold=Shot.Current.cold(raw,True);rows=[]
            for f,key in((Shot,'flower'),(Full,'full11')):
                text=f.controller(raw,key);meta=f.metadata(raw,key)
                assert text.split('\n',1)[1]==f.Previous.controller(f.Current.reference(raw),key).split('\n',1)[1]
                rows.append(dict(key=key,Lua_SHA256=f.H(text.encode()),bytes=len(text),metadata=meta))
            rejected=[]
            for name,bad in(('parent',parent),('projected',Shot.Current.reference(raw)),('truncated',raw[:-1]),('dirty',raw[:100]+bytes((raw[100]^1,))+raw[101:])):
                try:Shot.controller(bad)
                except AssertionError:rejected.append(name)
                else:raise AssertionError(name)
            q=dict(passed=True,actual_CPU_SHA256=Shot.PIN,cold=cold,rows=rows,wrong_roles_rejected=rejected)
        else:
            F=Shot if scope=='shot'else Full
            def cold(image,key):m,q=F.Current.cold(image,True);opening.append(q);return m
            family=F.family()
            with patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'mini',5100 if scope=='shot'else 8600)
            q['actual_cold']=opening
        q.update(composition=composition,source_scope=scope,outputs=0,Mesen=False)
        q['combined_receipt_SHA256']=Shot.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scope',choices=('cold','shot','full'),default='cold');a=p.parse_args()
    q=run(Shot.ROM.read_bytes(),a.scope);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True);assert q['passed']
