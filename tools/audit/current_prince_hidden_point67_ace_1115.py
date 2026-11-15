"""Explicit new point candidate CPU/cold boundary; no frozen API loosening."""
from pathlib import Path
from unittest.mock import patch
import compose_prince_hidden_point67_ace_1115 as C
import current_prince_stock_174fa_1115 as Previous

N,W,Game,Frames=Previous.N,Previous.W,Previous.Game,Previous.Frames

def reference40a(raw):
    assert isinstance(raw,bytes)and C.digest(raw)==C.CANDIDATE,'Exact new point candidate required'
    owning=C.inverse(raw);prior=C.reference(owning)
    return Previous.reference(prior)

def cold(raw):
    assert C.CANDIDATE is not None and C.digest(raw)==C.CANDIDATE
    def owning(image):assert image==raw;return raw
    with patch.object(Game,'proof_parent',owning):return Game.cold(raw)

def bind(text,raw):
    old=reference40a(raw);oldpin=C.digest(old)
    assert text.count(oldpin)==1;text=text.replace(oldpin,C.CANDIDATE,1)
    oldcookie=old[C.Packet.COOKIE:C.Packet.COOKIE+16].hex();newcookie=raw[C.Packet.COOKIE:C.Packet.COOKIE+16].hex()
    assert text.count(oldcookie)==1;return text.replace(oldcookie,newcookie,1)
