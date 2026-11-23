"""Natural Easy Mac-family native Star; exact3af, Root-only --run."""
import argparse,json
from pathlib import Path
from unittest.mock import patch
import run_mac_family_life_1123 as Life

PIN,FORMS=Life.PIN,Life.FORMS
PINS={'mac':'ef2f35b876c9222fae9975ad7ddf07cabb9a87da24b869c98302208b577f6313',
      'doc':'7d04f43f4dbf3c2b6af85d1e9547738547f2f06ae51c6187d7f285412c2f34e5',
      'tyson':'4e23c621f12d28a89d0779fb7ed11ed8afda67096fed3ebf31244b8cd222dbe0'}
POLICY=r'''
local T={phase='upgrades',events={}}
MAC_STOCK_STATE=T
local holdUntil=0
local function sample(c,a)
 return{x=c.x,y=c.y,state=c.state,update=c.update,motor=c.motor,hp=c.hp,
        stars=c.stars,hearts=c.hearts,nativeStar=c.star,item=a}
end
local function phase(c,p,a)
 if T.phase==p then return end
 assert(#T.events<40,'Bounded ordinary native Star phases')
 T.phase=p;T.since=c.update;T.events[#T.events+1]={phase=p,player=sample(c,a)}
end
local function steer(c,x,band)
 local v=c.vx<128 and c.vx or c.vx-256;local d=x-c.x-v/5
 return{right=d>band,left=d< -band}
end
local function item(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==2 then
   return{x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
          y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),slot=i}
  end
 end
end
local function defend(c,b)
 local e=c.enemy()
 if e and math.abs(e.dx)<56 and math.abs(e.y-c.y)<32 and c.grounded then
  local facing=e.dx>=0 and 1 or 2
  if c.r('PlayerFacingDir')~=facing then return{right=facing==1,left=facing==2}end
  return{down=true,b=c.update%12<3}
 end
 return b
end
return function(c)
 if c.star>0 then phase(c,'native-Star-credited');return{}end
 if not T.flower then
  if c.stars==0 then return prefix(c)end
  T.flower=sample(c);phase(c,'Flower-after');return{}
 end
 if c.update-T.flower.update<64 then return{}end
 if T.phase=='Flower-after'then phase(c,'travel')end
 local a=item(c)
 if a and not T.revealed then T.revealed=sample(c,a);phase(c,'rise',a)end
 if T.revealed and not a then T.missing=T.missing or sample(c);return{}end
 if a then
  T.latest=sample(c,a)
  if c.update%12==0 then
   T.trace=T.trace or{};if #T.trace==16 then table.remove(T.trace,1)end
   T.trace[#T.trace+1]=T.latest
  end
  if a.state&128==0 then return defend(c,steer(c,1644,3))end
  phase(c,'collect',a)
  -- Let the first high bounce pass overhead, then meet its descent.  An
  -- immediate launch under the rising Star spends Mac's short arc too soon.
  if T.intercept and c.update-T.intercept.update<42 then
   return{a=c.update<holdUntil}
  end
  if not T.intercept and a.x<1696 then
   if math.abs(c.x-1667)>3 then return defend(c,steer(c,1667,2))end
   if a.y>=110 and math.abs(a.x-c.x-6)<=13 and c.grounded and not c.lastA then
    T.intercept=sample(c,a);holdUntil=c.update+26;return{a=true}
   end
   return{}
  end
  assert(c.x<1900,'Bounded native Star pursuit runway')
  local target=math.max(c.camera+2,a.x-4)
  local b=steer(c,target,3)
  if c.grounded and c.y-a.y>14 and math.abs(c.x-a.x)<28 and not c.lastA then
   holdUntil=c.update+26
  end
  b.a=c.update<holdUntil
  return defend(c,b)
 end
 if T.phase=='travel'then
  if c.x<1580 then return opening(c)end
  phase(c,'align')
 end
 if T.phase=='bump'then
  if c.update-T.since>52 then phase(c,'align')end
  return{a=c.update<holdUntil}
 end
 if not c.grounded or c.y<160 then return defend(c,steer(c,1590,3))end
 if math.abs(c.x-1619)<=2 and math.abs(c.vx<128 and c.vx or c.vx-256)<=4 and not c.lastA then
  T.attempts=(T.attempts or 0)+1;assert(T.attempts<=8,'Bounded authored native Star bump')
  holdUntil=c.update+28;phase(c,'bump');return{a=true}
 end
 return defend(c,steer(c,1619,2))
end
'''


def controller(raw,form):
    text=Life.build(raw,form,kind=2,policy=POLICY)
    assert text.count('updates<3600')==1;text=text.replace('updates<3600','updates<2600',1)
    a='if kind<2 and q.collect and not q.grant and score()>=q.collect.score_before+1000 then'
    b='if kind<=2 and q.collect and not q.grant and score()>=q.collect.score_before+1000 then'
    assert text.count(a)==1;text=text.replace(a,b,1)
    a="elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')"
    b="elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Actual native Star timer and points persist')"
    assert text.count(a)==1;text=text.replace(a,b,1)
    Life.LuaRuntime().compile(text)
    if form in PINS:assert Life.H(text.encode())==PINS[form]
    return text


def native(raw,form):
    assert form in PINS
    program=controller(raw,form).encode();guard=Life.check(Life.ROM)
    candidate,script=Life.OUT/'candidate.nes',Life.OUT/'controller.lua'
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(Life.OUT.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    before=script.read_bytes()
    try:
        with Life.preserve_script(script,candidate,raw)as stage:
            stage(program);q=Life.run(script,Life.ROM,Life.OUT/'capture',PIN,180)
        print('MAC_STAR_NATIVE '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['script_SHA256']==Life.H(program)and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and Life.ROM.read_bytes()==raw and Life.check(Life.ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--form',choices=tuple(FORMS),default='mac')
    g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=3400);a=p.parse_args();assert 1000<=a.limit<=4000
    raw=Life.ROM.read_bytes();assert Life.H(raw)==PIN
    if a.run:return int(not native(raw,a.form)['passed'])
    def deny(*a,**k):raise AssertionError('Source attempted outputs or native process')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        text=controller(raw,a.form)
        q=Life.source(raw,a.form,a.limit,text=text)if a.source else dict(passed=True,ROM_SHA256=PIN,controller_SHA256=Life.H(text.encode()),route_executed=False,outputs=0)
    print('MAC_STAR_SOURCE '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
