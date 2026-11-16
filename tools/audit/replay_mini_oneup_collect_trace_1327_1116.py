"""Unchanged supported-L inputs; bounded mature actor/body chase samples."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_manual_ctor_1327_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='455c7b479efcbfea5460439effb72902c0b37783d2e445a446c94d76367047a5'

@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup' and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    old="  if a then item.phase=a.state<128 and 'wait-mature'or'collect'end"
    new=old+"""
  if a and a.state>=128 then
   item.chase_samples=item.chase_samples or{}
   if #item.chase_samples<20 and(not item.chase_last or steps-item.chase_last>=8)then
    item.chase_last=steps;item.chase_samples[#item.chase_samples+1]={state=s,actor=a,player_box=box('Player_BoundBox'),item_box=box('Enemy_BoundBox',a.slot)}
   end
  end"""
    assert text.count(old)==1;text=text.replace(old,new,1);LuaRuntime().compile(text);return text

def metadata(raw,key='oneup'):
    q=Previous.metadata(raw,key);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),parent_manual_ctor_SHA256=BASE_SHA,scope='Unchanged supported-L inputs; bounded mature actor/actual box chase diagnostic');return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
