-- Natural title -> Mr. Gimmick Select3 -> five rings -> Goomba -> recovery.
-- The bounded stdout runner supplies the exact tested ROM pin.
local rom = os.getenv('SMB_STDOUT_ROM_SHA') or ''
local variant = tonumber(os.getenv('SMB_TEST_VARIANT') or '0')
local wantImages = os.getenv('SMB_STDOUT_IMAGES') == '1'
local cookie = os.getenv('SMB_SONIC_COOKIE') or 'a72b014bfcfc603f5bf6c05820733ae8'
local A = {
 mode=0x771, task=0x773, engine=0x0f, owner=0x6002, title=0x6004, blank=0x775,
 menu=0x7307, slot=0x7309, alternate=0x5ffe, x=0x75, page=0x5c, y=0xbd,
 yPage=0xa4, playerState=0x1e, lives=0x75f, tier=0x75b, world=0x764,
 level=0x761, area=0x754, startCheat=0x7ffc, invincible=0x7ffb,
 scroll=0x71f, scrollPage=0x71d, joy=0xdc, injury=0x79b, timer=0x74a,
 enemyFlag=0x10, enemyID=0x17, enemyState=0x1f, enemyX=0x76, enemyPage=0x5d,
 enemyY=0xbe, oamCursor=0x6de, posePointer=0x6b06, playerStart=0x6c07,
 rotation=0x6c08, oamFirst=0x6c09, oamUsed=0x6c0a, rotating=0x6c0b
}
local frame, mains, completed, polls, activeMains = 0, 0, 0, 0, 0
local previousCompleted, pad, chrUpper, bodyPage, ppuCtrl, ppuMask = 0, 0, 0, -1, 0, 0
local stopped, gameplay, main, firstActive, previous, draw, routeEnd = false, false
local force, hit, activation, landed, resumed, expired, suppression
local calls, picks, recentDraws, images, hardwareValues, firstVisual = {}, {}, {}, {}, {}, {}
local firstRendered, raster, rejected, cursorExamples = {}, {}, {}, {}
local lastCursor
local oamPass, lastReservation, reservationConflict
local reservationExamples={}
local reservations={passes=0,closed=0,private_slots=0,world_slots=0,native_body_slots=0,
                    passes_with_private_and_world=0,max_world_slots=0}
local visual = {hud=0, world=0, sparkle=0, drop=0, oam_matches=0, unmatched=0,
               raster_matches=0, pixel_checks=0, pixel_rejections=0, empty_draws=0}
local cadence = {catchup=0, zero_updates=0, physical_gameplay=0, max_updates_per_frame=0}
local dropTiles = {[40]=true,[42]=true,[44]=true,[46]=true,[48]=true,[50]=true,[52]=true,[54]=true}

local function read(at, kind)
 return emu.read(at, kind or emu.memType.nesDebug)
end
local function native(name, index) return read(A[name] + (index or 0)) end
local function source(at, bank)
 return read((bank or 2)*8192 + (at&8191), emu.memType.nesWorkRam)
end
local function word(at) return source(at) + 256*source(at+1) end
local function signed(at)
 local n = word(at) + 65536*source(at+2)
 return n >= 0x800000 and n-0x1000000 or n
