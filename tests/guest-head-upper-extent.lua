-- Explicit collision-unit arenas, not traversal proof. Each case enters the
-- real PlayerBGCollision routine with one authored actor pose and a roof at
-- Y32. No CPU registers, ROM, projectile state or decoded save states change.
-- The expected probe uses the independently listed pose head offset; the
-- original Mario/Luigi cutoff and the native low-nibble rule remain controls.
local frame,index,current,finished=0,0,nil,false
local cases={}
local poses={
 {char=4,name='Link',offset=17},
 {char=1,name='MegaMan stand',offset=8},{char=1,name='MegaMan air',offset=4,state=1},
 {char=1,name='MegaMan slide',offset=17,slide=1,crouch=4},
 {char=2,name='Samus stand',offset=1},{char=2,name='Samus air',offset=7,state=1},
 {char=2,name='Samus crouch',offset=17,smCrouch=1,crouch=4},
 {char=2,name='Samus ball',offset=19,ball=1,crouch=4},
 -- Bill and Sophia are omitted: their heads read cells from source HRects
 -- (BillHeadDispatch/SophiaSourceHeadProbe), not this native probe/offset table or its canonical-Y low-nibble response.
 {char=5,name='Simon stand',offset=1},{char=5,name='Simon air',offset=7,state=1},
 {char=5,name='Simon crouch',offset=19,rgCrouch=1,crouch=4},
 {char=6,name='Pit',offset=8},{char=6,name='Pit crouch',offset=19,rgCrouch=1,crouch=4},
 {char=7,name='Rygar',offset=1},{char=7,name='Rygar crouch',offset=19,rgCrouch=1,crouch=4},
 {char=9,name='Bass',offset=8},{char=9,name='Bass crouch',offset=19,rgCrouch=1,crouch=4},
 {char=10,name='Ryu',offset=1},{char=10,name='Ryu crouch',offset=19,rgCrouch=1,crouch=4},
 {char=12,name='Scrooge',offset=8},{char=12,name='Scrooge crouch',offset=8,rgCrouch=1,crouch=4},
 {char=0,name='Mario big',offset=4,native=true},
 {char=0,name='Mario small',offset=18,size=1,native=true},
 {char=0,name='Mario crouch',offset=18,crouch=4,native=true},
 {char=8,name='Luigi big',offset=4,status=1,native=true},
 {char=8,name='Luigi small',offset=18,size=1,native=true},
 {char=8,name='Luigi crouch',offset=18,status=1,rgCrouch=1,crouch=4,native=true},
}
for _,p in ipairs(poses)do for _,head in ipairs({40,35,31})do
 cases[#cases+1]={pose=p,head=head}
end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local log=assert(io.open(OUTPUT..ROM_NAME..'-guest-head-upper-extent.csv','w'))
log:write('case,pose,character,canonicalY,headY,expectedProbe,actualProbe,vy\n')
emu.addEventCallback(function()emu.setInput({start=frame==240},0)end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<600 or current or finished then return end
 index=index+1;local c=cases[index]
 if not c then finished=true;log:close();print('PASS guest head cutoffs: all27 poses at3 roof/HUD heights; native Mario/Luigi and low-nibble semantics retained');emu.stop(0);return end
 current=c;c.probe=false
 local p=c.pose;local py=c.head-p.offset
 for i=0,415 do w('Block_Buffer_1',0,i)end
 -- $61 is the actual solid white castle wall (MTILE_BUMP), not a breakable
 -- terrain brick; this arena must take the native NYSpd collision path.
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x61,page*208+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('SelectedCharacter',p.char);w('PlayerStatus',p.status or 0);w('PlayerSize',p.size or 0)
 w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',py);w('Player_Y_HighPos',1)
 w('Player_State',p.state or 0);w('Player_Y_Speed',255);w('PlayerFacingDir',1)
 w('CrouchingFlag',p.crouch or 0);w('RgCrouch',p.rgCrouch or 0)
 -- Samus admits a roof only when her previous head (Y-MmVY) was at/below the
 -- cell bottom (2.02 checkLastHitPoints). Author a genuine upward crossing
 -- from the roof's bottom edge instead of inheriting the prior case's motion.
 if p.char==2 then
  for i=0,1 do w('MmVY',0,i);w('MmYFraction',0,i)end
  w('MmVY',c.head-48,2)
 end
 w('MmSliding',p.slide or 0);w('SmBall',p.ball or 0);w('SmCrouch',p.smCrouch or 0)
 w('DisableCollisionDet',0);w('SwimmingFlag',0);w('GameEngineSubroutine',8);w('BlockBounceTimer',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 c.expected=c.head>=32
 if p.native then c.expected=py>=((p.size==1 or p.crouch)and 16 or 32)end
end,emu.callbackType.exec,L.PlayerBGCollision)
-- PlayerBGCollision normally changes a grounded state to falling before the
-- adder is selected. Author the exact table pose here as well so the unit
-- matrix genuinely covers both standing and airborne head offsets.
emu.addMemoryCallback(function()
 if current then w('Player_State',current.pose.state or 0)end
end,emu.callbackType.exec,L.MegaManCollisionAdder)
emu.addMemoryCallback(function()if current then current.probe=true end end,emu.callbackType.exec,L.BlockBufferColli_Head)
emu.addMemoryCallback(function()
 if not current then return end
 local c=current;local p=c.pose
 log:write(table.concat({index,p.name,p.char,r('Player_Y_Position'),c.head,tostring(c.expected),tostring(c.probe),r('Player_Y_Speed')},',')..'\n');log:flush()
 assert(c.probe==c.expected,p.name..' headY'..c.head..' requires probe='..tostring(c.expected)..'; canonicalY='..r('Player_Y_Position'))
 local canonicalY=r('Player_Y_Position')
 local stop=c.probe and canonicalY%16>=4
 assert(r('Player_Y_Speed')==(stop and 1 or 255),p.name..' preserves native canonical-Y low-nibble rule and actually processes solid roof')
 current=nil
end,emu.callbackType.exec,L.DoFootCheck)
emu.addEventCallback(function()frame=frame+1;assert(frame<1500,'Bounded head collision fixture completes')end,emu.eventType.endFrame)
