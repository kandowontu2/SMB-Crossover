"""Exact source-only 00bb execution; frozen 7c0f remains reference-only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import inspect
import compose_metal_life_snapshot_root_1116 as Compose
import current_metal_stock_7c0f_1116 as Previous

R,ROM,W,N,Frames,digest=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.Frames,Previous.digest
PIN=Compose.CANDIDATE
COOKIE,NAV,labels=Compose.COOKIE,Previous.NAV,Previous.labels
COMPOSER_SHA='c9051abcb700dbb1401c0fdf8de2cfd8da7267cdbb457610454c13f867a5cd54'
PREVIOUS_SHA='6bd911e82b9891ce1c9ae39d4f8c3acdf2492731c83edf23612f27d76a857956'


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN
    assert digest(Path(Compose.__file__).read_bytes())==COMPOSER_SHA and digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    Compose.lease();old=Compose.inverse(raw);assert digest(old)==Previous.PIN;return old


@lru_cache(maxsize=1)
def payload(raw):
    old=reference(raw);actor,previous_renderer,extra,proof=Previous.payload(old)
    inventory=Previous.Previous.Inventory
    current_actor=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in inventory.ACTOR_PAGES)
    renderer=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in inventory.RENDER_PAGES)
    page=1048592+499*1024;assert current_actor==actor and raw[page:page+1024]==extra
    changed=[i for i,(a,b)in enumerate(zip(previous_renderer,renderer,strict=True))if a!=b]
    assert changed==[0xd4ad-0xcd00,0xd4ae-0xcd00]and renderer[changed[0]:changed[-1]+1]==bytes.fromhex('1036')
    for role in proof['residents_exact_bc5']:
        at,size=role['file'],role['bytes'];assert raw[at:at+size]==old[at:at+size].replace(Previous.COOKIE,COOKIE)
    q=dict(proof,actual_image_SHA256=PIN,reference7c0f_SHA256=Previous.PIN,new_cookie=COOKIE.hex(),
        only_two_renderer_bytes_changed=changed,actual_execution_required=True,portable_inverse=True)
    return actor,renderer,extra,q


@lru_cache(maxsize=1)
def bundle(raw):
    payload(raw);b=dict(Previous.bundle(reference(raw)));b['raw']=raw;return b


assert digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
exec(compile(inspect.getsource(Previous.Previous.check_loaded),str(Path(__file__))+':new-cookie-readback','exec'),globals())
exec(compile(inspect.getsource(Previous.Previous.cold),str(Path(__file__))+':actual00bb-cold','exec'),globals())
