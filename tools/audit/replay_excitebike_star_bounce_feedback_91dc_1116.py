"""Preserve exact Star head controls; observe/chase the actual native bounce."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_star_head_feedback_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='689526fe949bd3925c20ebd6e6bf18bf49bcf5510fc4068ece199c8f81de7d58'
CONTROL=R/'tools/playthroughs/excitebike_star_bounce_feedback_91dc_1116.lua'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);prefix,body=text.split('\n',1);b=Current.bundle(raw)
    ram='\n'.join('C.ram.'+name+'='+str(W.address(b,name))for name in('Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir'))
    marker='local function stockDrive()\n';assert body.count(marker)==1
    body=body.replace(marker,CONTROL.read_text()+'\n'+marker,1)
    a=body.index(' if a then\n');z=body.index(" if stock.phase=='travel'then",a)
    assert"phase='stock-ground-intercept'"in body[a:z]and"stock.brake"in body[a:z]
    body=body[:a]+""" if a then
  phase='stock-bounce-feedback';stock.phase='collect'
  if a.state<128 then return end
  bounceIntercept(s,a)
  return
 end
"""+body[z:]
    text=prefix+'\n'+ram+'\n'+body;Previous.Stock.Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),
        bounce_factory_SHA256=digest(Path(__file__).read_bytes()),bounce_control_SHA256=digest(CONTROL.read_bytes()),
        exact_head_parent_factory=BASE_SHA,head_controls_unchanged=True,
        retained_native_stationary_intercept_negative='2e44e26e23c3b9cb4ef3e54d0f063ae36a21e2c5e17d02c9de0c8aad57bf1d87',
        source_control='Actual mature actor speed/direction/height, original coast/charge and ordinary freshA/Up, no game writes')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
