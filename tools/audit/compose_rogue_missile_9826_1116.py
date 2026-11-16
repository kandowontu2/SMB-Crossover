"""Strict leased2B9826→cb95 composer/inverse, RAM only."""
from pathlib import Path
from functools import lru_cache
import json
import plan_rogue_missile_mini9826_1116 as Plan

R,ROM,H=Plan.R,Plan.ROM,Plan.H
PARENT=Plan.Mini.CANDIDATE
CANDIDATE='cb95eb8dff9929c8162e019d5e3f33e45b570946f5281c07584a9f11cacdba07'
GRANT=R/'docs/qa/allocations/rogue-missile-9826-source-root-1116.json'
GRANT_SHA='6029cd1290975bef1e59a20e2d89287385656610daab1ac5ca5aa56aacaf927d'
PLAN_SHA='ec241221bd4408f68f8aa35b5accdee2a1ab48d2fbbc8ce5a310fb182b0fa4ac'
AT,OLD,NEW=Plan.Rogue.AT,Plan.Rogue.OLD,Plan.Rogue.NEW


def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA and H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    g=json.loads(GRANT.read_bytes());assert(g['parent_SHA256'],g['candidate_SHA256'])==(PARENT,CANDIDATE)
    assert g['source_composition_in_memory_and_actual_CPU_authorized']and not g['physical_ROM_files_Mesen_Downloads_delivery_authorized']
    assert g['owned_spans']==[dict(file=AT,bytes=2,old_hex=OLD.hex(),new_hex=NEW.hex())]
    return g


def inverse(raw):
    lease();assert isinstance(raw,bytes)and H(raw)==CANDIDATE and raw[AT:AT+2]==NEW
    parent=raw[:AT]+OLD+raw[AT+2:];assert H(parent)==PARENT;return parent


@lru_cache(maxsize=1)
def proposal(parent):
    lease();assert isinstance(parent,bytes)and H(parent)==PARENT
    d=Plan.descriptor(parent);assert d['receipt_SHA256']=='a595487369d33fc3a16d3960c1a586a42a5a06004bd94a4b78c810f41a3b98d7'
    assert parent[AT:AT+2]==OLD
    raw=parent[:AT]+NEW+parent[AT+2:];assert H(raw)==CANDIDATE and inverse(raw)==parent
    assert[i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b]==[AT]
    protected=[]
    for owner,spans in(('Mini20',Plan.Mini.SPANS),('Sonic94',Plan.Sonic.spans())):
        for at,old,new in spans:assert raw[at:at+len(new)]==parent[at:at+len(new)]==new
        protected.append(owner)
    return raw,dict(passed=True,parent_SHA256=PARENT,candidate_SHA256=CANDIDATE,grant_SHA256=GRANT_SHA,
        owned_bytes=2,changed_bytes=1,all_unowned_bytes_exact=True,protected=protected,
        strict_portable_inverse=True,outputs=0,native=False)
