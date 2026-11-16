"""Execute the strict full-stage native controller against actual source CPU."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_jay_status_size_full11_1327_1116 as F
import check_jay_natural_sl_native_pack_1116 as Harness

J=F.J
HARNESS_SHA='0174111603295ae5a65a987613b7dc65e6b3d32c927db2c442fc304030ff56c2'


def run(raw,limit=5000):
    assert J.H(Path(Harness.__file__).read_bytes())==HARNESS_SHA
    source=inspect.getsource(Harness.run)
    edits=[("for kind in('life','star')","for kind in('full11',)"),
        ("('dirty',bytes(dirty),'life'),('historical91dc',J.reference(raw),'star'),('unknown-kind',raw,'flower')",
         "('dirty',bytes(dirty),'full11'),('parent00bb',J.reference(raw),'full11'),('unknown-kind',raw,'flower')"),
        ("scripts['life']","scripts['full11']"),
        ('for _ in range(16):','for _ in range('+str(limit)+'):'),
        ('instances.clear();assert not stopped,(stopped,receipts)','instances.clear()\n            if stopped:break'),
        ("assert len(witness.pending)==0 and result['Main']==result['updates']==result['motor']==16",
         "assert stopped==[0],(stopped,receipts)\n    assert len(witness.pending)==0 and result['Main']==result['updates']and result['motor']>=25"),
        ("for name in('GameLoop','JayIntegrate'):assert counts[name+'_entries']==counts[name+'_returns']==16",
         "for name,key in(('GameLoop','Main'),('JayIntegrate','motor')):assert counts[name+'_entries']==counts[name+'_returns']==result[key]"),
        ('actual_cold_and16_update_callback_smoke=True,','actual_full_controller_source_execution=True,'),
        ("cold_UI_boot_native_unrun=True,natural_collector_observer_native_unrun=True,",
         "actual_UI_cold=True,fullstage_native_unrun=True,controller_receipt=json.loads(next(s.removeprefix('SMB_NATIVE_RECEIPT ')for s in receipts if s.startswith('SMB_NATIVE_RECEIPT '))),"),
    ]
    for old,new in edits:assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
    ns=dict(Harness.__dict__,F=F,J=J,__file__=__file__)
    exec(compile(source,'<1327 actual callback transport full-stage driver>','exec'),ns)
    q=ns['run'](raw);r=q['controller_receipt']
    assert r['passed']and r['credit']['flag']and r['credit']['castle']and r['credit']['entrance']
    assert r['motor']>=r['credit']['entrance']['motor']+25 and r['terminal']['lives']==2
    q.update(actual_current1327=True,head_size_regression=True,retained_ordinary_policy_SHA256=J.H(F.policy_text().encode()),
        callback_harness_SHA256=HARNESS_SHA,derived_source_SHA256=J.H(source.encode()),
        existing_helpers_only=[dict(stage='1-1',left=x,center=x+16,initial_top=192,width=32)for x in(384,688,880)])
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=5000);a=p.parse_args();assert 100<=a.limit<=5500
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay1327 full-stage source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
