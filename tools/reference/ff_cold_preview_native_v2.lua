-- Bound original controller inputs only. FF_CLASS/FF_DIR are prepended by
-- the source packet. No emulator writes, savestates or debugger grants.
local wall,age=0,0
local phase='title'
local pad={}
local lastAction=-99
local previewFrame,confirmFrame,loadedFrame,gameFrame=nil,nil,nil,nil
local loader,loaded=false,false
local loaderCalls,loaderReads,cacheWrites=0,0,0
local hardwareMask=0
local sourceMoves,sourceWeapons,sourceDraws,mainCalls,nmis,lagNmis=0,0,0,0,0,0
local normalDmas,paletteChecks,shots=0,0,0
local selectDmas,livesDmas,lastSelectDma,lastLivesDma=0,0,-99,-99
local chrUpper,bodyPhysicalPage=0,-1
local startX,startY,minY=nil,nil,255
local moved,jumped,attack=false,false,false
local seenSpell,seenFamily={},{ }
local captured={}
local mainStart,maxMainElapsed=nil,0
local trace=assert(io.open(OUTPUT..'frames.csv','w'))
trace:write('frame,phase,age,mode,task,engine,index,selected,class,x,page,y,action,actionAge,power,pending,last,turn,moves,weapons,draws,mains,nmi,lagNmi\n')
local palette=assert(io.open(OUTPUT..'normal-DMA-palette.csv','w'))
palette:write('frame,age,family,P0,P1,P2,P3,bodyParts\n')
local guard=assert(io.open(OUTPUT..'cache-events.csv','w'))
guard:write('frame,event,address,value,rawA,rawC\n')
local oam=assert(io.open(OUTPUT..'gameplay-OAM.csv','w'))
oam:write('frame,page,rotation,used,records64hex\n')
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function pr(a)return emu.read(a,emu.memType.nesPpuDebug)end

local menuNames={'   FF FIGHTER   ','  FF WHITE MAGE ','  FF BLACK MAGE ','    FF THIEF    '}
local hudNames={'FIGHTER','WHITE M','BLACK M','THIEF  '}
local menuNameChecked,hudNameChecked=false,false
local function nameAt(address,text)
 for i=1,#text do
  local ch=text:sub(i,i);local value=ch==' 'and 36 or text:byte(i)-string.byte('A')+10
  assert(pr(address+i-1)==value,'Actual hardware name at '..address..' char '..i)
 end
end

local function snapshot(tag)
 if captured[tag]then return end
 shots=shots+1;assert(shots<=6,'Six screenshot bound')
 local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close();captured[tag]=true
end
local function readfile(name)
 local f=assert(io.open(FF_DIR..name,'rb'));local s=f:read('*a');f:close();return s
