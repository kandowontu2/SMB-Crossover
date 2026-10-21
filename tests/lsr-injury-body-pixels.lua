-- Raw2.02 primary body pixels, actual completed DMA. This checks the source
-- hurt frame/stand fallback and body colors; independent shield/whip submovie
-- extras are outside this oracle's stated scope. No OAM/ROM/CPU writes.
local ref=dofile(TEST_DIR..'fixtures/lsr-injury-body-source.lua')
local cases={}
for _,char in ipairs({4,5,10})do for _,dir in ipairs({1,2})do for _,off in ipairs({0,1})do
 for prior=0,(char==4 and 1 or 0)do cases[#cases+1]={char=char,dir=dir,off=off,prior=prior}end
end end end
local frame,ci,depth,checks=0,0,0,0
local current,draw,committed
local mmc5=ROM_NAME:find('mmc5')~=nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function bank(n)return depth==0 and r('CurrentBank')%128==n end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced source body IRQ')end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
local function inputs()
 w('SelectedCharacter',current.char);w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',96);w('Player_Y_HighPos',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_Rel_XPos',112);w('Player_Rel_YPos',96);w('PlayerFacingDir',current.dir);w('Player_State',2);w('PlayerStatus',0);w('PlayerOutlinesOff',current.off)
 w('InvOwnedLo',0,current.char);w('InvOwnedHi',0,current.char);w('InvSelected',0,current.char)
 w('GuestHurtKind',current.char);w('GuestHurtTicks',10);w('GuestHurtVisible',1);w('GuestPowerupActive',0);w('GameEngineSubroutine',8);w('TimerControl',0);w('RgPose',current.prior);w('StarInvincibleTimer',0)
end
emu.addMemoryCallback(function()if current and current.char~=10 and bank(22)then inputs()end end,emu.callbackType.exec,assert(L.RosterGraphics))
emu.addMemoryCallback(function()if current and current.char==10 and bank(30)then inputs()end end,emu.callbackType.exec,assert(L.ExpandedGraphics))
emu.addMemoryCallback(function()
 if not current or not bank(4)then return end
 assert(r('RgPose')==(current.char==4 and 0 or current.char==5 and 31 or assert(L.XG_POSE_HURT)),'Actual source hurt/Link missing-label stand pose selected before drawing')
 for i=1,23 do w('ObjectMetasprite',0,i)end
 draw={case=ci,char=current.char,dir=current.dir,off=current.off,prior=current.prior}
end,emu.callbackType.exec,assert(L.DrawAllMetasprites))
emu.addMemoryCallback(function()committed=draw end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()
 depth=depth-1;assert(depth>=0,'Balanced source body NMI')
 if not current or not committed or committed.case~=ci then return end
 local c=committed;committed=nil
 local state=mmc5 and emu.getState()or nil
 local function chr(a)return state and emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)or emu.read(a,emu.memType.nesPpuDebug)end
 local pixels={}
 for o=0,252,4 do
  local y,t,a,x=emu.read(o,emu.memType.nesSpriteRam),emu.read(o+1,emu.memType.nesSpriteRam),emu.read(o+2,emu.memType.nesSpriteRam),emu.read(o+3,emu.memType.nesSpriteRam)
  if y<240 then for yy=0,15 do for xx=0,7 do
   local row=a&128~=0 and 15-yy or yy;local bit=a&64~=0 and xx or 7-xx
   local address=(t&1)*4096+(t&254)*16+(row//8)*16+row%8
   local color=((chr(address)>>bit)&1)+2*((chr(address+8)>>bit)&1)
   local key=(y+1+yy)*256+x+xx
   if color~=0 and not pixels[key]then pixels[key]=(a&3)*4+color end
  end end end
 end
 local body=ref[c.char]
 for yy,row in ipairs(body.rows)do for xx=1,#row do
  local color=tonumber(row:sub(xx,xx),16)
  if color and not(c.off==1 and color==13)then
   local dx=body.x+xx-1;if c.dir==2 then dx=-1-dx end
   local key=(129+body.y+yy-1)*256+120+dx
   assert(pixels[key]==color,'Independent raw source body pixel c'..c.char..' direction'..c.dir..' outlineOff'..c.off..' prior'..c.prior..' X'..dx..' Y'..(body.y+yy-1)..' expected'..color..' got'..tostring(pixels[key]))
   checks=checks+1
  end
 end end
 ci=ci+1;current=cases[ci]
 if not current then print('PASS '..#cases..' actual-DMA source LSR hurt primary bodies/Link stand fallback, both directions/outlines; '..checks..' independently pinned opaque body pixels');emu.stop(0);return end
 w('SelectedCharacter',current.char)
end,emu.callbackType.exec,assert(L.NonMaskableInterrupt_RTI))
emu.addEventCallback(function()emu.setInput({start=frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 then ci=1;current=cases[ci];w('SelectedCharacter',current.char)end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('GameEngineSubroutine',8);w('TimerControl',0);w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('GuestPowerupActive',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('ScrollLock',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 assert(frame<1000,'Bounded source hurt body matrix completes')
end,emu.eventType.endFrame)
