"""Explicit174fa binding-only inverse; actual source CPU retains all52 Bub bytes."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import compose_bub_native_palette_current_1115 as Palette
import replay_prince_natural_stock_fast_40a_1115 as Old

C,N,W,Game,Frames=Old.C,Old.N,Old.W,Old.Base.Cold.Game,Old.Base.Cold.Frames
PIN=Palette.CANDIDATE
PALETTE_SOURCE='1b3e655bb5d44a0230d690d6dcc7ebd70959e5200fc661ece80f0758f95f58e6'

def reference(raw):
    assert isinstance(raw,bytes)and C.digest(raw)==PIN,'Exact typed174fa Prince input required'
    assert C.digest(Path(Palette.__file__).read_bytes())==PALETTE_SOURCE
    parent=Palette.inverse(raw);assert C.digest(parent)==Old.PIN and Palette.proposal(parent)[0]==raw
    assert C.Packet.extract(parent)==C.Packet.extract(raw),'Every Prince decoded byte/descriptor unchanged'
    at=C.Packet.COOKIE;assert parent[at:at+16]==raw[at:at+16]
    return parent

def bind(text,raw,parent):
    assert reference(raw)==parent and text.count(Old.PIN)==1 and PIN not in text
    rebound=text.replace(Old.PIN,PIN,1)
    assert rebound.replace(PIN,Old.PIN,1)==text,'Only current whole-ROM authentication is rebound'
    return rebound

def cold(raw):
    reference(raw)
    def owning(image):assert image==raw;return raw
    with patch.object(Game,'proof_parent',owning):return Game.cold(raw)

def source_run(raw,factory):
    import check_prince_natural_stock_40a_1115 as Previous
    cold_scope=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=cold))
    runner=Old.clone(Previous.run,dict(Factory=factory,Cold=cold_scope))
    q=runner(raw,'oneup',8);assert q['actual_CPU_ROM_SHA256']==PIN
    q['binding_only_reference_SHA256']=Old.PIN;q['actual_174fa_CPU_preserves_all_52_Bub_bytes']=True
    q['base_receipt_SHA256']=q.pop('receipt_SHA256')
    import json
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q
