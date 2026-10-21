-- Explicit native-boundary fixtures, not a level clear. Expected edges come
-- from pinned DuckTales D291: |dx|<18, |dy|<=20 for a16px target.
local frame,index=0,0
local current,entrySp,returnPc
local cases={}
for _,x in ipairs({96,255,256,511})do for _,dir in ipairs({1,2})do
 for _,q in ipairs({{0,20,true},{0,21,false},{17,16,true},{18,16,false},{-17,16,true},{-18,16,false},{0,-20,true},{0,-21,false}})do
  cases[#cases+1]={x=x,dir=dir,dx=q[1],dy=q[2],hit=q[3],vy=1,y=120,yHigh=1}
 end
end end
for _,q in ipairs({{vy=255,mid=0,hit=false},{vy=0,mid=0,hit=false},{vy=0,mid=1,hit=true}})do
 cases[#cases+1]={x=128,dir=1,dx=0,dy=20,hit=q.hit,vy=q.vy,mid=q.mid,y=120,yHigh=1}
end
cases[#cases+1]={x=128,dir=1,dx=0,dy=20,hit=false,vy=1,y=220,yHigh=0}
cases[#cases+1]={x=128,dir=1,dx=0,dy=20,hit=false,vy=1,y=224,yHigh=1}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local out=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-pogo-hitbox.csv','w'))
out:write('case,x,dir,dx,dy,vy,mid,yHigh,expectedHit,health,bounced\n')
emu.addMemoryCallback(function()
 if frame<640 or r('SelectedCharacter')~=12 or r('CurrentBank')%128~=61 then return end
 index=index+1;current=cases[index]
 if not current then out:close();print('PASS Scrooge native pogo rectangle: '..#cases..' strict/inclusive, facing, page-seam, descent and viewport boundary cases');emu.stop(0);return end
 local q=current
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyFlash',0,i);w('Enemy_State',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 w('Player_X_Position',q.x%256);w('Player_PageLoc',q.x//256);w('Player_Y_Position',q.y);w('Player_Y_HighPos',q.yHigh)
 w('ScreenLeft_X_Pos',(q.x-80)%256);w('ScreenLeft_PageLoc',(q.x-80)//256)
 w('ScreenRight_X_Pos',(q.x+175)%256);w('ScreenRight_PageLoc',(q.x+175)//256)
 w('Player_State',1);w('PlayerFacingDir',q.dir);w('Player_Y_Speed',q.vy);w('Player_X_Speed',0)
 w('PlayerStatus',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('TimerControl',0);w('GameEngineSubroutine',8)
 w('ScPogo',1);w('ScAttack',0);w('ScPrevious',0x44);w('RgPreviousButtons',0x44);w('SavedJoypadBits',0x44)
 w('SmBombHits',0);w('SmSlot',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('MmVY',q.vy,2);w('MmVY',q.mid or 0,1)
 local ex=q.x+q.dx
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('EnemyOffscrBitsMasked',0)
 w('Enemy_X_Position',ex%256);w('Enemy_PageLoc',ex//256);w('Enemy_Y_Position',q.y+4+q.dy);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('MmEnemyHealthLo',44);w('MmEnemyHealthHi',1)
 entrySp=emu.getState()['cpu.sp']
 local pc=(emu.read(0x100+(entrySp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(entrySp+2)%256,emu.memType.nesDebug)+1)%65536
 if not returnPc then
  returnPc=pc
  emu.addMemoryCallback(function()
   if not current or emu.getState()['cpu.sp']~=entrySp+2 then return end
   local health=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
   local bounced=r('MmVY',2)>=128 and r('Player_State')==1
   out:write(table.concat({index,current.x,current.dir,current.dx,current.dy,current.vy,current.mid or 0,current.yHigh,current.hit and 1 or 0,health,bounced and 1 or 0},',')..'\n');out:flush()
   assert(health==(current.hit and 200 or 300),'Native pogo edge case '..index..' damage; expectedHit='..tostring(current.hit)..' health='..health)
   assert(not current.hit or bounced,'A successful native body-sized pogo immediately rebounds')
   current=nil
  end,emu.callbackType.exec,pc)
 end
 assert(pc==returnPc,'Stable native pogo test caller')
end,emu.callbackType.exec,L.ScroogeWeapons)
emu.addEventCallback(function()emu.setInput({down=frame==80 or frame>=640,right=frame==100 or frame==120,start=frame==200,b=frame>=640},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
