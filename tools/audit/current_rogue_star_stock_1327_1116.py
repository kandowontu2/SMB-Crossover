"""Strict current1327 independent genuine M-to-native-Star input facade."""
from functools import lru_cache
from pathlib import Path
import current_rogue_grounded_stock_1327_1116 as Previous

R,ROM,N,W,Frames,H,PIN=Previous.R,Previous.ROM,Previous.N,Previous.W,Previous.Frames,Previous.H,Previous.PIN
GRANT_SHA=Previous.GRANT_SHA
PREVIOUS_SHA='e8682a76ce89431a925e152f360c93e59d9dfce6d2276d15a561bb0b31caa812'
POLICY=R/'tools/playthroughs/rogue_natural_star_1327_1116.lua'


@lru_cache(maxsize=1)
def bindings(raw):
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    q=dict(Previous.bindings(raw));q['hooks']=dict(q['hooks']);b=q['bundle']
    for n in('RdHsNewLife','RdBodyNewLife'):
        pc,at=W.address(b,n),W.location(b,n);bank=(at-16)//8192
        q['hooks'][n]=dict(PC=pc,file=at,physical_PRG_bank=bank,tag=bank+128,first16=raw[at:at+16].hex())
    return q


@lru_cache(maxsize=1)
def policy_text(raw):
    q=bindings(raw);sources={};body=Previous.Previous.Retained.route('rogue_dawn_11_v7.lua',sources)
    return 'local ROSTER_CONFIG={rogue_tile_attributes={'+','.join(map(str,q['attributes']))+'}}\nlocal base=(function()\n'+body+'\nend)()\n'+POLICY.read_text()


def cold(raw):bindings(raw);return Previous.cold(raw)
def load_current_image():return Previous.load_current_image()
