"""Strict candidate bindings for frozen Bub/Bob natural stock controls."""
from functools import lru_cache
from hashlib import sha256
import inspect
from pathlib import Path
from types import SimpleNamespace

import compose_bub_selected_star_palette_ace_1115 as C
import replay_bub_native_palette_current_1115 as Items
import replay_bub_star_174fa_1115 as Star
import replay_bub_star_images_174fa_1115 as StarImages

R,ROM,B,W,N,PIN=C.R,C.ROM,C.B,C.W,C.N,C.CANDIDATE
PINS=((Items,'9ce50ca8ba05b2d6c21f13b41b52258352db966c70b22ed113ee7971d34f694d'),
    (Star,'e3e7d0fed866697dcc1705e4385bcff1ff98556c32074790d4a2f068507f9e7a'),
    (StarImages,'6b82feeb52bbedcda50aedfb8ecaafe0e59fa7dba7a91df640b4c870a29553f5'))


@lru_cache(maxsize=1)
def reference(raw):
    return C.reference(C.inverse(raw))


@lru_cache(maxsize=8)
def controller(raw,identity=0,mode='mushroom',*,stock='star',images=False):
    assert identity in(0,1)and mode=='mushroom'and stock in('flower','oneup','star')
    for module,pin in PINS:assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    parent=reference(raw)
    if stock=='star':old=(StarImages if images else Star).controller(parent,identity)
    else:old=Items.controller(parent,identity,stock=stock,images=images)
    old_cookie=C.OLD_COOKIE.hex();new_cookie=raw[C.COOKIE:C.COOKIE+16].hex()
    assert old.count(C.Palette.CANDIDATE)>=2 and old.count(old_cookie)==1
    text=old.replace(C.Palette.CANDIDATE,PIN).replace(old_cookie,new_cookie)
    old_mapper=C.Palette.EDITS[2][2]
    assert text.count(old_mapper)==1
    text=text.replace(old_mapper,C.NEW.hex(),1)
    restored=text.replace(PIN,C.Palette.CANDIDATE).replace(new_cookie,old_cookie).replace(C.NEW.hex(),old_mapper,1)
    assert restored==old,'Only strict owning image/cookie/runtime56B authentication differs'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def source_check(raw,identity=0,stock='star'):
    Witness=Items.Witness
    base=SimpleNamespace(reference=C.inverse,Previous=Witness.Base.Previous)
    fn=lambda image,who=0,mode='mushroom':controller(image,who,mode,stock=stock)
    ns=dict(Witness.__dict__,Base=base,PIN=PIN,controller=fn)
    exec(compile(inspect.getsource(Witness.source_check),__file__+':actual-owning-candidate','exec'),ns)
    return ns['source_check'](raw,identity)


def metadata(raw):
    rows=[]
    for i in(0,1):
        for stock,images in(('flower',False),('oneup',False),('star',False),('star',True)):
            text=controller(raw,i,stock=stock,images=images)
            rows.append(dict(identity=i,stock=stock,images=images,Lua_SHA256=sha256(text.encode()).hexdigest(),bytes=len(text.encode())))
    return dict(ROM_SHA256=PIN,cookie=raw[C.COOKIE:C.COOKIE+16].hex(),controllers=rows,
        same_frozen_functional_bodies=True,actual_owning_candidate_CPU_required=True,output_files=0)


if __name__=='__main__':
    import argparse,json
    ap=argparse.ArgumentParser();ap.add_argument('--identity',type=int,choices=(0,1),default=0)
    ap.add_argument('--stock',choices=('flower','oneup','star'),default='star')
    ap.add_argument('--metadata',action='store_true');a=ap.parse_args()
    raw,composition=C.proposal(C.load_current())
    if a.metadata:q=metadata(raw)
    else:
        from unittest.mock import patch
        def forbid(*args,**kwargs):raise AssertionError('Source route attempted output')
        with patch.object(Path,'write_text',forbid),patch.object(Path,'write_bytes',forbid):
            q=source_check(raw,a.identity,a.stock)
        receipt=q['receipt'];natural=receipt.get('natural_star')or receipt.get('natural_stock')or receipt.get('natural_flower')
        natural={k:v for k,v in natural.items()if k in('born','mature','collector','collected','credit','erase','setup','popup','post_credit_returns','post_collector_returns','F_ready','credit_moves')}
        q=dict(passed=q['passed'],identity=a.identity,stock=a.stock,Lua_SHA256=q['controller_SHA256'],
            receipt_SHA256=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            Main=receipt.get('Main_updates'),entries=receipt.get('source_updates'),terminal=receipt.get('terminal'),natural=natural)
    print('RESULT '+json.dumps(dict(composition=composition,result=q,output_files=0),sort_keys=True,separators=(',',':')),flush=True)
