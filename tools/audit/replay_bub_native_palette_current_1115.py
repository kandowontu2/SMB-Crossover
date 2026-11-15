"""Candidate-bound frozen natural M/F/L controls and actual three-scene observers."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import inspect
import compose_bub_native_palette_current_1115 as C
import replay_bub_flower_margin_40a_1115 as Flower
import replay_bub_oneup_40a_1115 as Life
import replay_bub_three_images_40a_1115 as BubImages
import replay_bob_three_images_40a_1115 as BobImages

R,ROM,W,N,B,PIN=C.R,C.ROM,C.W,C.N,C.B,C.CANDIDATE
Witness=Flower.Witness
PINS=((Flower,'88a452e94489dea2749403abc193b7c4a2578b7a2e837183a0cf102af3d85b76'),
    (Life,'4794173b925520ffd5fedbc917a36b25dc36f45cae5ce52e2e5d66a7019d52fe'),
    (BubImages,'59fa9dbff4b9aa9d13759651c0baf30ed3ee9b116244093f84a1148019293526'),
    (BobImages,'9a35298e24168eceb6d06dffd9111aa8a1136b00a789ff38a8b3b39d61dc85a7'))

@lru_cache(maxsize=6)
def controller(raw,identity=0,mode='mushroom',*,stock='flower',images=False):
    assert identity in(0,1)and mode=='mushroom'and stock in('flower','oneup')
    assert not images or stock=='flower'
    for module,pin in PINS:assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    parent=C.inverse(raw)
    module=(BubImages if identity==0 else BobImages)if images else Flower if stock=='flower'else Life
    old=module.controller(parent,identity,mode)
    new_cookie=raw[C.COOKIE:C.COOKIE+16].hex();old_cookie=C.OLD_COOKIE.hex()
    assert old.count(C.PARENT)>=2 and old.count(old_cookie)==1
    text=old.replace(C.PARENT,PIN).replace(old_cookie,new_cookie)
    assert text.replace(PIN,C.PARENT).replace(new_cookie,old_cookie)==old
    # Runtime authentication is passive and occurs after the inherited full
    # two-header admission, before ordinary policy starts.
    marker="assert(header(2)==cookie and header(3)==cookie,'Both complete current source cookies')"
    checks=[]
    for file,before,after in C.EDITS:
        if file==1501131:bank,pc=2,0xd3bb
        elif file==1499208:bank,pc=3,0xb438
        elif file==1731082:bank,pc=3,0xbdfa
        elif file==1731088:bank,pc=3,0xbe00
        else:raise AssertionError(file)
        checks.append('do local s="'+after+'";for k=1,#s,2 do assert(work('+str(bank)+','+str(pc)+'+(k-1)//2)==tonumber(s:sub(k,k+1),16),"Exact allocated Bub palette component")end end')
    text=Flower.once(text,marker,marker+'\n '+('\n '.join(checks)))
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text

def source_check(raw,identity=0,stock='flower'):
    base=SimpleNamespace(reference=C.inverse,Previous=Witness.Base.Previous)
    fn=lambda image,who=0,mode='mushroom':controller(image,who,mode,stock=stock)
    ns=dict(Witness.__dict__,Base=base,PIN=PIN,controller=fn)
    exec(compile(inspect.getsource(Witness.source_check),str(Path(__file__))+':actual-candidate-source','exec'),ns)
    return ns['source_check'](raw,identity)

def metadata(raw):
    return dict(ROM_SHA256=PIN,cookie=raw[C.COOKIE:C.COOKIE+16].hex(),
        controllers=[dict(identity=i,stock=s,images=pic,SHA256=sha256(controller(raw,i,stock=s,images=pic).encode()).hexdigest())
            for i in(0,1)for s,pic in(('flower',False),('oneup',False),('flower',True))],output_files=0)
