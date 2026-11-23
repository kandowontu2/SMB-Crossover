"""Normal Easy Shinobi Mushroom -> authored Flower, stdout only.

Uses the delivered collector, original movement, four retained pipe takeoffs
and crouch shuriken. Root alone may --run after this controller is frozen.
"""
import argparse
from functools import lru_cache
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import compose_shinobi_pickups_1123 as P
import compose_dkjr_shinobi_1123 as DK

Prior=P.Head.Prior
W,N,H,Stock,ROM,Engine=Prior.W,Prior.N,Prior.H,Prior.Stock,Prior.ROM,Prior.Engine
PARENT=P.CANDIDATE
PIN=DK.STAR_UNDER
LUA='d4822ba98e075f0125b1c12955d2a3fb981cab1e46f967d5cf0f6e74d05dff2b'

DRIVE=r'''
local function solid(wx,wy)
 if wy<32 or wy>=240 then return false end
 local t=r('Block_Buffer_1',(wx//256)%2*208+((wy-32)//16)*16+(wx%256)//16)
 return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2
end
local function note(p)
 if F.phase==p then return end
 F.phase=p;F.at=steps;assert(#F.events<48,'Bounded original Shinobi Flower phases')
 F.events[#F.events+1]={phase=p,player=state(),pipe=F.pipe}
end
local function shot()
 return{state=r('ShShotState'),kind=r('ShShotType'),pose=r('ShShotPose'),speed=r('ShShotSpeed'),
  x=r('ShShotX')+256*r('ShShotXHi')+pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),
  y=r('ShShotY'),draw_bits=r('ShDrawBits')}
end
local function travel()
 local s=state();local b={right=true};F.ticks=F.ticks+1
 local starts={410,560,692,868};local ends={480,640,768,944}
 if F.pipe<=4 then
  if not F.jumping and s.x>=starts[F.pipe]and r('Player_State')==0 and released()then
   F.jumping=true;F.jump=steps;note('pipe-'..F.pipe)
  end
  if F.jumping then
   b.a=steps-F.jump<40
   if steps-F.jump>40 and r('Player_State')==0 and s.x>=ends[F.pipe]then
    F.jumping=false;F.pipe=F.pipe+1;F.cooldown=8
   end
  end
 else
  if F.cooldown>0 then F.cooldown=F.cooldown-1 end
  local danger=false;local firing=false
  for i=0,5 do local e=actor(i)
   if e.flag>0 and e.flag<128 and e.id<21 and e.state&32==0 then
    local dx=e.x-s.x
    if dx>0 and dx<45 and math.abs(e.y-s.y)<50 then danger=true end
    if dx>=45 and dx<110 and math.abs(e.y-s.y)<36 then firing=true end
   end
  end
  if firing and r('Player_State')==0 and not F.jumping then b.right=false end
  if not F.jumping and F.cooldown==0 and r('Player_State')==0 and released()
     and(not solid(s.x+8,216)or solid(s.x+32,s.y+24)or danger)then
   F.jumping=true;F.jump=steps;note('ground-jump')
  end
  if F.jumping then
   b.a=steps-F.jump<40
   if steps-F.jump>20 and r('Player_State')==0 then F.jumping=false;F.cooldown=8;b.a=false end
  end
 end
 if not F.jumping and r('Player_State')==0 then
  for i=0,5 do local e=actor(i)
   if e.flag>0 and e.flag<128 and e.id<21 and e.state&32==0 then
    local dx=e.x-s.x
    if dx>20 and dx<130 and math.abs(e.y-s.y)<36 then
     b.right=false;b.down=true;b.b=F.ticks%24<12
    end
   end
  end
 end
 return b
end
local function policy()
 if not F.first_ready then return firstPolicy()end
 local s=state();local a=item();latest={player=s,item=a,flower=F.phase}
 assert(s.ready==167 and r('SelectedCharacter')==36 and s.lives==2 and s.engine==8 and s.high==1,
  'Living authenticated original Shinobi in ordinary1-1')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Ordinary Flower before stage exit')
 assert(updates<3800,'Bounded complete normal Flower route')
 if s.x>(F.max_x or 0)then F.max_x=s.x;F.progress=steps end
 if F.consumed then
  assert(s.power==F.pickup.after.power and s.power==1,'Original earned weapon descriptor retained')
  if moves-F.consumed.moves>=25 and steps-F.consumed.steps>=25 and r('Player_State')==0 then
   assert(score()>=F.pickup.before.score+1000 and #births==2,'Both authored upgrades credited')
   F.retained=F.retained or state()
   F.weapon=F.weapon or{phase='crouch',at=steps,samples={}}
   local w=F.weapon;assert(steps-w.at<140,'Bounded original upgraded projectile use')
   local q=shot()
   if q.state~=0 then
    assert(q.kind==1 and q.speed==7 and q.pose==9,'Actual earned donor weapon descriptor1')
    w.first=w.first or q;w.last=q
    if #w.samples<8 then w.samples[#w.samples+1]=q end
    w.distance=math.max(w.distance or 0,math.abs(q.x-w.first.x))
   end
   if w.phase=='crouch'then
    if s.source_state~=5 then return{down=true}end
    assert(r('PreviousA_B_Buttons')&64==0,'Fresh B after real source crouch')
    w.phase='throw';w.press=steps;w.request=s;return{down=true,b=true}
   end
   if steps-w.press<4 then return{down=true,b=true}end
   if w.first and(w.distance or 0)>=16 and steps-w.press>=25 and(s.source_state==0 or s.source_state==5)then
    w.after=state();finish(true,'Natural Shinobi Flower raised weapon0 to1, retained25 moves and moved its genuine upgraded shot');return{}
   end
   return{}
  end
  return{}
 end
 if F.phase:sub(1,4)=='pipe'or F.phase=='ground-jump'or F.phase=='travel'then
  assert(steps-F.progress<500,'Normal source travel progress bound')
  if s.x>=1184 and r('Player_State')==0 then note('flower-align');F.jumping=false
  else return travel()end
 end
 if F.phase=='flower-align'then
  if r('Player_State')~=0 then return{}end
  if math.abs(s.x-1241)<=2 and r('Player_X_Speed')==0 and released()then
   F.head_attempts=(F.head_attempts or 0)+1;assert(F.head_attempts<=3,'Actual second authored block attempts')
   F.head_step=steps;note('flower-head');return{a=true}
  end
  return steer(1241,2)
 end
 if F.phase=='flower-head'then
  if F.birth then
   -- The hit cell is temporarily23 while its native block bounces. Its
   -- right edge is still known; scan the untouched cells to its right.
   F.terrain={};for yy=112,208,16 do local row={y=yy,tiles={}}
    for xx=1184,1344,16 do row.tiles[#row.tiles+1]=solid(xx,yy)end
    F.terrain[#F.terrain+1]=row
   end
   note('flower-wait')
  elseif steps-F.head_step>90 and r('Player_State')==0 then note('flower-align');return{}
  else return{a=steps-F.head_step<24}end
 end
 assert(a and a.kind==1,'Authored literal Flower remains before owning collection')
 if F.phase=='flower-wait'then
  assert(steps-F.at<160,'Bounded actual owning Flower contact')
  F.latest={player=s,actor=a}
  return steer(1250,1)
 end
 return{}
end
'''

