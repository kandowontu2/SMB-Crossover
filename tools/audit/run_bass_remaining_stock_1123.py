"""Continue Bass's ordinary 1-1 route after the verified first Mushroom."""

import argparse
from hashlib import sha256
import json

import run_bass_stock_1123 as Bass


KINDS = {'flower': 1, 'life': 3, 'star': 2}
FIRST = '6d17d88949e860ff63c4cf77fff07264da6beb701b8f203b741f5c3d0c9912eb'
SECOND = r'''
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
local function defend(c,pad)
 if pad.a or not c.grounded then return pad end
 local e=c.enemy()
 if not e or e.dx<=0 or e.dx>=95 or math.abs(e.y-c.y)>25 then return pad end
 for x=c.x+20,e.x-8,8 do if solid(c,x,c.y+20) then return pad end end
 if c.update%20<2 then pad.b=true end
 return pad
end
local function travel(c)
 if c.grounded then
  if route.hop and c.update-route.hop>3 then route.hop=nil end
  local obstacle=solid(c,c.x+30,c.y+16)or solid(c,c.x+30,c.y+24)
  local gap=not solid(c,c.x+29,math.min(c.y+38,232))
  if not c.lastA and (obstacle or gap) then
   route.hop=c.update;return{right=true,a=true}
  end
  return defend(c,{right=true})
 end
 if route.hop then
  local age=c.update-route.hop
  return{right=true,a=age<22 or (age>=28 and age<43 and c.r('XgJumpUsed')==0)}
 end
 return{right=true}
end
local function mountFlower(c,a)
 if route.phase~='flower-approach' and route.phase~='flower-mount'then
  change(c,'flower-approach')
 end
 if route.phase=='flower-approach'then
  if not a.mature or math.abs(c.x-1284)>3 or not c.grounded or c.vx~=0 then
   return defend(c,steer(c,1284,3))
  end
  if c.lastA then return{}end
  route.mounts=(route.mounts or 0)+1
  assert(route.mounts<=4,'Bounded right-side Bass Flower mount')
  change(c,'flower-mount');return{a=true,left=true}
 end
 local age=c.update-route.at
 if c.grounded and age>5 then
  change(c,'flower-approach');return steer(c,1284,3)
 end
 assert(age<120,'Bass Flower jump did not land')
 local pad=steer(c,a.x+11,2)
 pad.a=age<15 or (age>=17 and age<43)
 return pad
end
local function second(c)
 if BASS_TARGET_COLLECTED then return{}end
 local kind=C.targetKind
 local goal=kind==1 and 1248 or kind==2 and 1616 or 1024
 local a
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==kind then
   a={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),
      mature=c.r('Enemy_State',i)&128~=0};break
  end
 end
 if a then
  if kind==1 then return mountFlower(c,a)end
  if route.phase~='second-catch'then change(c,'second-catch')end
  local x=kind==3 and math.min(1085,a.x-3)or a.x-3
  if not a.mature then return defend(c,steer(c,goal+28,2))end
  if c.grounded and not c.lastA and c.y-a.y>12 and math.abs(a.x-c.x)<30 then
   route.catch=c.update;return{a=true,right=c.x<a.x-4,left=c.x>a.x+4}
  end
  local pad=steer(c,x,2)
  if route.catch and c.update-route.catch<25 then pad.a=true end
  return defend(c,pad)
 end
 if route.phase=='second-travel'then
  if c.x<goal-65 then return travel(c)end
  change(c,'second-align')
 end
 if route.phase=='second-align'then
  if not c.grounded then return steer(c,goal-8,3)end
  if not c.lastA and math.abs(c.x-(goal-6))<=2 then
   route.secondAttempts=(route.secondAttempts or 0)+1
   assert(route.secondAttempts<=5,'Bounded later Bass head bump')
   change(c,'second-jump');return{a=true}
  end
  return defend(c,steer(c,goal-6,2))
 end
 if route.phase=='second-jump'then
  if c.grounded and c.update-route.at>45 then change(c,'second-align')end
  return{a=c.update-route.at<26}
 end
 return{}
end
'''


