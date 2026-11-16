"""Same crouch controls; record actual first stock admission before its guard."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_supermaaa_flower_crouch_91dc_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='e88061faf375d3f40b7d829dc514ad60d8cbba5424a5bdc052952908e6a7d369'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);old=" assert(i==5 and a.flag==1 and a.id==46 and a.kind==C.stock_type and a.state>=128,'Actual mature expected stock')"
    new=""" if not stock.first_admission then
  local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
  stock.first_admission={state=state(),actor=a,pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],ObjectOffset=r('ObjectOffset'),crouch=r('CrouchingFlag'),player_box=pb,item_box=ib,
   overlap={math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1,math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1},
   caller=(read(256+((cpu['cpu.sp']+1)&255))+256*read(256+((cpu['cpu.sp']+2)&255))+1)&65535}
 end
"""+old
    assert text.count(old)==1;text=text.replace(old,new,1)
    marker="hook('GameLoop',function()"
    observer="""hook('PowerUpObjHandler',function()
 if not food.M_scope_passed or not stock.born then return end
 local cpu=emu.getState();stock.last_handler={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=actor(5)}
end)
"""
    assert text.count(marker)==1;text=text.replace(marker,observer+marker,1);LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),admission_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical=True,scope='Readonly first actual admission/boxes/handler before frozen mature assertion; diagnostic only')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
