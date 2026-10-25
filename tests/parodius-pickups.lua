-- Real menus and controller shots; explicitly positioned component actors.
local kinds={4,6,7,8,9,10};local observations={};local pendingPose;local pendingScreenshots={}
local banks={};local upper=0;local resetChecks=0;local resetBefore
local scoreBase;local streakBefore;local colorStep=0;local hitCycles=0
local function bytes(start,count,kind)
 local d={};for i=0,count-1 do d[#d+1]=string.char(emu.read(start+i,kind))end;return table.concat(d)
end
local function file(n,d)local f=assert(io.open(OUTPUT..n,'wb'));f:write(d);f:close()end
local function score()
 local n=0;for i=0,5 do n=n*10+r('Player1ScoreDisplay',i)end;return n
end
local function cap(kind,x,y)
 w('PnCapActive',kind);w('PnCapX',x or 184);w('PnCapY',y or 104);w('PnCapPage',0)
 w('PnCapAge',0);w('PnCapFraction',0);w('PnCapVX',0);w('PnCapVXF',0)
 w('PnCapHits',4);w('PnCapChange',0);w('PnCapAnim',0)
end
local function metadata()
 local s={};for _,n in ipairs({'PnCapVX','PnCapVXF','PnCapHits','PnCapChange','PnCapAnim'})do
  for i=0,3 do s[#s+1]=string.char(r(n,i))end
 end;return table.concat(s)
end
emu.addMemoryCallback(function(a,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)banks[a-0x5120]=v+upper*256 end,emu.callbackType.write,0x5120,0x5127)
emu.addMemoryCallback(function()
 if not entered or actual(0xa000)~=B.PnPickupPoseReady then return end
 local f=r('PnDrawFrame');if observations[f]then return end
 local slot=r('VvSlot')
 pendingPose={frame=f,kind=r('PnCapActive',slot),age=r('PnCapAnim',slot),
              x=r('PnCapX',slot)-r('ScreenLeft_X_Pos'),y=r('PnCapY',slot),pool=r('PnPool')}
end,emu.callbackType.exec,L.PnPickupPoseReady)
emu.addMemoryCallback(function()
 if not pendingPose or observations[pendingPose.frame]then return end
 local p=pendingPose;local key='pose-'..p.frame
 file(key..'-oam.bin',bytes(0,256,emu.memType.nesSpriteRam))
 local chr={};for i=0,7 do chr[#chr+1]=bytes(assert(banks[i])*1024,1024,emu.memType.nesChrRom)end
 file(key..'-chr.bin',table.concat(chr));file(key..'-palette.bin',bytes(0x3f00,32,emu.memType.nesPpuDebug))
 pendingScreenshots[#pendingScreenshots+1]={file=key..'.png',wait=3}
 p.bank7=banks[7];observations[p.frame]=p;pendingPose=nil
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()
 if entered and t>=550 and actual(0xa000)==B.Pn8bff then resetBefore=metadata()end
end,emu.callbackType.exec,L.Pn8bff)
emu.addMemoryCallback(function()
 if resetBefore and actual(0xa000)==B.Pn8c18 then
  assert(metadata()==resetBefore,'Native weapon clears preserve all20 physical pickup state bytes')
  resetChecks=resetChecks+1;resetBefore=nil
 end
end,emu.callbackType.exec,L.Pn8c18)
-- Keep one Bell in the firing lane for the isolated color-cycle arena.
-- Velocity/hit state still runs normally; this is not a campaign replay.
emu.addMemoryCallback(function()
 if entered and t>=620 and t<1450 and actual(0xa000)==B.PnNativeFrameReady and r('PnCapActive')~=0 then
  emu.write(L.PnCapX,112,emu.memType.nesDebug);emu.write(L.PnCapPage,0,emu.memType.nesDebug)
 end
end,emu.callbackType.exec,L.PnNativeFrameReady)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=60 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')<12 then b.down=true
   elseif r('CrossoverMenuIndex')~=17 then b.right=true
   elseif r('VvVariant')~=PN_VARIANT then b.select=true else b.a=true end
  end
 else b.a=t>=625 and t<1450 and t%12<4 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 for i=#pendingScreenshots,1,-1 do local p=pendingScreenshots[i];p.wait=p.wait-1
  if p.wait==0 then file(p.file,emu.takeScreenshot());table.remove(pendingScreenshots,i)end
 end
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=true;t=0 end
  assert(wall<1100,'Real menu enters pickup arena');return
 end
 t=t+1
 if t==1 then arena()end
 for i,kind in ipairs(kinds)do if t==20+(i-1)*45 then cap(kind)end end
 for i=0,4 do
  if t==310+i*40 then scoreBase=score();streakBefore=r('PnBellStreak');cap(6,72,128)end
  if t==320+i*40 then
   assert(r('PnCapActive')==11+i,'Gold Bell shows its native score sprite')
   assert(score()-scoreBase==({500,1000,2500,5000,10000})[i+1],'Gold score progression matches original cartridge')
   assert(r('PnBellStreak')==math.min(streakBefore+1,4),'Gold Bell streak cap')
  end
 end
 if t==540 then assert(r('PnCapActive')==0,'Native40-update score sprite expires')end
 if t==550 then cap(6);w('PnNativeStageFlags',32)end
 if t==575 then
  assert(resetChecks>0,'Native full weapon clear was exercised')
  w('PnNativeStageFlags',0)
 end
 if t==620 then arena();cap(6,112,120)end
 if t>=625 and t<=1450 then
  local step=r('PnCapChange')
  if step>colorStep then
   assert(step==colorStep+1,'No Bell color cycle is skipped')
   colorStep=step;hitCycles=hitCycles+1
   local expected=({7,6,9,6,8,6,10,6,7,6,9,6,8,6,10})[step]or 0
   assert(r('PnCapActive')==expected,'Four hits for Gold, one for each special color')
  end
 end
 if t==1450 then
  assert(hitCycles==16,string.format('Actual controller shots complete all16 native Bell color changes: changes=%d active=%d hits=%d y=%d shotY=%d',hitCycles,r('PnCapActive'),r('PnCapHits'),r('PnCapY'),r('PnY',6)))
  local entries={};for f,p in pairs(observations)do entries[#entries+1]=string.format('"%d":{"kind":%d,"x":%d,"y":%d,"pool":%d,"bank7":%d}',f,p.kind,p.x,p.y,p.pool,p.bank7)end
  for f=241,255 do assert(observations[f],'Every original pickup/score pose is actually displayed: '..f)end
  file('pickup-proof.json',string.format('{"variant":%d,"resetChecks":%d,"hitCycles":%d,"frames":%d,"poses":{%s},"scope":"Real menus; explicitly seeded pickup gallery, five physical Gold pickups, native weapon clear and controller Bell recoloring arena. No campaign/audio/fade-parity claim."}',PN_VARIANT,resetChecks,hitCycles,t,table.concat(entries,',')))
  print('PASS Parodius physical pickup/art/color arena v'..PN_VARIANT);emu.stop(0)
 end
 assert(wall<3000,'Bounded physical pickup/color arena')
end,emu.eventType.endFrame)