RETURNED=r'''
local function returned(p)
 local s=state();local cpu=emu.getState()
 if p.name=='Movement'then moves=moves+1
 elseif p.name=='TakeHit'or p.name=='SourceHit'then
  if s.health<p.before.health then damage={before=p.before,after=s,target=p.target}end
 elseif p.name=='Maturity'then
  local c=(cpu['cpu.ps']or cpu['cpu.p'])&1
  if p.actor and p.actor.state&128~=0 then
   maturity.queries=maturity.queries+1
   if c==0 then maturity.clear=maturity.clear+1 else maturity.set=maturity.set+1 end
   if p.overlap then maturity.overlap=maturity.overlap+1 end
   if p.actor.kind==1 then
    F.maturity={carry=c,actor=p.actor,player=p.before,overlap=p.overlap,player_box=p.player_box,item_box=p.item_box}
    F.mature=F.mature or{actor=p.actor,player=p.before,at='actual-HuMature-return'}
   end
  end
 elseif p.name=='SourcePickup'then
  assert(p.actor.flag>0 and p.actor.id==46 and p.actor.state&128~=0,'Real mature item at owning collector')
  if p.kind==0 then
   assert(not mushroom and #heads==1 and #births==1 and heads[1].pointer==0x3d5,
    'Verified first natural Mushroom precedes Flower travel')
   assert(s.status==1 and s.health==r('ShMaxHealth')and r('ShFoodUpdate')==1,'Original donor food refill')
   mushroom={before=p.before,after=s};pickup=mushroom
  else
   assert(p.kind==1 and mushroom and F.birth and F.mature and F.maturity and F.maturity.carry==1
      and F.maturity.overlap and F.maturity.actor.slot==p.actor.slot,
    'Genuine Flower birth, maturity and admitted contact')
   assert(p.before.power==0 and s.power==1 and s.health==p.before.health and s.status==1,
    'Exact original weapon increment, unchanged health and native tier')
   F.pickup={before=p.before,after=s,actor=p.actor};pickup=F.pickup
  end
 elseif p.name=='NativePickup'then
  assert(r('Enemy_Flag',p.slot)==0 and r('Square2SoundQueue')==32 and r('FloateyNum_Control',p.slot)==6,
   'Native erase,1000-point popup and cue at actual collector return')
  if p.kind==0 then assert(mushroom,'Owning first food before erase');consumed=s
  else assert(p.kind==1 and F.pickup,'Owning Flower before erase');F.consumed=s;note('flower-retain')end
 end
end
'''


