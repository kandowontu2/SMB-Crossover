"""Same ordinary hidden-route controls, new candidate point/caller observers."""
from functools import lru_cache
import current_prince_hidden_point67_ace_1115 as Current
import replay_prince_hidden_mount_fresh_A_40a_1115 as Previous
from replay_prince_natural_stock_40a_1115 import lua,LuaRuntime

C,N,W=Current.C,Current.N,Current.W
PIN=C.CANDIDATE

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8
    parent=Current.reference40a(raw);text=Current.bind(Previous.controller(parent,mode,jump),raw)
    part=C.Packet.extract(raw)[1][0]
    def hook(pc,size=8):return dict(pc=pc,address=3*8192+(pc&8191),bytes=list(part[pc-0xa000:pc-0xa000+size]),private=True)
    observer=r'''
stock.point67_calls=0;stock.point67_material_serial=0;stock.point67_hidden={};stock.point67_materials={}
stockHook(@POINT@,function(cpu)
 stock.point67_calls=stock.point67_calls+1
 if not stock.point67_readback then
  for i,v in ipairs(@CODE@)do assert(read(0xb30f+i)==v,'Entire owning point67 before its first SMC')end
  local c=0;for i=1,16 do
   local v=tonumber(cookie:sub(2*i-1,2*i),16)
   assert(source(0x1fdf+i,2)==v and source(0x1fdf+i,3)==v,'Both complete point67 cookies');c=c+1
  end
  stock.point67_readback={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],bytes=67,both_cookies=c==16,old_SMC_low=0xb33b,new_SMC_low=0xb338}
 end
 if stock.phase~='standing-flight'then return end
 local x=source(0x1369,3)+256*source(0x136a,3);local y=source(0x136b,3)+256*source(0x136c,3)
 local raw=tile(x,y);if raw~=95 and raw~=96 then return end
 local q={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],world_x=x,world_y=y,raw_tile=raw,state=stockState(),material_serial=stock.point67_material_serial}
 stockReturn(cpu,function(ret,returned)
  q.return_PC=ret.pc;q.return_SP=ret.sp;q.A=returned['cpu.a'];q.P=returned['cpu.ps']or returned['cpu.p'];q.classified_B36D=source(0x136d,3)
  assert(q.A==0 and q.P&1==0 and q.classified_B36D==0,'Hidden point is established empty result')
  if #stock.point67_hidden<8 then stock.point67_hidden[#stock.point67_hidden+1]=q end
  stock.point67_latest=q
 end)
end)
stockHook(@MATERIAL@,function(cpu)
 stock.point67_material_serial=stock.point67_material_serial+1
end)
stockHook(@RETURN@,function(cpu)
 local q=stock.point67_latest
 if q and q.material_serial==stock.point67_material_serial and #stock.point67_materials<8 then
  stock.point67_materials[#stock.point67_materials+1]={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],A=cpu['cpu.a'],Wall=source(0x8c),hidden=q,state=stockState()}
 end
end)
emu.addMemoryCallback(guarded(function(at,value)
 if not mapped(0xc60f,2)or stock.phase~='standing-flight'then return end
 local before=source(0x60f)+256*source(0x610);local after=value+256*source(0x610)
 if before>=1000 and before<1040 and after-before<=-8 and after-before>=-64 and not stock.point67_backtrack then
  local cpu=emu.getState();stock.point67_backtrack={PC=cpu['cpu.pc']-1,SP=cpu['cpu.sp'],before=before,after=after,state=stockState()}
 end
end),emu.callbackType.write,0xc60f)
'''.replace('@POINT@',lua(hook(0xb310))).replace('@CODE@',lua(list(C.NEW))).replace('@MATERIAL@',lua(hook(0xbde5))).replace('@RETURN@',lua(hook(0xbf9f,4)))
    old='local function naturalStockTick()\n';assert text.count(old)==1
    text=text.replace(old,observer+'\n'+old,1)
    LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        same_ordinary_fresh_A_controls=True,first_actual_B310_all67_pre_SMC_and_both_cookies=True,
        actual_SMC_low=0xb338,former_SMC_low_no_longer_mutable=0xb33b,
        only_hidden_point_semantics_changed=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
