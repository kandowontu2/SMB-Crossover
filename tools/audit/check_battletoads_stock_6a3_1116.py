"""Actual current6a3 BT item source scopes, zero output files."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import current_battletoads_stock_6a3_1116 as Current

def inspect(raw):
    b=Current.bundle(raw);rows={}
    for n in('BtConstruct','BtCoreStep','BtMovement','BtPickup','BtFoodHeal','BtFullPower','BtHostReady','BtVariant','BtSrc_Objects_Life',
        'UnionPwrUpCore','RlPrepareDispatch','GameLoop','IdleLoop'):
        pc=Current.W.address(b,n)
        if n.startswith('Bt'):
            rows[n]=dict(PC=pc,bytes=raw[Current.CACHE+(pc&8191):Current.CACHE+(pc&8191)+72].hex())
        else:
            at=Current.W.location(b,n);rows[n]=dict(PC=pc,file=at,bytes=raw[at:at+112].hex())
    m,cold=Current.cold(raw,'rash',True)
    return dict(passed=True,preservation=Current.preservation(raw),cold=cold,symbols=rows,
        initial_native_status=Current.N.get(m,'PlayerStatus'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inspect',action='store_true');p.add_argument('--metadata',action='store_true')
    p.add_argument('--identity',choices=Current.IDENTITIES,default='rash');p.add_argument('--kind',choices=('mushroom','flower'),default='mushroom');a=p.parse_args()
    raw=Current.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('BT stock source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Current.Cold.Runner.Native,'run',deny):
        if a.inspect:q=inspect(raw)
        else:
            import replay_battletoads_stock_6a3_1116 as F
            import wwf_stock_source_model_1115 as Model
            Runner=Current.Cold.Runner;family=F.family(a.kind);opening=[]
            def cold(image,key):
                m,report=Current.cold(image,key,True);opening.append(report);return m
            with patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):
                q=family.metadata(raw,a.identity)if a.metadata else Model.run(raw,a.identity,4050)
            if not a.metadata:q['actual_cold_readback']=opening
    if a.inspect or a.metadata:q['source_receipt_SHA256']=Current.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.inspect and not a.metadata:assert q['passed'],'Actual BT food scope remains unqualified'
