"""Actual combined cold/natural-picture callbacks and explicit proof transfer."""
import argparse
from hashlib import sha256
import inspect,json
from pathlib import Path

import replay_bub_selected_star_palette_prince_1115 as F
import check_bub_selected_star_palette_ace_1115 as Core
import check_bub_selected_star_picture_callbacks_ace_1115 as Callbacks

C=F.C
PINS=((Core,'1676887ddce07de4e31bfdc66ff8bf1755d78004ea529eae3481968b09146de6'),
      (Callbacks,'bbdbc72420438b46ee234361ad222936abf23a9b30d960ad86644b79532572e7'))


def callbacks(raw,identity):
    # Re-execute the exact frozen callback/driver source with new strict C/F
    # globals. The actual CPU image remains the combinedraw argument.
    ns=dict(Callbacks.__dict__,F=F,C=C)
    exec(compile(inspect.getsource(Callbacks.controller),__file__+':same-passive-callbacks','exec'),ns)
    exec(compile(inspect.getsource(Callbacks.run),__file__+':actual-combined-callback-route','exec'),ns)
    return ns['run'](raw,identity)


def cold(raw):
    ns=dict(Core.__dict__,C=C)
    exec(compile(inspect.getsource(Core.cold),__file__+':actual-combined-cold','exec'),ns)
    return ns['cold'](raw)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--gate',choices=('cold','callbacks','metadata'),required=True)
    ap.add_argument('--identity',type=int,choices=(0,1),default=0);a=ap.parse_args()
    for module,pin in PINS:assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    parent=C.load_current();raw,composition=C.proposal(parent);assert C.inverse(raw)==parent
    if a.gate=='cold':q=cold(raw)
    elif a.gate=='callbacks':q=callbacks(raw,a.identity)
    else:q=F.metadata(raw)
    text=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('RESULT '+json.dumps(dict(gate=a.gate,composition=composition,result=q,
        receipt_SHA256=sha256(text.encode()).hexdigest(),output_files=0),sort_keys=True,separators=(',',':')),flush=True)
