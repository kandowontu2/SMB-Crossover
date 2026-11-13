"""Explore Prince's first authored pickup using controller input only."""
import json
import argparse
from pathlib import Path
from replay_prince_koopa_1111 import PUBLISHED, NIGHTLY, R
from run_stdout_mesen_1110 import run, digest

PIN = 'cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7'
OUTPUT = R/'build/prince-first-pickup-1112'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jump-mask', type=int, choices=(8, 9, 128, 136), default=8)
    parser.add_argument('--hold-updates', type=int, default=8)
    parser.add_argument('--face-right', action='store_true')
    parser.add_argument('--runout-x', type=int, default=400)
    parser.add_argument('--observe-updates', type=int, default=100)
    parser.add_argument('--top-b', action='store_true')
    parser.add_argument('--top-walk', action='store_true')
    parser.add_argument('--reach-candidate', action='store_true')
    parser.add_argument('--sword-candidate', action='store_true')
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--flower', action='store_true')
    parser.add_argument('--descent',type=int,choices=(0,4,5,68),default=0)
    args = parser.parse_args()
    if args.sword_candidate:
        args.reach_candidate=True
    if args.flower:
        args.collect=True
    assert 1 <= args.hold_updates <= 90
    assert 324 <= args.runout_x <= 400
    assert 100 <= args.observe_updates <= 400
    assert digest(NIGHTLY) == PIN
    rom, expected = NIGHTLY, PIN
    import prince_cold_packet_1111 as Packet
    image = NIGHTLY.read_bytes()
    Packet.extract(image)  # Authenticate the complete current cold packet.
    if args.reach_candidate:
        from prince_pickup_reach_1112 import transform
        image, _, layout = transform(image)
        if args.sword_candidate:
            from prince_sword_box_1112 import transform as sword_transform
            image, _, layout=sword_transform(image)
        OUTPUT.mkdir(exist_ok=True)
        rom = OUTPUT/'candidate.nes'
        rom.write_bytes(image)
        expected = digest(rom)
    cookie = image[Packet.COOKIE:Packet.COOKIE+16].hex()
    source = PUBLISHED.read_text()
    source = source.replace('a726021676a00802119275ac7f48cce7', cookie)
    source = source.replace('emu.setInput({right=pad&1~=0,', 'emu.setInput({right=pad&1~=0,left=pad&2~=0,')
    if args.flower:
        import replay_prince_native_flag_1111 as Full
        # Sword metadata compaction moves the native support publication by
        # five bytes; observe the actual STA rather than its former address.
        source=Full.controller(cookie,0xd746 if args.sword_candidate else 0xd74b,3115,True)
        if args.descent:
            source=source.replace('walkers[1].direction==2 and walkers[2].direction==2\n      and walkers[1].x<=848 and walkers[2].x<=848', 'walkers[1].direction==1 and walkers[2].direction==1\n      and walkers[1].x>=850 and walkers[2].x>=850')
            source=source.replace("switch('third-standing-jump',129,walkers)",f"switch('third-descent',{args.descent},walkers)")
            source=source.replace("  elseif progress=='third-standing-jump' and s.action==3 then", """  elseif progress=='third-descent' then
    late.descent=late.descent or {}
    if commits%5==0 and #late.descent<40 then late.descent[#late.descent+1]=s end
    if s.y>=174 and s.y<=178 and support(s) then switch('fourth-descent-run',1)
    elseif commits-changedAt>150 then finish(false,'Bounded original descent probe');return end
  elseif progress=='fourth-descent-run' and s.action==1 and s.mode==1 and s.lock==0 then
    switch('fourth-descent-evade',129)
  elseif progress=='fourth-descent-evade' then
    if s.action==4 then switch('fourth-descent-air',1) end
  elseif progress=='fourth-descent-air' and s.y>=174 and s.y<=178 and support(s) then
    switch('fourth-recovery',1)
  elseif progress=='third-standing-jump' and s.action==3 then""")
    begin, end = source.index('local function tick()'), source.index('local function frames(count)')
    original_tick=source[begin:end].replace('local function tick()', 'local function routeTick()',1)
    tick = '''
local itemSeen=false
local minimumY=255
local jumpTrace={}
local yWrites={}
local supportTrace={}
local headTrace={}
local headCalls=0
local headReturns={}
local headHits={}
local returnedHeads=0
local headLayouts={}
local pendingHead=nil
emu.addMemoryCallback(guarded(function()
  if read(0x6002)==38 and progress:sub(1,7)=='pickup-' then
    local s=state()
    if s.x>=230 and s.x<=400 then
      headCalls=headCalls+1
      local cpu=emu.getState()
      local sp=cpu['cpu.sp']
      local index=read(0x106)
      local layout=string.format('%d/%d/%d',read(0x759),index,read(0xe194+index))
      headLayouts[layout]=(headLayouts[layout] or 0)+1
      local ret=read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1
      pendingHead={x=s.x,y=s.y,dy=read(0x8e),action=s.action,pose=s.pose,phase=progress}
      if not headReturns[ret] then
        headReturns[ret]=true
        emu.addMemoryCallback(guarded(function()
          if pendingHead and read(0x6002)==38 then
            local row=pendingHead
            pendingHead=nil
            returnedHeads=returnedHeads+1
            row.tile=emu.getState()['cpu.a']
            row.lowY=read(7)
            if row.tile~=0 and #headHits<30 then headHits[#headHits+1]=row end
          end
        end),emu.callbackType.exec,ret)
      end
      local last=headTrace[#headTrace]
      local dy=read(0x8e)
      if #headTrace<100 and (not last or last.y~=s.y or last.dy~=dy or last.action~=s.action) then
        headTrace[#headTrace+1]={x=s.x,y=s.y,dy=dy,action=s.action,pose=s.pose,phase=progress}
      end
    end
  end
end),emu.callbackType.exec,0xf113)
for _,pc in ipairs({0xd6d1,0xd6da,0xd6fb,0xd6fe,0xd720,0xd739,0xd752}) do
  observe(pc,2,function()
    local age=commits-changedAt
    if progress=='pickup-jump' and age>=120 and age<=140 and #supportTrace<80 then
      local cpu=emu.getState()
      supportTrace[#supportTrace+1]={pc=pc,a=cpu['cpu.a'],p=cpu['cpu.ps'],
        age=age,state=state(),oldFoot=source(0x86),delta=source(0x88),
        queryX=source(0x1369,3)+256*source(0x136a,3),queryY=source(0x136b,3)}
    end
  end)
end
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
      late.pickup={spawned=itemSeen,minimumY=minimumY,sword=source(0x6ee),trace=jumpTrace,yWrites=yWrites,supportTrace=supportTrace,headCalls=headCalls,headTrace=headTrace,headHits=headHits,returnedHeads=returnedHeads,headLayouts=headLayouts}
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
    if args.top_walk:
        assert not args.top_b and args.observe_updates >= 280
        tick = tick.replace('if age>%d then pad=0 end' % args.hold_updates,
                            'if age>%d then pad=0 end\n    if age>=120 and age<148 then pad=1 end\n    if age>=220 and age<240 then pad=64 end' % args.hold_updates)
    if args.collect:
        tick=tick.replace('local itemSeen=false','local itemSeen=false\nlocal itemTrace={}\nlocal matureSeen=false')
        tick=tick.replace('\n  local age=commits-changedAt', '''
  if itemSeen and (commits%10==0 or read(0x75b)==1) and #itemTrace<80 then
    itemTrace[#itemTrace+1]={commit=commits,playerX=s.x,playerY=s.y,status=read(0x75b),
      flag=read(0x15),id=read(0x1c),kind=read(0x34),state=read(0x24),
      x=read(0x7b)+256*read(0x62),y=read(0xc3)}
  end
  if itemSeen and read(0x24)>=128 then matureSeen=true end
  if itemSeen and matureSeen and read(0x75b)==1 and read(0x15)==0 then
    late.collection={trace=itemTrace,mature=matureSeen,status=read(0x75b),sword=source(0x6ee)}
    finish(true,'Naturally emerged mushroom collected');return
  end
  local age=commits-changedAt''')
        tick=tick.replace("      finish(itemSeen,'First authored powerup spawn probe')", "      switch('pickup-collect',1)")
        tick=tick.replace("  assert(commits<1000,'Bounded first pickup approach')", """  if progress=='pickup-collect' then
    if s.x>=420 then pad=0 end
    if age>250 then
      late.collection={trace=itemTrace,mature=matureSeen,status=read(0x75b),sword=source(0x6ee)}
      finish(false,'Bounded natural mushroom collection');return
    end
  end
  assert(commits<1200,'Bounded first pickup approach')""")
    if args.flower:
        source=source.replace("switch('late-second-approach',1)","switch('flower-approach',1)")
        begin,end=source.index('local function tick()'),source.index('local function frames(count)')
        original_tick=source[begin:end].replace('local function tick()', 'local function routeTick()',1)
        tick=tick.replace('local itemSeen=false','local collected=false\nlocal flowerSeen=false\nlocal flowerTrace={}\nlocal itemSeen=false')
        tick=tick.replace('local itemSeen=false', '''local itemSeen=false
