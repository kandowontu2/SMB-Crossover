"""Observe real player/projectile/render ordering in the original Karnov loop."""
from pathlib import Path
import hashlib,json,os,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from run_mesen import run
from mesen_session_guard_v1 import require_free_workspace
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
O=R/'build/karnov-frame-order-native-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
LUA='''local f,updates=0,0;local rows={}
local function r(a)return emu.read(a,emu.memType.nesDebug)end
emu.addEventCallback(function()local p={};if r(0x10)~=11 then p.start=f>=120 and f%60<3 end;emu.setInput(p,0)end,emu.eventType.inputPolled)
for _,item in ipairs({{0xf28d,'actor'},{0xaab2,'projectiles'},{0xa070,'body'},{0xa152,'shots'}})do
 emu.addMemoryCallback(function()
  if r(0x10)~=11 or item[1]<0xc000 and r(0x1a)~=11 then return end
  if item[2]=='actor'then updates=updates+1 end
  if updates>=3 and updates<=6 then rows[#rows+1]=string.format('{"frame":%d,"update":%d,"kind":"%s"}',f,updates,item[2])end
 end,emu.callbackType.exec,item[1])
end
emu.addEventCallback(function()
 f=f+1
 if updates>=12 then local out=assert(io.open(OUTPUT..'order.json','w'));out:write('{"passed":true,"events":['..table.concat(rows,',')..']}\\n');out:close();print('KARNOV_FRAME_ORDER_PASS');emu.stop(0)elseif f>=700 then assert(false,'700 frame bound')end
end,emu.eventType.endFrame)
'''


def main():
    assert sha(ROM)==EXPECTED;O.mkdir(exist_ok=True);assert not(O/'capture').exists();(O/'capture').mkdir();p=O/'controller.lua';p.write_text(LUA,encoding='utf-8')
    require_free_workspace(R,ROM);os.environ['SMB_RUN_OUTPUT']=str(O/'capture');assert run(p,ROM,timeout=120,emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])==0
    q=json.loads((O/'capture/order.json').read_text());assert q['passed'];groups={}
    for e in q['events']:groups.setdefault(e['frame'],[]).append(e['kind'])
    full=[v for v in groups.values()if len(v)==4];assert full and all(v==full[0]for v in full),groups
    (O/'controls.json').write_text(json.dumps(dict(passed=True,native_original=True,native_port=False,installed=False,donor_sha256=EXPECTED,order=full[0],observed=groups,bindings={str(x.resolve()):sha(x)for x in[Path(__file__),ROM,p,O/'capture/order.json',R/'tools/run_mesen.py']}),indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,order=full[0],frames=len(full))))


if __name__=='__main__':main()
