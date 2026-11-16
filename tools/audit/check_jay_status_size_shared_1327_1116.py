"""Exact00bb/1327 ordinary Mike and Steve pairing with the declared tail view."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import current_jay_status_size_publication_00bb_1116 as J
import check_jay_status_shared_regression_df0e_1116 as Frozen

C=J.C
FROZEN_SHA='00231d5434e4de2a2c28dfdd59ddb6e6fcacd7c696307751f750521d8e21122f'
COMPOSER_SHA='7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c'
FACADE_SHA='ffe06f7b53421b24a07da2918b846a67a3de28469ee7eed2d7e67d42816bf8f3'


def run(parent,candidate):
    assert J.H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    source=inspect.getsource(Frozen.cold)+'\n'+inspect.getsource(Frozen.run)
    before="expected=[(3,0x1800,C.OLD_MAIN,C.NEW_MAIN),(3,0x1ed7,b'\\xea'*8,C.LEAF)]"
    after="expected=[(3,0x17f6,b'\\xea'*10,C.TAIL),(3,0x1800,C.OLD_MAIN,C.NEW_MAIN),(3,0x1ed7,b'\\xea'*8,C.LEAF)]"
    assert source.count(before)==1;source=source.replace(before,after)
    ns=dict(Frozen.__dict__,J=J,C=C,Parent=J.Previous,COMPOSER_SHA=COMPOSER_SHA,FACADE_SHA=FACADE_SHA,__file__=__file__)
    exec(compile(source,'<1327 same ordinary shared-owner pairing>','exec'),ns)
    q=ns['run'](parent,candidate)
    q.update(frozen_context_recipe_SHA256=FROZEN_SHA,source_recipe_SHA256=J.H(source.encode()),
        restored_native_size_and_status_candidate=True,additional_declared_loaded_view='raw3:B7F6 tail10 only')
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    parent=J.Previous.load_current_image();candidate=C.proposal(parent)[0]
    def deny(*a,**kw):raise AssertionError('Jay1327 shared regression attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent,candidate)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
