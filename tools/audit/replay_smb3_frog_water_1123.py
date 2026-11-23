"""Exact2ac ordinary menu-selected2-1 Frog pickup, clear and2-2 swimming.

Default is bounded source-only checking, with no artifacts or emulator launch.
Only root may request --run against the existing shared native slot.
"""
import argparse
import json
import re

import compose_sonic_current_auth_epoch_1122 as Epoch
import replay_smb3_actions_1122 as Base
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value

R,ROM,H,N,W=Base.R,Base.ROM,Base.H,Base.N,Base.W
PIN=Epoch.CANDIDATE
PIPE_NIGHTLY='28708fa9a4e7dd88f1aaa72653b7d5a6ba0fb3c6d5abf544a526b09d333a884c'
COMBINED_NIGHTLY='14b0b4c23baa1ff454d25720b0585dd45f7fa4179bbba6b7f38d68b6e0c141b5'
POLICY=R/'tools/playthroughs/smb3_frog_water_1123.lua'
once=Base.Acquire.once
FROZEN_POLICY_SHA='9ca03d77e93f7d3babb5897952e4ef177b5dc21af3e4a4268cbaffeb7f3d7898'
FROZEN_PIPE_SCRIPTS={
    'toad3':'7dade7aa336dd716e38bbf9b59512c4d665cf5ed5f9004612cf1111b011be71a',
    'peach3':'e462ba074f0e85fefe950ec91dbca22dbf3ef15550a7a2c69d7463b644761004'}
FROZEN_BRIDGE_POLICY_SHA='d6a0f4f28d59fb8eba1590b8587b5de33717e076970a7b82d94e9f3c14f376fd'
FROZEN_BRIDGE_SCRIPTS={
    'toad3':'d83e3b288d7f82be3644c8cb77cd3141231681a756f5f46069ea2e985a481b30',
    'peach3':'89a9b271cd0a5c1ba72a110bdf1adcb849a1259f99e011367dd910dcaec642e2'}
FROZEN_ADAPTIVE_POLICY_SHA='6d325a4dc90e7bfb2ccf2de411bd46c667b4d572fff8b098a59e4ae05d7a3291'
FROZEN_ADAPTIVE_SCRIPTS={
    'toad3':'b99fdf1794428ade2b75e9674d135f006041d4836c12905201a06041af0edeef',
    'peach3':'09634f64a13bdc894c5f0c870612290319338ca8859c79b51522d79a3abb60fe'}
FROZEN_RETRACTION_POLICY_SHA='79e70638ebac7e969476cfa9608e1480a46819fe89b017f9f5c1eea4a1a703a2'
FROZEN_RETRACTION_SCRIPTS={
    'toad3':'c7390a3ff6e766ad51d3986e77c7158ecd1f865e3d0e83b67122d7736190a088',
    'peach3':'29c7f539fc0d1ab47f87385e5b2741192f412970df76e169ba4bf181ba920cdb'}
FROZEN_BRIDGE_STAGE=''' if g.phase=='stage'then
  if c.grounded and c.y<=112 and c.x>=1640 and c.x<=1672 then
   g.pipe_landing={motor=c.motor,x=c.x,y=c.y};gapPhase(c,g,'pipe-release')
  elseif c.grounded and c.y==48 and math.abs(c.x-1512)<=3 and vx==0
      and c.r('M3Previous')&128==0 then
   assert(solid(c,1520,80),'Stand on the actual1472-to1535 authored brick ledge')
   local actors={}
   for i=0,5 do
    if c.r('Enemy_Flag',i)>0 then
     actors[#actors+1]={slot=i,id=c.r('Enemy_ID',i),state=c.r('Enemy_State',i),
      x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
    end
   end
   g.bridge_transfer=true;g.bridge_staging={motor=c.motor,x=c.x,y=c.y,vx=c.vx,actors=actors}
   g.climb_input={motor=c.motor,x=c.x,y=c.y};gapPhase(c,g,'climb-pipe')
   return{right=true,b=true,a=true}
  else local b=steer(c,1512);b.a=not c.grounded and c.motor-jumpAt<32;return b end
 end'''