@lru_cache(maxsize=1)
def controller(raw):
    assert H(raw)==PIN
    base=DK.recover_parent(raw);assert H(base)==PARENT
    for page in set(P.Head.PAGES+(503,504,505,516,517)):
        at=1048592+page*1024;assert raw[at:at+1024]==base[at:at+1024]
    assert raw[P.Head.COOKIE:P.Head.COOKIE+16]==base[P.Head.COOKIE:P.Head.COOKIE+16]
    parent=P.recover_parent(base)
    cookie=list(raw[P.Head.COOKIE:P.Head.COOKIE+16])
    text=P.mushroom_program(parent,base,dict(cookie=cookie)).decode()
    assert text.count(PARENT)==1;text=text.replace(PARENT,PIN)
    once=Prior.once
    text=once(text,'assert(CPU_CONTROLLER_OPENING',
        "local F={phase='first',pipe=1,ticks=0,cooldown=0,jumping=false,events={}}\nassert(CPU_CONTROLLER_OPENING")
    text=once(text,'local function policy()','local function firstPolicy()')
    text=once(text,"finish(true,'Shinobi collected his authored first Mushroom');return {}end",
        "F.first_ready=true;F.phase='travel';F.at=steps;F.progress=steps;return {}end")
    start,stop=text.index('local function returned(p)'),text.index('local function settle()')
    text=text[:start]+DRIVE+'\n'+RETURNED+'\n'+text[stop:]
    text=once(text,'slot=cpu[\'cpu.x\']}','''slot=cpu['cpu.x']}
 if name=='SourcePickup'or name=='NativePickup'then
  assert(p.slot<6,'Actual six-slot powerup actor');p.actor=actor(p.slot);p.kind=p.actor.kind
 end''')
    text=text.replace("if x()<400 and #heads<8 then", "if x()<1400 and #heads<12 then")
    start,stop=text.index('local seenBirth={}'),text.index('local function pulse(key)')
    text=text[:start]+'''local seenBirth={}
local function observe()
 local a=item()
 if not a then return end
 local key=a.slot..':'..a.kind
 if not seenBirth[key]then
  assert(a.kind==0 or a.kind==1,'Only two standard authored upgrades')
  if a.kind==1 then
   assert(F.first_ready and r('PlayerStatus')==1 and a.x==1248,'Natural second block Flower at1248')
   F.birth={actor=a,player=state()}
  else assert(not mushroom and #heads==1 and a.x==336,'First authored Mushroom')end
  seenBirth[key]=true;births[#births+1]={actor=a,player=state()}
 end
 if a.state&128~=0 then
  if a.kind==0 and not mature then mature={actor=a,player=state()}
  elseif a.kind==1 and not F.mature then F.mature={actor=a,player=state()}end
 end
end
'''+text[stop:]
    text=once(text,'headmotion=headmotion,head_blocked=head_blocked',
        'headmotion=headmotion,flower=F,head_blocked=head_blocked')
    bundle=W.Symbols.bundle()
    extra='\n'.join(f'C.ram.{name}={W.address(bundle,name)}'for name in('Block_Buffer_1','PlayerFacingDir','FloateyNum_Control'))
    text=once(text,'C.hooks.QueryReturn=nil','C.hooks.QueryReturn=nil\n'+extra)
    work={'ShShotState':0x414,'ShShotType':0x482,'ShShotPose':0x301,'ShShotSpeed':0x3a6,
          'ShShotX':0x37a,'ShShotXHi':0x385,'ShShotY':0x390,'ShDrawBits':0x810}
    text=once(text,'C.hooks.QueryReturn=nil','C.hooks.QueryReturn=nil\n'+
        '\n'.join(f'C.work.{name}={at}'for name,at in work.items()))
    text=text.replace("frame<6500,'Physical Shinobi pickup bound'", "frame<16000,'Physical Shinobi Flower bound'")
    text=text.replace("updates<1800,'Bounded first Shinobi Mushroom'", "updates<3800,'Bounded original Shinobi Flower'")
    assert not any(word in text for word in('emu.write','emu.setState','io.open','dofile','takeScreenshot','saveState','loadState'))
    Stock.LuaRuntime().compile(text);program=text.encode()
    assert LUA is None or H(program)==LUA
    return program


