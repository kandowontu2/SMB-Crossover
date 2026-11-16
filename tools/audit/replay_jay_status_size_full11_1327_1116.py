"""Strict1327 ordinary full-stage regression using retained control functions."""
from functools import lru_cache
from pathlib import Path
import ast,json
import replay_jay_status_size_sl_1327_1116 as SL

J=SL.J
SCRIPT='tools/playthroughs/jay_scroll_stdout_1111.lua'
SCRIPT_SHA='3491acebcc4d9491063857456cd45a73e9c4f129a0abb4725edd59bd4c66d921'
STAIR='tools/audit/replay_jay_steve_regression_1111.py'
STAIR_SHA='85d27f71edf285cf03707d79a7440891b11754a64e541f71da7e78999fffcb1d'


def policy_text():
    old=(J.R/SCRIPT).read_text();assert J.H((J.R/SCRIPT).read_bytes())==SCRIPT_SHA
    path=J.R/STAIR;assert J.H(path.read_bytes())==STAIR_SHA
    node=next(n.value for n in ast.parse(path.read_text()).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FINAL_STAIR'for t in n.targets))
    stair=ast.literal_eval(node)
    old=old[old.index('local function enemyAhead('):old.index("emu.addEventCallback(guard('frame'")]
    line=' local grounded=ram(2,donorFlags-0xc000)&4==0\n';assert old.count(line)==1;old=old.replace(line,line+stair)
    start=r'''
local Opening=(function()
OPENING_TEXT
end)()
local P={};P.__index=P
local current,actors,entries,bits,phase={}, {},0,0,'first'
local donorFlags=49170
local late={step=1,hold=0,furthest=0,advanced=0}
local waypoints={{1082,1104},{1360,1376},{2428,2448},{2560},{2816},{3130}}
local flagReached,castleReached=false,false
local jumps,stairTrace={},{}
local function quote(s)return '"'..s..'"'end
local function read(at)
 if at==0x0f then return current.engine elseif at==0x761 then return current.level elseif at==0x753 then return current.area_type end
 for i=0,5 do local a=actors[i+1]or{}
  if at==0x10+i then return a.flag or 0 elseif at==0x17+i then return a.id or 0
  elseif at==0x5d+i then return(a.x or 0)//256 elseif at==0x76+i then return(a.x or 0)&255
  elseif at==0xbe+i then return a.y or 0 elseif at==0x1e+i then return a.state or 0 end
 end
 error('Unbound retained control read '..at)
end
local function ram(bank,at)assert(bank==2 and at==0x12);return current.source_flags end
local function finish(ok,why)assert(ok,why)end
'''.replace('OPENING_TEXT',SL.Frozen.Frozen.V3.text())
    end=r'''
function P.new(kind)assert(kind=='full11');return setmetatable({opening=Opening.new('star'),phase='opening'},P)end
function P:collect(kind)end
function P:decide(s,aa)
 current=s;actors={};for _,a in ipairs(aa)do actors[a.slot+1]=a end;entries=s.motor
 if self.phase~='late'then
  local pad=self.opening:decide(s,aa);self.phase=self.opening.phase
  if self.phase~='gap1-approach'then return pad end
  self.phase='late';phase='late';late.advanced=entries;late.furthest=s.x
 end
 lateControls(s.x,s.y)
 return bits
end
return P
'''
    return start+old+end


def body():
    s=SL.Frozen.Frozen.BODY
    start=s.index('local function afterMain()');end=s.index('local function returned(',start)
    after=r'''local function afterMain()
 if not game then return end
 updates=updates+1;local s=state();local aa={}
 assert(identity()and s.hp>0 and s.engine~=11 and s.lives==2,'Living full-stage Jay with both lives')
 assert(r('WorldNumber')==0 and(r('LevelNumber')==0 or r('LevelNumber')==1)and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Full1-1/1-2 no cheats')
 assert(updates<6000,'Finite full-stage route')
 for bank=2,3 do local h={};for i=0x1fe0,0x1fef do h[#h+1]=string.format('%02x',w(bank,i))end;assert(table.concat(h)==C.cookie,'Owning full-stage headers')end
 if s.level==0 and s.engine==4 and s.x>=3140 and not milestones.flag then milestones.flag={Main=updates,motor=motor,state=s}end
 if s.level==0 and s.engine==5 and s.x>=3160 and not milestones.castle then assert(milestones.flag,'Flag before castle');milestones.castle={Main=updates,motor=motor,state=s}end
 if s.level==1 and s.engine==8 and s.area_type==2 and s.x==40 and s.y==176 and s.native_yhigh==1 and s.native_state==0 and s.native_vy==0 then
  if not nextarea then assert(milestones.flag and milestones.castle,'Full flag/castle before next entrance');nextarea={Main=updates,motor=motor,state=s}end
  if motor>=nextarea.motor+25 then
   credit={flag=milestones.flag,castle=milestones.castle,entrance=nextarea,tail=state()}
   assert((counts.JayIntegrate_entries or 0)==(counts.JayIntegrate_returns or 0),'Balanced full-stage workers')
   finish(true,'Full1-1 flag/castle/1-2 entrance and25 living grounded worker returns');return
  end
 end
 for i=0,5 do local a=actor(i);if a.flag~=0 then aa[#aa+1]=a end end
 local bits=nextarea and 0 or policy:decide(s,aa);assert(type(bits)=='number'and bits>=0 and bits<=255);pad=bits
 if policy.phase~=lastphase then bounded(changes,{Main=updates,motor=motor,phase=policy.phase,x=s.x,y=s.y},8);lastphase=policy.phase end
 bounded(tail,{state=s,phase=policy.phase,pad=pad},8)
end
'''
    s=s[:start]+after+s[end:]
    s=s.replace('local music64=0','local music64=0\nlocal milestones,nextarea={},nil')
    s=s.replace('head=heads,births=births,','milestones=milestones,entrance=nextarea,head=heads,births=births,')
    a="if name=='PlayerHeadCollision'then\n  local s=state();local left="
    assert s.count(a)==1;s=s.replace(a,"if name=='PlayerHeadCollision'then\n  if C.kind=='full11'then return end\n  local s=state();local left=")
    a="elseif p.name=='HandlePowerUpCollision'and p.actor.flag~=0"
    assert s.count(a)==1;s=s.replace(a,"elseif p.name=='HandlePowerUpCollision'and C.kind~='full11'and p.actor.flag~=0")
    a="hp=r('JnHealth'),maximum=";assert s.count(a)==1;s=s.replace(a,"level=r('LevelNumber'),area_type=r('AreaType'),area_pointer=r('AreaPointer'),size=r('PlayerSize'),hp=r('JnHealth'),maximum=")
    s=s.replace('no_fullstage_or_cadence_claim=true','fullstage_regression=true,no_cadence_claim=true')
    return s.replace('POLICY_TEXT',policy_text())


@lru_cache(maxsize=1)
def bindings(raw,kind='full11'):
    assert kind=='full11'and J.H(raw)==J.PIN
    q=dict(SL.bindings(raw,'star'));q['ram']=dict(q['ram'])
    for name in('AreaType','AreaPointer','PlayerSize'):q['ram'][name]=J.W.address(J.bindings(raw)['bundle'],name)
    q.update(kind='full11',source_policy_SHA256=J.H(policy_text().encode()),retained_late_controller_SHA256=SCRIPT_SHA,
        retained_stair_control_SHA256=STAIR_SHA,retained_opening_policy_SHA256=J.H(SL.Frozen.Frozen.V3.text().encode()))
    return q


@lru_cache(maxsize=1)
def controller(raw,kind='full11'):
    q=bindings(raw,kind)
    def value(v):
        if isinstance(v,dict):return'{'+','.join('['+json.dumps(k)+']='+value(x)for k,x in sorted(v.items()))+'}'
        if isinstance(v,list):return'{'+','.join(value(x)for x in v)+'}'
        if isinstance(v,bool):return'true'if v else'false'
        if v is None:return'nil'
        return json.dumps(v,separators=(',',':'))
    return'local JAY_CONFIG='+value(q)+'\n'+body()