def policy_text(frozen=False):
    """Reconstruct the earlier approach from its small source delta, in memory."""
    text=POLICY.read_text(encoding='utf-8');assert POLICY.read_bytes()==text.encode()
    if not frozen:return text
    lo=text.index('-- high-pipe-retry-1123 begin\n')
    hi=text.index('-- high-pipe-retry-1123 end\n',lo)+len('-- high-pipe-retry-1123 end\n')
    text=text[:lo]+text[hi:]
    text=once(text," assert(c.motor-g.at<(g.x==2088 and 960 or 480)and c.r('Enemy_ID',g.slot)==13,'Finite live authored plant crossing')",
        " assert(c.motor-g.at<480 and c.r('Enemy_ID',g.slot)==13,'Finite live authored plant crossing')")
    text=once(text,' local staged,pad=highPipeStage(c,g);if staged then return pad end\n','')
    text=once(text,'''  else
   assert(not(g.step_from_right and c.grounded and c.y==176 and c.motor-g.step_at>16),
    'The single ordinary retry must reach the lower pipe')
   if g.step_from_right and c.x>2034 then return{left=true,a=c.motor-g.step_at<32}end
   local b=steer(c,2032);b.a=c.motor-g.step_at<32;return b
  end''',"  else local b=steer(c,2032);b.a=c.motor-g.step_at<32;return b end")
    text=once(text,'''  if g.x==2088 and not g.top_ready and c.grounded and c.y<=128 and c.x>=1968 and c.x<2048 then
   g.phase='stage-elevated';g.stage_at=c.motor;g.top_samples=0
   local handled,b=highPipeStage(c,g);if handled then return b end
  end
''','')
    text=once(text,'''  if g.x==2088 then
   if c.x>=2072 and c.x<=2112 and c.yHigh==1 and c.y<=96 then
    g.cap_cross=g.cap_cross or{motor=c.motor,x=c.x,y=c.y,native_air=c.r('M3Native::Player_InAir')}
   end
   if c.grounded and c.y==176 and c.x>=2048 and c.x<2080 and c.motor-g.jump_at>12 then
    return retryHighPipe(c,g,'short-high-cap')
   end
  end
''','')
    text=once(text,'''  if c.x>=g.x+24 then
   assert(g.x~=2088 or g.cap_cross,'Observe actual high-cap clearance before completing the crossing')
   g.clear={motor=c.motor,x=c.x,y=c.y};g.phase='brake'
''',"  if c.x>=g.x+24 then g.clear={motor=c.motor,x=c.x,y=c.y};g.phase='brake'\n")
    assert H(text.encode())==FROZEN_RETRACTION_POLICY_SHA,'Exact previous retraction policy reconstruction'
    if frozen=='retraction':return text
    lo=text.index('-- first-pipe-retraction-1123 begin\n')
    hi=text.index('-- first-pipe-retraction-1123 end\n',lo)+len('-- first-pipe-retraction-1123 end\n')
    text=text[:lo]+text[hi:]
    text=once(text,"     if not firstPipeReady(c,g,true)then return gapRecord(c,g,'first-plant-retraction',{})end\n",'')
    text=once(text,"    if not firstPipeReady(c,g,false)then return gapRecord(c,g,'first-plant-retraction',{})end\n",'')
    assert H(text.encode())==FROZEN_ADAPTIVE_POLICY_SHA,'Exact previous adaptive policy reconstruction'
    if frozen=='adaptive':return text
    lo=text.index('-- adaptive-approach-1123 begin\n')
    hi=text.index('-- adaptive-approach-1123 end\n',lo)+len('-- adaptive-approach-1123 end\n')
    text=text[:lo]+text[hi:]
    text=once(text," if not g then g={phase='stage',at=c.motor,start=c.motor,changes={}};F.gap=g;gapRecord(c,g,'entry')end",
        " if not g then g={phase='stage',at=c.motor,start=c.motor,changes={}};F.gap=g end")
    text=once(text," assert(c.motor-g.start<(g.low_arc and 600 or 480),'Finite ordinary pipe/pit crossing')",
        " assert(c.motor-g.start<480,'Finite ordinary pipe/pit crossing')")
    lo=text.index(' -- adaptive-stage-1123 begin\n')
    hi=text.index(' -- adaptive-stage-1123 end\n',lo)+len(' -- adaptive-stage-1123 end\n')
    text=text[:lo]+FROZEN_BRIDGE_STAGE+'\n'+text[hi:]
    assert H(text.encode())==FROZEN_BRIDGE_POLICY_SHA,'Exact previous bridge policy reconstruction'
    if frozen=='bridge':return text
    lo=text.index('  elseif c.grounded and c.y==48 and math.abs(c.x-1512)<=3 and vx==0')
    hi=text.index("\n end\n if g.phase=='climb-pipe'then",lo)
    text=text[:lo]+'''  elseif c.grounded and c.y==176 and math.abs(c.x-1608)<=3 and math.abs(vx)<=3
      and c.r('M3Previous')&128==0 then
   g.climb_input={motor=c.motor,x=c.x,y=c.y};gapPhase(c,g,'climb-pipe')
   return{right=true,a=true}
  else return steer(c,1608)end'''+text[hi:]
    lo=text.index('  if g.bridge_transfer and not g.bridge_jump')
    hi=text.index('  if c.grounded and c.y<=112',lo)
    text=text[:lo]+text[hi:]
    text=once(text,'''  else
   if g.bridge_transfer and c.x<1640 then return{right=true,b=true,a=c.motor-g.at<32}end
   local b=steer(c,1656);b.a=c.motor-g.at<32;return b
  end''',"  else local b=steer(c,1656);b.a=c.motor-g.at<32;return b end")
    text=once(text,'  if c.x>=1472 and c.x<1808','  if c.x>=1584 and c.x<1808')
    lo=text.index(" if g.phase=='step-up'then")
    hi=text.index(" if g.phase=='enemy-jump'then",lo)
    text=text[:lo]+text[hi:]
    lo=text.index('  if g.x==2088 and c.x>=1984 and c.x<=2008')
    hi=text.index('  local nearest',lo)
    text=text[:lo]+text[hi:]
    assert H(text.encode())==FROZEN_POLICY_SHA,'Exact previous policy reconstruction'
    return text


def bindings(raw,form,*,frozen=False):
    assert H(raw)==PIN and form in ('toad3','peach3')
    reference=Epoch.inverse(raw);assert H(reference)==Base.PIN
    q=Base.bindings(reference,form,'Frog');b=Base.authority()
    for name in ('M3Native::Player_InWater','M3Native::Player_InAir','M3Native::Player_XVel',
                 'M3Native::Player_YVel','M3Native::Pad_Holding','JumpspringAnimCtrl',
                 'JumpspringTimer','JumpspringForce','AreaAddrsLOffset',
                 'PiranhaPlantDownYPos','PiranhaPlantUpYPos','PiranhaPlant_MoveFlag','PiranhaPlant_Y_Speed',
                 'Enemy_X_Speed','EnemyFrameTimer'):
        q['ram'][name]=W.address(b,name)
    for key,symbol in (('FrogSwim','M3Native::Swim_Frog'),('FrogFlag','FlagpoleRoutine'),
                       ('FrogJump','M3Native::Player_JumpFlyFlutter')):
        at,pc=W.location(b,symbol),W.address(b,symbol);bank=(at-16)//8192
        code=raw[at:at+16]
        assert code==reference[at:at+16] and at-16==bank*8192+(pc&8191)
        q['hooks'][key]=dict(pc=pc,tag=bank|128,offset=at-16,hex=code.hex(),bytes=list(code))
    for name,hook in q['hooks'].items():
        at=hook['offset']+16
        assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes']),name
    areas={}
    for symbol in ('L_GroundArea9','E_GroundArea9','L_WaterArea2','E_WaterArea2'):
        at=W.location(b,symbol);stop=raw.index(0xfd if symbol.startswith('L_')else 0xff,at)
        assert raw[at:stop+1]==reference[at:stop+1]
        areas[symbol]=dict(file=at,bytes=stop-at+1,SHA256=H(raw[at:stop+1]))
    assert raw[W.location(b,'L_GroundArea9')+8:W.location(b,'L_GroundArea9')+10]==bytes.fromhex('0784')
    assert raw[W.location(b,'L_GroundArea9')+28:W.location(b,'L_GroundArea9')+30]==bytes.fromhex('5700')
    assert raw[W.location(b,'L_GroundArea9')+54:W.location(b,'L_GroundArea9')+58]==bytes.fromhex('77fbac02')
    q.update(sha=PIN,actual_input_CPU_SHA256=PIN,reference59=Base.PIN,
             frog_policy_SHA256=H(policy_text(frozen).encode()),authored_areas=areas,
             start_level=36,route='mushroom-suit',frog_route='menu-2-1-earned-Frog-to-2-2-swim',blockX=848,
             gap_geometry=dict(pipe_left=1648,pipe_top=144,pipe_width=32,pit_left=1696,pit_width=48,far_bank=1744),
             scope='Ordinary menu-selected2-1, real256/848 rewards, full clear and retained Frog2-2 controls; not an uninterrupted1-1 campaign')
    return q


