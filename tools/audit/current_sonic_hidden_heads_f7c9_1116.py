"""Owningf7c9 source facade; exact1327 is symbols/reference only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import compose_sonic_hidden_heads_1327_1116 as C
import audit_sonic_stock_foundation_1327_1116 as Previous

R,ROM,H,N,W,Frames=Previous.R,Previous.ROM,Previous.H,Previous.N,Previous.W,Previous.Frames
PIN,COOKIE=C.CANDIDATE,C.COOKIE
FORMS=Previous.FORMS
COMPOSER_SHA='ae3eecbb90b95ba3768cea6c1f1fc76baec9aadbd5bed35c48901b1616461865'
PREVIOUS_SHA='c388c7f1f0b7441a472ade0de2d981f1b07d322c529cae56d806928510a579bc'


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN,'Exact owningf7c9 only'
    assert H(Path(C.__file__).read_bytes())==COMPOSER_SHA and H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    parent=C.inverse(raw);assert H(parent)==Previous.PIN;return parent


@lru_cache(maxsize=1)
def bindings(raw):
    parent=reference(raw);old=Previous.bindings(parent);q=dict(old,bundle=dict(old['bundle'],raw=raw))
    page=lambda p:raw[Previous.CHR+p*1024:Previous.CHR+(p+1)*1024]
    kernel=b''.join(page(p)for p in Previous.CODE_PAGES);meta=page(328)
    assert kernel[0x1b26:0x1b39]==C.NEW and meta[0x344:0x371]==C.HELPER
    assert COOKIE==bytes.fromhex('a72b01')+sha256(b''.join(page(p)for p in Previous.COOKIE_PAGES)).digest()[:13]
    assert raw[1034472:1034488]==COOKIE
    owned={i for at,a,_ in C.spans()for i in range(at,at+len(a))}
    assert all(a==b for i,(a,b)in enumerate(zip(parent,raw,strict=True))if i not in owned)
    def loaded(pc):
        if 0xa000<=pc<0xc000:return kernel[pc-0xa000:]
        if 0xd000<=pc<0xd400:return meta[pc-0xd000:]
        if 0xd400<=pc<0xd800:return page(333)[pc-0xd400:]
        if 0xd800<=pc<0xdc00:return page(334)[pc-0xd800:]
        raise AssertionError(('Outside owning Sonic code',hex(pc)))
    assert q['services']==old['services'] and meta[0x100:0x172]==old['metadata'][0x100:0x172]
    q.update(cookie=COOKIE,kernel=kernel,metadata=meta,loaded=loaded,
        packet_pages=[dict(page=p,SHA256=H(page(p)))for p in Previous.COOKIE_PAGES],
        owning_SHA256=PIN,reference1327_only_SHA256=C.PIN,composer_SHA256=COMPOSER_SHA,
        actual_current_CPU_bytes_retained=True,all_unowned_bytes_exact=True)
    return q


def state(m):return Previous.state(m)


def cold(raw,form):
    q=bindings(raw);old=Previous.bindings
    with patch.object(Previous,'bindings',lambda image:q if image is raw else old(image)):
        m,info=Previous.cold(raw,form)
    assert m.bundle['raw']is raw and H(m.bundle['raw'])==PIN
    assert bytes(m.ram[3][0x1b26:0x1b39])==C.NEW and bytes(m.ram[2][0x1344:0x1371])==C.HELPER
    assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(COOKIE,)*2
    return m,info


def load_current_image():
    raw=ROM.read_bytes()
    if H(raw)==C.PIN:return C.proposal(raw)[0]
    assert H(raw)==PIN,'Only exact parent1327 or owningf7c9';assert C.proposal(C.inverse(raw))[0]==raw;return raw
