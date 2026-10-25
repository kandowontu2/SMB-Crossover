"""Freeze existing successful controls plus explicit native combat attempts."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
ARCHIVE=Path('C:/Users/kando/Videos/SMB Crossover Archive')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    sources={
        'baseline':ARCHIVE/'2026-10-24-matrix-oi/policies-v1/policy.lua',
        'scrooge':ARCHIVE/'2026-10-24-controllers-og/source-policies-v1/policy.lua',
        'simon':ARCHIVE/'2026-10-24-controllers-og/simon-combat-policy-v1/policy.lua',
        'native':ARCHIVE/'2026-10-24-native-controls-ok/policy-v1/policy.lua',
        'darkwing':ARCHIVE/'2026-10-24-native-controls-ok/darkwing-recovery-policy-v5/policy.lua',
    }
    text={n:p.read_text()for n,p in sources.items()}
    assert all('dofile('not in t and 'emu.write('not in t for t in text.values())
    nav=ROOT/'tools/playthroughs/mario_luigi_scrooge_nav.lua';mario=ROOT/'tools/playthroughs/mario_luigi_scrooge_policy.lua'
    motion=mario.read_text();anchor="local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n"
    include="local travel=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_nav.lua'))"
    assert motion.count(anchor)==motion.count(include)==1
    motion=motion.replace(anchor,'').replace(include,'local travel=(function()\n'+nav.read_text()+'\nend)()')
    text['mario']=motion
    final='-- Controller-only discovery. No emulated memory, equipment or physics writes.\n'
    for n,t in text.items():final+='local '+n+'=(function()\n'+t+'\nend)()\n'
    final+='''
local lateGap='approach';local holdA=0
return function(c)
 if c.char==12 and c.r('DarkwingVariant')~=0 then return darkwing(c)end
 if c.char==0 or c.char==8 then return mario(c)end
 if c.char==12 and c.r('DarkwingVariant')==0 then return scrooge(c)end
 if c.char==5 and c.r('Cv3Variant')==0 then return simon(c)end
 if c.char==2 or c.char==3 or c.char==10 or c.char==14 or(c.char==4 and c.r('Z2Variant')==0)or(c.char==9 and c.r('RlVariant')==0)then
  local b=native(c)
  local e=c.enemy()
  if c.char==3 and c.grounded and e and math.abs(e.dx)<120 and math.abs(e.y-c.y)<42 then
   local face=e.dx<0 and 2 or 1
   if c.r('PlayerFacingDir')~=face then return{left=face==2,right=face==1}end
   return{down=true,b=c.r('FrameCounter')%12<2}
  end
  return b
 end
 local b=baseline(c)
 if c.world==0 and c.level==0 and(c.char==17 or(c.char==5 and c.r('Cv3Variant')==3))and c.x>=2380 and c.x<2512 then
  if lateGap=='approach'and c.x>=2410 and c.y<=100 then lateGap='land'end
  if lateGap=='land'then
   b={right=c.x<2412,left=c.x>2420}
   if c.grounded and c.y<=112 then lateGap='jump';holdA=6;b={right=true,a=true}end
   return b
  elseif lateGap=='jump'then
   b.right=true;b.left=false;b.b=c.char==17;b.a=holdA>0 or c.vy>=128
   if holdA>0 then holdA=holdA-1 end
  end
 end
 if c.char==5 and c.r('Cv3Variant')>0 and c.grounded and b.a then
  b.b=false
  if c.r('Cv3AttackAge')~=0 then b.a=false;b.right=false;b.left=false end
 end
 return b
end
'''
    policy=a.output/'policy.lua';policy.write_text(final)
    q=dict(prepared=True,memory_writes=False,game_changes=False,source_hashes={str(p):sha(p)for p in [*sources.values(),nav,mario]},
        policy_sha256=sha(policy),driver_sha256=sha(Path(__file__)),
        scope='Frozen existing Mike/Vic/Meta, Scrooge, Simon and Mario/Luigi controllers; native grounded shooter/Ryu/crate attempts; crouch Contra combat; wait for CV3 attack before grounded A; land before late SMB3/Alucard gap. This grants no abilities, equipment, health, terrain or invincibility. Every route must still discover, independently replay, retain failures, and pass unchanged graphics/scroll/death criteria.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
