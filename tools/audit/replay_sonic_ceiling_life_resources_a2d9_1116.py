"""Same frozena2 controls/game gates; retain actual pre1UP source resources."""
from functools import lru_cache
from pathlib import Path
import replay_sonic_ceiling_life_a2d9_1116 as Frozen

F=J=Frozen.F
R,ROM,H,PIN=F.R,F.ROM,F.H,F.PIN
FROZEN_SHA='9b2cfa820588d02bb4a40b321ad2fe06bcc5b716b36f2472df2bc0f3bae07ee3'
RESOURCE_FUNCTION="local function sameResources(a,b)return a.rings==b.rings and a.ringLives==b.ringLives and a.hurt==b.hurt and a.sourceStar==b.sourceStar and a.status==b.status end"


@lru_cache(maxsize=2)
def bindings(raw,form='sonic'):
    assert H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    return dict(Frozen.bindings(raw,form),resource_contract='Actual pre-head and pre-collector rings/ringLives/hurt/privateStar/status retained through nativecredit plus25; no fixed five-ring assumption')


def body():
    s=Frozen.body()
    edits=(('local posthead={};local headJump=nil','local posthead={};local headJump=nil;local preOneup=nil'),
        ('local function actor(i)',RESOURCE_FUNCTION+'\nlocal function actor(i)'),
        ('first8_posthead_original_returns=posthead,head=heads,','pre_oneup_resources=preOneup,first8_posthead_original_returns=posthead,head=heads,'),
        ("assert(target and s.rings==target.before.rings and s.rings==5 and s.ringLives==0 and s.hurt==0 and s.sourceStar==0 and s.status==0 and s.lives==3,'Rings and source resources retained')",
         "assert(target and credit and preOneup and sameResources(target.before,preOneup)and sameResources(target.after,preOneup)and sameResources(credit.before,preOneup)and sameResources(credit.state,preOneup)and sameResources(s,preOneup)and s.lives==3,'Actual pre1UP source resources retained')"),
        ("headJump=policy.lastJump;heads[1]=", "headJump=policy.lastJump;preOneup={rings=s.rings,ringLives=s.ringLives,hurt=s.hurt,sourceStar=s.sourceStar,status=s.status};heads[1]="))
    for a,b in edits:assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
    assert 's.rings==5'not in s
    return s


@lru_cache(maxsize=2)
def controller(raw,form='sonic'):
    q=bindings(raw,form);s=body().replace('POLICY_TEXT',Frozen.Policy.text());assert 'POLICY_TEXT'not in s
    return'local SONIC_CONFIG='+Frozen.Frozen.value(q)+'\n'+s
