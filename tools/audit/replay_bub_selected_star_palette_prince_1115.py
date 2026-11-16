"""New strict combined-candidate facade; frozen ACE control bodies unchanged."""
from functools import lru_cache
from hashlib import sha256
import inspect,json
from pathlib import Path
from types import SimpleNamespace

import compose_bub_selected_star_palette_prince_1115 as C
import replay_bub_selected_star_palette_ace_1115 as Frozen
import replay_bub_selected_star_images_ace_1115 as Pictures

R,ROM,B,W,N,PIN=C.R,C.ROM,C.B,C.W,C.N,C.CANDIDATE
Items,Star=Frozen.Items,Frozen.Star
PINS=((Frozen,'923057a27c6bf7df4b51625186434eaafd7371d4baa27f29c1d48066197ec68b'),
    (Pictures,'8e7e0a138705be5c499b4593991167f5374cc52691bf05ea0525d550964b5fe1'))


@lru_cache(maxsize=1)
def reference(raw):return C.reference(C.inverse(raw))


@lru_cache(maxsize=6)
def controller(raw,identity=0,mode='mushroom',*,stock='star',images=False):
    assert identity in(0,1)and mode=='mushroom'and stock in('flower','oneup','star')
    assert not images or stock=='star'
    for module,pin in PINS:assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    e9=reference(raw)
    old=Pictures.controller(e9,identity)if images else Frozen.controller(e9,identity,mode,stock=stock)
    assert old.count(Frozen.PIN)>=2
    text=old.replace(Frozen.PIN,PIN)
    assert text.replace(PIN,Frozen.PIN)==old,'Only owning ROM identity differs; all old controls/assertions/callbacks exact'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def source_check(raw,identity=0,stock='star'):
    Witness=Items.Witness;base=SimpleNamespace(reference=C.inverse,Previous=Witness.Base.Previous)
    fn=lambda image,who=0,mode='mushroom':controller(image,who,mode,stock=stock)
    ns=dict(Witness.__dict__,Base=base,PIN=PIN,controller=fn)
    exec(compile(inspect.getsource(Witness.source_check),__file__+':actual-combined-source','exec'),ns)
    return ns['source_check'](raw,identity)


def metadata(raw):
    return dict(ROM_SHA256=PIN,cookie=raw[C.COOKIE:C.COOKIE+16].hex(),controllers=[
        dict(identity=i,stock=stock,images=images,Lua_SHA256=sha256(controller(raw,i,stock=stock,images=images).encode()).hexdigest())
        for i in(0,1)for stock,images in(('star',False),('oneup',False),('star',True))],
        exact_frozen_controls_except_ROM_identity=True,output_files=0)


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--identity',type=int,choices=(0,1),default=0)
    ap.add_argument('--stock',choices=('flower','oneup','star'),default='star');ap.add_argument('--metadata',action='store_true');a=ap.parse_args()
    raw,composition=C.proposal(C.load_current());assert C.inverse(raw)
    if a.metadata:q=metadata(raw)
    else:
        from unittest.mock import patch
        def forbid(*args,**kwargs):raise AssertionError('Combined route attempted output')
        with patch.object(Path,'write_text',forbid),patch.object(Path,'write_bytes',forbid):q=source_check(raw,a.identity,a.stock)
        receipt=q['receipt'];natural=receipt.get('natural_star')or receipt.get('natural_stock')or receipt.get('natural_flower')
        natural={k:v for k,v in natural.items()if k in('born','mature','collector','collected','credit','erase','setup','popup','post_credit_returns','post_collector_returns','F_ready','credit_moves')}
        q=dict(passed=q['passed'],identity=a.identity,stock=a.stock,Lua_SHA256=q['controller_SHA256'],
            receipt_SHA256=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            Main=receipt.get('Main_updates'),entries=receipt.get('source_updates'),terminal=receipt.get('terminal'),natural=natural)
    print('RESULT '+json.dumps(dict(composition=composition,result=q,output_files=0),sort_keys=True,separators=(',',':')),flush=True)
