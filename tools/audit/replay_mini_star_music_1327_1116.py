"""Unchanged recovery Star controls, direct actual music64 writer witness."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_star_recovery_1327_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='ca8a73798fd3423bd49a14113065ba5661f0685c6df0fea484b455becf2041bb'

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star' and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    old=' and item.native_effect and item.star35_writer)';assert text.count(old)==1;text=text.replace(old,' and item.native_effect and item.star35_writer and item.music64_writer)',1)
    observer="""emu.addMemoryCallback(guard(function(_,v)
 if pendingCollect and M.scope_passed and v==64 then
  local z=emu.getState();assert(z['cpu.ps']&1==0,'Original actual Star music64 writerC0')
  item.music64_writer={PC=z['cpu.pc'],SP=z['cpu.sp'],P=z['cpu.ps'],value=v,state=state()}
 end
end),emu.callbackType.write,C.ram.AreaMusicQueue)
"""
    old="hook('GameLoop',function()";assert text.count(old)==1;text=text.replace(old,observer+old,1);LuaRuntime().compile(text);return text

def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),parent_recovery_factory_SHA256=BASE_SHA,controls_identical=True,direct_actual_music64_writer_required=True);return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
