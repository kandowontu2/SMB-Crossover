-- Exercise pending->Proto directly, title/options reconstruction, and real launch.
local frame,phase,age,step=0,'title',0,1
local route={
 {'right',2,1,'mega'}, {'select',2,1,'proto'},
 {'right',2,2,'samus'}, {'select',2,2,'rogue'},
 {'left',2,1,'proto-return'}, {'right',2,2,'rogue-return'},
 {'b',0,2,'title'}, {'down',0,2,'title-options'},
 {'a',4,2,'options'}, {'b',0,2,'title-return'},
 {'down',0,2,'options-focus-again'}, {'start',4,2,'options-again'},
 {'b',0,2,'title-again'}, {'start',2,2,'roster-rebuilt'},
 {'left',2,1,'proto-rebuilt'}, {'start',-1,1,'launch'}
}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function ram(a)return emu.read(a,emu.memType.nesDebug)end
local shotcount=0
local function screenshot(tag)
 if tag~='rogue'and tag~='proto-return'and tag~='options'and tag~='roster-rebuilt'and tag~='proto-rebuilt'and tag~='game' then return end
 shotcount=shotcount+1;assert(shotcount<=8)
 local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
emu.addEventCallback(function()
 local b={}
 if phase=='open'and age<6 then b.start=true
 elseif phase=='route'and age<4 then b[route[step][1]]=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;age=age+1;assert(frame<1500,'Bounded native reentry')
 if phase=='title'and frame==100 then phase='open';age=0
 elseif phase=='open'and age>=36 then assert(r('CrossoverMenuState')==2);phase='route';age=0
 elseif phase=='route'and age>=30 then
  local s=route[step]
  if s[2]==-1 then phase='game';age=0;return end
  assert(r('CrossoverMenuState')==s[2],'Native page '..s[4])
  assert(r('CrossoverMenuIndex')==s[3],'Retained focus '..s[4])
  if s[4]=='proto-return'or s[4]=='proto-rebuilt'then
   assert(r('ProtoVariant')==1 and r('SelectedCharacter')==1,'Real Proto owner')
   for w=1,7 do
    assert(ram(L.X5ChrMode+w)==0,'No stale direct mode '..w)
    local expected=ram(L.CHRBankInitValues+w)
    assert(ram(L.CurrentCHRBank+w)==expected,'Restored native sprite window '..w)
   end
  end
  screenshot(s[4]);step=step+1;age=0
 elseif phase=='game'and age>=260 then
  assert(r('OperMode')==1 and r('SelectedCharacter')==1 and r('ProtoVariant')==1,'Native Proto launch')
  assert(r('CrossoverMenuState')==0,'Exited selector')
  for w=1,3 do assert(ram(L.X5ChrMode+w)==0,'Clean live Proto window')end
  screenshot('game')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(string.format('{"passed":true,"frames":%d,"pending_to_proto":true,"menu_reentry":true,"options_reentry":true,"native_proto_launch":true,"screenshots":%d}\n',frame,shotcount));f:close()
  print('PASS pending->Proto clean CHR, title/options reentry, RLE screen rebuild and native Proto launch')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
