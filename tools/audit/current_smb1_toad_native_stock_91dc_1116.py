"""Actual current inline native Toad owner, separate from Source Mario0."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import current_smb1_toad_stock_91dc_1116 as Previous

R,ROM,PIN,W,N,Frames,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Frames,Previous.digest
bundle,menu=Previous.bundle,Previous.menu


@lru_cache(maxsize=1)
def bindings(raw):
    q=deepcopy(Previous.bindings(raw));b=bundle(raw);parent=Previous.BT.inverse(raw)
    for name in('BmMarioMovement','BmNativeMovement','BmNativeVertical'):
        at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192;lo=16+bank*8192
        assert raw[lo:lo+8192]==parent[lo:lo+8192]
        q['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[lo:lo+8192]))
    return q


def foundation(raw):
    config=bindings(raw);_,selected=menu(raw)
    return dict(ROM_SHA256=PIN,facade_SHA256=digest(Path(__file__).read_bytes()),compiled_menu=selected,
        actual_movement='PlayerMovementSubs -> BmMarioMovement -> inline BmNativeMovement; SourceMovement not entered',
        original_return_counter='Actual mapped BmNativeMovement dynamic returnPC/SP, separate Main entries/returns',
        hooks=config['hooks'],ram=config['ram'],reference_6a3_SHA256=digest(Previous.BT.inverse(raw)),
        pickup_contract='Actual raw0 MarioSourcePowerupCollision -> non-Tank MarioSourceBeginPowerup/Freeze/Update must be reached by genuine M',
        current_BT27_preserved=True,actual91dc_execution=True,old421_and_wrong_Source_facades_unchanged=True,
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def cold(raw,key='toad',report=False):
    m,q=Previous.cold(raw,key,True)
    q.update(actual_movement_owner='BmNativeMovement, Source movement counter invalid for native Toad',
        actual_first_movement_readback='Deferred to reached mapped BmNativeMovement; no invented private cookie')
    return(m,q)if report else m