NAVIGATION=r'''
local phase='position';local at,jumpAt,attempts=0,-100,0
local T={phase=phase,changes={}};SMB3_FROG_OPENING=T
local function change(c,p)
 phase=p;at=c.motor;T.phase=p
 T.changes[#T.changes+1]={phase=p,motor=c.motor,x=c.x,y=c.y}
 assert(#T.changes<=16,'Finite stopped first-Mushroom route')
end
local function steer(c,goal)
 local vx=c.vx>=128 and c.vx-256 or c.vx;local dx=goal-c.x
 local stop=vx*vx/24+6
 if vx>2 and dx<=stop then return{left=true}end
 if vx< -2 and -dx<=stop then return{right=true}end
 return{right=dx>2,left=dx< -2}
end
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
return function(c)
 if c.r('M3Form')~=0 then
  local obstacle=solid(c,c.x+38,c.y+8)or solid(c,c.x+38,c.y+24)
  local support=false
  for y=math.min(c.y+40,232),232,16 do if solid(c,c.x+34,y)then support=true;break end end
  local e=c.enemy();local danger=e and e.dx>8 and e.dx<64 and e.y>=c.y-24 and e.y<=c.y+72
  if c.grounded and c.r('M3Previous')&128==0 and c.motor-jumpAt>24 and(obstacle or not support or danger)then jumpAt=c.motor end
  return{right=true,b=true,a=c.motor-jumpAt<32}
 end
 if not T.stomp then
  if not T.stomp_target then
   local vx=c.vx>=128 and c.vx-256 or c.vx
   if c.grounded and c.y==176 and math.abs(c.x-208)<=3 and math.abs(vx)<=3 and c.r('M3Previous')&128==0 then
    local e=c.enemy()
    if e and e.id==6 and e.dx>=24 and e.dx<=32 and e.y>=160 then
     T.stomp_target=e;jumpAt=c.motor;change(c,'clear-first-Goomba');return{right=true,a=true}
    end
    return{}
   end
   return steer(c,208)
  end
  local e=T.stomp_target;local state=c.r('Enemy_State',e.slot)
  if c.r('Enemy_ID',e.slot)==6 and state>=2 then
   T.stomp={motor=c.motor,x=c.x,y=c.y,enemy_state=state};change(c,'position')
  else
   assert(c.motor-jumpAt<90 and c.r('Enemy_Flag',e.slot)>0,'Bounded real first-Goomba stomp before revealing Mushroom')
   local b=steer(c,228);b.a=c.motor-jumpAt<18;return b
  end
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('InvPickupOwner',i)==17 and c.r('InvPickup',i)==0xd1 then
   item={slot=i,state=c.r('Enemy_State',i),x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
  end
 end
 if item then
  if not T.birth then T.birth={motor=c.motor,x=c.x,y=c.y,actor=item};change(c,'intercept')end
  assert(c.motor-T.birth.motor<240,'Finite ordinary Mushroom interception after first-enemy clearance')
  T.last_actor=item
  if item.state<128 then return{}end
  return steer(c,item.y<152 and 304 or item.x-6)
 end
 if T.birth then error('The authored Mushroom disappeared before a real collection')end
 if phase=='position'then
  assert(c.x<304,'Brake before leaving the first authored powerup column')
  local vx=c.vx>=128 and c.vx-256 or c.vx
  if c.grounded and c.y==176 and math.abs(c.x-252)<=2 and math.abs(vx)<=2 and c.r('M3Previous')&128==0 then
   attempts=attempts+1;assert(attempts<=3,'Finite real first-brick bump attempts')
   change(c,'bump');return{a=true}
  end
  return steer(c,252)
 end
 assert(c.motor-at<75,'Actual first-brick bump must create its reward')
 return{a=c.motor-at<20}
end
'''


def navigation():
    return NAVIGATION


def acquisition():
    text=Base.Acquire.POLICY.read_text(encoding='utf-8')
    text=once(text,'c.world~=0','c.world~=1')
    offsets={1248:848,1256:856,1244:844,1242:842,1246:846,1208:808,1152:752}
    text=re.sub(r'\b('+ '|'.join(map(str,offsets))+r')\b',lambda m:str(offsets[int(m[0])]),text)
    assert not re.search(r'\b(1248|1256|1244|1242|1246|1208|1152)\b',text)
    text=once(text,'local function suitActor(c)',CORRIDOR_GUARD+'\nlocal function suitActor(c)')
    text=once(text," if phase=='mushroom'then change(c,'travel')end", """ if c.x>=772 and not T.rng and not geometry and not progress.suit_prepared and not T.corridor_done then
  return corridorGuard(c)
 end
 if phase=='mushroom'then change(c,'travel')end""")
    return text


CORRIDOR_GUARD=r'''
local function corridorGuard(c)
 local g=T.corridor
 if not g then g={phase='align',at=c.update,stomps={}};T.corridor=g end
 assert(c.update-g.at<800,'Finite source-enemy clearance before the untouched suit block')
 local vx=c.vx>=128 and c.vx-256 or c.vx
 if g.phase=='align'then
  if not(c.grounded and c.y==176 and math.abs(c.x-780)<=3 and vx==0)then return steer(c,780,2)end
  g.phase='face'
 end
 if g.phase=='face'then
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  if vx~=0 then return{}end
  g.phase='wait'
 end
 if g.phase=='jump'then
  local e=g.target;local state=c.r('Enemy_State',e.slot);local flag=c.r('Enemy_Flag',e.slot)
  if flag==0 or state>=2 then
   g.stomps[#g.stomps+1]={update=c.update,x=c.x,y=c.y,slot=e.slot,id=e.id,state=state,flag=flag}
   assert(#g.stomps<=6,'Bounded native corridor stomps');g.phase='recover'
  else
   assert(c.update-g.jump_at<90 and not(c.grounded and c.update-g.jump_at>8),
    'Stationary corridor jump must clear the actual approaching actor before landing')
   return{a=c.update-g.jump_at<18}
  end
 end
 if g.phase=='recover'then
  if not c.grounded or c.r('M3Previous')&128~=0 then return{}end
  g.phase='face';return{}
 end
 local nearest
 for i=0,5 do
  local id=c.r('Enemy_ID',i);local flag=c.r('Enemy_Flag',i);local state=c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local y=c.r('Enemy_Y_Position',i)
  local dx=x-c.x
  if flag>0 and flag<128 and(id==0 or id==6)and state<2 and dx>=0 and dx<=192
     and y>=c.y-16 and y<=c.y+40 and(not nearest or dx<nearest.dx)then
   nearest={slot=i,id=id,state=state,x=x,y=y,dx=dx}
  end
 end
 if nearest then
  g.clear_at=nil;g.last_enemy=nearest
  assert(nearest.dx>=16,'Stop at a safe ground-enemy distance before the suit block')
  if nearest.dx<=26 and c.r('M3Previous')&128==0 then
   g.target=nearest;g.jump_at=c.update;g.phase='jump';return{a=true}
  end
  return{}
 end
 assert(#g.stomps>=1,'At least one actual source corridor enemy was cleared')
 g.clear_at=g.clear_at or c.update
 if c.update-g.clear_at>=8 then
  T.corridor_done={update=c.update,x=c.x,y=c.y};return{}
 end
 return{}
end
'''


