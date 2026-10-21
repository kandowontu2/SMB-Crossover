-- Only isolated arena setup/history is injected. Real controller directions
-- advance pinned2.02 Link checkState START->END, with Up taking precedence.
local frame,depth,index,pending,started=0,0,1,false,false
local specs={
 {mask=4,phase=1,active=0},{mask=4,phase=1,active=1},
 {mask=8,phase=2,active=0},{mask=8,phase=2,active=2},
 {mask=12,phase=2,active=2},{mask=0,phase=0,active=0},
 {mask=4,phase=1,active=0},{mask=68,phase=1,active=1,beam=true},
 {mask=4,phase=1,active=1},{mask=4,phase=0,active=0,ground=true},
 {mask=4,phase=1,active=0},{mask=4,phase=1,active=1},
}
local cases={}
for power=0,2 do for i,s in ipairs(specs)do local c={power=power,first=i==1};for k,v in pairs(s)do c[k]=v end;cases[#cases+1]=c end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced Link phase interrupts')end,emu.callbackType.exec,pc)end
emu.addEventCallback(function()
 local c=frame>=550 and cases[index]or nil;local mask=c and c.mask or 0
 emu.setInput({right=frame>=80 and frame<160 and(frame-80)%20==0,start=frame==200,up=(mask&8)~=0,down=(mask&4)~=0,b=(mask&64)~=0},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<560 or pending or depth~=0 or r('CurrentBank')%128~=22 then return end
 local c=cases[index];if not c or (r('SavedJoypadBits')&76)~=c.mask or
  (r('A_B_Buttons')&64)~=(c.mask&64)then return end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',c.ground and 176 or 96);w('Player_Y_HighPos',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0)
 w('GameEngineSubroutine',8);w('AreaType',1);w('SwimmingFlag',0);w('TimerControl',0);w('GuestPowerupActive',0)
 w('Player_State',c.ground and 0 or 1);w('PlayerStatus',c.power);w('InvOwnedLo',0,4);w('InvOwnedHi',0,4);w('PlayerSize',0)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_CollisionBits',255);w('InjuryTimer',0);w('RgAttack',0);w('RgCrouch',0);w('CrouchingFlag',0)
 w('PreviousA_B_Buttons',0);w('RgPreviousButtons',0)
 if c.first then w('RgThrustReset',0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('MmFrictionYActive',0);pending=true;started=true
end,emu.callbackType.exec,assert(L.RosterMovement))
emu.addMemoryCallback(function()
 if not pending or depth~=0 or r('CurrentBank')%128~=8 then return end
 local c=cases[index]
 assert(r('RgThrustReset')==c.phase and r('RgThrust')==c.active,'Source START/END direction phase '..index..': '..r('RgThrustReset')..'/'..r('RgThrust'))
 assert(r('RgAttack')==0,'Aerial thrust+B cannot start an ordinary forward sword attack')
 local beams=0;for i=0,9 do if r('RgShotType',i)==4 then beams=beams+1 end end
 assert(beams==((c.beam and c.power==2)and 1 or 0),'Only the red-ring actual B press emits a thrust sword beam')
 pending=false;index=index+1
 if not cases[index]then print('PASS '..#cases..' Link source held START/END phases, Up precedence, release/landing reset, thrust+B and red-ring beam');emu.stop(0)end
end,emu.callbackType.exec,assert(L.RosterWeaponsFinish))
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then assert(r('SelectedCharacter')==4 and r('GameEngineSubroutine')==8,'Real menu launches Link before phase arenas')end
 assert(frame<1400,'All real controller thrust phases complete '..index..' started'..tostring(started))
end,emu.eventType.endFrame)
