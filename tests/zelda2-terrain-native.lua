-- Explicit isolated geometry staging on actual1-1 terrain, after real selection.
-- This does not claim to earn Fairy, discover a route or prove all abilities.
local C=assert(Z2_TERRAIN_CONFIG)
local wall,updates,index,age=0,0,0,0
local entered,done,checked=false,false,false
local results,frames={},{}
local function json(v)
 if type(v)=='table'then
  local out={}
  if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',k)..':'..json(x)end
  return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)
 else return tostring(v)end
end
local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
local function w(n,v)emu.write(assert(C.ram[n],n),v&255,emu.memType.nesDebug)end
local function actual(h)
 local p=emu.convertAddress(h.address)
 return p and p.address//8192==h.physical_bank
end
local function bound(h)
 for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Geometry hook opcode binding')end
end
local function native()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function world()return r('Player_X_Position')+256*r('Player_PageLoc')end
local saved,nmis=nil,0
emu.addMemoryCallback(function()
 if not entered then return end
 saved={a=emu.convertAddress(0xa000).address//8192,c=emu.convertAddress(0xc000).address//8192,fields={}}
 for _,a in ipairs(C.smc_fields)do saved.fields[#saved.fields+1]=emu.read(a,emu.memType.nesDebug)end
 nmis=nmis+1
end,emu.callbackType.exec,C.nmi.address)
emu.addMemoryCallback(function()
 if not saved then return end
 assert(emu.convertAddress(0xa000).address//8192==saved.a and emu.convertAddress(0xc000).address//8192==saved.c,'Geometry NMI restores foreground banks')
 for i,a in ipairs(C.smc_fields)do assert(emu.read(a,emu.memType.nesDebug)==saved.fields[i],'Geometry NMI preserves five SMC operands')end
 saved=nil
end,emu.callbackType.exec,C.nmi_return.address)
emu.addMemoryCallback(function()
 if not actual(C.bg)or not native()or r('SelectedCharacter')~=4 or r('Z2Variant')~=1 then return end
 if not entered and world()<400 then return end
 bound(C.bg);entered=true;updates=updates+1
 index=(updates-1)//16+1;age=(updates-1)%16
 if index>#C.cases then done=true;return end
 if age~=0 then return end
 checked=false
 local q=C.cases[index]
 -- Stage only geometry, speed, spell form and isolated nearby actors. The
 -- native background collision, block/reward routines and post-hook execute.
 for i=0,5 do emu.write(C.ram.Enemy_Flag+i,0,emu.memType.nesDebug)end
 w('Player_X_Position',q.x%256);w('Player_PageLoc',q.x//256)
 w('Player_Y_Position',q.y);w('Player_Y_HighPos',1)
 w('Player_Y_Speed',q.vy);w('Z2NativeVY',q.vy)
 w('Z2NativeGravityFraction',0);w('Z2NativeAir',1);w('Player_State',1)
 w('Z2NativeVX',0);w('Player_X_Speed',0);w('Player_X_Scroll',0)
 w('Z2NativeXFraction',0);w('CrouchingFlag',q.crouch or 0)
 w('Z2ActiveSpells',q.fairy and 8 or 0);w('SmCeilingHit',0)
 w('Z2PreviousTerrainY',q.oldY or q.y)
 w('BlockBounceTimer',0);w('DisableCollisionDet',0)
end,emu.callbackType.exec,C.bg.address)
emu.addMemoryCallback(function()
 if not entered or done or age~=0 or not actual(C.after)then return end
 bound(C.after)
 local q=C.cases[index]
 local row={case=index,name=q.name,frame=wall,x=world(),y=r('Player_Y_Position'),state=r('Player_State'),vy=r('Player_Y_Speed'),sm=r('SmCeilingHit')}
 results[#results+1]=row;print('Z2_GEOMETRY '..json(row))
 assert(row.x==q.wantX and row.y==q.wantY,'Native geometry differs: '..q.name)
 assert(row.sm==0,'Post-BG geometry flag released')
 if q.blockX then
  local found=false
  for i=0,1 do
   local x=emu.read(C.ram.Block_X_Position+i,emu.memType.nesDebug)+256*emu.read(C.ram.Block_PageLoc+i,emu.memType.nesDebug)
   local state=emu.read(C.ram.Block_State+i,emu.memType.nesDebug)
   if state~=0 then assert(x==q.blockX,'Bumped block retains its contacted world column');found=true end
  end
  assert(found,'Real native bumped block actor')
 end
 checked=true
end,emu.callbackType.exec,C.after.address)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if native()then b.right=true
  elseif wall>=120 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')~=4 then b.right=true
   elseif r('Z2Variant')~=1 then b.select=true else b.a=true end
  end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;assert(wall<2200,'Bounded terrain component')
 if entered and index<=#C.cases and age>=1 and age<=8 then
  local name='case-'..index..'-frame-'..wall
  local f=assert(io.open(OUTPUT..name..'.argb','wb'))
  for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end
  f:close();frames[#frames+1]={case=index,frame=wall,file=name..'.argb'}
 end
 if done then
  assert(#results==#C.cases and nmis>20,'Every actual geometry case executed')
  local f=assert(io.open(OUTPUT..'proof.json','w'))
  f:write(json({passed=true,cases=results,physical_frames=frames,nmis=nmis,staged=true,scope='Real original1-1 terrain; explicit collision-entry geometry/Fairy/actor isolation staging. Native background and block effects plus bank/SMC NMI preservation. Not natural power acquisition, moving-platform or full-level proof.'}));f:close()
  emu.stop(0)
 end
end,emu.eventType.endFrame)
