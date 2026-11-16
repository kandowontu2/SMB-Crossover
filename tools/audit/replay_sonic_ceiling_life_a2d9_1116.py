"""New stricta2 root-native complete-ceiling1UP observer, original controls only."""
from functools import lru_cache
from pathlib import Path
import inspect
import current_sonic_ceiling_complete_a2d9_1116 as F
import sonic_ceiling_life_right_policy_a2d9_1116 as Policy
import replay_sonic_hidden_life_f7c9_1116 as Frozen

J=F
R,ROM,H,PIN=F.R,F.ROM,F.H,F.PIN
F_SHA='13b1050ecd45ad30d0f6f51f385d3eda6389d9e6d1bfdf11fa302557103571ff'
POLICY_SHA='88a4e2f5a3ac55bec9c5b18fc87e67d81385c953d7ff443f0654dbfceebb46a8'
FROZEN_SHA='3d8bd46b6e35507986dc1ee1180e597b3663a4f6cc76be56320bbdd1691e1ad5'


@lru_cache(maxsize=2)
def bindings(raw,form='sonic'):
    assert H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    ns=dict(Frozen.__dict__,F=F,F_SHA=F_SHA,Policy=Policy,POLICY_SHA=POLICY_SHA)
    exec(compile(inspect.getsource(Frozen.bindings),'<strictnewa2 native config>','exec'),ns)
    q=ns['bindings'](raw,form);q=dict(q,hooks=dict(q['hooks']));q.pop('actual_f7_CPU')
    actual=F.bindings(raw)
    for name,pc,size in(('CeilingStore',0xd08f,11),('TimerCancel',0xd371,11)):
        data=actual['loaded'](pc)[:size]
        if name=='TimerCancel':assert data==F.C.TIMER
        q['hooks'][name]=dict(pc=pc,tag=2,offset=2*8192+(pc&8191),hex=data.hex())
    q.update(actual_a2_CPU=True,sustained_ceiling_timer_cancel=True)
    return q


def body():
    s=Frozen.BODY
    edits=(
        ("'Exact owningf7c9'", "'Exact owninga2d9'"),
        ('local target,credit,lifePending=nil,nil,nil;local lastphase=nil', 'local target,credit,lifePending=nil,nil,nil;local lastphase=nil;local posthead={};local headJump=nil'),
        ('head=heads,births=births,collected=collections,credit=credit,', 'first8_posthead_original_returns=posthead,head=heads,births=births,collected=collections,credit=credit,'),
        ('original_emergence_state6_allowed=true,no_fully_mature128_claim=true,', 'original_state6_admission_preserved=true,fully_emerged_at_collection=target and target.item.state&128~=0,'),
        ("  finish(true,'Actual ceiling/head, early-emergence physical1UP, delayedINC and25 returned original workers');return", "  assert(#posthead==8 and counts.TimerCancel_entries==counts.TimerCancel_returns,'Complete ceiling/timer observer acknowledgments');finish(true,'Sustained ceiling/head, physical1UP, delayedINC and25 returned original workers');return"),
        ("elseif p.name=='OriginalFrame'then if c['cpu.ps']&1~=0 then motor=motor+1 else count('OriginalFrame_C0')end", """elseif p.name=='OriginalFrame'then
  if c['cpu.ps']&1~=0 then motor=motor+1 else count('OriginalFrame_C0')end
  if #heads>0 then local s=state()
   if policy.lastJump==headJump then assert(s.vy>=0,'No unrequested postceiling rise')end
   if #posthead<8 then
    assert(w(0xc058)==0 and s.vy>=0 and s.source_flags&8==0,'Original Suppress/gravity after nativeceiling')
    posthead[#posthead+1]={state=s,sourceY={w(0xc073),w(0xc074),w(0xc075)},JumpTimer=w(0xc058),HeadPending=w(0xc122),requested=pad,lastJump=policy.lastJump,hold=policy.hold,C=c['cpu.ps']&1}
   end
  end
 elseif p.name=='TimerCancel'then assert(w(0xc058)==0 and w(0xc122)==1 and c['cpu.a']==1,'Actual timer helper completed')"""),
        (" if name=='Selector'or name=='Helper'then count(name);return end", " if name=='Selector'or name=='Helper'or name=='CeilingStore'then count(name);return end"),
        ("  heads[1]={tile=96,player=s,PC=h.pc,SP=c['cpu.sp']}", "  assert(w(0xc058)==0,'Ceiling canceled original holdtimer');headJump=policy.lastJump;heads[1]={tile=96,player=s,PC=h.pc,SP=c['cpu.sp']}")
    )
    for a,b in edits:assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
    return s


@lru_cache(maxsize=2)
def controller(raw,form='sonic'):
    q=bindings(raw,form);text=body().replace('POLICY_TEXT',Policy.text());assert 'POLICY_TEXT'not in text
    return'local SONIC_CONFIG='+Frozen.value(q)+'\n'+text