def controller(raw, route):
    original = Bass.controller(raw)
    assert sha256(original).hexdigest() == FIRST
    text = original.decode()
    kind = KINDS[route]
    extra = dict(targetKind=kind, route=route)
    bundle = dict(Bass.Cadence.Authority.scoped_load(Bass.Cadence.Authority.AUTHORITY), raw=raw)
    at = 16 + 126 * 8192 + (0x8987 & 8191)
    lives = Bass.W.address(bundle, 'NumberofLives')
    assert raw[at:at+3] == b'\xee' + lives.to_bytes(2, 'little')
    binding = '\n'.join(f'C.{name}={Bass.value(val)}' for name, val in extra.items())
    binding += '\nC.ram.XgJumpUsed=' + str(Bass.W.address(bundle, 'XgJumpUsed'))
    binding += '\nC.hooks.LifeCredit=' + Bass.value(dict(pc=0x8987, tag=254, offset=at-16, hex=raw[at:at+8].hex()))

    def edit(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)

    edit('local choose=(function()', binding + '\nlocal choose=(function()')
    edit('return function(c)\n if BASS_EARNED then return{}end', SECOND + "\nreturn function(c)\n if BASS_FIRST_COMPLETE then\n  if not route.second then route.second=true;change(c,'second-travel')end\n  return second(c)\n end\n if BASS_EARNED then return{}end")
    edit('local expected={0}', 'local expected={0,C.targetKind}')
    edit('physical<=6900', 'physical<=4200')
    edit(' updates=updates+1\n local s=state()', " updates=updates+1\n local s=state()\n if updates%300==0 then print(string.format('BASS_PROGRESS Main=%d X=%d Y=%d status=%d',updates,s.x,s.y,s.status))end")
    edit("owned=r('InvOwnedLo',9)", "owned=r('InvOwnedLo',9),ownedHi=r('InvOwnedHi',9)")
    edit("assert(heads['0'] and a.owner==9 and a.stamp==0,'Bass Mushroom comes from a real head bump and owner 9');q.birth={actor=a,player=s}", "assert(heads[tostring(a.kind)] and a.owner==9 and (a.kind==0 and a.stamp==0 or a.kind==1 and a.stamp>=1 and a.stamp<=8 or a.kind>=2 and a.stamp==252),'Actual authored Bass head bump and owner metadata');q.birth={actor=a,player=s}")
    edit(" local q=checks['0']\n if q.collect then BASS_EARNED=true end", " local q=checks['0']\n if q.collect then BASS_EARNED=true end\n if q.after then BASS_FIRST_COMPLETE=true end\n local target=checks[tostring(C.targetKind)]\n if target.collect then BASS_TARGET_COLLECTED=true end\n if target.collect and not target.grant and C.targetKind==2 and s.star>0 and score()>=target.collect.score_before+1000 then target.grant=s end")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')", "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Earned Star and score persist during movement')")
    edit("else assert(s.status==1 and s.growth==0 and s.owned&1~=0,'Earned Bass tier persists during movement') end", "else assert(s.status==1 and s.growth==0 and s.owned&1~=0,'Earned Bass tier persists during movement');if kind==1 and score()<q.collect.score_before+1000 then return end end")
    edit("  assert(a.state&128~=0 and p.before.status==0 and s.owned&1~=0 and s.growth>0 and r('GuestPowerupTarget')==1,'Mature Bass Mushroom starts original growth');return", """  if a.kind==0 then
   assert(a.state&128~=0 and p.before.status==0 and s.owned&1~=0 and s.growth>0 and r('GuestPowerupTarget')==1,'Mature Bass Mushroom starts original growth');return
  end
  local bit=1<<a.stamp
  local before=p.before.owned+(p.before.ownedHi<<8)
  local after=s.owned+(s.ownedHi<<8)
  assert(a.state&128~=0 and p.before.status==1 and s.status==1 and before&bit==0 and after&bit~=0,'Real authored Flower grants its revealed Bass upgrade')""")
    edit(" q.grant=s\nend", " if a.kind~=2 then q.grant=s end\nend")
    text += "\nprint('BASS_REPLAY_READY')\n"
    Bass.LuaRuntime().compile(text)
    return text.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', choices=tuple(KINDS), required=True)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = Bass.ROM.read_bytes()
    program = controller(raw, args.route)
    digest = sha256(program).hexdigest()
    if not args.run:
        print('BASS STOCK SOURCE ' + json.dumps(dict(route=args.route, script_SHA256=digest)), flush=True)
        return 0
    guard = Bass.Cadence.check(Bass.ROM)
    assert guard['ROM_sha256'] == Bass.PIN and not guard['matching_patch_files']
    target, script = Bass.OUT/'candidate.nes', Bass.OUT/'controller.lua'
    assert set(Bass.OUT.iterdir()) == {target, script} and target.read_bytes() == raw
    with Bass.Stock.Host.Shared.preserve_script(script, target, raw) as stage:
        stage(program)
        result = Bass.Cadence.run(script, Bass.ROM, Bass.OUT/'capture', Bass.PIN, 165)
    assert result['script_SHA256'] == digest and result['outputs_written'] == 0 and not result['images']
    assert Bass.Cadence.check(Bass.ROM) == guard
    print('BASS STOCK NATIVE ' + json.dumps(result, separators=(',', ':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
