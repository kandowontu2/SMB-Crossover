"""Explore Prince's first authored pickup using controller input only."""
import json
import argparse
from pathlib import Path
from replay_prince_koopa_1111 import PUBLISHED, NIGHTLY, R
from run_stdout_mesen_1110 import run, digest

PIN = '464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0'
OUTPUT = R/'build/prince-first-pickup-1112'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jump-mask', type=int, choices=(8, 9, 128, 136), default=8)
    parser.add_argument('--hold-updates', type=int, default=8)
    parser.add_argument('--face-right', action='store_true')
    parser.add_argument('--runout-x', type=int, default=400)
    parser.add_argument('--observe-updates', type=int, default=100)
    parser.add_argument('--top-b', action='store_true')
    args = parser.parse_args()
    assert 1 <= args.hold_updates <= 90
    assert 324 <= args.runout_x <= 400
    assert 100 <= args.observe_updates <= 400
    assert digest(NIGHTLY) == PIN
    source = PUBLISHED.read_text()
    source = source.replace('a726021676a00802119275ac7f48cce7', 'a72602f65bd78bf89874939486b6742f')
    source = source.replace('emu.setInput({right=pad&1~=0,', 'emu.setInput({right=pad&1~=0,left=pad&2~=0,')
    begin, end = source.index('local function tick()'), source.index('local function frames(count)')
    tick = '''
local itemSeen=false
local minimumY=255
local jumpTrace={}
local yWrites={}
emu.addMemoryCallback(guarded(function(address,value)
  if progress=='pickup-jump' and mapped(0xc611,2) and #yWrites<160 then
    local cpu=emu.getState()
    yWrites[#yWrites+1]={pc=cpu['cpu.pc'],value=value,old=source(0x611),
      phase=source(0xa6),pose=source(0x617),action=source(0x616)}
  end
end),emu.callbackType.write,0xc611)
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
    if age<=100 then
      jumpTrace[#jumpTrace+1]={age=age,x=s.x,y=s.y,action=s.action,pose=s.pose,
        phase=s.phase,foot=s.foot,rawY=source(0x611),lastY=source(0x8b),
        delta=source(0x88),origin=source(0x89),originHigh=source(0x8a),
        surface=source(0x7f)+256*source(0x80)}
    end
    if age>8 then pad=0 end
    if age>100 then
      late.pickup={spawned=itemSeen,minimumY=minimumY,sword=source(0x6ee),trace=jumpTrace,yWrites=yWrites}
      finish(itemSeen,'First authored powerup spawn probe')
    end
  end
  assert(commits<1000,'Bounded first pickup approach')
end

'''
    tick = tick.replace("switch('pickup-jump',8)",
                        "switch('pickup-jump',%d)" % args.jump_mask)
    if args.face_right:
        marker = "    switch('pickup-jump',%d)" % args.jump_mask
        tick = tick.replace(marker, """    switch('pickup-turn',1)
  elseif progress=='pickup-turn' then
    if s.facing==255 then pad=0 end
    if age>4 and s.facing==255 and s.action==0 and s.mode==0 and s.pose==15 and s.lock==0 then
      switch('pickup-jump',%d)
    end""" % args.jump_mask)
    tick = tick.replace('if age>8 then pad=0 end',
                        'if age>%d then pad=0 end' % args.hold_updates)
    tick = tick.replace('s.x>=400', 's.x>=%d' % args.runout_x)
    tick = tick.replace('s.x<=375', 's.x<=%d' % (args.runout_x-25))
    tick = tick.replace('age<=100', 'age<=%d' % args.observe_updates)
    tick = tick.replace('age>100', 'age>%d' % args.observe_updates)
    if args.top_b:
        assert args.observe_updates >= 180
        tick = tick.replace('if age>%d then pad=0 end' % args.hold_updates,
                            'if age>%d then pad=0 end\n    if age>=120 and age<140 then pad=64 end' % args.hold_updates)
    source = source[:begin]+tick+source[end:]
    OUTPUT.mkdir(exist_ok=True)
    script = OUTPUT/'controller.lua'
    script.write_text(source, encoding='utf-8', newline='\n')
    result = run(script,NIGHTLY,OUTPUT/'capture',PIN,60)
    pickup = result['receipt'].get('later_route', {}).get('pickup', {})
    trace = pickup.get('trace', [])
    pickup['trace'] = [s for i,s in enumerate(trace) if i == 0 or
        any(s[k] != trace[i-1][k] for k in ('rawY','origin','originHigh','delta','action'))]
    print(json.dumps(dict(passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],
                         script_SHA256=result['script_SHA256'],receipt=result['receipt'].get('later_route'),
                         reason=result['receipt']['reason'],terminal=result['receipt']['terminal'])),flush=True)
    assert result['passed'],result['receipt']['reason']


if __name__ == '__main__':
    main()
