"""Run a frozen genuine FF stock route on strict actual571 source bytes."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import current_ff_stock_input_1114 as Current


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',type=int,choices=range(4),default=0);p.add_argument('--kind',choices=('life','star'),default='life');a=p.parse_args()
    raw=Current.ROM.read_bytes();old=(Current.White.ROM,Current.White.PIN,Current.All.W,Current.Flower.W,Current.Stock.W)
    log=io.StringIO();original_read=Path.read_bytes
    def read(path):
        assert path.resolve()!=Current.ROM.resolve(),'Mutable Nightly reread after initial input capture'
        return original_read(path)
    def forbid(*args,**kwargs):raise RuntimeError('FF stock source lane attempted file output')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):
        source,info=Current.bind(raw,kind=Current.KIND)
        try:
            with redirect_stdout(log):q=source.route(a.variant,a.kind)
        except Exception:
            print(log.getvalue(),flush=True);raise
    assert old==(Current.White.ROM,Current.White.PIN,Current.All.W,Current.Flower.W,Current.Stock.W)
    receipt=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(dict(passed=q['passed'],binding=info,variant=a.variant,class_name=q['class_name'],kind=a.kind,
        receipt_SHA256=receipt,born=q['born'],collected=q['collected'],life_award=q['life_award'],
        protected_enemy=q['protected_enemy'],music_restored=q['music_restored'],terminal=q['terminal'],
        outputs=0,Mesen_run=False,source_only=True),separators=(',',':')),flush=True)
    assert q['passed'],'Current FF source stock route remains unqualified'
