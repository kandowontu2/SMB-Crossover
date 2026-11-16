"""Explicit owning00bb Jay bridge; exact7c0f is metadata/reference only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import re
import compose_metal_life_snapshot_root_1116 as Compose
import current_jay_natural_stock_7c0f_1116 as Previous

R,ROM,H,N,W,Frames=Previous.R,Previous.ROM,Previous.H,Previous.N,Previous.W,Previous.Frames
PIN='00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21'
COMPOSER_SHA='c9051abcb700dbb1401c0fdf8de2cfd8da7267cdbb457610454c13f867a5cd54'
PREVIOUS_SHA='b8c128b51bd47cb2c3f7dce828277a06c54ed034b7d2e1071f667fee41016aeb'
COOKIE,Foundation,GRANT_SHA=Previous.COOKIE,Previous.Foundation,Previous.GRANT_SHA
OldBindings,OldPrimary=Previous.bindings,Previous.primary


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN,'Exact owning current00bb only'
    assert H(Path(Compose.__file__).read_bytes())==COMPOSER_SHA and H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    old=Compose.inverse(raw);assert H(old)==Previous.PIN;return old


@lru_cache(maxsize=1)
def bindings(raw):
    old=reference(raw);q=dict(OldBindings(old));q['bundle']=dict(q['bundle'],raw=raw)
    assert q['bundle']['raw']is raw
    pages=(218,222,232,234,331,332,371,375,379,336,338,167,304,306,307)
    carriers=[]
    for p in pages:
        at=1048592+p*1024;assert raw[at:at+1024]==old[at:at+1024]
        carriers.append(dict(page=p,SHA256=H(raw[at:at+1024])))
    cookie_sites=[m.start()for m in re.finditer(re.escape(COOKIE),old)]
    assert len(cookie_sites)==3
    assert cookie_sites==[m.start()for m in re.finditer(re.escape(COOKIE),raw)]
    for at in cookie_sites:assert raw[at:at+16]==old[at:at+16]==COOKIE
    for at,n in((Foundation.prg(65,0xa696),162),(Foundation.prg(94,0xb2ef),16)):
        assert raw[at:at+n]==old[at:at+n]
    hooks={}
    for name,row in q['hooks'].items():
        row=dict(row)
        if row['tag']>=128:
            bank=row['tag']&127;at=16+8192*bank+(row['PC']&8191)
            assert raw[at:at+16]==old[at:at+16]==bytes.fromhex(row['first16_hex'])
            row['bank_SHA256']=H(raw[16+8192*bank:16+8192*(bank+1)])
        hooks[name]=row
    q.update(hooks=hooks,owning_SHA256=PIN,metadata7c0f_only_SHA256=Previous.PIN,
        normalization00bb_module_SHA256=COMPOSER_SHA,preserved_carriers=carriers,
        all_three_ROM_cookie_files=cookie_sites,all_three_ROM_cookies_preserved=True,
        actual_current_CPU_bytes_retained=True)
    return q


def primary(raw):return OldPrimary(reference(raw))


def cold(raw):
    q=bindings(raw);frozen=Previous.Frozen
    def bound(image):
        if image is raw:return q
        return frozen_old_bindings(image)
    def code(image):
        if image is raw:return primary(raw)
        return frozen_old_primary(image)
    frozen_old_bindings,frozen_old_primary=frozen.bindings,frozen.primary
    with patch.object(frozen,'bindings',bound),patch.object(frozen,'primary',code):m=frozen.cold(raw)
    assert m.bundle['raw']is raw and H(m.bundle['raw'])==PIN
    return m


def load_current_image():
    raw=ROM.read_bytes();assert H(raw)==PIN,'Exact owning current00bb only';return raw
