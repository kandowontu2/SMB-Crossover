"""Strict current FF1UP successor:25 actual FF movement entries after credit."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_ff_natural_oneup_current_1114 as Previous

R,ROM,PIN,W,N=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_SOURCE_SHA='7dfe004b5fbe7cf25a0ab29526494cf067bce051a6914872a6f520ddd94a1fb8'


@lru_cache(maxsize=4)
def controller(raw,key='fighter-life'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==OLD_SOURCE_SHA
    text=Previous.controller(raw,key)
    if key=='fighter-life':assert sha256(text.encode()).hexdigest()=='87eb9e022094471afb99e45531ff159ad840c787d972a6efdb6d5f545df21e84'
    once=Previous.once
    text=once(text,'  if not gameplay or bindingChecked then return end',
        '  if not gameplay then return end\n  stock.actual_FF_entries=(stock.actual_FF_entries or 0)+1\n  if bindingChecked then return end')
    text=once(text,'stock.credit={before=stockCreditPending,after=state(),cue=64};stockCreditPending=nil',
        'stock.credit={before=stockCreditPending,after=state(),cue=64,actual_FF_entries=assert(stock.actual_FF_entries)};stockCreditPending=nil')
    text=once(text,'stock.resume=stock.resume+1',
        "stock.resume=stock.actual_FF_entries-stock.credit.actual_FF_entries\n     assert(stock.resume<=25,'Bounded actual post-credit FF entries')")
    text=once(text,'Natural FF mushroom/hidden1UP/native credit and25 resumed calls',
        'Natural FF mushroom/hidden1UP/native credit and25 actual post-credit FF entries')
    Frozen.LuaRuntime().compile(text)
    return text


def metadata(raw,key='fighter-life'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        prior_factory_SHA256=OLD_SOURCE_SHA,
        scope='Named-class real M/hidden1UP and native INC2-to3, then25 actual FfMovement entries strictly after writer; no sibling transfer, Star/fullstage/graphics claim')
    return q
