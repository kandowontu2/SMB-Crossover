"""Strict owning9826 Sonic; a2 reference only, all94 Sonic bytes preserved."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import current_sonic_ceiling_complete_a2d9_1116 as Previous
import compose_mini_weapon_owner_a2_1116 as C

R,ROM,H,N,W,Frames=Previous.R,Previous.ROM,Previous.H,Previous.N,Previous.W,Previous.Frames
PIN,COOKIE,FORMS=C.CANDIDATE,Previous.COOKIE,Previous.FORMS
PREVIOUS_SHA='13b1050ecd45ad30d0f6f51f385d3eda6389d9e6d1bfdf11fa302557103571ff'

@lru_cache(maxsize=1)
def reference(raw):
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    return C.inverse(raw)

@lru_cache(maxsize=1)
def bindings(raw):
    parent=reference(raw);old=Previous.bindings(parent);q=dict(old,bundle=dict(old['bundle'],raw=raw))
    foundation=Previous.Previous
    page=lambda p:raw[foundation.CHR+p*1024:foundation.CHR+(p+1)*1024]
    kernel=b''.join(page(p)for p in foundation.CODE_PAGES);meta=page(328)
    assert kernel==old['kernel']and meta==old['metadata']and raw[1034472:1034488]==COOKIE
    assert all(page(row['page'])==parent[foundation.CHR+row['page']*1024:foundation.CHR+(row['page']+1)*1024]for row in old['packet_pages'])
    def loaded(pc):
        if 0xa000<=pc<0xc000:return kernel[pc-0xa000:]
        if 0xd000<=pc<0xd400:return meta[pc-0xd000:]
        if 0xd400<=pc<0xd800:return page(333)[pc-0xd400:]
        if 0xd800<=pc<0xdc00:return page(334)[pc-0xd800:]
        raise AssertionError(('Outside owning Sonic code',hex(pc)))
    q.update(kernel=kernel,metadata=meta,loaded=loaded,owning_SHA256=PIN,reference_a2_only_SHA256=C.PARENT,
        Sonic94_preserved=True,actual_current_CPU_bytes_retained=True,combined_grant_SHA256=C.GRANT_SHA)
    return q

def state(m):return Previous.state(m)

def cold(raw,form):
    q=bindings(raw);foundation=Previous.Previous;old=foundation.bindings
    with patch.object(foundation,'bindings',lambda image:q if image is raw else old(image)):
        m,info=foundation.cold(raw,form)
    assert m.bundle['raw']is raw and H(m.bundle['raw'])==PIN
    assert bytes(m.ram[3][0x1b26:0x1b39])==Previous.C.NEW
    assert bytes(m.ram[2][0x108f:0x1092])==Previous.C.HOOK and bytes(m.ram[2][0x1344:0x137c])==Previous.C.HELPER
    assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(COOKIE,)*2
    info.update(actual_CPU_SHA256=PIN,reference_a2_metadata_only=True,source_menu_vblank_limit=True);return m,info