end
local function header(bank)
 local out = {}
 for at=0x1fe0,0x1fef do out[#out+1] = string.format('%02x',source(at,bank)) end
 return table.concat(out)
end
local function state()
 return {frame=frame,main=mains,completed=completed,mode=native('mode'),task=native('task'),
  engine=native('engine'),owner=native('owner'),world=native('world'),level=native('level'),area=native('area'),
  x=native('x')+256*native('page'),y=native('y'),y_page=native('yPage'),player_state=native('playerState'),
  camera=native('scroll')+256*native('scrollPage'),lives=native('lives'),tier=native('tier'),
  saved_input=native('joy'),injury_timer=native('injury'),timer=native('timer'),
  tick=source(0x92),source_x=word(0x71),source_y=word(0x74),vx=signed(0x20),vy=signed(0x60),
  flags=source(0x30),pose=source(0x31),width=source(0x41),source_input=source(0xa8),ready=source(0x119),
  frame_status=source(0x116),bcd=source(0x340),stun=source(0x34f),drop_flags=source(0x351),
  drop=source(0x35e),drop_x=word(0x360),drop_y=word(0x363),drop_vy=signed(0x368),
  drop_sprite=word(0x36d),spark=source(0x34c),cells={source(0x378),source(0x379),source(0x37a)}}
end
local function active(s) return s.mode == 1 and s.task == 3 and s.engine == 8 end
local function enemy(index)
 return {slot=index,flag=native('enemyFlag',index),id=native('enemyID',index),
  state=native('enemyState',index),x=native('enemyX',index)+256*native('enemyPage',index),
  y=native('enemyY',index)}
end
local function quote(s)
 return '"' .. s:gsub('[%z\1-\31\\"]', function(c)
  if c == '"' then return '\\"' end
  if c == '\\' then return '\\\\' end
  return string.format('\\u%04x',string.byte(c))
 end) .. '"'
end
local function json(value)
 local t=type(value)
 if t=='string' then return quote(value) end
 if t=='number' or t=='boolean' then return tostring(value) end
 if t=='nil' then return 'null' end
 assert(t=='table','JSON value type '..t)
 local out={}
 if #value>0 then
  for _,x in ipairs(value) do out[#out+1]=json(x) end
  return '['..table.concat(out,',')..']'
 end
 for k,x in pairs(value) do out[#out+1]=quote(tostring(k))..':'..json(x) end
 table.sort(out)
 return '{'..table.concat(out,',')..'}'
end
local function finish(ok, reason)
 if stopped then return end
 stopped, pad = true, 0
 local got, terminal=pcall(state)
 if not got then terminal={snapshot_error=tostring(terminal)} end
 local values={}
 for n=0,5 do if hardwareValues[n] then values[#values+1]=n end end
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=reason,ROM_SHA256=rom,variant=variant,
  controller_only=true,script_RAM_writes=false,save_load_or_cheats=false,output_files=0,
  physical_frames=frame,logical_Main_entries=mains,completed_Main=completed,input_polls=polls,
  active_Main_updates=activeMains,menu={slot=25,select=3,raw=43},cadence=cadence,
  headers={header(2),header(3)},first_active=firstActive,pickups=picks,native_hit=force,ring_loss=hit,
  input_suppressed=suppression,type55_activation=activation,grounded_recovery=landed,resumed=resumed,
  type55_expired=expired,terminal=terminal,calls=calls,visual_counts=visual,hardware_hud_values=values,
  first_hardware_publications=firstVisual,first_rendered_publications=firstRendered,
  pixel_rejection_examples=rejected,last_oam_cursor=lastCursor,oam_cursor_examples=cursorExamples,
  reservation_counts=reservations,last_reservation=lastReservation,
  reservation_examples=reservationExamples,reservation_conflict=reservationConflict,
  route_completed=routeEnd~=nil,image_tags=images,
  scope='Sonic five-ring fixture in SMB 1-1, real Goomba contact, original ring drop and recovery'}))
 emu.stop(ok and 0 or 1)
end
local function guarded(name, fn)
 return function(...)
  if stopped then return end
  local ok, reason=pcall(fn,...)
  if not ok then finish(false,name..': '..tostring(reason)) end
 end
end
local function mapped(pc, bank, kind)
 local entry=emu.convertAddress(pc)
 return entry and entry.memType==emu.memType[kind] and entry.address==8192*bank+(pc&8191)
end
local function hook(pc, bank, kind, name, fn)
 emu.addMemoryCallback(guarded(name,function()
  if not mapped(pc,bank,kind) then return end
  calls[name]=(calls[name] or 0)+1
  fn(emu.getState())
 end),emu.callbackType.exec,pc)
end
local function watchWrite(at, fn)
 emu.addMemoryCallback(guarded('register '..string.format('%04x',at),function(_,v) fn(v) end),
  emu.callbackType.write,at)
end
local function stackReturn(c)
 local sp=c['cpu.sp']
 return (read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535,(sp+2)&255
end
local function oamState()
 return {cursor=native('oamCursor'),player_start=native('playerStart'),used=native('oamUsed'),
         first=native('oamFirst'),rotation=native('rotation'),active=native('rotating')}
end
local function slotCount(slots)
 local n=0
 for _ in pairs(slots) do n=n+1 end
 return n
end
local function reservationCheck(ok, reason, at, pc)
 if ok then return end
 reservationConflict={reason=reason,address=at,pc=pc,phase=oamPass and oamPass.phase}
 error(reason)
end
local function buttons(bits)
 return {right=bits&1~=0,left=bits&2~=0,down=bits&4~=0,up=bits&8~=0,
  start=bits&16~=0,select=bits&32~=0,b=bits&64~=0,a=bits&128~=0}
end

local function classify(sprites)
 local out={hud={},world={},sparkle={},drop={}}
 for _,s in ipairs(sprites) do
  local y,tile,attr,x=s.y,s.tile,s.attr,s.x
  if y<240 and attr==2 then
   if y==34 and ((x==208 and tile==24) or (x==216 and tile==26)
      or ((x==224 or x==232) and tile>=4 and tile<=22 and tile%2==0)) then
    out.hud[#out.hud+1]=s
   elseif y==167 and (tile==28 or tile==30) then out.world[#out.world+1]=s
   elseif tile==36 or tile==38 then out.sparkle[#out.sparkle+1]=s
   elseif dropTiles[tile] then out.drop[#out.drop+1]=s end
  end
 end
 return out
end
local function displayedCount(hud)
 if #hud~=4 then return nil end
 local tiles={}
 for _,s in ipairs(hud) do tiles[s.x]=s.tile end
 if tiles[208]~=24 or tiles[216]~=26 or not tiles[224] or not tiles[232] then return nil end
 return 16*((tiles[224]-4)//2)+(tiles[232]-4)//2
end
local function signature(groups)
 local all={}
 for name,parts in pairs(groups) do
  for _,s in ipairs(parts) do all[#all+1]=string.format('%s/%d/%d/%d/%d',name,s.y,s.tile,s.attr,s.x) end
 end
 table.sort(all)
 return table.concat(all,':')
end
local function sprite(at,kind,slot)
 return {slot=slot,y=read(at,kind),tile=read(at+1,kind),attr=read(at+2,kind),x=read(at+3,kind)}
end
local function pairsVisible(world)
 for _,s in ipairs(world) do
  if s.tile==28 then
   for _,other in ipairs(world) do if other.tile==30 and other.x==s.x+8 then return true end end
  end
 end
 return false
end
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function base64(bytes)
 local out={}
 for i=1,#bytes,3 do
  local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2)
  local n=(a<<16)|((b or 0)<<8)|(c or 0)
  local x,y,z,w=(n>>18)&63,(n>>12)&63,(n>>6)&63,n&63
  out[#out+1]=alphabet:sub(x+1,x+1)..alphabet:sub(y+1,y+1)
   ..(b and alphabet:sub(z+1,z+1) or '=')..(c and alphabet:sub(w+1,w+1) or '=')
 end
 return table.concat(out)
end
local function png(tag)
 if not wantImages then return end
 assert(#images<3,'Three stdout PNGs maximum')
 local bytes=emu.takeScreenshot()
 assert(type(bytes)=='string' and bytes:sub(1,8)=='\137PNG\r\n\26\n','In-memory PNG')
 images[#images+1]={tag=tag,frame=frame,bytes=#bytes}
 print('SMB_NATIVE_IMAGE '..base64(bytes))
end
local function stamp()
 local p=emu.getState()
 return {ppu_frame=p['ppu.frameCount'],scanline=p['ppu.scanline'],dot=p['ppu.cycle'],cpu_cycle=p['cpu.cycleCount']}
end
local function oamPublication()
 if not gameplay or bodyPage~=224 or ppuCtrl&0x20==0 or ppuMask&0x10==0 then return end
 local oam={}
 for i=0,63 do oam[#oam+1]=sprite(i*4,emu.memType.nesSpriteRam,i) end
 local groups=classify(oam)
 local value=displayedCount(groups.hud)
 if not value then return end
 local fingerprint=signature(groups)
 local published
 for i=#recentDraws,1,-1 do
  if recentDraws[i].key==fingerprint then published=recentDraws[i];break end
 end
 if not published then return nil,true end
 local palette={}
 for i=0x3f19,0x3f1b do palette[#palette+1]=read(i,emu.memType.nesPpuDebug) end
 assert(palette[1]==0x16 and palette[2]==0x30 and palette[3]==0x27,'Native ground palette 2')
 return {groups=groups,count=value,palette=palette,source=published,physical_chr_page=bodyPage,at=stamp()}
end
local function eachEvent(pub, remember)
 local groups,value=pub.groups,pub.count
 if pairsVisible(groups.world) and value==0 and not hit then remember('world_rings_and_count_00',groups.world) end
 if #groups.sparkle>0 and value>0 then remember('pickup_sparkle_and_count',groups.sparkle) end
 if #groups.drop>0 and hit and value==0 then remember('thrown_ring_and_count_00',groups.drop) end
end
local function hardware()
 local pub,unmatched=oamPublication()
 if unmatched then visual.unmatched=visual.unmatched+1 end
 if not pub then return end
 local groups,value=pub.groups,pub.count
 visual.oam_matches=visual.oam_matches+1;visual.hud=visual.hud+1;hardwareValues[value]=true
 local function remember(tag, parts)
  if firstVisual[tag] then return end
  firstVisual[tag]={frame=frame,source_main=pub.source.main,source_tick=pub.source.tick,count=value,
                    palette=pub.palette,sprites=parts,physical_chr_page=pub.physical_chr_page,oam_sample=pub.at}
 end
 if pairsVisible(groups.world) then visual.world=visual.world+1 end
 if #groups.sparkle>0 and value>0 then visual.sparkle=visual.sparkle+1 end
 if #groups.drop>0 and hit and value==0 then visual.drop=visual.drop+1 end
 eachEvent(pub,remember)
end

local patterns={}
local function pixels(parts, screen, visit)
 for _,s in ipairs(parts) do
  local data=patterns[s.tile]
  if not data then
   data={};patterns[s.tile]=data
   local at=224*1024+s.tile*16
   for i=0,31 do data[i]=read(at+i,emu.memType.nesChrRom) end
  end
  for y=0,15 do
   local sy=s.y+1+y
   if sy<240 then
    local offset=(y//8)*16+y%8
    for x=0,7 do
     if s.x+x<256 then
      local bit=7-x
      local index=(data[offset]>>bit&1)|((data[offset+8]>>bit&1)<<1)
      visit(index,screen[sy*256+s.x+x+1]&0xffffff)
     end
    end
   end
  end
 end
end
local function visiblePattern(pub, parts, screen)
 local bins,totals={},{[0]=0,0,0,0}
 for i=0,3 do bins[i]={} end
 pixels(pub.groups.hud,screen,function(i,rgb)
  totals[i]=totals[i]+1;bins[i][rgb]=(bins[i][rgb] or 0)+1
 end)
 local function mode(bin)
  local color,count=nil,0
  for c,n in pairs(bin) do if n>count then color,count=c,n end end
  return color,count
 end
 local backdrop=mode(bins[0])
 local colors,distinct,unique={},0,{}
 for i=1,3 do
  local c,n=mode(bins[i])
  if n>=6 and n*3>=totals[i]*2 and c~=backdrop then
   colors[i]=c
   if not unique[c] then distinct=distinct+1;unique[c]=true end
  end
 end
 local eligible,matched,transparent,tinted=0,0,0,0
 pixels(parts,screen,function(i,rgb)
  if colors[i] then
   eligible=eligible+1;if colors[i]==rgb then matched=matched+1 end
  elseif i==0 then
   transparent=transparent+1;if unique[rgb] then tinted=tinted+1 end
  end
 end)
 local observed={hud_color_count=distinct,effect_matched_pixels=matched,
  effect_eligible_pixels=eligible,transparent_pixels=transparent,transparent_pixels_with_hud_color=tinted}
 return distinct>=2 and matched>=8 and matched*4>=eligible and (transparent==0 or tinted*3<transparent),observed
end
local function sampleRaster(phase)
 if not gameplay or #raster>=4 then return end
 local pub=oamPublication()
 if not pub or not pub.at.scanline or pub.at.scanline>=35 then return end
 pub.phase=phase;pub.wall_frame=frame+1;raster[#raster+1]=pub
end
local function completedRaster()
 local screen,ending
 for i=#raster,1,-1 do
  local pub=raster[i]
  if pub.wall_frame==frame then
   visual.raster_matches=visual.raster_matches+1
   eachEvent(pub,function(tag,parts)
    if firstRendered[tag] then return end
    if not screen then
     screen=emu.getScreenBuffer();ending=stamp()
     assert(#screen==256*240,'Rendered NES pixel buffer')
    end
    local ok,pixel=visiblePattern(pub,parts,screen)
    visual.pixel_checks=visual.pixel_checks+1
    local witness={frame=frame,sample_phase=pub.phase,raster=pub.at,completed_ppu=ending,
      source_main=pub.source.main,source_tick=pub.source.tick,count=pub.count,palette=pub.palette,
      sprites=parts,physical_chr_page=pub.physical_chr_page,pixel_check=pixel}
    if ok then firstRendered[tag]=witness;png(tag)
    else
     visual.pixel_rejections=visual.pixel_rejections+1
     if #rejected<12 then rejected[#rejected+1]={tag=tag,observation=witness} end
    end
   end)
  end
 end
 raster={}
end

local function drive()
 if not gameplay then return end
 local s=state()
 assert(active(s) and s.owner==43 and s.world==0 and s.level==0 and s.area==5,'Ordinary Sonic 1-1')
 assert(s.lives==2 and s.tier==0 and s.injury_timer==0 and s.timer==0,'Lives, tier and native timers')
 assert(native('startCheat')==0 and native('invincible')==0,'No cheats')
 activeMains=activeMains+1
 assert(activeMains<=700,'Ordinary Main bound')
 if not firstActive then
  assert(s.x==40 and s.bcd==0,'Initial X40 and count zero')
  firstActive=s
 end
 if s.ready~=1 then assert(s.x==40,'Source initializes before movement');pad=0;return end
 assert(header(2)==cookie and header(3)==cookie,'Both authenticated Sonic headers')
 if previous and s.bcd>previous.bcd then
  local count=#picks+1
  local ringX=192+16*count
  assert(s.bcd==count and count<=5 and s.source_x+12>=ringX and s.source_x+12<ringX+16
      and s.source_y==176 and s.spark==6,'Sequential authored ring acquisition')
  picks[#picks+1]=s
 end
 if force and not hit then
  assert(#picks==5 and s.bcd==0 and s.stun&0x40~=0 and s.drop==0x55 and s.drop_flags&1==0,
         'Goomba spends five rings and spawns one type55')
  assert(s.vx==-512 and s.vy==-1024 and s.drop_vy==-1024,'Original 24-bit impact velocities')
  assert(s.cells[1]==0x78 and s.cells[2]==0x78 and s.cells[3]==0x78,'All original fixture bits depleted')
  assert(calls.RingHurt==1 and (calls.DamageContact or 0)>0,'One authenticated damage transaction')
  hit=s
 elseif hit then
  assert(s.bcd==0 and calls.RingHurt==1,'Count stays zero after the contact')
  if s.drop_flags&1~=0 and not activation then
   assert(s.drop==0x55 and s.tick%8==0,'Original object activation phase')
   activation=s
  end
  if previous and previous.stun&0x40~=0 then
   assert(s.source_input==0 and s.flags&5==0,'Stun clears accepted source input and roll/spin')
   if s.saved_input&0x81==0x81 and not suppression then suppression=s end
   if s.stun&0x40==0 then
    assert(not landed and s.flags&0x80~=0 and s.vy>=0 and s.vx==0
       and s.pose==16 and s.width==28,'Original grounded release and hurt pose')
    landed=s
   end
  end
  if landed and s.x>=landed.x+16 and not resumed then resumed=s end
  if s.drop==255 and not expired then
   assert(activation and s.drop_flags&1==0 and calls.DropStep==81,'Original 81-step type55 expiry')
   expired=s
  end
 end
 previous=s
 if resumed and expired then routeEnd=routeEnd or frame;pad=0;return end
 if activeMains<=3 then pad=0
 elseif hit and s.stun&0x40~=0 and ((s.tick-hit.tick)&255)<=12 then pad=0x81
 else pad=1 end
end

local function install()
 assert(variant==0 and #rom==64 and not rom:find('[^0-9a-f]'),'Runner ROM pin and variant 0')
 assert(#cookie==32 and cookie:sub(1,6)=='a72b01' and not cookie:find('[^0-9a-f]'),'Sonic owner cookie')
 local prg,ram='nesPrgRom','nesWorkRam'
 hook(0x82d9,126,prg,'GameLoop',function(cpu)
  assert(read(0x82d9)==0xa9 and read(0x82da)==0xff and read(0x82db)==0x8d,'Actual Main opcode')
  assert(not main,'Synchronous Main')
  mains=mains+1;assert(mains<=2000,'Main limit')
  local ret,sp=stackReturn(cpu)
  assert(ret==0x82be or ret==0x82d0,'Native IdleLoop/catchup caller')
  if ret==0x82d0 then cadence.catchup=cadence.catchup+1 end
  main={ret=ret,sp=sp}
 end)
 for _,pc in ipairs({0x82be,0x82d0}) do
  hook(pc,126,prg,'GameLoopReturn',function(cpu)
   if not main or main.ret~=cpu['cpu.pc'] or main.sp~=cpu['cpu.sp'] then return end
   main=nil;completed=completed+1;drive()
  end)
 end
 for _,item in ipairs({{0xbebb,3,'SonicHostConstruct'},{0xbbb0,3,'OriginalSonicFrame'},
  {0xd400,2,'AcquireRingTile'},{0xd498,2,'RingHurt'},{0xd64d,2,'DamageStatus'},
  {0xd689,2,'DamageContact'},{0xd75d,2,'DropStep'}}) do
  hook(item[1],item[2],ram,item[3],function() end)
 end
 hook(0x9771,126,prg,'ForceInjury',function(cpu)
  if not gameplay then return end
  local i=cpu['cpu.x']
  assert(i<6,'Native enemy slot')
  local a=enemy(i)
  if not force then
   assert(a.flag==1 and a.id==6 and a.state<2,'Natural live Goomba contact')
   local s=state()
   assert(s.bcd==5 and s.y==176 and math.abs(a.x-s.x)<=24,'Five-ring ground contact')
   force={actor=a,player=s}
  end
 end)
 hook(0x97d6,126,prg,'KillPlayer',function() if gameplay then error('Native death on ring route') end end)
 hook(0x97a4,126,prg,'NativeStatusStore',function()
  if gameplay then error('Native injury tier store on ring route') end
 end)
 -- The expanded bank-4 loop calls the private renderer before the native
 -- reservation. Watch both sides of the same pass through the final RTS.
 hook(0xa000,4,prg,'DrawAllMetasprites',function()
  if not gameplay then return end
  reservationCheck(not oamPass,'Unclosed native OAM reservation')
  lastReservation={frame=frame,main=mains,entry=oamState()}
  oamPass={phase='clear_or_private',private={},world={},body={},record=lastReservation}
  reservations.passes=reservations.passes+1
 end)
 local function beginReservation(pc)
  if not oamPass then return end
  local r=oamPass.record
  r.reserve=oamState()
  r.reserve.pc=pc
  r.pose_ptr=native('posePointer')+256*native('posePointer',1)
  r.pose_size=read(r.pose_ptr)
  oamPass.phase='reservation'
 end
 hook(0xa12b,4,prg,'RosterProjectileOamReadyFixed',function() beginReservation(0xa12b) end)
 hook(0xa12d,4,prg,'RosterProjectileOamReadyPrior',function() beginReservation(0xa12d) end)
 hook(0xa155,4,prg,'InitObjectLoop',function()
  if not oamPass then return end
  local r=oamPass.record
  r.world_begin=oamState()
  oamPass.phase='world'
  if r.private_stop then
   reservationCheck(r.reserve and r.reserve.player_start>=r.private_stop,
                    'Native player start precedes private OAM end')
   reservationCheck(r.world_begin.cursor%4==0 and r.world_begin.cursor>=r.reserve.player_start,
                    'Native world cursor leaves the player reservation')
   reservationCheck(r.world_begin.active==0 or r.world_begin.rotation%4==0,
                    'Native world rotation splits a four-byte OAM slot')
  end
 end)
 hook(0xa200,4,prg,'NativePlayerOamRewind',function()
  if not oamPass then return end
  oamPass.record.world_end=oamState()
  oamPass.phase='native_body'
 end)
 hook(0xa24a,4,prg,'RosterOamReady',function()
  if not oamPass then return end
  local r=oamPass.record
  r.leave=oamState()
  r.private_slots=slotCount(oamPass.private)
  r.world_slots=slotCount(oamPass.world)
  r.native_body_slots=slotCount(oamPass.body)
  reservations.closed=reservations.closed+1
  reservations.private_slots=reservations.private_slots+r.private_slots
  reservations.world_slots=reservations.world_slots+r.world_slots
  reservations.native_body_slots=reservations.native_body_slots+r.native_body_slots
  reservations.max_world_slots=math.max(reservations.max_world_slots,r.world_slots)
  if r.private_slots>0 and r.world_slots>0 then
   reservations.passes_with_private_and_world=reservations.passes_with_private_and_world+1
  end
  if #reservationExamples<12 and (r.private_slots>0 and r.world_slots>0 or #reservationExamples==0) then
   reservationExamples[#reservationExamples+1]=r
  end
  oamPass=nil
 end)
 hook(0xd80f,2,ram,'DrawFeedback',function()
  if gameplay then
   assert(not draw,'Synchronous Sonic OAM producer')
   local rotating=native('rotating')
   draw={cursor=native('oamCursor'),rotation=rotating~=0 and native('rotation') or 0,
         rotate_active=rotating,writes={}}
  end
 end)
 emu.addMemoryCallback(guarded('CPU OAM write',function(at,value)
  if draw then
   assert(#draw.writes<72,'Bounded Sonic OAM write count')
   draw.writes[#draw.writes+1]={address=at,value=value,pc=emu.getState()['cpu.pc']}
  elseif oamPass and (oamPass.phase=='world' or oamPass.phase=='native_body') then
   local slot=(at-0x200)//4
   local pc=emu.getState()['cpu.pc']
   reservationCheck(at<=0x2ff,'Native OAM write exceeds page $02',at,pc)
   reservationCheck(not oamPass.private[slot],'Native OAM write overlaps a private Sonic slot',at,pc)
   local slots=oamPass.phase=='world' and oamPass.world or oamPass.body
   slots[slot]=true
  end
 end),emu.callbackType.write,0x200,0x303)
 hook(0xd84a,2,ram,'DrawDone',function()
  if not gameplay then return end
  assert(draw,'Actual draw entry')
  local stop=native('oamCursor')
  local change=stop-draw.cursor
  lastCursor={frame=frame,main=mains,start=draw.cursor,stop=stop,rotation=draw.rotation,
              rotate_active=draw.rotate_active,cpu_writes=#draw.writes,
              first_write=draw.writes[1],last_write=draw.writes[#draw.writes]}
  local function check(ok) if not ok then error('OAM allocation '..json(lastCursor)) end end
  check(change>=0 and change%4==0 and #draw.writes==change)
  if change==0 then
   visual.empty_draws=visual.empty_draws+1
   if #cursorExamples<12 then cursorExamples[#cursorExamples+1]=lastCursor end
   draw=nil;return
  end
  local sprites={}
  local first
  reservationCheck(oamPass and oamPass.phase=='clear_or_private',
                   'Private Sonic slots emitted outside the native pre-reservation pass')
  oamPass.record.private_start=draw.cursor
  oamPass.record.private_stop=stop
  for i=1,#draw.writes,4 do
   local seen,min,max={},0x304,0
   for j=i,i+3 do
    local at=draw.writes[j].address
    seen[at]=true;min=math.min(min,at);max=math.max(max,at)
   end
   first=first or min
   lastCursor.physical_start=first-0x200
   lastCursor.applied_rotation=(first-0x200-draw.cursor)&255
   lastCursor.checked_group={first=min,last=max}
   check(min>=0x200 and max<=0x2ff and min%4==0 and max-min==3
     and seen[min+1] and seen[min+2] and min==0x200+((first-0x200+i-1)&255))
   local slot=(min-0x200)//4
   reservationCheck(not oamPass.private[slot],'Private Sonic slot emitted twice',min)
   oamPass.private[slot]=true
   sprites[#sprites+1]=sprite(min,emu.memType.nesDebug,slot)
  end
  if (draw.cursor%4~=0 or draw.rotation~=lastCursor.applied_rotation or stop>252) and #cursorExamples<12 then
   cursorExamples[#cursorExamples+1]=lastCursor
  end
  local groups=classify(sprites)
  local value=displayedCount(groups.hud)
  if value then
   assert(value==source(0x340),'CPU OAM count matches source BCD')
   recentDraws[#recentDraws+1]={key=signature(groups),tick=source(0x92),main=mains}
   if #recentDraws>16 then table.remove(recentDraws,1) end
  end
  draw=nil
 end)
 watchWrite(0x5130,function(v) chrUpper=v&3 end)
 watchWrite(0x5120,function(v) bodyPage=v+256*chrUpper end)
 watchWrite(0x2000,function(v) ppuCtrl=v end)
 watchWrite(0x2001,function(v) ppuMask=v end)
 hook(0x8000,126,prg,'IrqScrollSplit',function() sampleRaster('scroll_irq') end)
 emu.addEventCallback(guarded('startFrame',function() sampleRaster('start_frame') end),emu.eventType.startFrame)
 emu.addEventCallback(guarded('inputPolled',function()
  polls=polls+1;emu.setInput(buttons(pad),0)
 end),emu.eventType.inputPolled)
end

local function frames(n) for _=1,n do coroutine.yield() end end
local function press(bits) pad=bits;frames(4);pad=0;frames(8) end
local function ready(predicate)
 for _=1,900 do if predicate() then return end;coroutine.yield() end
 error('Natural title/menu readiness timeout')
end
local route=coroutine.create(function()
 ready(function()return frame>=70 and native('title')==1 and native('blank')==0 end)
 press(16);ready(function()return native('menu')==2 and native('blank')==0 end)
 assert(native('slot')==0,'Natural initial slot0')
 for _,bits in ipairs({1,4,4,4}) do press(bits) end
 assert(native('slot')==25 and native('alternate')==0,'Mr. Gimmick slot25')
 for _=1,3 do press(32) end
 assert(native('owner')==43 and native('alternate')==3,'Mr. Gimmick Select3 Sonic')
 press(16);ready(function()return active(state()) end)
 gameplay=true;drive()
 while not stopped do coroutine.yield() end
end)

guarded('setup',function()
 install()
 emu.addEventCallback(guarded('endFrame',function()
  frame=frame+1;assert(frame<=3000,'Physical frame bound')
  local updates=completed-previousCompleted
  previousCompleted=completed
  cadence.max_updates_per_frame=math.max(cadence.max_updates_per_frame,updates)
  if gameplay then
   cadence.physical_gameplay=cadence.physical_gameplay+1
   if updates==0 then cadence.zero_updates=cadence.zero_updates+1 end
   hardware()
   completedRaster()
  end
  if routeEnd then
   local ready=true
   for n=0,5 do ready=ready and hardwareValues[n] end
   if ready and firstRendered.world_rings_and_count_00 and firstRendered.pickup_sparkle_and_count
      and firstRendered.thrown_ring_and_count_00 then
    assert(suppression and calls.SonicHostConstruct==1 and (calls.OriginalSonicFrame or 0)>=100,
           'Observed suppressed A+Right and one original constructor')
    assert(reservations.passes_with_private_and_world>0 and reservations.closed==reservations.passes,
           'Native passes closed with separately owned Sonic and world slots')
    assert(not wantImages or #images==3,'Three distinct stdout PNG events')
    finish(true,'Five pickups, real Goomba loss, recovery, hardware OAM and displayed pixels');return
   end
   assert(frame-routeEnd<=30,'Completed route without all three rendered sprite events')
  end
  local ok,why=coroutine.resume(route);assert(ok,why)
 end),emu.eventType.endFrame)
end)()
