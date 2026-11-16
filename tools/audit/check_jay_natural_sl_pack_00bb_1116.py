"""Small typed00bb preservation/compile/true-return check; no item rerun."""
from pathlib import Path
from unittest.mock import patch
import json
import current_jay_natural_stock_00bb_1116 as J
import replay_jay_natural_sl_00bb_1116 as F
import check_jay_natural_sl_native_pack_1116 as Frozen

FROZEN_CHECK_SHA='0174111603295ae5a65a987613b7dc65e6b3d32c927db2c442fc304030ff56c2'


def run(raw):
    assert J.H(Path(Frozen.__file__).read_bytes())==FROZEN_CHECK_SHA
    proof=J.bindings(raw);old=J.reference(raw)
    bodies={}
    for kind in('life','star'):
        text=F.controller(raw,kind);previous=F.Frozen.controller(old,kind)
        assert text.split('\n',1)[1]==previous.split('\n',1)[1]
        bodies[kind]=J.H(text.split('\n',1)[1].encode())
    try:F.controller(J.Previous.reference(old),'life')
    except AssertionError:pass
    else:raise AssertionError('Historical91dc accepted')
    # Reuse the frozen sixteen-update callback test with a new typed execution
    # binding; no frozen function or default input is broadened.
    with patch.object(Frozen,'F',F),patch.object(Frozen,'J',J):q=Frozen.run(raw)
    q['wrong_inputs_rejected']=['dirty','historical7c0f','unknown-kind','historical91dc']
    q.update(metadata7c0f_only_SHA256=J.Previous.PIN,normalizer_SHA256=J.COMPOSER_SHA,
        preserved15_carriers=proof['preserved_carriers'],all_three_ROM_cookie_files=proof['all_three_ROM_cookie_files'],
        all_three_ROM_cookies_preserved=True,frozen_observer_body_SHA256=bodies,
        actual00bb_CPU_bytes_executed=True,no_full_natural_route_repeated=True,
        frozen_callback_harness_SHA256=FROZEN_CHECK_SHA,typed_facade_SHA256=J.H(Path(J.__file__).read_bytes()),
        checker_SHA256=J.H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay00bb native package check attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
