"""Candidate54b ordinary MF then genuine missile/expiry/+25 production replay."""
from functools import lru_cache
from pathlib import Path
from copy import deepcopy
import re
import current_rogue_missile_dispatch_54b_v2_1116 as J
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,H,N,W,Frames,PIN=J.R,J.ROM,J.H,J.N,J.W,J.Frames,J.PIN
ATTACK=R/'tools/playthroughs/rogue_earned_missile54b_1116.lua'
NEW_HOOKS=('RdControlDispatch','RdWxSpawn','RdWxUpdateSlot','RdWxCell','RdWxMove','RdAnimateProjectile','RdWpRender')


def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)


@lru_cache(maxsize=1)
def pack(raw):
    b=J.bindings(raw)['bundle'];parent=J.C.inverse(raw);old=J.mf_controller(raw)
    cfg=deepcopy(J.Frozen.bindings(parent));cfg['sha']=PIN
    text=ATTACK.read_text()
    extra=set(re.findall(r"\br\('([^']+)'",text))|{'RdSourceAltPalette','RdMissileMode','RdSlot','RdWX','RdWHi','RdWY','RdWAction','RdWVX','RdWVY','RdWAge','RdWFrame','RdWOnScreen'}
    for name in extra:cfg['ram'][name]=W.address(b,name)
    for name in NEW_HOOKS:
        at=W.location(b,name);cfg['hooks'][name]=dict(PC=W.address(b,name),offset=at-16,bytes=list(raw[at:at+32]))
    old_line=old.split('\n',1)[0];new_line='local C='+J.Frozen.lua(cfg)
    baseline=once(old,old_line,new_line)
    changes=[]
    def edit(a,z):
        nonlocal baseline
        baseline=once(baseline,a,z);changes.append((a,z))
    edit("local function finish(reason)","local attack={started=false,events={},calls={},moves=0,slot_updates=0}\nlocal function finish(reason)")
    edit("reason=='natural-tank-missile-credit-and25workers'", "reason=='earned-missile-motion-expiry-and25workers'and attack.complete ")
    edit('completed_tank_gate=completed[1],stock_phase=stock,','completed_tank_gate=completed[1],earned_missile=attack,stock_phase=stock,')
    edit("{'RdControlStep','RdLifeMovement','GameLoop'}", "{'RdControlStep','RdControlDispatch','RdLifeMovement','GameLoop'}")
    edit('local function afterMain()',text+'\nlocal function afterMain()')
    edit(" if not first then return end\n", " if not first then return end\n if attack.started then attackDrive();return end\n")
    edit("else finish('natural-tank-missile-credit-and25workers');return end", "else attack.started=true;attack.phase='release';attack.start=updates;attack.baseline=state();attack.mf_credit=credit;buttons={};return end")
    edit("local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}",
        "local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}\n if n=='RdWxSpawn'then p.weapon_slot=c['cpu.y']elseif n=='RdWxUpdateSlot'then p.weapon_slot=r('RdSlot');p.weapon_before=shot(p.weapon_slot)end")
    edit("elseif n=='RdHsCollectActor'then", "elseif n=='RdWxSpawn'or n=='RdWxUpdateSlot'then weaponReturned(n,p)\n  elseif n=='RdHsCollectActor'then")
    edit("'GameLoop','RdControlStep','RdLifeMovement','HandlePowerUpCollision'", "'GameLoop','RdControlStep','RdControlDispatch','RdLifeMovement','RdWxSpawn','RdWxUpdateSlot','RdWxCell','RdWxMove','RdAnimateProjectile','RdWpRender','HandlePowerUpCollision'")
    edit("count(n..'_entered');if n=='GameLoop'then", "count(n..'_entered');if attack.started and attack.birth and r('RdSlot')==attack.slot then attack.calls[n]=(attack.calls[n]or 0)+1 end;if n=='GameLoop'then")
    edit('local function written(address,value)', '''local function written(address,value)
 if attack.started and address==C.ram.RdSfx and(value&32)~=0 and(emu.read(address,emu.memType.nesDebug)&32)==0 then attack.request={Main=updates,PC=cpu()['cpu.pc'],old=emu.read(address,emu.memType.nesDebug),new=value}end
 if attack.started and address==C.ram.RdMissiles and emu.read(address,emu.memType.nesDebug)==5 and value==4 then attack.ammo={Main=updates,PC=cpu()['cpu.pc'],old=5,new=4}end''')
    edit("for _,name in ipairs({'Square2SoundQueue','RdTanks','PlayerStatus'})do", "for _,name in ipairs({'Square2SoundQueue','RdTanks','PlayerStatus','RdSfx','RdMissiles'})do")
    restored=baseline
    for a,z in reversed(changes):restored=once(restored,z,a)
    restored=once(restored,new_line,old_line);assert restored==old
    LuaRuntime().compile(baseline)
    assert all(x not in baseline for x in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return baseline,dict(owning_SHA256=PIN,factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(baseline.encode()),
        attack_source_SHA256=H(ATTACK.read_bytes()),parent_MF_controller_SHA256=H(old.encode()),
        exact_parent_restoration=True,ordinary_input_body_before_MF_endpoint_unchanged=True,images=0,outputs=0,native=False)


def controller(raw):return pack(raw)[0]
def metadata(raw):return pack(raw)[1]
