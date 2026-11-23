"""Exact2ac7 earned Tank boots: source/controller QA only by default.

--cpu uses the existing actual machine/compiled menu harness. --run belongs
only to Root's shared Mesen queue, restores controller.lua, and writes no ROM.
"""
import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import profile_sonic_empty_cpu_1110 as B
import replay_mario_luigi_stock_1122 as Stock
import check_smb1_alts_full11_1114 as Linked
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value

R,ROM,N,W=Stock.R,Stock.ROM,B.N,B.W
PIN='2ac7c084b079ca6920b71346013bca82f1b8dd37a4de48f13d39de9ab2605446'
PIPE='28708fa9a4e7dd88f1aaa72653b7d5a6ba0fb3c6d5abf544a526b09d333a884c'
POLICY=R/'tools/playthroughs/mario_tank_earned_boots_1123.lua'
H=lambda x:sha256(x).hexdigest()

def reference(raw):
    assert isinstance(raw,bytes)and len(raw)==2097168 and H(raw)in(PIN,PIPE)
    if H(raw)==PIN:return raw,[]
    import repair_rogue_side_pipe_1123 as Rogue
    parent=Rogue.restore_pipe_bytes(raw);assert H(parent)==PIN
    spans=[(Rogue.file_at(pc),len(new))for pc,new in((0xbf5f,Rogue.HOOK_NEW),(Rogue.FIRST_PC,Rogue.FIRST),(Rogue.SECOND_PC,Rogue.SECOND))]
    owned={i for at,size in spans for i in range(at,at+size)}
    assert {i for i,(x,y)in enumerate(zip(parent,raw,strict=True))if x!=y}<=owned
    return parent,spans