MENU=r'''
local function menu()
 if physical<45 or r('CrossoverTitleDrawn')==0 or r('DisableScreenFlag')~=0 then return{}end
 assert(r('CheatInvincible')==0 and r('CrossoverBehaviorVersion')==0,'All ability cheats remain off; Easy selection')
 local mode=r('CrossoverMenuState')
 if mode==0 then
  local focus=F.menu_configured and 0 or 1
  if r('CrossoverOptionsFocus')~=focus then return pulse('down')end
  return pulse('start')
 elseif mode==4 then
  if F.menu_configured then return pulse('b')end
  if r('CrossoverOptionsFocus')~=2 then return pulse('down')end
  return pulse('a')
 elseif mode==6 then
  if r('CrossoverOptionsFocus')~=1 then return pulse('down')end
  local level=r('CheatStartLevel')
  assert(level==0 or(level>=32 and level<=36),'Only four forward Start-Level menu choices')
  if level~=36 then return pulse('right')end
  F.menu_configured={frame=physical,start_level=level,other_cheats=r('CheatInvincible')}
  return pulse('b')
 elseif mode==2 then
  local cursor=r('CrossoverMenuIndex')
  if cursor~=C.slot then return pulse(assert(C.navigation[cursor+1]))end
  if r('M3Variant')~=C.variant then return pulse('select')end
  assert(identity(),'Actual requested SMB3 variant, Easy and only selected2-1')
  return pulse('start')
 end
 return{}
end
'''


OBSERVE=r'''
local F=assert(SMB3_FROG_WATER)
local function frogState()
 local s=actionState();s.area_type=r('AreaType');s.area_offset=r('AreaAddrsLOffset')
 s.native_water=r('M3Native::Player_InWater');s.native_air=r('M3Native::Player_InAir')
 s.native_vx=r('M3Native::Player_XVel');s.native_vy=r('M3Native::Player_YVel')
 s.native_input=r('M3Native::Pad_Holding');s.input=r('SavedJoypadBits');return s
end
local function frogEntry(name,p)
 if not A.acquired then return end
 if name=='FrogFlag'and r('WorldNumber')==1 and r('LevelNumber')==0 and r('GameEngineSubroutine')==4 then
  F.flag=F.flag or frogState()
 elseif name=='FrogJump'and F.gap and F.gap.phase=='gap-launch'and r('M3Fresh')&128~=0
     and r('M3Native::Player_InAir')==0 then
  p.frog_jump={before=frogState()}
 elseif name=='M3Step'and F.gap and F.gap.phase=='land-bank'and not F.gap.complete then
  p.frog_ground={before=frogState()}
 elseif name=='FrogSwim'then
  assert(r('WorldNumber')==1 and r('LevelNumber')==1 and r('AreaType')==0 and r('AreaAddrsLOffset')==1,
   'Actual authored2-2 native Frog water path')
  p.frog_swim={before=frogState(),segment=F.segment}
 end
end
local function frogJumpReturned(p)
 local q=p.frog_jump;local s=frogState()
 assert(F.gap.jump_input and q.before.state==0 and q.before.y==112 and q.before.x>=1652 and q.before.x<=1660
  and s.native_air~=0 and s.native_vy>=128 and s.power==4 and s.input&128~=0,
  'Actual fresh native Frog jump starts on the real authored pipe top')
 q.after=s;F.gap.jump=q
end
local function frogGroundReturned(p)
 if not p.frog_ground then return end
 local before=p.frog_ground.before;local s=frogState()
 if before.state==0 and s.state==0 and s.native_air==0 and s.native_vy==0
    and s.y==176 and before.y==176 and s.x>=1744 and before.x>=1744 and s.input&128==0 then
  F.gap.ground_return={before=before,after=s}
 else F.gap.ground_return=nil end
end
local function signed(v)return v>=128 and v-256 or v end
local function decay(v)
 v=signed(v);if v>0 then return v-1 elseif v<0 then return(v+1)&255 end;return 0
end
local function frogReturned(p)
 local before=p.frog_swim.before;local s=frogState();local q=p.frog_swim.segment
 assert(before.power==4 and s.power==4 and before.native_water==1 and s.native_water==1,
  'The naturally earned Frog executes its real native underwater controller')
 F.swim_returns=(F.swim_returns or 0)+1
 if not q then return end
 if before.native_input~=q.mask then
  q.stale=q.stale+1;assert(q.stale<=8,'Bounded cached inputs before actual next swim segment');return
 end
 local speed=q.mask&128~=0 and 32 or 16
 local vx=q.mask&1~=0 and speed or q.mask&2~=0 and(256-speed)or decay(before.native_vx)
 local vy=q.mask&4~=0 and speed or q.mask&8~=0 and(256-speed)or decay(before.native_vy)
 assert(s.native_vx==vx and s.native_vy==vy,'Actual Frog cardinal/A speeds and one-subpixel release inertia')
 q.returns=q.returns+1;assert(q.returns<=q.wanted+4,'Bounded authenticated swim segment returns')
 q.first=q.first or {before=before,after=s};q.last={before=before,after=s}
 q.frames=q.frames or {};q.frames[tostring(s.native_frame)]=true
end
local function frogTick()
 local s=frogState()
 assert(s.power==4 and s.lives==2 and not A.injury,'Retain the naturally earned Frog and two lives without injury')
 assert(s.world==1 and(s.level==0 or s.level==1),'No warp or unrelated stage')
 local gap=F.gap
 if gap and gap.jump then
  if s.native_air~=0 and s.yHigh==1 and s.y<=gap.jump.before.y-16 then gap.lift=gap.lift or s end
  local q=gap.ground_return
  if gap.phase=='land-bank'and not gap.complete then
   if q and q.after.motor==s.motor and gap.last_ground_motor~=s.motor and s.state==0
      and s.native_air==0 and s.native_vy==0 and s.y==176 and s.x>=1744 then
    if gap.last_ground_motor~=s.motor-1 then gap.ground_steps=0 end
    gap.ground_steps=(gap.ground_steps or 0)+1;gap.last_ground_motor=s.motor
    if gap.ground_steps==25 then
     assert(gap.lift and gap.bank_landing,'Real jump lift and far-bank landing precede25 full grounded returns')
     gap.complete=s
    end
   elseif gap.last_ground_motor~=s.motor then gap.ground_steps=0;gap.last_ground_motor=nil end
  end
 end
 if s.level==0 and s.engine==5 then F.castle=F.castle or s end
 if s.level==1 then
  assert(F.flag and F.castle,'Full2-1 flag and castle precede the actual2-2 entrance')
  if s.engine==8 then
   assert(s.area_type==0 and s.area_offset==1,'Actual authored2-2 room')
   F.water_entry=F.water_entry or s
  end
 end
 if #F.checkpoints<20 and s.level==0 and s.x>=256+#F.checkpoints*256 then F.checkpoints[#F.checkpoints+1]=s end
 if F.complete then
  assert(F.gap and F.gap.complete and F.pit2 and F.pit2.complete and F.pit3 and F.pit3.complete
   and F.water_entry and #F.segments==17 and F.swim_returns>=345,
   'Completed authored pit jumps, every admitted native swim exercise and final25 returns')
  local q=F.segments[#F.segments]
  assert(q.name=='retained-neutral'and q.returns>=25 and q.last.after.native_vx==0
   and q.last.after.native_vy==0 and s.growth==0 and s.poof==0,'Released controls finish with25 retained-suit native water updates')
 end
end
'''