end
local image,cookie=readfile('ram3.bin'),readfile('ff-cookie.bin')
local originalROM=readfile('candidate.nes')
assert(#image==8192 and #cookie==16,'Exact bound8KB source and16B cookie')
local function verify()
 assert(r('CurrentBank')==3 and r('SelectedCharacter')==22 and r('FfVariant')==FF_CLASS,'Actual selected source RAM3 entry')
 for i=0,8191 do
  local expected=image:byte(i+1)
  if i>=0x1fe0 and i<0x1ff0 then expected=cookie:byte(i-0x1fe0+1)end
  assert(emu.read(0xa000+i,emu.memType.nesDebug)==expected,'Actual loaded FF byte '..i)
 end
end
emu.addMemoryCallback(function(_,v)hardwareMask=v end,emu.callbackType.write,0x2001)

emu.addMemoryCallback(function(_,v)chrUpper=(v&3)*256 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(_,v)bodyPhysicalPage=chrUpper+v end,emu.callbackType.write,0x5120)
local ui=assert(io.open(OUTPUT..'select-lives-DMA.csv','w'))
ui:write('frame,stage,class,physicalPage,header,parts,visible,opaquePixels,P0,background\n')
local function uiBody(stage,page)
 local all={};for i=0,255 do all[i]=emu.read(page*256+i,emu.memType.nesDebug)end
 local base=L.FfRenderBuffer;local header=emu.read(base,emu.memType.nesDebug)
 assert(header>=4 and header<=32 and header%4==0,'Actual UI original body0 record')
 assert(r('FfTemp2')==0 and bodyPhysicalPage==756+r('FfRenderPage') and bodyPhysicalPage>=756 and bodyPhysicalPage<788,'Actual UI hardware window0 is original FF ART, never code carrier')
 local color=FF_CLASS>=2 and{0x28,0x18,0x21}or{0x16,0x30,0x36}
 for i=1,3 do assert(pr(0x3f10+i)==color[i],'Actual UI original class palette '..stage)end
 if stage=='lives'then assert(pr(0x3f00)==0x0f and pr(0x3f10)==0x0f,'Native lives black backdrop preserved')end
 local px=(r('Player_X_Position')-r('ScreenLeft_X_Pos'))&255
 local py=r('Player_Y_Position');local matched,pixels,visible=0,0,0
 for i=0,252,4 do if all[i]<240 then visible=visible+1 end end
 local function signed(v)return v>=128 and v-256 or v end
 for i=1,header,4 do
  local tile=emu.read(base+i,emu.memType.nesDebug)
  local attr=emu.read(base+i+1,emu.memType.nesDebug)&0xdf
  local y=(py+signed(emu.read(base+i+2,emu.memType.nesDebug)))&255
  local x=(px+signed(emu.read(base+i+3,emu.memType.nesDebug)))&255
  assert(tile<64 and attr&3==0 and attr&0x20==0,'UI source body uses original window0/P0/in-front')
  local found=false
  for at=0,252,4 do
   if all[at]==y and all[at+1]==tile and all[at+2]==attr and all[at+3]==x then found=true;break end
  end
  assert(found,'Complete original UI body part submitted to physical DMA '..stage..' part '..i)
  matched=matched+1
  for row=0,15 do
   local pattern=(tile&254)*16+math.floor(row/8)*16+row%8
   local source=1048592+bodyPhysicalPage*1024+pattern
   local lo,hi=originalROM:byte(source+1),originalROM:byte(source+9)
   assert(pr(pattern)==lo and pr(pattern+8)==hi,'Actual hardware UI patterns match original CHR')
   for bit=0,7 do if ((lo>>bit)&1)|(((hi>>bit)&1)<<1)~=0 then pixels=pixels+1 end end
  end
 end
 assert(matched==header/4 and pixels>0 and visible>=matched and visible<=8,'Nonempty complete UI body within normal sprite hardware budget')
 ui:write(table.concat({wall,stage,FF_CLASS,bodyPhysicalPage,header,matched,visible,pixels,string.format('%02x%02x%02x',color[1],color[2],color[3]),pr(0x3f00)},',')..'\n');ui:flush()
end

emu.addMemoryCallback(function()
 if r('CurrentBank')~=(B.FwLoad|0x80)or r('SelectedCharacter')~=22 then return end
 assert(previewFrame and confirmFrame,'Loader follows actual cold preview and confirmation')
 assert(hardwareMask&0x18==0 and r('Mirror_PPUMASK')&0x18==0 and r('DisableScreenFlag')~=0 and r('NmiDisable')>=128,'Actual forced blank loader boundary')
 loader=true;loaderCalls=loaderCalls+1
end,emu.callbackType.exec,L.FwLoad)
emu.addMemoryCallback(function()if loader then loaderReads=loaderReads+1 end end,emu.callbackType.read,0x2007)
emu.addMemoryCallback(function(a,v)
 local raw=a<0xc000 and r('CurrentBank')or r('CurrentBankC')
 if raw~=3 then return end
 cacheWrites=cacheWrites+1
 if cacheWrites==1 then
  assert(a==0xdfe0 and v==0,'Loader invalidates full cookie FIRST')
  guard:write(table.concat({wall,'first',a,v,r('CurrentBank'),r('CurrentBankC')},',')..'\n')
 end
 assert(loader and not loaded,'FF executable/cache has no active gameplay writes')
end,emu.callbackType.write,0xa000,0xdfff)
emu.addMemoryCallback(function()
 if r('CurrentBank')~=3 then return end
 assert(r('SelectedCharacter')==22 and r('FfVariant')==FF_CLASS,'Source identity remains selected class')
 if not loaded then
  verify();loaded=true;loader=false;loadedFrame=wall
  assert(loaderCalls==1 and loaderReads==16400,'Actual buffered8KB copy and full verify')
  guard:write(table.concat({wall,'verified',0xa000,8192,r('CurrentBank'),r('CurrentBankC')},',')..'\n');guard:flush()
 end
end,emu.callbackType.exec,L.FfEnsure)
emu.addMemoryCallback(function()
 if r('CurrentBank')==3 then
  sourceMoves=sourceMoves+1
  assert(loaded and r('FfReady')==0xf7,'Movement follows real verified constructor')
 end
end,emu.callbackType.exec,L.FfMovement)
emu.addMemoryCallback(function()if r('CurrentBank')==3 then sourceWeapons=sourceWeapons+1 end end,emu.callbackType.exec,L.FfWeapons)
emu.addMemoryCallback(function()if r('CurrentBank')==3 then sourceDraws=sourceDraws+1 end end,emu.callbackType.exec,L.FfHostDrawShots)
emu.addMemoryCallback(function(a,v)
 if r('CurrentBank')~=3 or not loaded then return end
 local delta=a-L.FfProjectile
 if(delta==0 or delta==12 or delta==24)and v>=1 and v<=4 then seenSpell[v]=true end
end,emu.callbackType.write,L.FfProjectile,L.FfProjectile+35)
emu.addMemoryCallback(function()
 mainCalls=mainCalls+1;mainStart=emu.getState()['cpu.cycleCount']
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if mainStart then maxMainElapsed=math.max(maxMainElapsed,emu.getState()['cpu.cycleCount']-mainStart+6);mainStart=nil end
end,emu.callbackType.exec,FF_MAIN_RETURN)
emu.addMemoryCallback(function()
 nmis=nmis+1;if r('NmiDisable')>=128 then lagNmis=lagNmis+1 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
local function vec(a)return{pr(a),pr(a+1),pr(a+2)}end
local function equal(a,b)return a[1]==b[1]and a[2]==b[2]and a[3]==b[3]end
local function text(a)return string.format('%02x%02x%02x',a[1],a[2],a[3])end
local families={[0]={0x1a,0x30,0x27},[1]={0x16,0x26,0x30},[2]={0x12,0x21,0x30},[3]={0x18,0x28,0x30},[4]={0x0c,0x1c,0x2c},[5]={0x0f,0x0f,0x0f}}
emu.addMemoryCallback(function(_,page)
 if r('SelectedCharacter')==22 and r('FfVariant')==FF_CLASS then
  if phase=='select' and r('OperMode')==0 and r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==21 and wall-lastAction>=8 and wall-lastSelectDma>=8 then
   uiBody('select',page);selectDmas=selectDmas+1;lastSelectDma=wall
  elseif loaded and r('OperMode')==1 and r('ScreenRoutineTask')==7 and wall-lastLivesDma>=8 then
   uiBody('lives',page);livesDmas=livesDmas+1;lastLivesDma=wall
  end
 end
 if phase~='game'then return end
 normalDmas=normalDmas+1;assert(normalDmas<=1200,'Bounded OAM stream')
 local all={};for i=0,255 do all[i]=emu.read(page*256+i,emu.memType.nesDebug)end
 local hex={};for i=0,255 do hex[#hex+1]=string.format('%02x',all[i])end
 oam:write(table.concat({wall,page,r('RgOamRotation'),r('RgOamUsed'),table.concat(hex)},',')..'\n')
 if age<8 then return end
 assert(r('SmFreezeLastBlue')>=0x80 and r('SmFreezeLastBlue')<=0x85,'Completed FF palette owner family')
 assert(r('SmFreezePalettePending')==0,'Complete palette packet consumed before OAM DMA')
 assert(pr(0x3f00)==0x22 and pr(0x3f10)==0x22,'Actual native overworld universal blue remains')
 local p0,p1,p2,p3=vec(0x3f11),vec(0x3f15),vec(0x3f19),vec(0x3f1d)
 local body=FF_CLASS>=2 and{0x28,0x18,0x21}or{0x16,0x30,0x36}
 assert(equal(p0,body),'Actual original class P0 colors')
 local family=r('SmFreezeLastBlue')&7
 assert(equal(p1,assert(families[family])),'Actual source-exact selected P1 family')
 assert(equal(p2,{0x16,0x30,0x27})and equal(p3,{0x0f,0x36,0x17}),'Native world P2/P3 remain unchanged')
 local ptr=r('SmPosePtr')+256*emu.read(L.SmPosePtr+1,emu.memType.nesDebug)
 local header=emu.read(ptr,emu.memType.nesDebug)
 local first=r('RgOamPlayerStart');assert(header>=4 and header<=64 and header%4==0,'Actual source body0 descriptor')
 local count=0
 for logical=first,first+header-4,4 do
  local at=(logical+r('RgOamRotation'))&255
  if all[at]<240 and all[at+2]&3==0 then count=count+1 end
 end
 assert(count>0,'Actual visible source body0 submitted to hardware OAM')
 for at=0,252,4 do
  if all[at]<240 then
   assert(all[at+2]&0x1c==0,'All transient family/world markers stripped before DMA')
   if all[at+2]&3==1 then seenFamily[family]=true end
  end
 end
 paletteChecks=paletteChecks+1
 palette:write(table.concat({wall,age,family,text(p0),text(p1),text(p2),text(p3),count},',')..'\n')
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()emu.setInput(pad,0)end,emu.eventType.inputPolled)
local function action(button)
 if wall-lastAction<8 then return end
 pad[button]=true;lastAction=wall
end
local function finish()
 assert(menuNameChecked and hudNameChecked,'Actual cold menu and gameplay hardware class names')
 assert(selectDmas>0 and livesDmas>0,'Actual select AND lives nonempty physical OAM/original hardware CHR/PPU verified')
 assert(previewFrame and loaded and gameFrame and captured['lives'],'Actual cold menu/lives/load/gameplay reached')
 assert(sourceMoves>=20 and sourceWeapons>=20 and sourceDraws>=10,'Actual original source updates and render reached')
 assert(moved and jumped and attack,'Actual movement/jump/attack observed')
 assert(paletteChecks>=20 and normalDmas>=20,'Actual completed-NMI PPU/OAM coverage')
 if FF_CLASS==1 then assert(seenSpell[4]and seenFamily[2],'Real controller Down+B Light allocated and displayed')
 elseif FF_CLASS==2 then assert(seenSpell[1]and seenFamily[1],'Real controller Fire allocated and displayed')
 else assert(seenFamily[4],'Real controller melee sword source family displayed')end
 snapshot('gameplay-final')
 trace:close();palette:close();guard:close();oam:close();ui:close()
 local u=assert(io.open(OUTPUT..'ui-result.json','w'));u:write(string.format('{"passed":true,"class":%d,"select_DMA_checks":%d,"lives_DMA_checks":%d,"actual_original_chr_oam_ppu":true}\n',FF_CLASS,selectDmas,livesDmas));u:close()
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(string.format('{"passed":true,"native":true,"debug_RAM_writes":false,"class":%d,"physical_frames":%d,"game_frames":%d,"preview_frame":%d,"loaded_frame":%d,"game_frame":%d,"loader_calls":%d,"loader_reads":%d,"cache_writes_during_loader":%d,"source_moves":%d,"source_weapons":%d,"source_draws":%d,"mains":%d,"nmis":%d,"lag_nmis":%d,"normal_DMAs":%d,"palette_checks":%d,"moved":true,"jumped":true,"attack":true,"minY":%d,"maximum_Main_elapsed_including_ISR":%d,"cadence_qualification":false}\n',FF_CLASS,wall,age,previewFrame,loadedFrame,gameFrame,loaderCalls,loaderReads,cacheWrites,sourceMoves,sourceWeapons,sourceDraws,mainCalls,nmis,lagNmis,normalDmas,paletteChecks,minY,maxMainElapsed));f:close()
 emu.stop(0);return
end
emu.addEventCallback(function()
 wall=wall+1;pad={}
 local mode,state,index=r('OperMode'),r('CrossoverMenuState'),r('CrossoverMenuIndex')
 if phase=='title'then
  if mode==0 and state==2 then phase='select'elseif wall>=50 then action('start')end
 elseif phase=='select'then
  assert(not loaded,'Cold menu precedes source execution')
  if state==2 then
   local row,col=math.floor(index/8),index%8
   if row<2 then action('down')elseif row>2 then action('up')elseif col<5 then action('right')elseif col>5 then action('left')
   elseif r('FfVariant')~=FF_CLASS then action('select')
   elseif wall-lastAction>=16 and selectDmas>0 and wall-lastSelectDma<=8 then
    assert(r('SelectedCharacter')==22,'Actual selected FF identity')
    nameAt(0x2328,menuNames[FF_CLASS+1]);menuNameChecked=true; snapshot('class-cold-menu');previewFrame=wall;phase='confirm'
   end
  end
 elseif phase=='confirm'then
  if wall-previewFrame>=12 then pad.a=true;confirmFrame=wall;phase='loading'end
 elseif phase=='loading'then
  if state==2 and wall-confirmFrame<8 then pad.a=true end
  if mode==1 and r('ScreenRoutineTask')==7 and loaded and livesDmas>0 and wall-lastLivesDma<=8 then snapshot('lives')end
  if mode==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and loaded then
   assert(r('FfVariant')==FF_CLASS and r('FfReady')==0xf7,'Real selected constructor survived native entrance')
   gameFrame=wall;startX=r('Player_X_Position');startY=r('Player_Y_Position');phase='game'
  end
 elseif phase=='game'then
  age=age+1
  if age>=8 and not hudNameChecked then nameAt(0x2043,hudNames[FF_CLASS+1]);hudNameChecked=true end
  assert(r('SelectedCharacter')==22 and r('FfVariant')==FF_CLASS,'Selected class remains during play')
  assert(r('MmDeathFlag')==0 and r('NumberofLives')==2,'No death/life loss in bounded first-look scene')
  pad.right=age<=36
  pad.a=age>=12 and age<52
  pad.b=age>=72 and age<122
  pad.down=FF_CLASS==1 and pad.b or false
  minY=math.min(minY,r('Player_Y_Position'))
  moved=moved or r('Player_X_Position')>=startX+8
  jumped=jumped or r('Player_Y_Position')<=startY-16
  attack=attack or r('FfAction')~=0
  if jumped then snapshot('source-jump')end
  if attack then snapshot('source-attack')end
  if age>=260 then finish();return end
 end
 trace:write(table.concat({wall,phase,age,mode,r('OperMode_Task'),r('GameEngineSubroutine'),index,r('SelectedCharacter'),r('FfVariant'),r('Player_X_Position'),r('Player_PageLoc'),r('Player_Y_Position'),r('FfAction'),r('FfAge'),r('FfPower'),r('SmFreezePalettePending'),r('SmFreezeLastBlue'),r('SmFreezeTurn'),sourceMoves,sourceWeapons,sourceDraws,mainCalls,nmis,lagNmis},',')..'\n')
 if wall>=1200 then snapshot('timeout');assert(false,'Bounded native FF timeout phase='..phase)end
end,emu.eventType.endFrame)
