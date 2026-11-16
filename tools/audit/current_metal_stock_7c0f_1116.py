"""Explicit current7c0f Metal execution; strict91dc is reference metadata only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import inspect
import compose_dkjr_forced_entry_current_1116 as DK
import current_metal_stock_91dc_1116 as Previous

R,ROM,W,N,Frames,digest=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.Frames,Previous.digest
PIN='7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
REFERENCE=Previous.PIN
DK_SHA='67b6ccef60386789854c9f5a9634b92f5178301948b2f0004b0f640f2e9cb7b1'
PARENT_SHA='44f7ece4b1501a163d1e6551b0d40609fba5db525d2737ad94ff51d861868ab1'
OLD_SHA='5afbce524f5bbf9bd4a966bb39e7fb95c62b0e8a17820d37d0c56a9aa5b0e3ff'
COOKIE,NAV=Previous.COOKIE,Previous.NAV
labels=Previous.labels


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Only exact current7c0f Metal input'
    assert digest(Path(DK.__file__).read_bytes())==DK_SHA and digest(Path(DK.Parent.__file__).read_bytes())==PARENT_SHA
    assert digest(Path(Previous.__file__).read_bytes())==OLD_SHA
    alpha=DK.inverse(raw);assert digest(alpha)==DK.PIN
    old=DK.Parent.inverse(alpha);assert digest(old)==REFERENCE
    return old


@lru_cache(maxsize=1)
def payload(raw):
    old=reference(raw);actor,renderer,extra,proof=Previous.payload(old)
    for pages in(Previous.Inventory.ACTOR_PAGES,Previous.Inventory.RENDER_PAGES,(499,)):
        for page in pages:
            at=1048592+page*1024;assert raw[at:at+1024]==old[at:at+1024],('Metal current carrier',page)
    for role in proof['residents_exact_bc5']:
        at,size=role['file'],role['bytes'];assert raw[at:at+size]==old[at:at+size],role['role']
    q=dict(proof,actual_image_SHA256=PIN,reference91dc_SHA256=REFERENCE,actual_execution_required=True,
        typed_inverse='Strict DK C.inverse7c0f→Alpha a3fb→Parent.inverse91dc for symbols/reference only',
        all_Metal_carriers_full499_and_residents_preserved=True,old91dc_APIs_unchanged=True)
    return actor,renderer,extra,q


@lru_cache(maxsize=1)
def bundle(raw):
    payload(raw);old=reference(raw);b=dict(Previous.bundle(old));b['raw']=raw
    # Current native anchors are checked against owning bytes, with fresh banks.
    for name in('GameLoop','IdleLoop','HandlePowerUpCollision','NrPickupCollision','NrPickup','FloateyNumbersCore'):
        at=W.location(b,name);assert raw[at:at+64]==old[at:at+64],name
    return b


# Compile the two frozen, reviewed transport functions into THIS namespace.
# Their payload/bundle/PIN globals above use actual7c0f; Previous remains strict.
assert digest(Path(Previous.__file__).read_bytes())==OLD_SHA
exec(compile(inspect.getsource(Previous.check_loaded),str(Path(__file__))+':same-readback-contract','exec'),globals())
exec(compile(inspect.getsource(Previous.cold),str(Path(__file__))+':actual-current-cold','exec'),globals())
