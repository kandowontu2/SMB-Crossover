"""Separate strict1327 tank-to-missile controls with genuine hurt-clear admission."""
from functools import lru_cache
from pathlib import Path
import current_rogue_grounded_stock_1327_1116 as Previous

R,ROM,N,W,Frames,H,PIN=Previous.R,Previous.ROM,Previous.N,Previous.W,Previous.Frames,Previous.H,Previous.PIN
GRANT_SHA=Previous.GRANT_SHA
PREVIOUS_SHA='e8682a76ce89431a925e152f360c93e59d9dfce6d2276d15a561bb0b31caa812'
POLICY=R/'tools/playthroughs/rogue_natural_missile_hurt_clear_1327_1116.lua'


@lru_cache(maxsize=1)
def bindings(raw):
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    return Previous.bindings(raw)


@lru_cache(maxsize=1)
def policy_text(raw):
    q=bindings(raw);sources={};body=Previous.Previous.Retained.route('rogue_dawn_11_v7.lua',sources)
    return 'local ROSTER_CONFIG={rogue_tile_attributes={'+','.join(map(str,q['attributes']))+'}}\nlocal base=(function()\n'+body+'\nend)()\n'+POLICY.read_text()


def cold(raw):return Previous.cold(raw)
def load_current_image():return Previous.load_current_image()


