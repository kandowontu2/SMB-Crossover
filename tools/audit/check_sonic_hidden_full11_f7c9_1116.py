"""Retained ordinary stage policy, actual f7 Sonic/Super full1-1 regression."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter,deque
import argparse,json
import current_sonic_hidden_heads_f7c9_1116 as F
import sonic_natural_stock_policy_1327_1116 as Sensors
from check_ff_stdout_controller_source_1110 import LuaRuntime


def control():
    path=F.R/'tools/playthroughs/sonic_original_full_stage_stdout_1110.lua'
    assert F.H(path.read_bytes())==Sensors.STAGE_SHA
    old=path.read_text();sensors=old[old.index('local function solid('):old.index('local function drive()')]
    return '''local P={};P.__index=P;local r=SONIC_READ
local function read(at)return SONIC_MEMORY(at)end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
'''+sensors+'''
function P.new()return setmetatable({clock=0,lastJump=-100,jumps=0},P)end
function P:decide(s)
 local bits=self.clock>3 and 1 or 0
 if s.state==0 and s.source_flags&8~=0 and self.clock-self.lastJump>24 then
  local why=jumpReason(s)
  if why then self.lastJump=self.clock;self.jumps=self.jumps+1;assert(self.jumps<=64,'Retained route jump bound')end
 end
 if self.clock-self.lastJump<20 then bits=bits|128 end
 self.clock=self.clock+1;assert(self.clock<=3500,'Retained active-update bound');return bits
end
return P
'''


def run(raw,form='sonic',limit=5500):
    q=F.bindings(raw);m,cold=F.cold(raw,form);N=F.N;counts=Counter();objects=[];events={};tail=deque(maxlen=8)
    rt=LuaRuntime();rt.globals().SONIC_READ=lambda n,i=0:N.get(m,n,i);rt.globals().SONIC_MEMORY=lambda at:m[at];policy=rt.execute(control()).new()
    complete=False;fault=None;grounded=0;ctx={};points={(q['hooks']['GameLoop']['tag'],q['hooks']['GameLoop']['PC']):'Main',(3,0xbbb0):'OriginalFrame'}
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def state():
        r=lambda n:N.get(m,n)
        return dict(x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),yhigh=r('Player_Y_HighPos'),
            state=r('Player_State'),source_flags=m.ram[2][0x30],frame_status=m.ram[2][0x116],ready=m.ram[2][0x119],
            world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaAddrsLOffset'),area_type=r('AreaType'),engine=r('GameEngineSubroutine'),
            lives=r('NumberofLives'),rings=m.ram[2][0x340],status=r('PlayerStatus'),Main=counts['Main_returns'],motor=counts['accepted_original'])
    def after_main():
        nonlocal complete,grounded
        s=state();assert N.get(m,'SelectedCharacter')==43 and m[0x5ffe]==F.FORMS[form][0]
        assert s['lives']==2 and s['engine']!=11 and s['world']==0 and s['level']in(0,1),('Actual living current stage route',s)
        assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
        if s['level']==0 and s['engine']==4 and s['x']>=3000:events.setdefault('flag',s)
        if s['level']==0 and s['engine']==5 and s['x']>=3000:events.setdefault('castle',s)
        if s['level']==1 and s['engine']==7:events.setdefault('entrance',s)
        active=N.get(m,'OperMode')==1 and N.get(m,'OperMode_Task')==3 and s['engine']==8
        if active and s['level']==1:
            assert all(n in events for n in('flag','castle','entrance'))and s['area']==0 and s['area_type']==2
            if s['yhigh']==1 and s['y']==176 and s['state']==0 and s['source_flags']&8:grounded+=1
            else:grounded=0
            m.controller_pad=0
            if grounded>=25:complete=True
        elif active:
            assert s['area']==5 and s['frame_status']==0
            m.controller_pad=policy.decide(policy,rt.table_from(s))
        else:m.controller_pad=0
        tail.append(dict(state=s,pad=m.controller_pad))
        assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(F.COOKIE,)*2
    base=N.NesMPU
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pending=[];objects.append(self)
        def settle(self):
            while self.pending and(self.pc,self.sp,tag(self.pc))==self.pending[-1][1]:
                name,_=self.pending.pop();counts[name+'_returns']+=1
                if name=='OriginalFrame':counts['accepted_original'if self.p&1 else'rejected_original']+=1
                else:after_main()
        def step(self):
            self.settle();t=tag(self.pc);name=points.get((t,self.pc))
            if(t,self.pc)==(2,0xd344):counts['helper']+=1
            if name:
                counts[name+'_entries']+=1;sp=self.sp;pc=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
                self.pending.append((name,(pc,(sp+2)&255,tag(pc))))
            ctx.update(PC=self.pc,tag=t,SP=self.sp)
            return super().step()
    try:
        with patch.object(N,'NesMPU',CPU):
            for _ in range(limit):
                F.Frames.frame(m,whole_pass=True)
                for c in objects:c.settle();assert not c.pending
                objects.clear()
                if complete:break
    except Exception as e:fault=dict(error=repr(e),context=dict(ctx),state=state())
    out=dict(passed=complete and fault is None,ROM_SHA256=F.PIN,form=form,cold=cold,fault=fault,counts=dict(counts),
        events=events,grounded_1_2_updates=grounded,jumps=policy.jumps,tail=list(tail),terminal=state(),
        retained_stage_control_SHA256=Sensors.STAGE_SHA,policy_SHA256=F.H(control().encode()),source_SHA256=F.H(Path(__file__).read_bytes()),
        no_new_physics_helpers_or_gameplay_seeds=True,native=False,outputs=0)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Stage source regression attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(F.load_current_image(),a.form)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
