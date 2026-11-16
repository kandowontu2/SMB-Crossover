"""Same guarded inputs, actual Mini tile/head reader and ascent point oracle."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_guard_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='b91def8e906e98383cb889ebde183ff83cc1536146e8b6d8d1cc84ef3c9cf698'


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    c=deepcopy(Previous.Previous.bindings(raw));b=Current.bindings(raw)['bundle']
    for n in('Enemy_X_Speed','Enemy_MovingDir','Player_Y_Speed'):c['ram'][n]=W.address(b,n)
    at=16+84*8192+(0xb43e&8191);c['hooks']['NativeMiniHead']=dict(pc=0xb43e,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+84*8192:16+85*8192]))
    at=Current.CODE_AT+0xcbf;c['hooks']['MiniNativeTile']=dict(pc=0xacbf,offset=3*8192+0xcbf,work=True,bytes=list(raw[at:at+4]))
    _,body=Previous.controller(raw).split('\n',1)
    observer="""hook('MiniNativeTile',function()
 if not M.scope_passed or item.phase~='bump'or work(0xc27b)~=2 or work(0xc27c)~=1 then return end
 local qx,qy=word(0xc2e0),word(0xc2e2);if qx<960 or qx>=1072 then return end
 local z=emu.getState();local q={PC=z['cpu.pc'],SP=z['cpu.sp'],state=state(),world_x=qx,world_y=qy,mask=work(0xc27b),negative=work(0xc27c),native_vy=r('Player_Y_Speed')}
 returning(function(t)
  local a=emu.getState();q.returned={PC=t.pc,SP=t.sp,A=a['cpu.a'],P=a['cpu.ps'],raw_tile=work(0xc2e4),cell=word(0xc2e5),flags=work(0xc2e8)}
  if not item.source_head_min or qy<item.source_head_min.world_y then item.source_head_min=q end
  if qx>=1024 and qx<1040 and qy>=128 and qy<144 and not item.first_actual_hidden_cell then item.first_actual_hidden_cell=q end
  item.up_query_count=(item.up_query_count or 0)+1
 end)
end)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw).encode()),parent_guard_factory_SHA256=BASE_SHA,
        scope='Same guarded inputs; correct owning PRG84:B43E native Mini head path and source MiniNativeTileACBF ascent point/cell/raw/flags/minimum, observer diagnostic only')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
