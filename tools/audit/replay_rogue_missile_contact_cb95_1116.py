"""Separate ordinary approach to actual aligned native target; frozen MF exact."""
from functools import lru_cache
from pathlib import Path
import re
import replay_rogue_missile_cb95_1116 as Base
from check_ff_stdout_controller_source_1110 import LuaRuntime

J,R,H,W,N,Frames,PIN=Base.J,Base.R,Base.H,Base.W,Base.N,Base.Frames,Base.PIN
SOURCE=R/'tools/playthroughs/rogue_earned_missile_contact_cb95_1116.lua'


def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)


@lru_cache(maxsize=1)
def pack(raw):
    old=Base.controller(raw,'missile');assert H(old.encode())=='614b87d9365dcd07268084e47824874a4055b9b1b90d70459efe4ccf18a303d3'
    b=J.bindings(raw)['bundle'];source=SOURCE.read_text();text=old;edits=[];lua=Base.Attack.J.Frozen.lua
    def edit(a,z):
        nonlocal text
        text=once(text,a,z);edits.append((a,z))
    names=set(re.findall(r"\br\('([^']+)'",source))|{'RdGravity','RdRadiusY','RdRadiusX','MmEnemyHealthLo','MmEnemyHealthHi','MmEnemyFlash','Enemy_BoundBoxCtrl','Enemy_Y_HighPos','RdWAnim','RdWHit','ObjectOffset'}
    defs=['C.ram['+lua(n)+']='+str(W.address(b,n))for n in sorted(names)]
    at=W.location(b,'BoundBoxCtrlData');defs.append('C.impact_bbox='+lua(list(raw[at:at+13*4])))
    at=W.location(b,'MTileAttribute');defs.append('C.impact_attributes='+lua(list(raw[at:at+256])))
    defs.append('C.impact_eligible={[6]=true,[0]=true,[3]=true,[14]=true,[15]=true,[16]=true,[13]=true,[18]=true,[5]=true,[17]=true}')
    name='RdWxActorContact';at=W.location(b,name);defs.append('C.hooks['+lua(name)+']='+lua(dict(PC=W.address(b,name),offset=at-16,bytes=list(raw[at:at+16]))))
    line=old.split('\n',1)[0];edit(line,line+'\n'+'\n'.join(defs))
    edit(Base.Attack.ATTACK.read_text(),source)
    edit('local function finish(reason)',"local impact={HP_writes={}}\nlocal function finish(reason)")
    edit("reason=='earned-missile-motion-expiry-and25workers'", "reason=='earned-missile-native-contact-and25workers'")
    edit('earned_missile=attack,stock_phase=stock,','earned_missile=attack,missile_contact=impact,stock_phase=stock,')
    edit("elseif n=='RdWxSpawn'or n=='RdWxUpdateSlot'then", "elseif n=='RdWxSpawn'or n=='RdWxUpdateSlot'or n=='RdWxActorContact'then")
    edit("if n=='RdWxSpawn'then p.weapon_slot", "if n=='RdWxActorContact'then p.enemy_slot=c['cpu.x'];p.enemy_before=nativeEnemy(p.enemy_slot)end\n if n=='RdWxSpawn'then p.weapon_slot")
    edit("'RdWxSpawn','RdWxUpdateSlot','RdWxCell'", "'RdWxSpawn','RdWxUpdateSlot','RdWxActorContact','RdWxCell'")
    edit('local function written(address,value)', """local function written(address,value)
 if impact.target and address==C.ram.MmEnemyHealthLo+impact.target.slot and #impact.HP_writes<3 then
  for i=#pending,1,-1 do local p=pending[i];if p.name=='RdWxActorContact'and p.A==11 then impact.HP_writes[#impact.HP_writes+1]={Main=updates,PC=cpu()['cpu.pc'],slot=impact.target.slot,old=emu.read(address,emu.memType.nesDebug),new=value};break end end
 end""")
    edit("emu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram.RdSfx+4)", "emu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram.RdSfx+4)\nemu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram.MmEnemyHealthLo,C.ram.MmEnemyHealthLo+4)")
    restored=text
    for a,z in reversed(edits):restored=once(restored,z,a)
    assert restored==old;LuaRuntime().compile(text)
    assert not any(t in text for t in('emu.write','emu.setState','takeScreenshot','io.open','dofile','saveState','loadState'))
    return text,dict(owning_SHA256=PIN,controller_SHA256=H(text.encode()),factory_SHA256=H(Path(__file__).read_bytes()),
        continuation_SHA256=H(SOURCE.read_bytes()),qualified_prefix_exact=True,explicit_restoration_to614b=True,
        target_snapshot_receipt='ead28aed9829e81c4f6a39c7fbcc8190cf3cec079e6aec9bac5d7f16d4f61c11',
        ordinary_ground_approach_and_actual_gap_inputs_only=True,damage1_unchanged=True,game_changes=0,seeds=0,images=0,outputs=0,native=False)


def controller(raw):return pack(raw)[0]
def metadata(raw):return pack(raw)[1]


if __name__=='__main__':
    import json
    from unittest.mock import patch
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    raw,provenance=Engine.Reader.load_current()
    def deny(*a,**kw):raise AssertionError('Natural missile contact attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        text=controller(raw);q=Engine.run(raw,4000,text=text);q['policy_metadata']=metadata(raw)
    print('RESULT '+json.dumps(dict(input=provenance,result=q),separators=(',',':')),flush=True)
