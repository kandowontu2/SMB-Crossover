"""Controller-only Kirby 1-1 discovery with current hardware guards; no video."""
from pathlib import Path
import re,json
from prepare_selected_native_packet_v1 import R,sha,prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from observe_chip_committed_write import lua
O=R/'build/kirby-full11-1102-v7'
ROM=R/'build/thomas-current-candidate-1102-v3/candidate.nes'
BASE=R/'build/kirby-current-native-1102-v4/native'
BODY=r'''
local C=assert(CURRENT_KIRBY_META_EARNED)
local wall,updates,polls=0,0,0
local entered,done=false,false
local menuPhase='options-focus'
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis=255,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local maxX,initialLives,lastA=0,nil,false
local inputFile=assert(io.open(OUTPUT..'inputs.csv','w'));inputFile:write('poll,frame,mask\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function world()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function json(v)
 if type(v)=='table'then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function hook(name,fn)
 local h=assert(C.hooks[name],name)
 emu.addMemoryCallback(function()
  local actual=bank(h.pc);local allowed=false;for _,b in ipairs(h.banks)do if actual==b then allowed=true end end
  if not allowed then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook '..name)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function finish(passed,why)
 if done then return end;done=true;inputFile:close()
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=passed,reason=why,ROM_sha256=C.ROM_sha256,controller_only=true,world=r('WorldNumber'),level=r('LevelNumber'),x=world(),y=r('Player_Y_Position'),maximum_x=maxX,frames=wall,updates=updates,initial_lives=initialLives,final_lives=r('NumberofLives'),health=r('KbHealth'),copy=r('KbCopy'),mouth=r('KbMouth'),NMI=nmis,IRQ=irqCount,DMA=dmas,CHR=chrChecks,minSP=minSP,full_stage=passed}));f:close()
 local p=assert(io.open(OUTPUT..'endpoint.png','wb'));p:write(emu.takeScreenshot());p:close();emu.stop(passed and 0 or 1)
end
ROSTER_CONFIG={name='kirby'}
local choose=assert(dofile(POLICY))
hook('GameLoopOwned',function()
 if done or r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==13 and r('KbVariant')==0 and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Cold Kirby Hard without cheats')
  entered=true;initialLives=r('NumberofLives')
 end
 updates=updates+1;maxX=math.max(maxX,world())
 if r('NumberofLives')<initialLives or r('GameEngineSubroutine')==11 or r('MmDeathFlag')~=0 then finish(false,'Natural death');return end
 if r('WorldNumber')==0 and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 and updates>100 then finish(true,'Reached active1-2')end
end)
-- MENU
-- HARDWARE
emu.addEventCallback(function()
 polls=polls+1;local b={}
 if not entered then b=menu()
 elseif not done then
  local c={frame=wall,poll=polls,char=13,variant=0,r=r,x=world(),y=r('Player_Y_Position'),yHigh=r('Player_Y_HighPos'),state=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),status=r('PlayerStatus'),world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),engine=r('GameEngineSubroutine'),camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),lastA=lastA,grounded=r('Player_State')==0,stageFrame=updates}
  c.block=function(wx,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',math.floor(wx/256)%2*208+math.floor((y-32)/16)*16+math.floor(wx%256/16))end
  c.enemy=function()local nearest;for i=0,5 do local f,id,st=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i);if f>0 and f<128 and(id<0x15 or id==0x2d or id==0x33)and st<32 and not(id==6 and st>=2)then local x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i);local dx=x-c.x;if dx> -160 and dx<160 and(not nearest or math.abs(dx)<math.abs(nearest.dx))then nearest={slot=i,id=id,x=x,y=r('Enemy_Y_Position',i),state=st,dx=dx}end end end;return nearest end
  b=choose(c)
 end
 local mask=0;for k,v in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do if b[k]then mask=mask|v end end
 inputFile:write(polls..','..wall..','..mask..'\n');lastA=not not b.a;emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'CHR hardware latch');chrChecks=chrChecks+1 end end
 if wall>=14000 then finish(false,'Controller deadline')end
end,emu.eventType.endFrame)
'''

def main():
    O.mkdir(exist_ok=True)
    ready=json.loads((BASE/'ready.json').read_text());assert sha(ROM)==ready['ROM_sha256']
    for p,h in ready['bindings'].items():assert sha(p)==h,p
    prefix=(BASE/'controller.lua').read_text().split('\n',1)[0]
    template=(R/'tools/audit/current_kirby_meta_earned_v1.lua').read_text()
    menu=template[template.index('local function menu()'):template.index("hook('GameLoopOwned'")]
    hardware=template[template.index('local function bytes('):template.index('emu.addEventCallback(function()\n if not entered')]
    policy=R/'tools/playthroughs/full_roster_policy_og.lua';bundle=scoped_load(R/'build/kirby-approach-owner-1101-v3/candidate.nes')
    names=set(re.findall(r"\br\('([^']+)'",BODY+policy.read_text()))
    ram={n:address(bundle,n) for n in names}
    script=prefix+'\nfor n,a in pairs('+lua(ram)+')do assert(CURRENT_KIRBY_META_EARNED.ram[n]==nil or CURRENT_KIRBY_META_EARNED.ram[n]==a);CURRENT_KIRBY_META_EARNED.ram[n]=a end\nlocal POLICY='+lua(policy.as_posix())+'\n'+BODY.replace('-- MENU',menu).replace('-- HARDWARE',hardware)
    assert 'emu.write(' not in script and 'loadSavestate' not in script
    sys_path=R/'build/smb2-final62-observer-lua-deps-v1'
    import sys;sys.path.insert(0,str(sys_path));from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(script);assert ok,error
    prepare(O/'native',ROM,script,[Path(__file__),BASE/'ready.json',BASE/'controller.lua',policy,R/'tools/audit/current_kirby_meta_earned_v1.lua'],expected=sha(ROM),timeout=240,scope='Current Hard Kirby controller-only natural1-1 discovery; no scene/actor/health/ability writes. Native hardware guards, compact input CSV, one endpointPNG. Success requires active1-2 without life loss; discovery policy is not assumed to pass.',allow_interactive=True)

if __name__=='__main__':main()
