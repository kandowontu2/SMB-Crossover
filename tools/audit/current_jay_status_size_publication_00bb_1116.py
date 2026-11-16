"""Strict owning1327; public00bb metadata/reference only, actual CPU1327."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import compose_jay_status_size_publication_00bb_1116 as C
import current_jay_natural_stock_00bb_1116 as Previous

R,ROM,H,N,W,Frames=Previous.R,Previous.ROM,Previous.H,Previous.N,Previous.W,Previous.Frames
PIN,COOKIE=C.CANDIDATE,C.COOKIE
Foundation,GRANT_SHA=Previous.Foundation,C.GRANT_SHA
PREVIOUS_SHA='4bff33bfc8895d86dc1a405ebd0d7b2b041ca27d73c7d536068588b7e372abb1'
COMPOSER_SHA='7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c'


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN,'Exact owning1327 only'
    assert H(Path(C.__file__).read_bytes())==COMPOSER_SHA and H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    parent=C.inverse(raw);assert H(parent)==Previous.PIN;return parent


@lru_cache(maxsize=1)
def bindings(raw):
    parent=reference(raw);old=Previous.bindings(parent);q=dict(old,bundle=dict(old['bundle'],raw=raw))
    assert q['bundle']['raw']is raw
    owned={i for at,a,_ in C.spans()for i in range(at,at+len(a))}
    assert all(a==b for i,(a,b)in enumerate(zip(parent,raw,strict=True))if i not in owned)
    carriers=[]
    for page in(218,222,232,234,331,332,371,375,379,336,338,167,304,306,307,739):
        at=1048592+page*1024;changed=[i for i in range(at,at+1024)if raw[i]!=parent[i]]
        assert set(changed)<=owned
        carriers.append(dict(page=page,SHA256=H(raw[at:at+1024]),changed=len(changed)))
    hooks={}
    for name,row in q['hooks'].items():
        row=dict(row)
        if row['tag']>=128:
            bank=row['tag']&127;at=16+8192*bank+(row['PC']&8191)
            assert raw[at:at+16]==parent[at:at+16]==bytes.fromhex(row['first16_hex'])
            row['bank_SHA256']=H(raw[16+8192*bank:16+8192*(bank+1)])
        elif name=='JayPrivateUpdate':
            assert(row['PC'],row['tag'])==(0xb800,3)
            at=1048592+232*1024;assert raw[at:at+50]==C.NEW_MAIN;row['first16_hex']=raw[at:at+16].hex()
        hooks[name]=row
    sites=(534328,774911,1429421);assert all(raw[at:at+16]==COOKIE for at in sites)
    q.update(hooks=hooks,cookie=COOKIE.hex(),owning_SHA256=PIN,metadata00bb_only_SHA256=Previous.PIN,
        normalization_module_SHA256=COMPOSER_SHA,preserved_carriers=carriers,all_three_ROM_cookie_files=list(sites),
        all_three_ROM_cookies_preserved=False,all_three_ROM_cookies_rebound=True,
        actual_current_CPU_bytes_retained=True,original_native_status_and_size_publication=True)
    return q


def primary(raw):return Previous.primary(reference(raw))


def cold(raw):
    q=bindings(raw);frozen=Previous.Previous.Frozen
    prior_bindings,prior_primary=frozen.bindings,frozen.primary
    def bound(image):return q if image is raw else prior_bindings(image)
    def code(image):return primary(raw)if image is raw else prior_primary(image)
    with patch.object(frozen,'bindings',bound),patch.object(frozen,'primary',code),patch.object(frozen,'COOKIE',COOKIE):m=frozen.cold(raw)
    assert m.bundle['raw']is raw and H(m.bundle['raw'])==PIN
    assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(1,2,3))==(COOKIE,)*3
    assert bytes(m.ram[3][0x17c0:0x17f6])==C.Plan.TRANSFER64[:54]
    assert bytes(m.ram[3][0x17f6:0x1800])==C.TAIL
    assert bytes(m.ram[3][0x1800:0x1832])==C.NEW_MAIN and bytes(m.ram[3][0x1ed7:0x1edf])==C.LEAF
    assert bytes(m.ram[3][:0x8c0])==primary(raw)
    return m


def load_current_image():
    raw=ROM.read_bytes();assert H(raw)==Previous.PIN,'Installed public00bb only before promotion'
    return C.proposal(raw)[0]
