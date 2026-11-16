"""Strict current Mini natural Mushroom controller; source/native API, no runs."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile
import json,re
import current_mini_stock_1327_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.H
GRANT=R/'docs/qa/allocations/mini-natural-stock-source-root-1116.json'
GRANT_SHA='c14b33a23d5afc19a9513e35aa14dcbe68f24ddc51e6344b7e3662f5b5c70153'
CURRENT_SHA='4c04b9df54ef434dd11aa02d8ed1aab59b123652705f857b4dfca3018e5a036f'
TEMPLATE=R/'tools/playthroughs/mini_natural_mushroom_1327_1116.lua'


@lru_cache(maxsize=1)
def controls():
    assert H(GRANT.read_bytes())==GRANT_SHA;g=json.loads(GRANT.read_bytes())
    assert g['ROM_SHA256']==PIN and g['source_in_memory_gameplay_authorized']and not g['game_bytes_physical_ROM_native_Downloads_authorized']
    assert H(Path(Current.__file__).read_bytes())==CURRENT_SHA
    I=Current.Inventory;assert H(I.PACKET.read_bytes())==I.PACKET_SHA
    name=next(n for n in I.MEMBERS if n.endswith('controller.lua'))
    with ZipFile(I.PACKET)as z:text=z.read(name)
    assert H(text)==I.MEMBERS[name]
    for line in("if power.phase=='approach'and s.x/16<280",'if s.x>=304*16 and s.contacts&1~=0',"route_pad={right=x<item.x+1,left=x>item.x+7}"):
        assert line in text.decode()
    return dict(path=I.PACKET.relative_to(R).as_posix(),member=name,SHA256=I.MEMBERS[name],scope='Input formulas only; no old controller execution or stale hooks/defaultbuild')


@lru_cache(maxsize=1)
def bindings(raw):
    controls();q=Current.bindings(raw);b=q['bundle'];body=TEMPLATE.read_text();names=set(re.findall(r"r\('([^']+)'",body))
    names.update(re.findall(r'C\.ram\.(\w+)',body))
    names.update(('Player_X_Position','Player_PageLoc','Enemy_X_Position','Enemy_PageLoc','BoundingBox_UL_Corner','EnemyBoundingBoxCoord'))
    ram={n:W.address(b,n)for n in names};hooks={}
    def native(name,pc,at):
        bank=(at-16)//8192;hooks[name]=dict(pc=pc,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    def private(name,pc,n=4):hooks[name]=dict(pc=pc,offset=3*8192+(pc&8191),work=True,bytes=list(raw[Current.CODE_AT+pc-0xa000:Current.CODE_AT+pc-0xa000+n]),kernel_SHA256=Current.KERNEL_SHA)
    for n in('GameLoop','HandlePowerUpCollision','MarioSourcePowerupCollision','EraseEnemyObject','SetupFloateyNumber','GuestPowerupUpdate'):
        native(n,W.address(b,n),W.location(b,n))
    for name,pc,n in(('MiniMovement',0xa000,3),('MiniStep',0xa3e5,4),('MiniPickupVector',0xa048,3),('MiniPickup',0xb3da,4),('MiniPowerup',0xb3f1,4)):private(name,pc,n)
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');needle=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little');hits=[i+3 for i in range(61)if raw[at+i:at+i+3]==needle];assert len(hits)==2
    for i,k in enumerate(hits):native('MainReturn'+str(i),pc+k,at+k)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=ram['FloateyNum_Timer'];needle=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1;native('ScoreDEC',pc+hits[0],at+hits[0])
    pc,at=W.address(b,'PowerUpObjHandler'),W.location(b,'PowerUpObjHandler');needle=bytes((0xb5,ram['Enemy_State'],0xc9,6));hits=[i for i in range(300-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1;native('PowerMin6',pc+hits[0],at+hits[0])
    return dict(sha=PIN,ram=ram,hooks=hooks,kernel_hex=raw[Current.CODE_AT:Current.CODE_AT+5120].hex(),cookie=Current.COOKIE.hex())


@lru_cache(maxsize=1)
def controller(raw,key='mushroom'):
    assert key=='mushroom';text='local C='+Text.lua(bindings(raw))+'\n'+TEMPLATE.read_text();LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='mushroom'):
    assert key=='mushroom';return dict(ROM_SHA256=PIN,factory_SHA256=H(Path(__file__).read_bytes()),facade_SHA256=CURRENT_SHA,template_SHA256=H(TEMPLATE.read_bytes()),controller_SHA256=H(controller(raw).encode()),grant_SHA256=GRANT_SHA,control_reference=controls(),current_full_bank_pins=Current.bindings(raw)['full_bank_pins'],scope='Current compiled Mini mature natural M/wholeC1/nativepickup1/1000/actual60/25 returned original MiniStep+public at actual Main',outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
