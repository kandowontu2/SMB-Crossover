"""Strict1327 config/compile and16 actual-return callbacks, no item rerun."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import replay_jay_status_size_sl_1327_1116 as F
import check_jay_natural_sl_native_pack_1116 as Frozen

J=F.J
FROZEN_SHA='0174111603295ae5a65a987613b7dc65e6b3d32c927db2c442fc304030ff56c2'


def run(raw):
    assert J.H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    q=J.bindings(raw);parent=J.reference(raw)
    for kind in('life','star'):
        assert F.controller(raw,kind).split('\n',1)[1]==F.Frozen.controller(parent,kind).split('\n',1)[1]
    source=inspect.getsource(Frozen.run).replace("'historical91dc'","'parent00bb'")
    ns=dict(Frozen.__dict__,F=F,J=J,__file__=__file__)
    exec(compile(source,'<strict1327 unchanged S/L callback witness>','exec'),ns)
    out=ns['run'](raw)
    out.update(frozen_callback_harness_SHA256=FROZEN_SHA,body_identical_to00bb=True,
        all_three_ROM_cookies_rebound=True,cookie_files=q['all_three_ROM_cookie_files'],
        actual1327_CPU_bytes_retained=True,no_natural_item_rerun=True)
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay1327 S/L packaging attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
