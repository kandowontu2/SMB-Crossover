-- Explicit body/pixel alignment arena. Source: pinned DuckTales native center,
-- ±10/±12 tile body and7px crouch contact reduction. No level-clear claim.
local frame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function fixture(x,dir)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col);w('MmSolidTerrain',1,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('Player_X_Position',x%256);w('Player_PageLoc',x//256);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('ScreenLeft_X_Pos',(x-80)%256);w('ScreenLeft_PageLoc',(x-80)//256)
 w('ScreenRight_X_Pos',(x+175)%256);w('ScreenRight_PageLoc',(x+175)//256)
 w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerFacingDir',dir)
 w('PlayerStatus',0);w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('RgPreviousButtons',0);w('TimerControl',0);w('InjuryTimer',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
local function pixels()
 local state=ROM_NAME:find('mmc5') and emu.getState() or nil
 local function chr(a)
  if state then return emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)end
  return emu.read(a,emu.memType.nesPpuDebug)
 end
 local px,py=r('Player_Rel_XPos'),r('Player_Y_Position')
 local minx,maxx,miny,maxy=256,-1,240,-1
 for s=0,63 do
  local y=emu.read(s*4,emu.memType.nesSpriteRam)+1
  local t=emu.read(s*4+1,emu.memType.nesSpriteRam)
  local a=emu.read(s*4+2,emu.memType.nesSpriteRam)
  local x=emu.read(s*4+3,emu.memType.nesSpriteRam)
  if x>=px-24 and x<px+32 and y>=py-8 and y<py+40 then
   local base=(t&1)*4096+(t&254)*16
   for dy=0,15 do for dx=0,7 do
    local row=a&128~=0 and 15-dy or dy
    local col=a&64~=0 and dx or 7-dx
    local q=base+(row//8)*16+row%8
    local c=((chr(q)>>col)&1)+2*((chr(q+8)>>col)&1)
    if c~=0 then minx=math.min(minx,x+dx);maxx=math.max(maxx,x+dx);miny=math.min(miny,y+dy);maxy=math.max(maxy,y+dy)end
   end end
  end
 end
 return minx-px,maxx-px,miny-py,maxy-py
end
local function check(crouch,dir)
 local px,py=r('Player_Rel_XPos'),r('Player_Y_Position')
 local expected={px-2,py+(crouch and 15 or 8),px+18,py+(crouch and 25 or 32)}
 assert(r('Player_BoundBoxCtrl')==(crouch and 20 or 19),'Native Scrooge body control dispatch')
 for i=0,3 do assert(r('BoundingBox_UL_Corner',i)==expected[i+1],'Native body coordinate '..i..': got '..r('BoundingBox_UL_Corner',i)..' expected '..expected[i+1])end
 local x0,x1,y0,y1=pixels()
 local ex0=crouch and(dir==1 and -1 or -7)or -4
 local ex1=crouch and(dir==1 and 22 or 16)or 19
 assert(x0==ex0 and x1==ex1,'Native fixed-origin '..(crouch and 'crouch' or 'stand')..' pixels: '..x0..'..'..x1)
 assert(y0==(crouch and 13 or 4)and y1==32,'Native body and art share the same32px foot origin')
 print('PASS Scrooge '..(crouch and 'crouch' or 'stand')..' native body bounds and actual PPU/OAM pixels, facing '..dir)
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80 or(frame>=680 and frame<820),right=frame==100 or frame==120,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==620 then assert(r('SelectedCharacter')==12,'Scrooge selected');fixture(128,1)end
 if frame==650 then check(false,1)end
 if frame==660 then w('PlayerFacingDir',2)end
 if frame==675 then check(false,2)end
 if frame==685 then w('PlayerFacingDir',1)end
 if frame==710 then check(true,1)end
 if frame==720 then w('PlayerFacingDir',2)end
 if frame==745 then check(true,2)end
 if frame==760 then fixture(255,2)end
 if frame==800 then check(true,2);print('PASS Scrooge standing/crouching native hitboxes and fixed art origins including world-page seam');emu.stop(0)end
end,emu.eventType.endFrame)
