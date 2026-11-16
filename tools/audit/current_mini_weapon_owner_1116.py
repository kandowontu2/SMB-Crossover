"""Strict e32f actual CPU; inverse1327 is reference metadata only."""
from functools import lru_cache
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import inspect
import compose_mini_weapon_owner_1116 as Compose
import current_mini_stock_1327_1116 as Previous

R,ROM,W,N,Frames,H=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.Frames,Previous.H
PIN=Compose.CANDIDATE
PREVIOUS_SHA='4c04b9df54ef434dd11aa02d8ed1aab59b123652705f857b4dfca3018e5a036f'
KERNEL_SHA,PAYLOAD_SHA,COOKIE,CODE_AT=Previous.KERNEL_SHA,Previous.PAYLOAD_SHA,Previous.COOKIE,Previous.CODE_AT
Inventory=Previous.Inventory

@lru_cache(maxsize=1)
def reference(raw):
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    assert isinstance(raw,bytes)and H(raw)==PIN
    return Compose.inverse(raw)

@lru_cache(maxsize=1)
def bindings(raw):
    parent=reference(raw);q=deepcopy(Previous.bindings(parent));q['bundle']['raw']=raw
    assert raw[CODE_AT:CODE_AT+7168]==parent[CODE_AT:CODE_AT+7168]
    q.update(actual_CPU_SHA256=PIN,metadata_reference_only_SHA256=Compose.PARENT,Mini7168_cookie_headers_exact=True)
    actual=raw[CODE_AT+1]+256*raw[CODE_AT+2];h=q['hooks']['MiniHostMain'];h['reference_alias_PC']=h['PC'];h.update(PC=actual,physical=3*8192+(actual&8191),first16_hex=raw[CODE_AT+actual-0xa000:CODE_AT+actual-0xa000+16].hex())
    q.update(native_owner_repair_changed_bytes=20,Mini_private_source_code_changes=0,source_helpers_or_game_bytes_changed=True,source_helpers_changed=False)
    at=16+79*8192;q['full_bank_pins'].append(dict(bank=79,actual_SHA256=H(raw[at:at+8192]),reference_SHA256=H(parent[at:at+8192]),changed_bytes=20))
    return q

def metadata(raw):return{k:v for k,v in bindings(raw).items()if k!='bundle'}

exec(compile(inspect.getsource(Previous.cold),str(Path(__file__))+':actual-e32f-cold','exec'),globals())
_actual_cold=cold
def cold(raw,report=False):
    m,q=_actual_cold(raw,True)
    q['scope']='Actual e32f compiled UI/cold16 and returned public/original MiniStep; inverse1327/00bb reference metadata only, no native/cadence claim'
    return(m,q)if report else m
