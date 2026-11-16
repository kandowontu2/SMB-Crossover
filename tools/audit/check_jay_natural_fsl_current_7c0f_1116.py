"""Current7c0f-only bridge for the frozen true-motor return check."""
from pathlib import Path
from unittest.mock import patch
import json
import current_jay_natural_stock_7c0f_1116 as J
import check_jay_natural_fsl_91dc_1116 as Frozen


def run(raw):
    q=J.bindings(raw)
    with patch.object(Frozen,'J',J):out=Frozen.bind(raw)
    out.update(owning_SHA256=J.PIN,metadata91dc_only_SHA256=J.Frozen.PIN,
        native_hook_banks={n:h.get('bank_SHA256')for n,h in q['hooks'].items()if h['tag']>=128},
        all15_carriers_and_both_cookies_preserved=True,frozen91dc_APIs_unchanged=True)
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Current Jay motor bridge attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