late.hpWrites={}
emu.addMemoryCallback(guarded(function(address,value)
  if read(0x6002)==38 and read(0x0f)==8 and value<source(0x6cf) and #late.hpWrites<12 then
    local cpu=emu.getState()
    local sp=cpu['cpu.sp']
    local stack={}
    for i=1,12 do stack[i]=read(0x100+((sp+i)&255)) end
    late.hpWrites[#late.hpWrites+1]={pc=cpu['cpu.pc'],value=value,old=source(0x6cf),state=state(),stack=stack,fall=source(0x6c6)}
  end
end),emu.callbackType.write,0xc6cf)
''',1)
        tick=tick.replace('local function tick()\n', '''local function tick()
  if collected then
    if progress:sub(1,7)~='flower-' then routeTick();return end
    if commits==lastCommit then return end
    lastCommit=commits
    local s=state()
    local age=commits-changedAt
    assert(s.lives==2 and s.hp>0,'Alive reaching flower')
    if read(0x15)~=0 and read(0x1c)==0x2e and read(0x34)==1 then flowerSeen=true end
    if #flowerTrace<80 and commits%5==0 then flowerTrace[#flowerTrace+1]={state=s,itemFlag=read(0x15),kind=read(0x34),itemState=read(0x24),sword=source(0x6ee)} end
    if progress=='flower-approach' and s.x>=1224 then switch('flower-settle',0)
    elseif progress=='flower-settle' and s.action==0 and s.pose==15 and s.mode==0 and s.lock==0 then switch('flower-up',8)
    elseif progress=='flower-up' then
      if age>=80 then pad=0 end
      if age>=110 then
        late.flower={spawned=flowerSeen,trace=flowerTrace,sword=source(0x6ee)}
        finish(flowerSeen,'Natural flower reveal after mushroom');return
      end
    end
    assert(age<500,'Bounded flower approach');return
  end
''',1)
        tick=tick.replace("    finish(true,'Naturally emerged mushroom collected');return", "    collected=true;switch('pipe-settle',0);return")
        tick=tick.replace("      switch('pickup-evade',129)","      jump={request=s,enemy=enemy,minimumY=s.y};switch('pickup-evade',129)")
        tick=tick.replace("    if s.action==4 then pad=1 end", "    jump.minimumY=math.min(jump.minimumY,s.y)\n    if s.action==4 then jump.admission=jump.admission or s;pad=1 end")
        tick=original_tick+'\n'+tick
    source = source[:begin]+tick+source[end:]
    OUTPUT.mkdir(exist_ok=True)
    script = OUTPUT/'controller.lua'
    script.write_text(source, encoding='utf-8', newline='\n')
    result = run(script,rom,OUTPUT/'capture',expected,120 if args.flower else 60,variant=3 if args.flower else 0)
    pickup = result['receipt'].get('later_route', {}).get('pickup', {})
    trace = pickup.get('trace', [])
    pickup['trace'] = [s for i,s in enumerate(trace) if i == 0 or
        any(s[k] != trace[i-1][k] for k in ('rawY','origin','originHigh','delta','action'))]
    if args.top_walk:
        pickup.pop('trace', None)
        pickup.pop('yWrites', None)
        pickup.pop('supportTrace', None)
        pickup['headTrace'] = [s for s in pickup.get('headTrace', []) if s['dy'] >= 128]
    if args.flower:
        route=result['receipt'].get('later_route',{})
        flower=route.get('flower',{})
        flower['trace']=[{'x':r['state']['x'],'y':r['state']['y'],'action':r['state']['action'],'pose':r['state']['pose'],'itemFlag':r['itemFlag'],'kind':r['kind']} for r in flower.get('trace',[])]
        hp_writes=route.get('hpWrites',[])
        descent=route.get('descent',[])
        route.clear();route['flower']=flower;route['hpWrites']=hp_writes;route['descent']=descent
    print(json.dumps(dict(passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],
                         script_SHA256=result['script_SHA256'],receipt=result['receipt'].get('later_route'),
                         injuries=result['receipt'].get('injuries'),
                         reason=result['receipt']['reason'],terminal=result['receipt']['terminal'])),flush=True)
    assert result['passed'],result['receipt']['reason']


if __name__ == '__main__':
    main()
