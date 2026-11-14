"""Explicit82ec Rogue Dawn full-stage controller, no files or emulator launch.

The legacy421 factories remain frozen. Normal input follows the retained
Rogue route, embedded without its old capture/output infrastructure.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re

import compose_shared_world_chr_reset_1114 as Reset
import replay_smb1_alts_full11_1114 as Frozen

R,ROM,W,N=Frozen.R,Frozen.ROM,Frozen.W,Frozen.N
PIN=Reset.CANDIDATE
IDENTITIES={'rogue':('ROGUE DAWN',1,1)}
SOURCE_PIN='e25b9510f2fbdc5ece466033ad02d8ba25abc19cf8359bb15e3bcfe669b3af61'
TEMPLATE_PIN='7057409ee03b52b0cd58394164e715521279772884ebae5488a47522b5124744'
ENTRY='rogue_dawn_11_v9.lua'
LUA_PIN='3e8dee121821187a9c57bd742980c0c59b6c417348af4703a13abef92cd36471'
ROUTE_PINS={
    'rogue_dawn_11_v9.lua':'c9d98bf554ead8e3976cfee0bccbc4693de938985024139f59aaf10c5dde2eed',
    'rogue_dawn_11_v7.lua':'c064b5e8c682c8a0bef078984a753ba141c376fad2c0a3ec964a783a766800bc',
    'rogue_dawn_11_v6.lua':'cb674ac2c6708806d7c2b77c37675b631a7039963b052f7d7ef3b0be4248422f',
    'rogue_dawn_11_v5.lua':'d0bf587c3edbb4a009bcf81c616cbb3a7f64706a8658d5651e3fd273eb5b2770',
    'rogue_dawn_11_v4.lua':'623c908486cc3ca3180d0d6d1331c632957ab685c0709ba110a58078cdb7c0c5',
    'rogue_dawn_opening_route_v1.lua':'49193a155d26040ddfa3c8423adbe5f82226b4bfa982a1bd962a0888416db21a',
    'roster_samus_contra_nav.lua':'b80b164e8583565f14e9ac6145c7aa2d314c55b253325630d9438a13e17514b0'
}


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


def route(name,bindings):
    assert name in ROUTE_PINS and re.fullmatch(r'[a-z0-9_]+\.lua',name)
    path=R/'tools/playthroughs'/name;text=path.read_text()
    pin=sha256(path.read_bytes()).hexdigest();assert pin==ROUTE_PINS[name],name
    bindings[path.relative_to(R).as_posix()]=pin
    prefix="local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n"
    text=text.replace(prefix,'')
    def embed(match):
        return '(function()\n'+route(match[1],bindings)+'\nend)()'
    text=re.sub(r"assert\(dofile\(root\.\.'/tools/playthroughs/([a-z0-9_]+\.lua)'\)\)",embed,text)
    assert 'dofile'not in text and 'root..'not in text
    return text


@lru_cache(maxsize=1)
def normalize(raw):
    assert sha256(raw).hexdigest()==PIN
    return Frozen.normalize(Reset.inverse(raw))


@lru_cache(maxsize=1)
def bindings(raw,key='rogue'):
    assert key=='rogue'and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==SOURCE_PIN
    parent=Reset.inverse(raw);q=deepcopy(Frozen.bindings(parent,'peach'))
    b=dict(W.Symbols.bundle(),raw=raw);m=W.UI.seed(b,0)
    for pad in(1,1,32):W.UI.key(m,pad)
    name=W.UI.menu_name(m)[0]
    assert name=='ROGUE DAWN'and N.get(m,'CrossoverMenuIndex')==2
    assert N.get(m,'SelectedCharacter')==2 and N.get(m,'RdVariant')==1
    q.update(sha=PIN,key=key,name=name,cycle=1,variant=1,slot=2,owner=2)
    for name in('RdVariant','RdAction','RdGravity','RdVY','RdX','RdY','RdRoomHi',
                 'RdRadiusX','RdRadiusY','RdHeld','RdFresh','RdHealthLo','RdHealthHi','SmBall'):
        q['ram'][name]=W.address(b,name)
    for name in('RdLifeMovement',):
        at=W.location(b,name);q['hooks'][name]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+8]))
    for name,h in q['hooks'].items():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes']),(name,'hook bytes')
        if 'bank'in h:
            first=16+h['bank']*8192
            h['bank_SHA256']=sha256(raw[first:first+8192]).hexdigest()
    attr=W.location(b,'MTileAttribute');q['rogue_tile_attributes']=list(raw[attr:attr+256])
    assert len(q['rogue_tile_attributes'])==256
    return q


@lru_cache(maxsize=1)
def controller(raw,key='rogue'):
    q=bindings(raw,key);parent=Reset.inverse(raw)
    original=Frozen.controller(parent,'peach')
    assert sha256(original.encode()).hexdigest()==TEMPLATE_PIN
    marker='-- Normal controller inputs and readonly native witnesses. No game-state writes.'
    body=marker+original.split(marker,1)[1]
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant",
              "r('SelectedCharacter')==2 and r('RdVariant')==C.variant")
    assert body.count("variant=r('MarioVariant')")==2
    body=body.replace("variant=r('MarioVariant')","variant=r('RdVariant')")
    body=once(body,'MarioVariant=C.variant','RdVariant=C.variant')
    body=once(body,"power=r('PlayerStatus'),lives=r('NumberofLives')",
              "power=r('PlayerStatus'),source_action=r('RdAction'),source_vy=r('RdVY'),source_hp=r('RdHealthLo')+256*r('RdHealthHi'),lives=r('NumberofLives')")
    body=once(body,'frame=frame,poll=polls,char=0','frame=updates,poll=updates,char=2')
    body=once(body,'lastA=lastA,grounded=',"lastA=(r('RdHeld')&128)~=0,grounded=")
    body=once(body," for i=1,C.cycle do press('select');",
              " press('right');press('right')\n assert(r('CrossoverMenuIndex')==2 and r('SelectedCharacter')==2 and r('RdVariant')==0,'Actual Samus slot')\n for i=1,C.cycle do press('select');")
    body=once(body,'local function finish(reason)',
              'local rogueInput,rogueDecide={},nil\nlocal rogueMoves,rogueNext,rogueMin=0,0,65535\nlocal function finish(reason)')
    body=once(body,"hook('GameLoop',function()", """hook('RdLifeMovement',function()
 if not first or not identity()then return end
 rogueMoves=rogueMoves+1
 if r('WorldNumber')==0 and r('LevelNumber')==1 and active()then rogueNext=rogueNext+1 end
end)
hook('GameLoop',function()""")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+"\n if first and active()then rogueMin=math.min(rogueMin,r('RdHealthLo')+256*r('RdHealthHi'))end\n if rogueDecide then rogueDecide()end")
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2",
              "and nextUpdates==25 and identity()and r('NumberofLives')==2 and rogueMoves>0 and rogueNext>=25 and r('RdHealthLo')+256*r('RdHealthHi')>0")
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false',
              'Rd_movement_calls=rogueMoves,Rd_1_2_movement_calls=rogueNext,minimum_source_HP=rogueMin,navigation_clock="completed Main snapshots",full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    start=body.index("local stairPhase,stairAge='approach',0")
    end=body.index('emu.addEventCallback(guard(function()\n polls=polls+1',start)
    body=body[:start]+"""local function controls(c)return choose(c)end
rogueDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then rogueInput=controls(context())else rogueInput={}end
end
"""+body[end:]
    body=once(body,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",
              'if menuDone then b=rogueInput end')
    sources={};policy=route(ENTRY,sources)
    text='local C='+Frozen.lua(q)+'\nlocal ROSTER_CONFIG={rogue_tile_attributes=C.rogue_tile_attributes}\nlocal choose=(function()\n'+policy+'\nend)()\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_PIN
    return text


def metadata(raw,key='rogue'):
    q=bindings(raw,key);text=controller(raw,key);sources={};route(ENTRY,sources)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:q[k]for k in('name','slot','owner','cycle','variant')},
        controller_SHA256=sha256(text.encode()).hexdigest(),route_sources=sources,
        current82_common_CHR_reset_preserved=True,legacy421_factories_unchanged=True,
        actual_source_movement_and_positive_health_required=True,normal_controls_only=True,
        full_nonshortcut1_1_then25grounded1_2=True,navigation_clock='completed Main snapshots',
        gameplay_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':print(json.dumps(metadata(ROM.read_bytes()),separators=(',',':')),flush=True)
