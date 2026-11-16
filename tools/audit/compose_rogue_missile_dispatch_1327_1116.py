"""Strict leased2B Rogue missile composer/inverse; no files or emulator."""
from pathlib import Path
import json
import plan_rogue_missile_dispatch_1327_1116 as Plan

R,ROM,H,PIN=Plan.R,Plan.ROM,Plan.H,Plan.PARENT
CANDIDATE='54b146972d416f9eeab1c2b62b0ee445dbaa99c345ea6fa88240cb3d70fe24f8'
GRANT=R/'docs/qa/allocations/rogue-missile-source-root-1116.json'
GRANT_SHA='7f6242616e6d2a46e1b4f9f53606cfeb109c607d5d6b572c3bce5d9f628a3ed7'
PLAN_SHA='25bd091f5040cc68eedf0b441c0724faf12183d67cc8508bb75aee405065b16d'
AT,OLD,NEW=Plan.AT,Plan.OLD,Plan.NEW


def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA and H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    g=json.loads(GRANT.read_text());assert(g['parent_SHA256'],g['candidate_SHA256'])==(PIN,CANDIDATE)
    assert g['source_composition_in_memory_and_actual_CPU_authorized']and not g['physical_ROM_files_Mesen_Downloads_delivery_authorized']
    assert g['owned_spans']==[dict(file=AT,bytes=2,old_hex=OLD.hex(),new_hex=NEW.hex())]
    return g


def spans():lease();return((AT,OLD,NEW),)


def proposal(raw):
    lease();assert isinstance(raw,bytes)and H(raw)==PIN
    d=Plan.descriptor(raw);assert d['receipt_SHA256']=='6ac12cede977a6ce1dba92d54775755153246570761fe23d38be505d6b8feebe'
    assert raw[AT:AT+2]==OLD
    out=raw[:AT]+NEW+raw[AT+2:];assert H(out)==CANDIDATE
    assert [i for i,(a,b)in enumerate(zip(raw,out,strict=True))if a!=b]==[AT]
    assert inverse(out)==raw
    return out,dict(parent_SHA256=PIN,candidate_SHA256=CANDIDATE,grant_SHA256=GRANT_SHA,
        owned_bytes=2,changed_bytes=1,all_unowned_bytes_exact=True,strict_inverse=True,outputs=0)


def inverse(raw):
    lease();assert isinstance(raw,bytes)and H(raw)==CANDIDATE and raw[AT:AT+2]==NEW
    old=raw[:AT]+OLD+raw[AT+2:];assert H(old)==PIN;return old
