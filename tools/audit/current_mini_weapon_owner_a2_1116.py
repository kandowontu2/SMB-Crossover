"""Actual 9826 CPU; e32f projection is metadata only, old APIs unchanged."""
from functools import lru_cache
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import inspect
import compose_mini_weapon_owner_a2_1116 as Compose
import current_mini_weapon_owner_1116 as Previous

R,ROM,W,N,Frames,H=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.Frames,Previous.H
PIN=Compose.CANDIDATE
PREVIOUS_SHA='bdf56ab0a1fa66e25dde6814f9577ea450fd8d8c1540e9b44fe0df4189d06d3c'
KERNEL_SHA,PAYLOAD_SHA,COOKIE,CODE_AT=Previous.KERNEL_SHA,Previous.PAYLOAD_SHA,Previous.COOKIE,Previous.CODE_AT
Inventory=Previous.Inventory

@lru_cache(maxsize=1)
def reference(raw):
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    parent=Compose.inverse(raw);old=Compose.Plan.Reader.reference(parent)
    projected=Compose.Plan.Mini.proposal(old)[0];assert H(projected)==Previous.PIN;return projected

@lru_cache(maxsize=1)
def bindings(raw):
    projected=reference(raw);q=deepcopy(Previous.bindings(projected));q['bundle']['raw']=raw
    assert raw[CODE_AT:CODE_AT+7168]==projected[CODE_AT:CODE_AT+7168]
    assert raw[536595:536611]==projected[536595:536611]==COOKIE
    for h in q['hooks'].values():
        if 'file_offset'in h:
            at=h['file_offset'];assert raw[at:at+16]==bytes.fromhex(h['first16_hex'])
            bank=(at-16)//8192;h['bank_SHA256']=H(raw[16+bank*8192:16+(bank+1)*8192])
    for row in q['full_bank_pins']:
        at=16+row['bank']*8192;row.update(actual_SHA256=H(raw[at:at+8192]),metadata_projection_SHA256=H(projected[at:at+8192]),
            changed_from_projection=sum(a!=b for a,b in zip(raw[at:at+8192],projected[at:at+8192],strict=True)))
        row.pop('changed_bytes',None)
    q.update(actual_CPU_SHA256=PIN,metadata_reference_only_SHA256=Previous.PIN,combined_Sonic94_preserved=True,
        owning_grant_SHA256=Compose.GRANT_SHA,projection_executed=False)
    return q

def metadata(raw):return{k:v for k,v in bindings(raw).items()if k!='bundle'}

exec(compile(inspect.getsource(Previous.Previous.cold),str(Path(__file__))+':actual-9826-cold','exec'),globals())
_actual_cold=cold
def cold(raw,report=False):
    m,q=_actual_cold(raw,True)
    q['scope']='Actual9826 compiled UI/cold16 and returned public/original MiniStep; projected e32f metadata only, source menu lacks real vblank'
    return(m,q)if report else m
