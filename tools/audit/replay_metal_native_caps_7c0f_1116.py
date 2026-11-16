"""Actual authored pipe cells and completed original MsFrame witnesses."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_metal_head_column_7c0f_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
KINDS=Previous.KINDS


def once(text,old,new):
    assert text.count(old)==1,old;return text.replace(old,new,1)


@lru_cache(maxsize=2)
def controller(raw,key='oneup'):
    text=Previous.controller(raw,key)
    text=once(text,'local PIPES={{448,144},{592,128},{720,112},{896,112}}','local PIPES={{448,144},{608,128},{736,112},{912,112}}')
    text=once(text,'local pendingMain,pendingMove,pendingStep,pendingCollect,pendingScore','local originalEntries,originalReturns=0,0\nlocal pendingFrame\nlocal pendingMain,pendingMove,pendingStep,pendingCollect,pendingScore')
    text=text.replace('move=moveOK,step=stepOK','move=moveOK,step=stepOK,original=originalReturns')
    text=once(text,'physical_frames=frame,input_polls=polls,M=M','originalFrame_entries=originalEntries,originalFrame_returns=originalReturns,pendingFrame=pendingFrame~=nil,physical_frames=frame,input_polls=polls,M=M')
    text=once(text,'if pendingMain or pendingMove or pendingStep or pendingCollect or pendingScore then return end','if pendingMain or pendingMove or pendingStep or pendingFrame or pendingCollect or pendingScore then return end')
    text=once(text,'local a,b=moveOK-q.credit.move,stepOK-q.credit.step;q.resumed_move=a;q.resumed_step=b','local a,b,d=moveOK-q.credit.move,stepOK-q.credit.step,originalReturns-q.credit.original;q.resumed_move=a;q.resumed_step=b;q.resumed_original=d')
    text=once(text,"assert(a<=25 and b<=25,'Exactly25 actual accepted returned Metal work')","assert(a<=25 and b<=25 and d<=25,'Exactly25 actual accepted and original returned Metal work')")
    text=once(text,'if a==25 and b==25 then','if a==25 and b==25 and d==25 then')
    text=once(text,"assert(moveEntries==moveReturns and stepEntries==stepReturns and mainEntries==mainReturns,'Balanced actual worker/Main returns')","assert(moveEntries==moveReturns and stepEntries==stepReturns and originalEntries==originalReturns and mainEntries==mainReturns,'Balanced actual original/worker/Main returns')")
    actor=Current.payload(raw)[0];pc=Current.labels()['MsFrame'];assert pc==0xb461
    h=dict(pc=pc,space='wram',bank=3,offset=3*8192+(pc&8191),bytes=list(actor[pc-0xa000:pc-0xa000+8]))
    observer='C.hooks.OriginalFrame='+Text.lua(h)+'\n'+"""hook('OriginalFrame',function()
 assert(not pendingFrame,'Original frame returned before another entry');originalEntries=originalEntries+1
 pendingFrame=returning(function(t)originalReturns=originalReturns+1;pendingFrame=nil end)
end)
"""
    text=once(text,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        original_work='Authenticated MsFrame B461 entered/returned, Ms12Movement and HostStep accepted/returned; exactly25 of each after credit at actual Main return',
        scope='Actual7c0f earned M then natural '+key+'; real authored cap left edges448/608/736/912, no game changes',
        retained_previous_negative='Source2b664bd4 stopped before second jump because old fixture expected a cap at592 instead of actual608')
    return q


def family(kind='oneup'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
