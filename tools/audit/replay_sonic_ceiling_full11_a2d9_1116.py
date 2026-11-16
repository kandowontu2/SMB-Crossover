"""Stricta2 root-native full1-1/25 grounded1-2, retained ordinary stage policy."""
from functools import lru_cache
from pathlib import Path
import current_sonic_ceiling_complete_a2d9_1116 as F
import replay_sonic_ceiling_life_a2d9_1116 as Life
import check_sonic_hidden_full11_f7c9_1116 as Stage

J=F
R,ROM,H,PIN=F.R,F.ROM,F.H,F.PIN
LIFE_SHA='9b2cfa820588d02bb4a40b321ad2fe06bcc5b716b36f2472df2bc0f3bae07ee3'
STAGE_SHA='3e19563d65124a443ec4f13117afa4d6bdb41e9b02ae04215e17ae5ac1909a36'


@lru_cache(maxsize=2)
def bindings(raw,form='sonic'):
    assert H(Path(Life.__file__).read_bytes())==LIFE_SHA and H(Path(Stage.__file__).read_bytes())==STAGE_SHA
    old=Life.bindings(raw,form);q=dict(old,hooks={n:h for n,h in old['hooks'].items()if n in('GameLoop','SonicHostMain','OriginalFrame','CeilingStore','TimerCancel')})
    q.update(route='full11',source_policy_SHA256=H(Stage.control().encode()),retained_stage_SHA256=Stage.Sensors.STAGE_SHA)
    return q


def body():
    s=Life.body().replace("local policy=P.new('life')",'local policy=P.new()')
    s=s.replace('local target,credit,lifePending=nil,nil,nil;local lastphase=nil;local posthead={};local headJump=nil',
        'local target,credit,lifePending=nil,nil,nil;local lastphase=nil;local posthead={};local headJump=nil;local flag,castle,entrance=nil,nil,nil;local grounded,lastMotor=0,0')
    s=s.replace("status=r('PlayerStatus'),lives=", "world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaAddrsLOffset'),area_type=r('AreaType'),status=r('PlayerStatus'),lives=")
    s=s.replace('first8_posthead_original_returns=posthead,head=heads,', 'full_1_1=flag~=nil and castle~=nil and entrance~=nil,native_flag=flag,native_castle=castle,native_entrance=entrance,grounded_1_2_original_updates=grounded,first8_posthead_original_returns=posthead,head=heads,')
    s=s.replace('no_game_actor_inventory_health_seeds=true,no_fullstage_or_fidelity_or_cadence_claim=true', 'no_game_actor_inventory_health_seeds=true,no_fidelity_or_cadence_claim=true')
    lo=s.index('local function afterMain()');hi=s.index('local function returned(',lo)
    replacement=r'''local function afterMain()
 if not game then return end;updates=updates+1;local s=state();local progressed=motor>lastMotor;lastMotor=motor
 assert(identity()and s.engine~=11 and s.lives==2 and s.world==0 and s.level<=1,'Living genuine Sonic fullstage identity')
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'No cheats');headers();assert(updates<5500,'Bounded fullstage')
 if s.level==0 and s.engine==4 and s.x>=3000 and not flag then flag=s end
 if s.level==0 and s.engine==5 and s.x>=3000 and not castle then castle=s end
 if s.level==1 and s.engine==7 and not entrance then entrance=s end
 local active=r('OperMode')==1 and r('OperMode_Task')==3 and s.engine==8
 if active and s.level==1 then
  assert(flag and castle and entrance and s.area==0 and s.area_type==2,'Native flag/castle/entrance before underground1-2')
  if s.native_yhigh==1 and s.y==176 and s.state==0 and s.source_flags&8~=0 then if progressed then grounded=grounded+1 end else grounded=0 end
  pad=0
  if grounded>=25 then
   assert(counts.OriginalFrame_entries==counts.OriginalFrame_returns and counts.SonicHostMain_entries==counts.SonicHostMain_returns,'Balanced original and owning public workers')
   assert((counts.TimerCancel_entries or 0)==(counts.TimerCancel_returns or 0),'Balanced actual ceiling helper')
   finish(true,'Full1-1 flag/castle/entrance and25 living grounded original updates in1-2');return
  end
 elseif active then assert(s.area==5 and s.frame_status==0,'Actual1-1 original actor');pad=policy:decide(s)
 else pad=0 end
 bounded(tail,{state=s,pad=pad},8)
end
'''
    return s[:lo]+replacement+s[hi:]


@lru_cache(maxsize=2)
def controller(raw,form='sonic'):
    q=bindings(raw,form);s=body().replace('POLICY_TEXT',Stage.control());assert 'POLICY_TEXT'not in s
    return'local SONIC_CONFIG='+Life.Frozen.value(q)+'\n'+s
