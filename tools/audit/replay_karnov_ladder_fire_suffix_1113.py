"""Separate normal-fire/terrain-aware ordinary controller after earned Bomb."""
import argparse
from hashlib import sha256
import json
from multiprocessing.connection import Listener
import zipfile
from unittest.mock import patch

import replay_karnov_ladder_early_1113 as Frozen

PIN='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
BASE='7d1ea719a760ac0dedb17fedde3705d5ccfdc67d1af34018efc017f859c79091'
SCRIPT='7d5f87b634174a4e35b282389569b5bb7059d1801d90522413e9051e33b9a50b'
SOURCE=Frozen.SOURCE.with_name('karnov_ladder_fire_suffix_1113.lua')


def controller(raw):
    assert sha256(raw).hexdigest()==PIN
    text=Frozen.current_controller(raw);assert sha256(text.encode()).hexdigest()==BASE
    b=dict(Frozen.Late.Native.W.Symbols.bundle(),raw=raw)
    prefix='local FIRE_CONTACT_OFFSET='+str(Frozen.Late.Native.W.location(b,'HandleEnemyFBallCol')-16)+'\n'
    prefix+='local FIRE_TERRAIN_BASE='+str(Frozen.Late.Native.W.address(b,'MmSolidTerrain'))+'\n'
    point='local function mapped(pc,physical)';assert text.count(point)==1
    text=text.replace(point,SOURCE.read_text()+'\n'+point)
    point='native_blast_contacts=blastCalls,fifth=stockFifth';assert text.count(point)==1
    text=text.replace(point,point+',normal_fire=stockFifth.normal_fire')
    text=prefix+text
    assert all(word not in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    Frozen.Late.LuaRuntime().compile(text)
    assert sha256(text.encode()).hexdigest()==SCRIPT,'Frozen experimental terrain/fire controller'
    return text


def cpu(raw,limit=12000):
    with patch.object(Frozen.Late,'controller',controller):q=Frozen.Late.run(raw,limit=limit)
    q['ROM_SHA256']=PIN
    q['normal_fire']=q['fifth'].get('normal_fire')
    q['receipt']={key:q['receipt'].get(key)for key in('passed','reason')}if q['receipt']else None
    q.pop('geometry',None);q.pop('actors',None)
    q['fifth']={key:q['fifth'].get(key)for key in('stage','site','art','grown','climbed','complete','restored_cells','restored_attributes')}
    return q


def component_check(raw):
    """Synthetic readonly controller cases plus owning-source muzzle proof."""
    packet=Frozen.Late.Feature.Owner.R/'docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/source.zip'
    assert sha256(packet.read_bytes()).hexdigest()=='ae5e53e01d7796f6d5beab97668b4f02a270c5dc60027d1cda181b6dfe11f777'
    with zipfile.ZipFile(packet)as z:
        actor=z.read('host/kr-host-actor.inc').decode();host=z.read('host/kr-terrain.inc').decode()
        combat=z.read('host/kr-combat-v7.inc').decode();controls=z.read('host/kr-options-host-v8.inc').decode()
    assert 'Kr_FAFD: .byte $20'in actor and 'Kr_FB03: .byte $18'in actor
    assert 'adc #32\n sta KrState+$64'in host
    assert 'lda KrState+$70,x\n clc\n adc #8\n sta KC_Y'in combat
    assert 'lda KC_Y\n clc\n adc #4\n and #$f0'in combat
    assert 'jsr Kr_C28C\n beq KrOptionsUnhandled'in controls
    for tile in('23','26','c2','c3','5f','60'):assert 'cmp #$'+tile+'\n beq KcNoBlock'in combat
    b=dict(Frozen.Late.Native.W.Symbols.bundle(),raw=raw)
    at=Frozen.Late.Native.W.location(b,'MTileAttribute');attributes=raw[at:at+256]
    lua=Frozen.Late.LuaRuntime(unpack_returned_tuples=True)
    lua.globals().ATTR=lua.table_from(dict(enumerate(attributes)))
    prefix=r'''
local pickups={1,2,3,4};local armed,blastSeen,done,game=true,true,false,false
local frame=0;local stockFifth={stage='travel'};local L={HandleEnemyFBallCol=0}
local MTILE_ATTRIBUTES_OFFSET,FIRE_TERRAIN_BASE,FIRE_CONTACT_OFFSET=10000,20000,0
local registers={Player_State=0,Player_Y_Position=176,PlayerFacingDir=1}
local work={[0x8e]=255,[0x8f]=0,[0xc0]=0,[0xe8]=0};local tiles,terrain={},{}
local function r(n)return registers[n]or 0 end
local function kr(a)return work[a]or 0 end
local function wx()return 849 end
local function state()return{x=wx(),y=r('Player_Y_Position')}end
local enemies={};local function actor(i)return enemies[i]or{flag=0,id=0,state=0,x=0,y=0,slot=i}end
local function key(x,y)return(x//16)..':'..(y//16)end
local function tile(x,y)return tiles[key(x,y)]or 0 end
local function set(x,y,t,flag)
 tiles[key(x,y)]=t
 terrain[((x//256)%2)*208+((y-32)//16)*16+(x%256)//16]=flag or 0
end
local function fifthClearEnemy()return 77 end
local function fifthEnemyNear()return true end
local function control()return 129 end
local emu={memType={nesDebug=0,nesPrgRom=1},callbackType={exec=0}}
emu.read=function(at,kind)
 if kind==1 then return ATTR[at-10000]or 0 end
 return terrain[at-20000]or 0
end
emu.addMemoryCallback=function()end
'''
    tests=r'''
local checks=0
for _,t in ipairs({0,35,38,194,195,95,96})do set(864,196,t);assert(not shotCell(864,196).blocked);checks=checks+1 end
set(864,196,82,0);assert(shotCell(864,196).brick);checks=checks+1
set(864,196,82,1);assert(shotCell(864,196).blocked and not shotCell(864,196).brick);checks=checks+1
set(864,196,97);assert(shotCell(864,196).blocked);checks=checks+1
set(864,188,82,0);set(864,196,82,0);assert(terrainFire(849,176)==64);checks=checks+1
set(864,188,35);assert(terrainFire(849,176)==64);checks=checks+1
set(864,188,0);assert(terrainFire(849,176)==68);checks=checks+1
set(864,196,35);assert(terrainFire(849,176)==68);checks=checks+1
set(864,196,0);assert(terrainFire(849,176)==nil);checks=checks+1
work[0xe8]=6;set(864,188,82,0);assert(terrainFire(849,176)==0);set(864,188,0);work[0xe8]=0;checks=checks+1
enemies[1]={flag=1,id=6,state=0,x=916,y=184,slot=1}
assert(fifthClearEnemy(849,176)==68);checks=checks+1
enemies[1].x=840;assert(fifthClearEnemy(849,176)==nil);checks=checks+1
enemies[1].x=916;set(880,196,97);assert(fifthClearEnemy(849,176)==nil);checks=checks+1
set(880,196,0);work[0x8e]=1;assert(control()==32);checks=checks+1
work[0x8e]=255;assert(control()==129 and work[0x8f]==0);checks=checks+1
pickups={1,2,3};assert(control()==129 and fifthClearEnemy(849,176)==77);checks=checks+1
return checks
'''
    cases=lua.execute(prefix+SOURCE.read_text()+tests)
    return dict(synthetic_controller_only=True,checks=cases,real_current_tile_attributes=True,
        owning_source_SHA256='ae5e53e01d7796f6d5beab97668b4f02a270c5dc60027d1cda181b6dfe11f777',
        standing_combat_center_offset=12,crouch_combat_center_offset=20,empty_Bomb_retains_B=True,
        runtime_field_writes_or_grants=0,full_route_or_native_claim=False)


def development(raw):
    """One genuine prefix, then ordinary-input forks; never a full proof."""
    with patch.object(Frozen.Late,'controller',controller):
        prefix,seed=Frozen.Late.run(raw,limit=7600,checkpoint_x=800,checkpoint_pickups=4,return_model=True)
    assert len(prefix['pickups'])==4 and prefix['source']['health']==0,prefix
    assert prefix['terminal']['x']>=800,prefix
    models={'seed':seed}
    def probe(model,limit):
        with patch.object(Frozen.Late,'controller',controller):
            return Frozen.Late.run(raw,input_model=Frozen.Late.Native.N.fork(model),history=prefix['pickups'],
                limit=limit,return_model=True)
    q,model=probe(seed,3000);models['first']=model
    print('KARNOV_FIRE_SUFFIX_DEVELOPMENT '+json.dumps(dict(prefix_Main=prefix['actual_Main_NMI_updates'],
        genuine_prefix_derived_fork=True,final_unbroken_claim=False,result=q),separators=(',',':')),flush=True)
    if q['passed']:return
    with Listener(('127.0.0.1',0),authkey=b'karnov-fire-suffix-1113')as listener:
        print('KARNOV_FIRE_SUFFIX_MEMORY_READY '+json.dumps(dict(port=listener.address[1],models=list(models))),flush=True)
        while True:
            with listener.accept()as connection:
                command=connection.recv()
                if command['op']=='close':connection.send(dict(closed=True));break
                assert command['op']=='suffix'and command.get('from','seed')in models
                assert len(models)<6
                q,m=probe(models[command.get('from','seed')],min(command.get('limit',1800),3000))
                models[command['name']]=m;connection.send(q)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cpu',action='store_true')
    p.add_argument('--limit',type=int,default=12000);p.add_argument('--develop',action='store_true')
    p.add_argument('--component-check',action='store_true');args=p.parse_args()
    raw=Frozen.Late.Feature.Owner.NIGHTLY.read_bytes()
    if args.develop:development(raw)
    elif args.cpu:
        q=cpu(raw,args.limit);print(json.dumps(q,separators=(',',':')),flush=True);assert q['passed']
    else:
        text=controller(raw);print(json.dumps(dict(ROM_SHA256=PIN,base_SHA256=BASE,
            controller_SHA256=sha256(text.encode()).hexdigest(),bytes=len(text),Lua_compile=True,
            ROM_or_runtime_writes=0,outputs=0,Mesen_run=False,
            component=component_check(raw)if args.component_check else None)),flush=True)
