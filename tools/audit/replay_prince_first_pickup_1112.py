"""Explore Prince's first authored pickup using controller input only."""
import json
from pathlib import Path
from replay_prince_koopa_1111 import PUBLISHED, NIGHTLY, R
from run_stdout_mesen_1110 import run, digest

PIN = '464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0'
OUTPUT = R/'build/prince-first-pickup-1112'


def main():
    assert digest(NIGHTLY) == PIN
    source = PUBLISHED.read_text()
    source = source.replace('a726021676a00802119275ac7f48cce7', 'a72602f65bd78bf89874939486b6742f')
    source = source.replace('emu.setInput({right=pad&1~=0,', 'emu.setInput({right=pad&1~=0,left=pad&2~=0,')
    begin, end = source.index('local function tick()'), source.index('local function frames(count)')
    tick = '''
local itemSeen=false
local minimumY=255
local function tick()
  if commits==lastCommit then return end
  lastCommit=commits
  local s=state()
  assert(s.lives==2 and s.hp>0,'Prince survives pickup approach')
  assert(hexHeader(2)==cookie and hexHeader(3)==cookie,'Current Prince headers')
  minimumY=math.min(minimumY,s.y)
  if read(0x15)~=0 and read(0x1c)==0x2e then itemSeen=true end
  if s.hp~=previousHP then
    injuries[#injuries+1]={from=previousHP,to=s.hp,state=s}
    previousHP=s.hp
  end
  local age=commits-changedAt
  if progress=='settle-start' and age>=4 then
    switch('pickup-approach',1)
  elseif progress=='pickup-approach' then
    local enemy=enemyNear(s.x)
    if enemy and enemy.gap>=115 and enemy.gap<=136 and s.action==1 and s.mode==1
      and s.pose>=6 and s.pose<14 and s.lock==0 and s.ground==0 then
      switch('pickup-evade',129)
    end
  elseif progress=='pickup-evade' then
    if s.action==4 then pad=1 end
    if age>=16 and s.action==1 and s.mode==1 and floor(s) then
      switch('pickup-runout',1)
    end
  elseif progress=='pickup-runout' and s.x>=400 then
    switch('pickup-backtrack',2)
  elseif progress=='pickup-backtrack' and s.action==1 and s.ground==0 and s.facing==0 and s.x<=375 then
    switch('pickup-settle',0)
  elseif progress=='pickup-settle' and s.action==0 and s.ground==0 and s.pose==15 and s.mode==0 and s.lock==0 then
    switch('pickup-jump',8)
  elseif progress=='pickup-jump' then
    if age>8 then pad=0 end
    if age>100 then
      late.pickup={spawned=itemSeen,minimumY=minimumY,sword=source(0x6ee)}
      finish(itemSeen,'First authored powerup spawn probe')
    end
  end
  assert(commits<1000,'Bounded first pickup approach')
end

'''
    source = source[:begin]+tick+source[end:]
    OUTPUT.mkdir(exist_ok=True)
    script = OUTPUT/'controller.lua'
    script.write_text(source, encoding='utf-8', newline='\n')
    result = run(script,NIGHTLY,OUTPUT/'capture',PIN,60)
    print(json.dumps({k:v for k,v in result.items() if k not in ('images','capture_preflight')}),flush=True)
    assert result['passed'],result['receipt']['reason']


if __name__ == '__main__':
    main()
