"""Explicit owning7c0f Jay facade;91dc is metadata/reference only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import current_jay_natural_stock_91dc_1116 as Frozen
import compose_dkjr_forced_entry_current_1116 as DK
import compose_dkjr_footer_bt91dc_current_1116 as Parent

R,ROM,H,N,W,Frames=Frozen.R,Frozen.ROM,Frozen.H,Frozen.N,Frozen.W,Frozen.Frames
PIN='7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
DK_SHA='67b6ccef60386789854c9f5a9634b92f5178301948b2f0004b0f640f2e9cb7b1'
PARENT_SHA='44f7ece4b1501a163d1e6551b0d40609fba5db525d2737ad94ff51d861868ab1'
OldBindings,OldPrimary=Frozen.bindings,Frozen.primary
COOKIE=Frozen.COOKIE
Foundation,GRANT_SHA=Frozen.Foundation,Frozen.GRANT_SHA


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN,'Exact owning current7c0f required'
    assert H(Path(DK.__file__).read_bytes())==DK_SHA and H(Path(Parent.__file__).read_bytes())==PARENT_SHA
    alpha=DK.inverse(raw);assert H(alpha)==DK.PIN
    old=Parent.inverse(alpha);assert H(old)==Frozen.PIN
    return old


@lru_cache(maxsize=1)
def bindings(raw):
    old=reference(raw);q=dict(OldBindings(old));q['bundle']=dict(q['bundle'],raw=raw)
    assert q['bundle']['raw']is raw
    # Complete Jay carriers plus shared Steve packet carriers stay exact;
    # no claims are made from only a header or short code prefix.
    pages=(218,222,232,234,331,332,371,375,379,336,338,167,304,306,307)
    carriers=[]
    for p in pages:
        at=1048592+p*1024;assert raw[at:at+1024]==old[at:at+1024]
        carriers.append(dict(page=p,SHA256=H(raw[at:at+1024])))
    for at,n in((Frozen.Foundation.prg(65,0xa696),162),(Frozen.Foundation.prg(94,0xb2ef),16)):
        assert raw[at:at+n]==old[at:at+n]
    hooks={}
    for name,row in q['hooks'].items():
        row=dict(row)
        if row['tag']>=128:
            bank=row['tag']&127;at=16+bank*8192+(row['PC']&8191)
            assert raw[at:at+16]==old[at:at+16]==bytes.fromhex(row['first16_hex'])
            row['bank_SHA256']=H(raw[16+bank*8192:16+(bank+1)*8192])
        hooks[name]=row
    q.update(hooks=hooks,owning_SHA256=PIN,metadata91dc_only_SHA256=Frozen.PIN,
        normalization_modules_SHA256=[DK_SHA,PARENT_SHA],preserved_carriers=carriers,
        actual_current_CPU_bytes_retained=True)
    return q


def primary(raw):return OldPrimary(reference(raw))


def cold(raw):
    q=bindings(raw)
    def bound(image):
        if image is raw:return q
        return OldBindings(image)
    def code(image):
        if image is raw:return primary(raw)
        return OldPrimary(image)
    with patch.object(Frozen,'bindings',bound),patch.object(Frozen,'primary',code):m=Frozen.cold(raw)
    assert m.bundle['raw']is raw and H(m.bundle['raw'])==PIN
    return m


def load_current_image():
    raw=ROM.read_bytes();assert H(raw)==PIN,'Exact owning current7c0f only';return raw
