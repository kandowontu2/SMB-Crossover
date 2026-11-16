"""Explicit 9826/cb95 CF observer binding; a2/bc5 are metadata only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import compose_mini_weapon_owner_a2_1116 as Mini
import compose_rogue_missile_9826_1116 as Rogue
import current_contra_force_readonly_1327_1116 as Previous

R,ROM,H,N,W,Frames=Previous.R,Previous.ROM,Previous.H,Previous.N,Previous.W,Previous.Frames
P=Previous.Previous
MINI_SHA='c644e50735327826d2f6de932954d501283ca963b4fc12d8408ae75519750a8c'
ROGUE_SHA='f38d2e2859631b1156ad5805d29a481a89f6e68e77b17a4f509de8af7d19d3a1'
PREVIOUS_SHA='2fd8fc83a6d3d55f967bb5ccef3efbcb25c7cd6638acc3ca7235ec13c7115c94'


@lru_cache(maxsize=2)
def reference(raw):
    assert isinstance(raw,bytes)and H(raw)in(Mini.CANDIDATE,Rogue.CANDIDATE),'Exact owning9826 or cb95 only'
    for module,pin in((Mini,MINI_SHA),(Rogue,ROGUE_SHA),(Previous,PREVIOUS_SHA)):assert H(Path(module.__file__).read_bytes())==pin
    old=Rogue.inverse(raw)if H(raw)==Rogue.CANDIDATE else raw
    assert H(old)==Mini.CANDIDATE
    old=Mini.inverse(old);assert H(old)==Mini.PARENT
    return old


@lru_cache(maxsize=2)
def bindings(raw):
    old=reference(raw);base=Previous.bindings(old);q=dict(base,bundle=dict(base['bundle'],raw=raw))
    assert raw[P.CHR+935*1024:P.CHR+959*1024]==base['carrier']
    for row in base['current_proof']['protected_native_callers']:
        at=16+row['bank']*8192+(row['PC']&8191);assert raw[at:at+row['bytes']]==old[at:at+row['bytes']]
    points={};changed=[]
    for key,point in base['points'].items():
        point=dict(point)
        if point['tag']>=128:
            at=point['source_file'];actual=raw[at:at+8]
            if list(actual)!=point['bytes']:changed.append(point['name'])
            point['bytes']=list(actual);bank=point['tag']&127
            point['owning_bank_SHA256']=H(raw[16+bank*8192:16+(bank+1)*8192])
        points[key]=point
    q['points']=points;proof=dict(base['current_proof'])
    proof.update(owning_SHA256=H(raw),reference_a2_only_SHA256=H(old),normalizers=[MINI_SHA,ROGUE_SHA],
        current_native_profile_points_refreshed=True,changed_point_prefixes=changed,
        actual_current_CPU_bytes_retained=True,old_1327_a2_APIs_unchanged=True,
        bank79_121=[dict(bank=bank,reference_a2_SHA256=H(old[16+bank*8192:16+(bank+1)*8192]),
            owning_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))for bank in(79,121)])
    q['current_proof']=proof;return q


def bound(raw):
    return bindings(raw)if H(raw)in(Mini.CANDIDATE,Rogue.CANDIDATE)else Previous.bound(raw)


def cold(raw):
    q=bindings(raw)
    with patch.object(P,'bindings',bound):m=P.cold(raw)
    assert m.bundle['raw']is raw and type(m)is W.ControllerBus;return m


def empty(m,key='burns'):
    assert key=='burns';return P.empty(m)


def load_current_image():
    raw=ROM.read_bytes();assert H(raw)in(Mini.CANDIDATE,Rogue.CANDIDATE);return raw