def cold(raw):
    assert H(raw)==PIN
    code=P.Head.carrier(raw);meta=P.chr_page(raw,516)+P.chr_page(raw,517)
    art=b''.join(P.chr_page(raw,page)for page in(503,504,505))
    with patch.object(Prior,'PIN',PIN),patch.object(Prior,'payload',lambda image:(code,meta,art)):
        return Prior.cold(raw)


def source(raw,limit):
    body=inspect.getsource(Engine.run)
    body=Prior.once(body,'for fn in tuple(callbacks[0].get(self.pc,())):fn()',
        'for fn in tuple(callbacks[0].get(self.pc,())):fn(self.pc)')
    scope=dict(Engine.__dict__);exec(compile(body,__file__,'exec'),scope)
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',PIN):
        return scope['run'](raw,limit,text=controller(raw).decode())


def native(raw):
    program=controller(raw);assert LUA and H(program)==LUA,'Source-qualified frozen Flower controller'
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua'
    guard=Stock.check(ROM);previous=script.read_bytes()
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:
            stage(program);q=Stock.run(script,ROM,out/'capture',PIN,240)
        assert q['script_SHA256']==LUA and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==previous and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group()
    g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=3200);a=p.parse_args();assert 600<=a.limit<=4200
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw)
    else:
        def deny(*args,**kwargs):raise AssertionError('Source-only Flower probe attempted output/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            q=source(raw,a.limit)if a.source else dict(passed=True,controller_SHA256=H(controller(raw)),outputs=0)
    print('SHINOBI_FLOWER '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
