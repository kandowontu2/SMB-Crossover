"""Current controller-only Arthur profile; root owns the Mesen launch."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import prepare,sha,R
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/arthur-idle-profile-1101-v1'
ROM=R/'build/metal-storm-idle-shots-1101-v41/candidate.nes'

def main():
 O.mkdir(exist_ok=True);b=scoped_load(ROM)
 watches=[]
 for n in ['HuMovement','HuGraphics','HuDraw','HuVisible','HuBody','HuAdder','HuBox','HuHead','HuSide','HuFullBox','HuAfterTerrainGate','HuArthurFeetGate','HuUi','HuWeaponTail','ArDispatch','ArProbeDispatch','ArStep']:
  if n in b['syms']:watches.append(dict(name=n,pc=address(b,n),tag=128+(location(b,n)-16)//8192))
 auth=address(b,'ArGenCheckForeground');cookie=address(b,'ArGenCookieOnly')
 text=r'''
local phase,age,frame,polls='title',0,0,0
local captured=0
local counts={{},{}}
local totals={{mainCalls=0,mainCycles=0,authCalls=0,authCycles=0},{mainCalls=0,mainCycles=0,authCalls=0,authCycles=0}}
local mainStart,mainBucket,authStart,authBucket=nil,nil,nil,nil
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function cycle()return emu.getState()['cpu.cycleCount']end
local function bucket()if phase~='play' or age>=240 then return nil end return age<120 and 1 or 2 end
local function tag(pc)return r(pc>=0xc000 and 'CurrentBankC' or 'CurrentBank')end
local function state(p)phase=p;age=0;polls=0 end
local function shot(name)captured=captured+1;assert(captured<=2);local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
WATCHES
local function authEntry()
 local b=bucket();if not b or tag(AUTH)~=198 then return end
 assert(not authStart,'No nested foreground auth');authStart=cycle();authBucket=b
end
emu.addMemoryCallback(authEntry,emu.callbackType.exec,AUTH)
emu.addMemoryCallback(authEntry,emu.callbackType.exec,COOKIE)
local function authReturn()
 if not authStart or tag(AUTH)~=198 then return end
 local q=totals[authBucket];q.authCalls=q.authCalls+1;q.authCycles=q.authCycles+cycle()-authStart+6;authStart=nil
end
RETURNS
emu.addMemoryCallback(function()local b=bucket();if b then mainStart=cycle();mainBucket=b end end,emu.callbackType.exec,L.NoDecTimers)
emu.addMemoryCallback(function()if mainStart then local q=totals[mainBucket];q.mainCalls=q.mainCalls+1;q.mainCycles=q.mainCycles+cycle()-mainStart;mainStart=nil end end,emu.callbackType.exec,L.PauseSkip+2)
emu.addEventCallback(function()
 local p={}
 if phase~='title' and polls<8 then
  if phase=='open' or phase=='start' then p.start=true elseif phase=='up' then p.up=true elseif phase=='left' then p.left=true end
 end
 if phase=='play' and age>=120 then p.right=true end
 emu.setInput(p,0);polls=polls+1
end,emu.eventType.inputPolled)
local startx
emu.addEventCallback(function()
 frame=frame+1;age=age+1;assert(frame<=1000,'Bounded profile')
 if phase=='title' and age==100 then state('open')
 elseif phase=='open' and age>=36 and polls>=12 then assert(r('CrossoverMenuState')==2);state('up')
 elseif phase=='up' and age>=28 and polls>=12 then assert(r('CrossoverMenuIndex')==24);state('left')
 elseif phase=='left' and age>=36 and polls>=12 then assert(r('SelectedCharacter')==32);state('start')
 elseif phase=='start' and age>=300 then assert(r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==32);startx=r('Player_X_Position')+256*r('Player_PageLoc');shot('idle-start');state('play')
 elseif phase=='play' and age>=240 then
  local x=r('Player_X_Position')+256*r('Player_PageLoc');shot('walk-end')
  local f=assert(io.open(OUTPUT..'profile.json','w'));local rows={}
  for b=1,2 do local q=totals[b];local c={};for n,v in pairs(counts[b])do c[#c+1]=string.format('"%s":%d',n,v)end;rows[#rows+1]=string.format('{"phase":"%s","physical_frames":120,"main_calls":%d,"main_mean_cycles":%.2f,"auth_calls":%d,"auth_total_cycles":%d,"counts":{%s}}',b==1 and 'idle' or 'walk',q.mainCalls,q.mainCycles/math.max(1,q.mainCalls),q.authCalls,q.authCycles,table.concat(c,','))end
  f:write('['..table.concat(rows,',')..']');f:close()
  local passed=x>startx and r('SelectedCharacter')==32 and r('GameEngineSubroutine')==8
  f=assert(io.open(OUTPUT..'result.json','w'));f:write(string.format('{"passed":%s,"frames":%d,"start_x":%d,"end_x":%d,"controller_only":true,"timing_includes_interrupts":true}',tostring(passed),frame,startx,x));f:close();emu.stop(passed and 0 or 1)
 end
end,emu.eventType.endFrame)
'''
 callbacks=[]
 for w in watches:
  callbacks.append("emu.addMemoryCallback(function()local b=bucket();if b and tag(%d)==%d then counts[b]['%s']=(counts[b]['%s'] or 0)+1 end end,emu.callbackType.exec,%d)"%(w['pc'],w['tag'],w['name'],w['name'],w['pc']))
 # These three genuine return instructions are bounded by the current source
 # constructor/ordinary cookie paths. Verify bytes rather than stale labels.
 raw=b['raw'];base=location(b,'ArGenCheckForeground')
 returns=[auth+44,auth+47,auth+89]
 assert all(raw[base+(p-auth)]==0x60 for p in returns)
 text=text.replace('WATCHES','\n'.join(callbacks)).replace('RETURNS','\n'.join(f'emu.addMemoryCallback(authReturn,emu.callbackType.exec,{p})' for p in returns)).replace('AUTH',str(auth)).replace('COOKIE',str(cookie))
 prepare(O/'native',ROM,text,[Path(__file__)],expected=sha(ROM),timeout=120,scope='Cold actual Arthur menu route,120 physical idle/120 right-only frames, no enemies arranged/state writes. Main/auth elapsed cycles include interrupts, two screenshots maximum. Counts are actual physical-bank-filtered entries.')
if __name__=='__main__':main()