@lru_cache(maxsize=1)
def bindings(raw,key='tank'):
    assert key=='tank';parent,pipe_spans=reference(raw)
    b=W.Symbols.bundle();names=set(('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Speed','Player_Y_Speed','PlayerStatus','PlayerSize','PlayerFacingDir','PreviousA_B_Buttons','WorldNumber','LevelNumber','AreaPointer','AreaType','AreaAddrsLOffset','GameEngineSubroutine','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Block_Buffer_1','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','OperMode','OperMode_Task','NumberofLives','MarioVariant','SelectedCharacter','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel','CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState','CrossoverMenuIndex','CrossoverOptionsFocus','TimerControl','StarInvincibleTimer','PowerUpType','FloateyNum_Control','Square1SoundQueue','Square2SoundQueue','PlayerScoreDisplay','Fireball_State','R2','R6','R7'))
    ram={n:W.address(b,n)for n in names};hooks={}
    for n in('GameLoop','HandlePowerUpCollision','PlayerHeadCollision'):
        pc,at=W.address(b,n),W.location(b,n);bank=(at-16)//8192
        hooks[n]=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+12].hex())
    image=raw[1048592+501*1024:1048592+503*1024]
    for n,pc in(('TankMovement',0xb676),('TankContact',0xb60b),('TankDestroy',0xb765),('TankUpgrade',0xb692)):
        data=image[pc-0xb600:pc-0xb600+12]
        hooks[n]=dict(pc=pc,tag=2,offset=2*8192+(pc&8191),hex=data.hex())
    assert hooks['TankContact']['hex'].startswith('0848ad5b07c902')
    assert hooks['TankDestroy']['hex'].startswith('482090b8')
    for h in hooks.values():
        if h['tag']>=128:
            at=h['offset']+16;size=len(bytes.fromhex(h['hex']))
            assert raw[at:at+size]==parent[at:at+size]
            assert not any(at<lo+n and lo<at+size for lo,n in pipe_spans)
    assert image==parent[1048592+501*1024:1048592+503*1024]
    cookie=raw[16+28*8192+8112+55:16+28*8192+8112+71]
    assert cookie[:4]==bytes.fromhex('a7f70501')
    selected=W.UI.seed(dict(b,raw=raw),0)
    for _ in range(7):W.UI.key(selected,32)
    assert W.UI.menu_name(selected)[0]=='MARIO THE TANK'and N.get(selected,'MarioVariant')==7
    return dict(sha=H(raw),key='tank',name='MARIO THE TANK',form='tank',slot=0,cycle=7,variant=7,mode_value=0,route='earned-boots',ram=ram,hooks=hooks,cookie=list(cookie),image=list(image),navigation=[('left'if i%8<=4 else'right')if i%8 else('up'if i//8 in(1,2)else'down'if i//8==3 else'')for i in range(32)])

AFTER=r'''
local function score()
 local n=0;for i=0,5 do local d=r('PlayerScoreDisplay',i);assert(d<10,'Native score digit');n=n*10+d end;return n
end
local function work(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
local function afterMain()
 if not entered then return end
 updates=updates+1
 local s=state();s.score=score();s.mask=mask
 if #tail==12 then table.remove(tail,1)end;tail[#tail+1]=s
 assert(identity()and s.world==0 and s.level==0 and s.engine~=11 and s.lives==2,'Living Tank with two original lives')
 assert(updates<3500 and s.yHigh<2,'Finite living earned-boot route')
 if not tankChecked then
  for i,v in ipairs(C.cookie)do assert(work(0x1fe0+i-1)==v,'Actual complete Tank cookie')end
  for i,v in ipairs(C.image)do assert(work(0x1600+i-1)==v,'Actual complete Tank cold worker')end
  tankChecked=true
 end
 for i=0,5 do
  local a=actor(i);local q=checks[tostring(a.kind)]
  if q and a.flag>0 and a.flag<128 and a.id==46 and not q.birth and math.abs(a.x-item_x[a.kind])<=2 then
   assert(heads[tostring(a.kind)],'Real authored head before item birth');q.birth={actor=a,player=s}
  end
  if q and q.birth and q.birth.actor.slot==i and a.state&128~=0 then q.mature=q.mature or {actor=a,player=s}end
 end
 for _,kind in ipairs({0,1})do
  local q=checks[tostring(kind)]
  if q.collect and not q.after and s.status==kind+1 and scope()and s.motor-q.collect.after.motor>=25 then
   assert(s.score>=q.collect.before.score+1000,'Native1000-point pickup credit');q.after=s
  end
 end
 -- Current native BrickShatter and Tank both write literal5 to the final
 -- score modifier. Record counter units honestly; do not assert a display
 -- convention or silently label the observed +5 as a new +50 award.
 if terrain and not terrain.score_credit and s.score>=terrain.before.score+5 then terrain.score_credit=s;TANK_BOOT_PROGRESS.terrain=true end
 if contact and not contact.score_credit and s.score>=contact.before.score+1000 then contact.score_credit=s;TANK_BOOT_PROGRESS.enemy=true end
 local complete=checks['0'].after and checks['1'].after and(C.test=='terrain'and TANK_BOOT_PROGRESS.terrain or C.test=='enemy'and TANK_BOOT_PROGRESS.enemy or C.test=='both'and TANK_BOOT_PROGRESS.terrain and TANK_BOOT_PROGRESS.enemy)
 if complete and not afterAttack then afterAttack=s;TANK_BOOT_PROGRESS.complete=true end
 if afterAttack and s.motor-afterAttack.motor>=25 and scope()and s.state==0 and s.yHigh==1 then
  assert(s.status==2 and s.star==0,'Earned boots retained without Star')
  finish(true,'Natural Mushroom and boots, actual boot action and25 living grounded movement returns')
 end
end
'''

COLLECT=r'''
local function collected(p)
 local a=p.actor;local q=checks[tostring(a.kind)]
 assert(q and q.birth and q.mature and not q.collect,'Real born, mature ordinary powerup')
 assert(r('Enemy_Flag',a.slot)==0 and r('FloateyNum_Control',a.slot)==6,'Native item erase/1000-point popup')
 assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')
 local s=state();s.score=score()
 assert(s.status==a.kind+1 and p.before.status==a.kind,'Natural0->1->2 Tank upgrades')
 assert(upgradeReturns>p.upgrades,'Actual Tank upgrade worker returned')
 q.collect={actor=a,before=p.before,after=s};q.grant=s
end
'''

def controller(raw,key='tank',test='both'):
    c=dict(bindings(raw,key),test=test)
    s=(R/'tools/audit/ice_climbers_stock_observer_1122.lua').read_text()
    s=s.replace("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact published ROM')","if not CPU_CONTROLLER_OPENING then assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact published ROM')end")
    s=s.replace("r('SelectedCharacter')==20 and r('IcVariant')==C.variant","r('SelectedCharacter')==0 and r('MarioVariant')==7")
    s=s.replace("power=r('IcPower')","power=r('PlayerStatus')")
    s=s.replace("local expected=C.route=='life' and {0,3} or {0,1,2}",'local expected={0,1}')
    s=s.replace('local lifePending','local lifePending\nlocal terrain,contact,afterAttack,tankChecked\nlocal upgradeReturns=0\nlocal counts={}\nTANK_BOOT_PROGRESS={}')
    s=s.replace('c.poll=polls;c.char=20;c.variant=C.variant;c.r=r','c.poll=polls;c.char=0;c.variant=7;c.r=r;c.update=updates')
    s=s.replace('c.lastMask=mask;c.lastA=mask&128~=0',"c.lastMask=mask;c.lastA=r('PreviousA_B_Buttons')&128~=0")
    s=s.replace('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0','phase=TANK_BOOT_POLICY or {},terrain=terrain,enemy=contact,after_attack=afterAttack,actual_Tank_cold=tankChecked,counts=counts,controller_only=true,game_state_writes=false,files=0,images=0')
    lo=s.index('local function afterMain()');hi=s.index('local function collected(p)');s=s[:lo]+AFTER+'\n'+s[hi:]
    lo=s.index('local function collected(p)');hi=s.index('local function settle()');s=s[:lo]+COLLECT+'\n'+s[hi:]
    s=s.replace("  if p.name=='IcMovement' then motor=motor+1",'''  counts[p.name..'_returned']=(counts[p.name..'_returned']or 0)+1
  if p.name=='TankMovement'then motor=motor+1
  elseif p.name=='TankUpgrade'then upgradeReturns=upgradeReturns+1
  elseif p.name=='TankDestroy'and p.action then
   if emu.getState()['cpu.ps']&1~=0 and emu.getState()['cpu.a']==0 and work(0x88a)==1 and emu.read(p.action.cell,emu.memType.nesDebug)==0 then
    assert(r('NoiseSoundQueue')==1,'Native brick-smash sound')
    local delta=score()-p.before.score;assert(delta==5,'Actual native last-digit modifier5')
    terrain=terrain or {before=p.before,after=state(),cell=p.action.cell,tile=p.action.tile,removed_before=0,removed_after=work(0x88a),native_score_delta=delta,smash_sound=r('NoiseSoundQueue'),return_A=emu.getState()['cpu.a'],return_C=emu.getState()['cpu.ps']&1,used_boot_block=p.before.x>=1230 and p.before.x<=1260 and p.before.vy>=128}
   end
  elseif p.name=='TankContact'and p.enemy then
   assert(r('Enemy_State',p.enemy.slot)&32~=0 and r('FloateyNum_Control',p.enemy.slot)==6 and r('Square1SoundQueue')==8,'Tank native defeat bit/1000 popup/smack')
   contact=contact or {before=p.before,after=state(),enemy=p.enemy,enemy_state=r('Enemy_State',p.enemy.slot),popup=r('FloateyNum_Control',p.enemy.slot),smack=r('Square1SoundQueue'),return_C=emu.getState()['cpu.ps']&1}
  ''')
    s=s.replace(" if name=='LifeCredit' then",''' if name=='TankDestroy'then
  if r('PlayerStatus')~=2 or terrain then return end
 elseif name=='TankContact'then
  if r('PlayerStatus')~=2 or contact then return end
 end
 if name=='LifeCredit' then''')
    marker=" local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}"
    s=s.replace(marker,marker+'''
 counts[name..'_entered']=(counts[name..'_entered']or 0)+1
 if name=='TankDestroy'and work(0x88a)==0 then
  p.before=state();p.before.score=score();p.action={tile=cpu['cpu.a'],cell=r('R6')+256*r('R7')+r('R2')}
 elseif name=='TankContact'then
  local a=actor(cpu['cpu.x'])
  if a.id~=6 or a.flag==0 or a.state>=32 or r('Player_State')~=0 or mask&192~=0 or r('StarInvincibleTimer')~=0 or r('Fireball_State')~=0 or r('Fireball_State',1)~=0 then return end
  p.before=state();p.before.score=score();p.before.mask=mask;p.before.fireballs={r('Fireball_State'),r('Fireball_State',1)};p.enemy=a
 end''')
    s=s.replace('p.actor=a;p.before=state()','p.actor=a;p.before=state();p.before.score=score();p.upgrades=upgradeReturns')
    s=s.replace("if r('IcVariant')~=C.variant","if r('MarioVariant')~=7")
    c['ram']['NoiseSoundQueue']=W.address(W.Symbols.bundle(),'NoiseSoundQueue')
    text='\n'.join(('local C='+value(c),'local base=(function()\n'+Stock.travel()+'\nend)()','local choose=(function()\n'+POLICY.read_text()+'\nend)()',s))
    LuaRuntime().compile(text)
    assert not any(t in text for t in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot','dofile','Ic'))
    return text

def metadata(raw,key='tank'):
    c=bindings(raw,key)
    _,spans=reference(raw)
    return dict(ROM_SHA256=H(raw),reference2ac_SHA256=PIN,Rogue_inverse_spans=spans,Tank_hooks_and_carrier_disjoint=True,identity='MARIO THE TANK',raw=0,variant=7,historical_stock_pass_preserved='7ec9cd5c natural Mushroom and boots',carrier_SHA256=H(bytes(c['image'])),controller_only=True,outputs=0)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cpu',action='store_true');p.add_argument('--cpu-parent2ac',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--test',choices=('terrain','enemy','both'),default='both');a=p.parse_args()
    assert not(a.run and a.cpu_parent2ac)
    raw=ROM.read_bytes()
    if a.cpu_parent2ac:raw=reference(raw)[0];a.cpu=True
    text=controller(raw,test=a.test)
    print('TANK BOOTS SOURCE '+json.dumps(dict(**metadata(raw),test=a.test,controller_SHA256=H(text.encode()))),flush=True)
    if a.cpu:
        import sys
        with patch.object(Linked,'Factory',sys.modules[__name__]),patch.object(Linked,'strict_metadata',lambda raw,key:metadata(raw,key)),patch.object(sys.modules[__name__],'controller',lambda raw,key='tank':text):q=Linked.run(raw,'tank',limit=3500)
        print('TANK BOOTS CPU '+json.dumps(q,separators=(',',':')),flush=True);assert q['passed']
    if a.run:
        from run_mario_luigi_stock_native_1122 import OUT,preserve_script
        from nightly_patch_guard_v1 import check
        from run_stdout_mesen_1110 import run
        guard=check(ROM);assert guard['ROM_sha256']==H(raw) and not guard['matching_patch_files']
        candidate,script=OUT/'candidate.nes',OUT/'controller.lua'
        assert set(OUT.iterdir())=={candidate,script}and candidate.read_bytes()==raw
        try:
            with preserve_script(script,candidate,raw)as stage:
                stage(text.encode());q=run(script,ROM,OUT/'capture',H(raw),180)
                print('TANK BOOTS NATIVE '+json.dumps(q,separators=(',',':')),flush=True)
                assert q['passed']and q['outputs_written']==0 and not q['images']
        finally:assert ROM.read_bytes()==raw and check(ROM)==guard

if __name__=='__main__':main()