def controller(raw,form,*,frozen=False):
    q=bindings(raw,form,frozen=frozen);reference=Epoch.inverse(raw)
    _,text=Base.controller(reference,form,'Frog').split('\n',1)
    text=once(text,Base.Acquire.Stock.Navigation.policy(),navigation())
    text=once(text,Base.Acquire.POLICY.read_text(encoding='utf-8'),acquisition())
    text=once(text,Base.POLICY.read_text(encoding='utf-8'),policy_text(frozen))
    text=once(text,"r('CheatStartLevel')==0","r('CheatStartLevel')==36")
    text=once(text,'local item_x={[0]=336,1248,1616,1024}','local item_x={[0]=256,848,1616,1024}')
    text=once(text,"s.world==0 and s.level==0 and s.engine~=11", "s.world==1 and(s.level==0 or s.level==1)and s.engine~=11")
    text=once(text,"r('WorldNumber')==0 and r('LevelNumber')==0,'Natural first gameplay'",
        "r('WorldNumber')==1 and r('LevelNumber')==0 and r('AreaType')==1 and r('AreaAddrsLOffset')==8,'Natural menu-selected2-1 first gameplay'")
    text=once(text,'local expectedX=kind==0 and 336 or 1248','local expectedX=kind==0 and 256 or 848')
    text=once(text,'local function afterMain()',OBSERVE+'\nlocal function afterMain()')
    text=once(text,'  actionTick()','  frogTick()')
    text=once(text,"  if A.complete then finish(true,'Naturally acquired suit, real native action and25 resumed source steps');return end",
        "  if F.complete then finish(true,'Menu-selected2-1 natural Mushroom/Frog, full clear and retained native2-2 swimming');return end")
    text=once(text,'\n actionEntry(name,p,cpu)\n','\n actionEntry(name,p,cpu);frogEntry(name,p)\n')
    text=once(text,'elseif p.action_poof then','elseif p.frog_swim then frogReturned(p)\n  elseif p.action_poof then')
    text=once(text,'elseif p.frog_swim then frogReturned(p)',
        'elseif p.frog_jump then frogJumpReturned(p)\n  elseif p.frog_swim then frogReturned(p)')
    text=once(text,"if p.name=='M3Step' then motor=motor+1",
        "if p.name=='M3Step' then motor=motor+1;frogGroundReturned(p)")
    lo=text.index('local function menu()');hi=text.index("emu.addEventCallback(guarded('Controller'",lo)
    text=text[:lo]+MENU+'\n'+text[hi:]
    text=once(text,'physical<=6900','physical<=12000')
    text=once(text,'updates<5100','updates<9000')
    text=once(text,'actions=SMB3_ACTION_STATE','actions=SMB3_ACTION_STATE,frog=SMB3_FROG_WATER,selected_stage=C.start_level,scope=C.scope')
    script='local C='+value(q)+'\n'+text
    LuaRuntime().compile(script)
    names=set(re.findall(r"\br\('([^']+)'",text))
    assert not(names-set(q['ram'])),('Unbound literal RAM field',sorted(names-set(q['ram'])))
    assert not any(word in script for word in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return script


def pipe_controller(raw,form,*,frozen=False):
    """Keep exact2ac controls, rebinding only the disjoint Rogue successor."""
    import repair_rogue_side_pipe_1123 as Pipe
    assert H(raw)==PIPE_NIGHTLY
    parent=Pipe.restore_pipe_bytes(raw);assert H(parent)==PIN
    reference=Epoch.inverse(parent);restored=bytearray(parent);spans=Pipe.spans(reference)
    for at,before,after in spans:
        assert parent[at:at+len(before)]==before
        restored[at:at+len(after)]=after
    assert bytes(restored)==raw
    q=bindings(parent,form,frozen=frozen)
    for name,hook in q['hooks'].items():
        assert raw[16+hook['offset']:16+hook['offset']+len(hook['bytes'])]==bytes(hook['bytes']),name
    for bank in Base.NATIVE_BANKS:
        lo=16+bank*8192;assert raw[lo:lo+8192]==parent[lo:lo+8192]
    q.update(sha=PIPE_NIGHTLY,actual_input_CPU_SHA256=PIPE_NIGHTLY,reference2ac=PIN,
             disjoint_pipe_spans=[dict(file=at,bytes=len(after))for at,_,after in spans])
    _,body=controller(parent,form,frozen=frozen).split('\n',1)
    script='local C='+value(q)+'\n'+body
    assert script.split('\n',1)[1]==controller(parent,form,frozen=frozen).split('\n',1)[1]
    LuaRuntime().compile(script)
    if frozen:
        expected=FROZEN_RETRACTION_SCRIPTS if frozen=='retraction'else FROZEN_ADAPTIVE_SCRIPTS if frozen=='adaptive'else FROZEN_BRIDGE_SCRIPTS if frozen=='bridge'else FROZEN_PIPE_SCRIPTS
        assert H(script.encode())==expected[form],'Exact previous controller reconstruction'
    return script


def combined_parent(raw):
    """Strict in-memory recovery of287; never install or write recovered bytes."""
    import compose_dkjr_sonic_dispatch_1123 as Combined
    assert H(raw)==COMBINED_NIGHTLY==Combined.CANDIDATE
    parent=Combined.inverse(raw);assert H(parent)==PIPE_NIGHTLY==Combined.PIN
    assert Combined.proposal(parent)[0]==raw
    return parent


def combined_controller(raw,form,*,frozen=False):
    """Strict actual14b0 facade, distinct from every earlier287 script identity."""
    import repair_rogue_side_pipe_1123 as Pipe
    parent=combined_parent(raw)
    old=pipe_controller(parent,form,frozen=frozen)
    _,body=old.split('\n',1)
    reference=Pipe.restore_pipe_bytes(parent)
    q=bindings(reference,form,frozen=frozen)
    for name,hook in q['hooks'].items():
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes']),name
    for bank in Base.NATIVE_BANKS:
        lo=16+bank*8192;assert raw[lo:lo+8192]==parent[lo:lo+8192]
    for area in q['authored_areas'].values():
        at=area['file'];assert H(raw[at:at+area['bytes']])==area['SHA256']
    spans=Pipe.spans(Epoch.inverse(reference))
    q.update(sha=COMBINED_NIGHTLY,actual_input_CPU_SHA256=COMBINED_NIGHTLY,reference2ac=PIN,
        reference287=PIPE_NIGHTLY,disjoint_pipe_spans=[dict(file=at,bytes=len(after))for at,_,after in spans],
        parent_script_SHA256=H(old.encode()),strict_combined_roundtrip=True)
    script='local C='+value(q)+'\n'+body
    assert script.split('\n',1)[1]==old.split('\n',1)[1]
    LuaRuntime().compile(script);return script


def source_checks(raw):
    """Real native water policies and spring impulses; typed component poses."""
    b=dict(Base.authority(),raw=raw);base=N.fresh(b)
    N.put(base,SelectedCharacter=17,M3Marker=179,NumberofLives=2,AreaType=0,
          AreaNumber=2,LevelNumber=1,WorldNumber=1,AreaAddrsLOffset=1,PlayerFacingDir=1,
          OperMode=1,OperMode_Task=3,GameEngineSubroutine=8)
    N.invoke(base,'M3Reset');water=[];springs=[]
    swim_pc=W.address(b,'M3Native::Swim_Frog');swim_tag=((W.location(b,'M3Native::Swim_Frog')-16)//8192)|128
    for variant,period in ((2,1),(2,2),(3,1),(3,2)):
        m=N.fork(base)
        N.put(m,M3Variant=variant,M3Form=4,Player_X_Position=112,Player_PageLoc=0,
              Player_Y_Position=112,Player_Y_HighPos=1,Player_State=2,Player_X_Speed=0,Player_Y_Speed=0)
        lua=LuaRuntime();lua.execute('SMB3_ACTION_ACQUIRE=function()return{}end')
        choose=lua.execute(POLICY.read_text(encoding='utf-8'));f=lua.globals().SMB3_FROG_WATER
        a=lua.globals().SMB3_ACTION_STATE;a.acquired=True;f.flag=True;f.castle=True
        f.gap=lua.table_from(dict(complete=True)) # Explicit observer fixture precondition, not a stage claim.
        f.pit2=lua.table_from(dict(complete=True))
        f.pit3=lua.table_from(dict(complete=True))
        def read(name,index=0):return N.get(m,name,index or 0)
        def state():
            return dict(motor=tick,update=tick,frame=tick,x=read('Player_X_Position')+256*read('Player_PageLoc'),
                y=read('Player_Y_Position'),yHigh=read('Player_Y_HighPos'),state=read('Player_State'),
                vx=read('Player_X_Speed'),vy=read('Player_Y_Speed'),power=read('M3Form'),lives=read('NumberofLives'),
                growth=read('M3Growth'),poof=read('M3Poof'),world=1,level=1,engine=8,
                native_frame=read('M3Native::Player_Frame'))
        lua.globals().actionState=lambda:lua.table_from(state());lua.globals().r=read
        lua.globals().A=a;lua.globals().C=lua.table_from(dict(variant=variant))
        observe=lua.execute(OBSERVE+'\nreturn{entry=frogEntry,returned=frogReturned,tick=frogTick}')
        pending=[];cached=0;step_original=N.NesMPU.step
        def step(cpu):
            if cpu.pc==swim_pc and m.rawtags[(cpu.pc-32768)//8192]==swim_tag:
                p=lua.table_from({});observe.entry('FrogSwim',p)
                pending.append((m[256+((cpu.sp+1)&255)]+256*m[256+((cpu.sp+2)&255)]+1,(cpu.sp+2)&255,p))
            result=step_original(cpu)
            if pending and(cpu.pc,cpu.sp)==pending[-1][:2]:observe.returned(pending.pop()[2])
            return result
        N.NesMPU.step=step
        try:
            for tick in range(500):
                c=state();c.update(char=17,areaType=0,grounded=c['state']==0,r=read,block=lambda x,y:0,enemy=lambda:None)
                pad=choose(lua.table_from(c))
                if tick%period==0:cached=sum(v for k,v in dict(a=128,b=64,up=8,down=4,left=2,right=1).items()if pad[k])
                N.put(m,SavedJoypadBits=cached,FrameCounter=tick&255);N.invoke(m,'M3Movement');observe.tick()
                if f.complete:
                    assert not pending and len(f.segments)==17 and read('M3Form')==4
                    water.append(dict(variant=variant,input_poll_period=period,native_returns=f.swim_returns,
                        terminal=state(),segments=[dict(name=z.name,returns=z.returns,stale=z.stale,
                            frames=sorted(z.frames.keys()))for z in f.segments.values()]))
                    break
            else:raise AssertionError(('Bounded water policy',variant,period,f.phase,f.test_index,state()))
        finally:N.NesMPU.step=step_original
    for variant in (2,3):
        for force,wanted in ((249,202),(244,129)):
            m=N.fork(base)
            N.put(m,M3Variant=variant,M3Form=4,AreaType=1,Player_State=0,Player_X_Position=184,
                  Player_PageLoc=11,Player_Y_Position=176,Player_Y_HighPos=1,
                  JumpspringForce=force,Player_X_Speed=0,Player_Y_Speed=0)
            N.invoke(m,'MegaManSpringVelocity')
            before={n:N.get(m,n)for n in ('Player_State','Player_Y_Speed','M3LastVY','M3Native::Player_YVel','M3Native::Player_InAir')}
            assert before['M3Native::Player_YVel']==wanted and before['Player_State']==1
            assert before['M3LastVY']==before['Player_Y_Speed']
            N.put(m,SavedJoypadBits=129,FrameCounter=1);N.invoke(m,'M3Movement')
            assert N.get(m,'Player_State')==1 and N.get(m,'M3Native::Player_YVel')>=128
            springs.append(dict(variant=variant,spring_force=force,actual_impulse=before,
                next_native_vy=N.get(m,'M3Native::Player_YVel'),next_y=N.get(m,'Player_Y_Position'),retained_form=N.get(m,'M3Form')))
    return dict(passed=True,water=water,springs=springs,files=0,
        scope='Typed exact2ac native water movement/observer with normal and delayed polls, plus actual shared spring publication. No earned pickup or full-stage/native claim.')


def cpu_opening(raw,form,*,full=False,frozen=False):
    """Actual2-1 parser/inputs/observer from the established source menu arena."""
    b=dict(Base.authority(),raw=raw);execs={};writes={};events={};status=None;receipt=None;current=None
    original_bus=N.Bus
    class Bus(W.ControllerBus):
        def __setitem__(self,at,v):
            super().__setitem__(at,v)
            if isinstance(at,int):
                for fn in tuple(writes.get(at,())):fn(at,v)
    N.Bus=Bus
    try:m=W.UI.seed(b,16)
    finally:N.Bus=original_bus
    # The compact roster arena skips Reset's genuine RNG seed. Execute those
    # exact cold instructions; an all-zero LFSR can never select Frog.
    pc=W.address(b,'FinializeMarioInit');at=W.location(b,'FinializeMarioInit')
    expected=b'\x58\xa9\xa5\x8d'+W.address(b,'WarmBootValidation').to_bytes(2,'little')
    expected+=b'\x8d'+W.address(b,'PseudoRandomBitReg').to_bytes(2,'little')
    assert raw[at:at+9]==expected
    maps=tuple(m.rawtags);m.raw_page((pc-32768)//8192,((at-16)//8192)|128)
    seed=N.NesMPU(memory=m,pc=pc)
    for _ in range(4):seed.step()
    assert seed.pc==pc+9 and N.get(m,'PseudoRandomBitReg')==165
    for window,tag in enumerate(maps):m.raw_page(window,tag)
    for _ in range(Base.FORMS[form][0]):W.UI.key(m,32)
    # Fixture selects the existing Cheats page, then changes Start Level only
    # through four actual Right inputs. Restore the source roster arena before
    # actual Start/ChkContinue. No gameplay pose/actor/reward/RNG writes follow.
    N.put(m,CrossoverMenuState=6,CrossoverOptionsFocus=1)
    for _ in range(4):W.UI.key(m,1)
    assert N.get(m,'CheatStartLevel')==36 and N.get(m,'CheatInvincible')==0
    N.put(m,CrossoverMenuState=2);start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    lua=LuaRuntime();g=lua.globals();g.os.getenv=lambda name:H(raw)if name=='SMB_STDOUT_ROM_SHA'else None
    lua.execute('emu={memType={nesDebug=0,nesPrgRom=1,nesWorkRam=2},callbackType={exec=1,write=2},eventType={inputPolled=1,endFrame=2}}')
    def read(at,kind):
        if kind==0:return m[at]
        if kind==1:return raw[16+at]
        return m.ram[(at//8192)&3][at&8191]
    def convert(pc):
        if pc<32768:return lua.table_from(dict(address=pc,memType=0))
        tag=m.rawtags[(pc-32768)//8192]
        return lua.table_from(dict(address=(tag&127)*8192+(pc&8191),memType=1 if tag&128 else 2))
    def getstate():return lua.table_from({'cpu.pc':current.pc,'cpu.sp':current.sp,'cpu.ps':current.p,
        'cpu.a':current.a,'cpu.x':current.x,'cpu.y':current.y})
    def addmem(fn,kind,first,last=None):
        for at in range(first,(last if last is not None else first)+1):(execs if kind==1 else writes).setdefault(at,[]).append(fn)
    def addevent(fn,kind):events.setdefault(kind,[]).append(fn)
    def setinput(pad,port):m.controller_pad=sum(v for k,v in dict(a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1).items()if pad[k])
    def stop(v):
        nonlocal status
        status=v
    def output(v):
        nonlocal receipt
        if v.startswith('SMB_NATIVE_RECEIPT '):receipt=json.loads(v.removeprefix('SMB_NATIVE_RECEIPT '))
    for name,fn in dict(read=read,convertAddress=convert,getState=getstate,addMemoryCallback=addmem,
                        addEventCallback=addevent,setInput=setinput,stop=stop).items():g.emu[name]=fn
    g.print=output
    make=combined_controller if H(raw)==COMBINED_NIGHTLY else pipe_controller if H(raw)==PIPE_NIGHTLY else controller
    lua.execute(make(raw,form,frozen=frozen))
    g.SMB3_FROG_WATER.menu_configured=lua.table_from(dict(source_menu_arena=True))
    original_cpu=N.NesMPU
    def dispatch(cpu):
        nonlocal current
        current=cpu
        for fn in tuple(execs.get(cpu.pc,())):fn(cpu.pc)
    class CPU(original_cpu):
        def step(self):dispatch(self);return super().step()
    N.NesMPU=CPU;idle=W.address(b,'IdleLoop');last=None
    def snapshot():
        return {k:N.get(m,k)for k in ('WorldNumber','LevelNumber','AreaType','AreaAddrsLOffset',
            'GameEngineSubroutine','M3Form','M3Growth','M3Poof','NumberofLives','Player_X_Position',
            'Player_PageLoc','Player_Y_Position','Player_Y_HighPos')}
    try:
        for epoch in range(7000 if full else 2400):
            for fn in events.get(1,()):fn()
            W.clear_logs(m);N.consume(m)
            cpu=CPU(memory=m,pc=idle);cpu.sp=255;cpu.p=49;cpu.stPushWord(0xe33b)
            for _ in range(250000):
                if(cpu.pc,cpu.sp)==(idle+12,252):dispatch(cpu);break
                assert m[cpu.pc],('Source BRK',epoch,hex(cpu.pc));cpu.step()
                if status is not None:break
            else:raise AssertionError('Bounded source IdleLoop')
            for fn in events.get(2,()):fn()
            now=snapshot();opening=g.SMB3_FROG_OPENING
            phase=opening.phase if opening else None
            if epoch%100==0 or phase!=last:
                print('FROG LINKED OPENING '+json.dumps(dict(epoch=epoch,phase=phase,**now)),flush=True);last=phase
            if status is not None:
                items={}
                for kind,q in(receipt or{}).get('items',{}).items():
                    items[kind]={k:q[k]for k in ('collect','growth_ticks','poof_ticks','after')if k in q}
                observed=(receipt or{}).get('frog',{});gap=observed.get('gap',{})
                compact_frog={k:observed[k]for k in ('phase','flag','castle','water_entry','swim_returns','plant_active','plants','pit2','pit3',
                    'jumps','spring_compress','spring_release')if k in observed}
                if gap:
                    compact_frog['gap']={k:gap[k]for k in ('phase','changes','approach_entry','last_decision','last_requested','floor','first_plant','bridge_staging','bridge_jump','pipe_landing','jump','lift','bank_landing','ground_steps','complete')if k in gap}
                    compact_frog['gap']['approach_trace_count']=len(gap.get('approach_trace',[]))
                compact_frog['segments']=[dict(name=q['name'],returns=q['returns'])for q in observed.get('segments',[])]
                return dict(passed=bool(receipt and receipt['passed']),reason=receipt and receipt['reason'],epoch=epoch,terminal=now,
                    receipt_SHA256=H(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode())if receipt else None,
                    items=items,frog=compact_frog,tail=receipt and receipt['tail'][-2:],files=0,
                    scope='Actual source input/parser/controller with logical normal NMI scheduling; no Mesen or physical cadence claim')
            if g.SMB3_ACTION_STATE.acquired and not full:
                return dict(passed=True,epoch=epoch,terminal=now,acquired=dict(g.SMB3_ACTION_STATE.acquired),files=0,
                    scope='Actual cold-seed instructions and2-1 authored block/rise/collector/effects/25-return opening from source roster arena; no Mesen or physical cadence claim')
        f=g.SMB3_FROG_WATER
        diagnostic=dict(phase=f.phase,flag=bool(f.flag),castle=bool(f.castle))
        for key in ('spring_compress','spring_release'):
            if f[key]:diagnostic[key]=dict(f[key].items())
        return dict(passed=False,reason='Bounded source opening cutoff',terminal=now,opening_phase=phase,
            frog=diagnostic,files=0)
    finally:N.NesMPU=original_cpu


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',action='store_true',help='Root only: existing shared sequential Mesen slot')
    p.add_argument('--form',choices=('toad3','peach3','both'),default='toad3')
    p.add_argument('--pipe-nightly',action='store_true',help='Strict disjoint28708 successor; keep exact2ac controls')
    p.add_argument('--combined-nightly',action='store_true',help='Strict actual14b0 full source/native binding')
    p.add_argument('--frozen-pipe-approach',action='store_true',help='Reproduce exact7dade7aa/e462ba07 earlier controls in memory')
    p.add_argument('--frozen-bridge-approach',action='store_true',help='Reproduce exactd83e3b28/89a9b271 bridge controls in memory')
    p.add_argument('--frozen-adaptive-approach',action='store_true',help='Reproduce exactb99fdf17/09634f64 controls in memory')
    p.add_argument('--frozen-retraction-approach',action='store_true',help='Reproduce exactc7390a3f/29c7f539 controls in memory')
    p.add_argument('--cpu-opening',action='store_true',help='Optional real linked parser/input opening; source-only')
    p.add_argument('--cpu-full',action='store_true',help='Continue the linked controller through2-2 or first failure; source-only')
    args=p.parse_args();forms=('toad3','peach3')if args.form=='both'else(args.form,)
    assert not(args.run and(args.cpu_opening or args.cpu_full))
    assert not(args.pipe_nightly and args.combined_nightly)
    assert sum((args.frozen_pipe_approach,args.frozen_bridge_approach,args.frozen_adaptive_approach,args.frozen_retraction_approach))<=1
    frozen='retraction'if args.frozen_retraction_approach else 'adaptive'if args.frozen_adaptive_approach else 'bridge'if args.frozen_bridge_approach else args.frozen_pipe_approach
    pin=COMBINED_NIGHTLY if args.combined_nightly else PIPE_NIGHTLY if args.pipe_nightly else PIN
    installed=ROM.read_bytes();raw=installed
    if args.pipe_nightly and H(installed)==COMBINED_NIGHTLY:
        assert not args.run,'287 identity is source-only after14b0 delivery; use --combined-nightly for Mesen'
        raw=combined_parent(installed)
    assert H(raw)==pin
    make=combined_controller if args.combined_nightly else pipe_controller if args.pipe_nightly else controller
    program=lambda raw,form:make(raw,form,frozen=frozen)
    if not args.run:
        rows=[dict(form=form,script_SHA256=H(program(raw,form).encode()))for form in forms]
        opening=[dict(form=form,**cpu_opening(raw,form,full=args.cpu_full,frozen=frozen))for form in forms]if(args.cpu_opening or args.cpu_full)else None
        passed=opening is None or all(case['passed']for case in opening)
        print('SMB3 FROG WATER SOURCE '+json.dumps(dict(passed=passed,ROM_SHA256=pin,cases=rows,
            controller_only=True,source_validated=True,installed_input_SHA256=H(installed),reconstructed_in_memory=raw!=installed,
            opening=opening,components=None if(args.cpu_opening or args.cpu_full)else source_checks(raw),files=0,Mesen=False)),flush=True);return int(not passed)
    from capture_budget import preflight
    from nightly_patch_guard_v1 import check
    from mesen_session_guard_v1 import require_free_workspace
    from run_stdout_mesen_1110 import run
    output=Base.OUT;before=check(ROM)
    assert before['ROM_sha256']==pin and not before['matching_patch_files']
    assert {f.name for f in output.iterdir()}=={'candidate.nes','controller.lua'}and(output/'candidate.nes').read_bytes()==raw
    preflight(output/'capture',reserved_files=0);require_free_workspace(R,ROM,allow_interactive=True)
    script=output/'controller.lua';previous=script.read_bytes()
    try:
        for form in forms:
            script.write_bytes(program(raw,form).encode())
            result=run(script,ROM,output/'capture',pin,280,long_no_capture=True)
            assert not result['images']and result['outputs_written']==0
            print('SMB3 FROG WATER '+json.dumps(dict(form=form,**result),separators=(',',':')),flush=True)
            assert ROM.read_bytes()==raw and check(ROM)==before
            if not result['passed']:return 1
    finally:script.write_bytes(previous);assert ROM.read_bytes()==raw and check(ROM)==before
    return 0


if __name__=='__main__':raise SystemExit(main())
