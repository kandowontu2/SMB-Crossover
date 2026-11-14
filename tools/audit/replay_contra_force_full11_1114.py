"""Separate exact421 CF full-stage controls; frozen factories unchanged."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re

import replay_smb1_alts_full11_1114 as Frozen

R=Frozen.R
PIN=Frozen.PIN
ROM=Frozen.ROM
W,N=Frozen.W,Frozen.N
IDENTITIES={name:(name.upper(),i)for i,name in enumerate(('burns','smith','iron','beans'))}
POLICY=R/'tools/playthroughs/contra_force_full11_1114.lua'
KERNEL=R/'build/contra-force-projectile-contact-1031-v3/kernel'
LEGACY_POLICY=R/'tools/playthroughs/contra_force_11_1031_v2.lua'
FROZEN_SOURCE='e25b9510f2fbdc5ece466033ad02d8ba25abc19cf8359bb15e3bcfe669b3af61'
POLICY_SOURCE='8c4435d5732048997794641ff3d2a235ce5f7de8227f76923bb86aa80622b121'
LABELS_SOURCE='8944961064964d2bac2d7b2ebca31fbb4ac4c2d9b555af032f7477ee16414ab2'
LUA_SHA={'burns':'ef9188cdc9d95d6a9c11105ef60b08b09a14701bd21779571a272b9f44b9cce3',
    'smith':'b47968a12a866ed1b37ae603f5780ebf41be66c6cdff0ab99ba9d649646cd87b',
    'iron':'a5134c9ff9ffbd6fadcfeb91ea3135c9ba9c759678a79832a7ccd05076161cf9',
    'beans':'f22368807ec51f52fa3b3e3ec85f49548be7b4a19fff136fb7242bfda5ec6347'}
normalize=Frozen.normalize


@lru_cache(maxsize=4)
def bindings(raw,key):
    assert key in IDENTITIES and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    assert sha256((KERNEL/'runtime.lbl').read_bytes()).hexdigest()==LABELS_SOURCE
    q=deepcopy(Frozen.bindings(raw,'toad'))
    name,variant=IDENTITIES[key]
    m=W.UI.seed(dict(W.Symbols.bundle(),raw=raw),0)
    for pad in(4,4,4,1,1,1,1,1,1):W.UI.key(m,pad)
    assert N.get(m,'CrossoverMenuIndex')==30,('Actual slot30 navigation',N.get(m,'CrossoverMenuIndex'))
    for _ in range(variant):W.UI.key(m,32)
    assert (W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),(N.get(m,'FmGroups')>>3)&3)==(name,31,variant)
    q.update(key=key,name=name,variant=variant,cycle=variant,slot=30)
    b=dict(W.Symbols.bundle(),raw=raw)
    q['ram']['FmGroups']=W.address(b,'FmGroups')
    labels={n:int(at,16)for at,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\w+)$',(KERNEL/'runtime.lbl').read_text(),re.M)}
    carrier=raw[1048592+935*1024:1048592+959*1024]
    assert len(carrier)==24576
    for bank in(1,2,3):
        old=bytearray((KERNEL/f'ram{bank}.bin').read_bytes());old.extend(bytes(8192-len(old)))
        if bank in(2,3):old[0x1fe0:]=bytes(32)
        assert carrier[(bank-1)*8192:bank*8192]==old,('Current CF carrier differs from f476 source',bank)
    at=W.location(b,'CfExternalCookie');cookie=bytearray(raw[at:at+16])
    assert len(cookie)==16 and cookie[:2]==bytes((0xa7,31));cookie[2]=variant
    hooks={}
    for name in('CfHostMovement','CfHostExport','CfSourceImpact'):
        pc=labels[name];offset=pc-0xa000
        hooks[name]=dict(pc=pc,raw=3*8192+offset,bytes=list(carrier[16384+offset:16384+offset+8]))
    q['cf']=dict(cookie=list(cookie),hooks=hooks,carrier_SHA256=sha256(carrier).hexdigest())
    return q


OBSERVER=r'''
local function cfOwner()
 if not first then return end
 local nextArea=r('WorldNumber')==0 and r('LevelNumber')==1 and active()
 if not cfChecked or(nextArea and not cfNextChecked)then
  for bank=2,3 do for i,v in ipairs(C.cf.cookie)do assert(emu.read(bank*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==v,'Actual complete CF cookie')end end
  cfChecked=true;if nextArea then cfNextChecked=true end
 end
end
local function cfHook(name,fn)
 local h=C.cf.hooks[name]
 emu.addMemoryCallback(guard(function()
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=emu.memType.nesWorkRam or a.address~=h.raw then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Exact source CF seam '..name)end
  fn()
 end),emu.callbackType.exec,h.pc)
end
cfHook('CfHostMovement',function()
 if not first then return end
 cfCalls=cfCalls+1
 if r('WorldNumber')==0 and r('LevelNumber')==1 and active()then cfNextCalls=cfNextCalls+1 end
end)
cfHook('CfHostExport',function()
 if not first then return end
 local function s(at)return emu.read(2*8192+at,emu.memType.nesWorkRam)end
 cfLastSource={input=s(0x4aa),contact=s(0x4d2),jump_age=s(0x4b4),x=s(0x34e),y=s(0x368),variant=s(0x2e0)}
 assert(cfLastSource.variant==C.variant,'Genuine source class constructor')
end)
cfHook('CfSourceImpact',function()if first then cfImpacts=cfImpacts+1 end end)
'''


@lru_cache(maxsize=4)
def controller(raw,key):
    config=bindings(raw,key)
    assert sha256(POLICY.read_bytes()).hexdigest()==POLICY_SOURCE
    template=Frozen.TEMPLATE.read_text()
    assert sha256(Frozen.TEMPLATE.read_bytes()).hexdigest()==Frozen.ROUTE_PINS[Frozen.TEMPLATE]
    def once(old,new):
        nonlocal template
        assert template.count(old)==1,old
        template=template.replace(old,new,1)
    once("r('SelectedCharacter')==0 and r('MarioVariant')==C.variant","r('SelectedCharacter')==31 and((r('FmGroups')>>3)&3)==C.variant")
    once(" for i=1,C.cycle do press('select');menuEvents[i]={frame=frame,variant=r('MarioVariant'),raw=r('SelectedCharacter')}end",
         " for i=1,3 do press('down')end\n for i=1,6 do press('right')end\n assert(r('CrossoverMenuIndex')==30 and r('SelectedCharacter')==31,'Actual compiled slot30')\n for i=1,C.cycle do press('select');menuEvents[i]={frame=frame,variant=(r('FmGroups')>>3)&3,raw=r('SelectedCharacter')}end")
    once('char=0,variant=C.variant,r=r,','char=31,variant=C.variant,r=r,update=updates,heldA=lastA,')
    once('local function finish(reason)',
         'local cfCalls,cfNextCalls,cfChecked,cfNextChecked,cfImpacts=0,0,false,false,0\nlocal cfLastSource,cfPhase,cfPhaseChanges=nil,nil,{}\nlocal cfDecisionUpdate,cfButtons=nil,{}\nlocal function finish(reason)')
    begin=template.index("local stairPhase,stairAge='approach',0")
    end=template.index('emu.addEventCallback(guard(function()\n polls=polls+1',begin)
    template=template[:begin]+'''local function controls(c)
 if cfDecisionUpdate==updates then return cfButtons end
 local b,phase,why=choose(c);assert(not why,why)
 cfDecisionUpdate,cfButtons=updates,b
 if phase~=cfPhase then
  cfPhase=phase
  if #cfPhaseChanges<48 then cfPhaseChanges[#cfPhaseChanges+1]={phase=phase,state=state()}end
 end
 return b
end
'''+template[end:]
    once("hook('GameLoop',function()",OBSERVER+"\nhook('GameLoop',function()")
    once(' pendingReturn=nil;updates=updates+1',' pendingReturn=nil;updates=updates+1\n cfOwner()')
    once("and nextUpdates==25 and identity()and r('NumberofLives')==2",
         "and nextUpdates==25 and identity()and r('NumberofLives')==2 and cfChecked and cfNextChecked and cfCalls>0 and cfNextCalls>=25")
    once('full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false',
         'CF_cookie_verified=cfChecked,CF_1_2_cookie_verified=cfNextChecked,CF_movement_calls=cfCalls,CF_1_2_movement_calls=cfNextCalls,CF_source_impacts=cfImpacts,CF_last_source=cfLastSource,CF_phase_changes=cfPhaseChanges,full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    once("variant=r('MarioVariant'),chr_mode=", "variant=(r('FmGroups')>>3)&3,chr_mode=")
    text='local C='+Frozen.lua(config)+'\nlocal choose=(function()\n'+POLICY.read_text()+'\nend)()\n'+template
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key):
    q=bindings(raw,key);text=controller(raw,key)
    parent=normalize(raw).postbg;b=dict(W.Symbols.bundle(),raw=raw);preserved={}
    for name in('CfExternalCookie','MenuResolveCharacter','CfOrBtCheck','FmDrawCfPreview','ScrollHandler','PlayerBGCollision'):
        at=W.location(b,name);bank=(at-16)//8192;lo=16+bank*8192
        assert raw[lo:lo+8192]==parent[lo:lo+8192]
        preserved[name]=dict(bank=bank,SHA256=sha256(raw[lo:lo+8192]).hexdigest())
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:q[k]for k in('name','slot','cycle','variant')},
        controller_SHA256=sha256(text.encode()).hexdigest(),CF_carrier935_958_SHA256=q['cf']['carrier_SHA256'],
        all24576_carrier_bytes_exact_f476_kernel=True,current_native_banks_equal12397=preserved,
        complete_C2_C3_cookies_and_real_movement_export_assertions_in_controller=True,
        normal_controls_only=True,gameplay_seeds=0,current176_fixes_preserved=True,
        full_nonshortcut1_1_then25living_grounded1_2_required=True,
        source_route_pass=False,native_route_pass=False,natural_items_not_claimed=True,outputs=0,Mesen_run=False)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=IDENTITIES,required=True)
    args=p.parse_args();print(json.dumps(metadata(ROM.read_bytes(),args.identity),separators=(',',':')),flush=True)
