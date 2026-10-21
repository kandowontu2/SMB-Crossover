-- Source re-audit observations. Explicit flat-world fixtures; measurements are
-- data, not parity assertions. A mismatch must remain visible in the report.
local c=assert(AUDIT_CHARACTER)
local frame=0
local csv=assert(io.open(AUDIT_OUTPUT..'motion.csv','w'))
csv:write('frame,phase,t,character,power,x,y,state,vx,vy,nativeVX,nativeVY,pose,crouch,shoot,cooldown,shots,palette0,palette1,palette2,palette3,palette4,palette5,palette6,palette7,palette8\n')
local weapons=assert(io.open(AUDIT_OUTPUT..'weapons.csv','w'))
weapons:write('frame,phase,t,power,pool,slot,type,age,x,y,vx,vy\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function v(n)local a=r(n)+256*r(n,1)+65536*r(n,2);return (a>=0x800000 and a-0x1000000 or a)/65536 end
local function signed(a)return a>=128 and a-256 or a end
local function phase()return math.floor((frame-650)/100),(frame-650)%100 end
local function fixture(p)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i) end
 if p~=4 then for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col) end end end
 for i=0,9 do w('RgShotType',0,i) end
 for i=0,3 do w('MmBulletType',0,i) end
 for i=0,2 do w('SmShotType',0,i);w('SmBombAge',0,i) end
 for i=0,1 do w('Fireball_State',0,i) end
 w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',(p==4 and 32 or (p==5 or p==11) and 80 or 176));w('Player_Y_HighPos',1)
 w('Player_State',(p==4 or p==5 or p==11) and 1 or 0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('MmLastXSpeed',0)
 local power=(p>=8 and p<=10) and p-8 or (p>=14 and p<=16) and p-14 or 0
 w('PlayerStatus',c==0 and p<8 and 1 or power);w('PlayerSize',c==0 and power==0 and p>=8 and 1 or 0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('GuestPowerupActive',0);w('MmDeathFlag',0);w('MmDeathAge',0)
 w('SwimmingFlag',(p==6 or p==7) and 1 or 0)
 for _,n in ipairs({'XgDash','XgBassDashJump','XgBassStep','XgJumpUsed','MmJumpReleased','MmFrictionYActive','MmSliding','MmSlideStop','XgWall','XgWallContact','XgWallLock','XgCeiling','XgRise','XgHoverActive','RgAttack','RgAttackAge','RgThrust','RgDoubleJump','RgCooldown','RgShootPose','RgPreviousButtons','XgBassFirePhase','SmBall','SmShootPose','CrouchingFlag'}) do w(n,0) end
 w('PreviousA_B_Buttons',0);w('Player_CollisionBits',3)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 for _,n in ipairs({'MmXFraction','MmYFraction','MmSlideTravel'}) do w(n,0);w(n,0,1) end
end
emu.addEventCallback(function()
 local p,t=phase();local mask=0
 if p==0 then mask=t>=1 and t<26 and 1 or 0
 elseif p==1 then mask=t>=1 and t<65 and 65 or 0
 elseif p==2 or p==6 then mask=t>=1 and t<36 and 128 or 0
 elseif p==3 then mask=t>=1 and t<6 and 128 or 0
 elseif p==5 then mask=t>=1 and t<11 and 1 or 0
 elseif p==7 then mask=t>=1 and t<40 and 1 or 0
 elseif p>=8 and p<=10 then mask=t>=1 and t<80 and 64 or 0
 elseif p==11 then mask=t==1 and 72 or 0
 elseif p==12 then mask=4+(t==1 and 64 or 0)
 elseif p==13 then mask=t==1 and 32 or 0
 elseif p>=14 and p<=16 then mask=t>=1 and t<90 and t%4<2 and 64 or 0
 elseif p==17 then mask=t>=1 and t<40 and 9 or 0
 elseif p==18 then mask=(t>=1 and t<26 and 1 or 0)+(t>=10 and t<13 and 64 or 0)
 elseif p==19 then mask=((t>=1 and t<6) or (t>=12 and t<17) or (t>=23 and t<28)) and 128 or 0
 elseif p==20 then mask=(t>=1 and t<25 and 128 or 0)+(t>=12 and t<15 and 68 or 0)
 end
 emu.setInput({start=frame==240,down=frame==80 and c>=6 or (mask&4)>0,
 right=(frame>=100 and frame<100+20*(c%6) and (frame-100)%20==0) or (mask&1)>0,
 left=(mask&2)>0,up=(mask&8)>0,a=(mask&128)>0,b=(mask&64)>0,select=(mask&32)>0},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<650 then return end
 assert(r('SelectedCharacter')==c,'Selected audit character')
 local p,t=phase()
 if p==21 then csv:close();weapons:close();print('PASS reference observations captured for character '..c..'; no parity claim');emu.stop(0);return end
 if t==0 then fixture(p) end
 local count=0
 local function pool(kind,names,n)
  for i=0,n-1 do
   local ty=r(names[1],i)
   if ty>0 then
    count=count+1
    local age=names[2] and r(names[2],i) or 0
    local x=names[3] and r(names[3],i) or 0
    if names[4] then x=x+256*r(names[4],i) end
    local y=names[5] and r(names[5],i) or 0
    local vx=kind=='Rg' and signed(r('RgShotVXHi',i))+r('RgShotVXLo',i)/256 or 0
    local vy=kind=='Rg' and signed(r('RgShotVYHi',i))+r('RgShotVYLo',i)/256 or 0
    weapons:write(table.concat({frame,p,t,r('PlayerStatus'),kind,i,ty,age,x,y,vx,vy},',')..'\n')
   end
  end
 end
 if c==1 then pool('Mm',{'MmBulletType','MmBulletAge','MmBulletX','MmBulletPage','MmBulletY'},4)
 elseif c==2 then pool('Sm',{'SmShotType','SmShotAge','SmShotX','SmShotPage','SmShotY'},3)
 elseif c==0 then pool('Native',{'Fireball_State',nil,'Fireball_X_Position','Fireball_PageLoc','Fireball_Y_Position'},2)
 else pool('Rg',{'RgShotType','RgShotAge','RgShotX','RgShotPage','RgShotY'},10) end
 local row={frame,p,t,c,r('PlayerStatus'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),v('MmVX'),v('MmVY'),signed(r('Player_X_Speed'))/16,signed(r('Player_Y_Speed'))+r('Player_Y_MoveForce')/256,r('RgPose'),r('RgCrouch'),r('RgShootPose'),r('RgCooldown'),count}
 for _,address in ipairs({0x3f11,0x3f12,0x3f13,0x3f19,0x3f1a,0x3f1b,0x3f1d,0x3f1e,0x3f1f}) do row[#row+1]=emu.read(address,emu.memType.nesPpuDebug) end
 csv:write(table.concat(row,',')..'\n')
 if t==10 or t==50 then local f=assert(io.open(AUDIT_OUTPUT..'phase-'..p..'-'..t..'.png','wb'));f:write(emu.takeScreenshot());f:close() end
 if p==4 or p==5 or p==11 then w('Player_Y_Position',32);w('Player_Y_HighPos',1) end
 for i=0,5 do w('Enemy_Flag',0,i) end
end,emu.eventType.endFrame)
