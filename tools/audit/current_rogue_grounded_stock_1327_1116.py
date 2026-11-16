"""Separate actual1327 facade for retained source-grounded first-tank inputs."""
from functools import lru_cache
from pathlib import Path
import current_rogue_natural_stock_1327_1116 as Previous

R,ROM,N,W,Frames,H,PIN=Previous.R,Previous.ROM,Previous.N,Previous.W,Previous.Frames,Previous.H,Previous.PIN
GRANT_SHA=Previous.GRANT_SHA
PREVIOUS_SHA='b2ff0569e379c12265fe7c4923f5e6d8ff3bce140c59118b1449b5245c53d45e'


@lru_cache(maxsize=1)
def bindings(raw):
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    q=dict(Previous.bindings(raw));b=q['bundle'];at=W.location(b,'MTileAttribute')
    q['attributes']=list(raw[at:at+256]);assert len(q['attributes'])==256
    q['attributes_SHA256']=H(raw[at:at+256]);return q


@lru_cache(maxsize=1)
def policy_text(raw):
    q=bindings(raw);sources={};body=Previous.Retained.route('rogue_dawn_11_v6.lua',sources)
    expected={n:Previous.Retained.ROUTE_PINS[n]for n in('rogue_dawn_11_v6.lua','rogue_dawn_11_v5.lua',
        'rogue_dawn_11_v4.lua','rogue_dawn_opening_route_v1.lua','roster_samus_contra_nav.lua')}
    assert sources=={'tools/playthroughs/'+n:h for n,h in expected.items()}
    return 'local ROSTER_CONFIG={rogue_tile_attributes={'+','.join(map(str,q['attributes']))+'}}\n'+body


def cold(raw):
    bindings(raw);return Previous.cold(raw)


def load_current_image():return Previous.load_current_image()
