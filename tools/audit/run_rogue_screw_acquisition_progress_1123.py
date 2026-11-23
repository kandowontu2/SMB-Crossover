"""Bounded no-capture progress diagnostic for the exact earned Screw route."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import run_rogue_screw_block_native_1123 as Block
import run_stdout_mesen_1110 as Stdout
from check_ff_stdout_controller_source_1110 import LuaRuntime


H, ROM, PIN = Block.H, Block.ROM, Block.PIN
PARENT_CONTROLLER = 'fa8d2a096585f2539e72c25a3cf854bcb536fbcf5fcb8f544f50fbb94c4ae9c4'
CONTROLLER = 'b0f379712e19d10e0781e20dea08060c8f9f36611aa806a90d4f1ca350bbc052'
TIMEOUT = 345

PROGRESS = r'''
local screwProgressSent={}
local screwProgressCount=0
local function screwProgress()
 local function emit(name,detail)
  if screwProgressSent[name]then return end
  screwProgressCount=screwProgressCount+1
  assert(screwProgressCount<=12,'Bounded native progress records')
  screwProgressSent[name]=true
  print('SMB_NATIVE_PROGRESS '..json({milestone=name,Main=updates,player=state(),detail=detail}))
 end
 if first then emit('first-active')end
 if gear.high and gear.high.complete then emit('high-jump-verified')end
 local f=gear.screw
 if not f then return end
 emit('wall-jump-earned')
 if f.arrival then emit('first-1-3',f.arrival.player)end
 local l=f.low
 if l then
  if l.highBank then emit('high-tree-bank',{x=l.highBank.player.x,y=l.highBank.player.y,plane=l.highBank.bottom})end
  if l.lowLanding then emit('low-tree-landing',{x=l.lowLanding.player.x,y=l.lowLanding.player.y,plane=l.lowLanding.bottom})end
  if l.blockLanding then emit('power-block-landing',{x=l.blockLanding.player.x,y=l.blockLanding.player.y,plane=l.blockLanding.bottom,tile=l.blockLanding.tile})end
 end
 if r('RdGear')==15 and collector and collector.actor.private==211 then
  emit('Screw-native-grant',{C=collector.C,before=collector.before.gear,after=collector.after.gear,
                           private=collector.actor.private,raw=collector.actor.saved_raw})
 end
 if stock=='screw-credit'and credit then
  emit('Screw-native-score',{before=credit.writer.before,after=credit.writer.after,
                            writes=#credit.writer.six_decimal_writes})
 end
 if f.acquisition and f.acquisition.complete then
  emit('Screw-credit-and25',f.acquisition.complete.returned)
 end
end
'''


def controller(installed):
    original=Block.controller(installed,acquisition_only=True)
    assert H(original.encode())==PARENT_CONTROLLER
    text=original;edits=[]
    def edit(old,new):
        nonlocal text
        assert text.count(old)==1,(old,text.count(old))
        text=text.replace(old,new,1);edits.append((old,new))
    edit('local function screwDrive(c)',PROGRESS+'\nlocal function screwDrive(c)')
    old='if gear.started then buttons=bombDrive()else buttons=choose(context(),stock,items)end'
    edit(old,old+'\n screwProgress()')
    edit("    finish('natural-Screw-acquisition-and25')", "    screwProgress()\n    finish('natural-Screw-acquisition-and25')")
    restored=text
    for old,new in reversed(edits):
        assert restored.count(new)==1
        restored=restored.replace(new,old,1)
    assert restored==original
    LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot','dofile'))
    return text


def native(installed):
    program=controller(installed)
    assert H(program.encode())==CONTROLLER
    original_run=Stdout.run
    def compiled(raw,*,block_only=False,acquisition_only=False):
        assert raw is installed and not block_only and acquisition_only
        return program
    def long_run(script,rom,output,expected,timeout,*args,**kwargs):
        assert expected==PIN and timeout==240 and not kwargs.pop('long_no_capture',False)
        assert H(script.read_bytes())==CONTROLLER
        return original_run(script,rom,output,expected,TIMEOUT,*args,long_no_capture=True,**kwargs)
    with patch.object(Block,'controller',compiled),patch.object(Block,'ACQUISITION_PIN',CONTROLLER), \
         patch.object(Stdout,'run',long_run):
        result=Block.native(installed,False,True)
    assert result['script_SHA256']==CONTROLLER and result['ROM_SHA256']==PIN
    assert not result['images']and result['outputs_written']==0 and result['capture_watchdog']
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',action='store_true')
    a=p.parse_args();raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw)
    else:
        def deny(*args,**kwargs):raise AssertionError('Progress validation attempted files or process launch')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            program=controller(raw);assert H(program.encode())==CONTROLLER
            q=dict(passed=True,route_executed=False,controller_SHA256=CONTROLLER,
                   ROM_SHA256=PIN,timeout_seconds=TIMEOUT,long_no_capture=True,
                   maximum_progress_records=12,outputs=0,native=False)
    print('ROGUE_SCREW_PROGRESS '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
