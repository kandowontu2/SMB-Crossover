"""New GB Pit natural firstM controls on explicit actual owning images."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from copy import deepcopy
import re
import current_gb_pit_stock_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,W,N,H=Current.R,Current.ROM,Current.W,Current.N,Current.H
TEMPLATE=R/'tools/playthroughs/smb1_toad_mushroom_91dc_1116.lua'
CONTROL=R/'tools/playthroughs/smb1_toad_native_mushroom_controls_91dc_1116.lua'
POLICY=R/'tools/playthroughs/pit_rygar_sophia_policy.lua'
PINS={TEMPLATE:'37f1f9eb0e63f6713a46ffbdb6559d5d70662c19874ae5ad9ab1f821592b427c',
      CONTROL:'43182f991998686012f373319ff84d32216f06bff9908e65da47c3db0930c0da',
      POLICY:'c45a2c78cf036ee39076a5befa293843447658a4d3fb7816831c367688b1e001'}
CURRENT_SHA='197f0ecdd9543471b483e4ce6e65d31bfeb33ce0a85a3f706354a05acf6ddd57'

def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)

def body():
    for path,pin in PINS.items():assert H(path.read_bytes())==pin
    s=TEMPLATE.read_text();s=s.replace('MarioVariant','PitVariant').replace('MarioSourceMovement','ExpandedMovement').replace('MarioSourcePowerupUpdate','GuestPowerupUpdate')
    s=s.replace('Mario_entries=guestEntries,Mario_returns=guestReturns','PitMovement_entries=guestEntries,PitMovement_returns=guestReturns,PitFlight_entries=pitEntries,PitFlight_returns=pitReturns')
    s=s.replace('SMB1 Toad','GB Pit').replace('returned Mario movements','returned Pit movements').replace('resumed Mario returns','resumed Pit returns')
    s=s.replace('pendingMain=pendingMain~=nil,pendingGuest=pendingGuest~=nil,pendingCollect=pendingCollect~=nil,','pendingMain=pendingMain~=nil,pendingGuest=pendingGuest~=nil,pendingCollect=pendingCollect~=nil,pendingPit=pendingPit~=nil,')
    s=once(s,'local pendingMain,pendingGuest,pendingCollect','local pitEntries,pitReturns=0,0\nlocal pendingMain,pendingGuest,pendingCollect,pendingPit')
    s=once(s,"r('SelectedCharacter')==0 and r('PitVariant')==5 and r('X5ChrMode')==131,'Actual compiled GB Pit'","r('SelectedCharacter')==6 and r('PitVariant')==1,'Actual compiled GB Pit'")
    s=once(s,'char=0,variant=5','char=6,variant=1')
    s=once(s,"variant=r('PitVariant'),chr_mode=r('X5ChrMode')","variant=r('PitVariant'),chr_mode=r('X5ChrMode'),fuel=r('XgPitFuel'),flight=r('XgPitFlight')")
    s=once(s,'local function drive()','local firstM=(function()\n'+CONTROL.read_text()+'\nend)()\nlocal function drive()')
    s=once(s,'buttons=travel(context())','buttons=firstM(context())')
    s=once(s,'or pendingMain or pendingGuest or pendingCollect then return end','or pendingMain or pendingGuest or pendingCollect or pendingPit then return end')
    s=once(s,'if not food.resumeBase then food.resumeBase=guestReturns end','if not food.resumeBase then food.resumeBase=guestReturns;food.pitBase=pitReturns end')
    s=once(s,"assert(mainEntries==mainReturns and guestEntries==guestReturns,'Balanced completed native calls')","assert(mainEntries==mainReturns and guestEntries==guestReturns and pitEntries==pitReturns and pitReturns-food.pitBase>=25,'Balanced Main and25 actual returned movement/ability calls')")
    marker="hook('HandlePowerUpCollision',function()"
    observer="""hook('PitFlightUpdate',function()
 identity();assert(not pendingPit,'Prior Pit ability returned');pitEntries=pitEntries+1
 pendingPit=returning(function(t)pendingPit=nil;pitReturns=pitReturns+1 end)
end)
"""
    s=once(s,marker,observer+marker)
    old="assert(r('CrossoverMenuIndex')==0);for _=1,2 do press({select=true})end\n assert(r('SelectedCharacter')==0 and r('PitVariant')==5 and r('X5ChrMode')==131,'Compiled Toad Select2')"
    new="assert(r('CrossoverMenuIndex')==0);press({left=true});press({left=true});press({select=true})\n assert(r('CrossoverMenuIndex')==6 and r('SelectedCharacter')==6 and r('PitVariant')==1,'Actual compiled GB Pit Select alternate')"
    s=once(s,old,new)
    assert 'MarioSourceMovement'not in s and 'emu.write'not in s
    return s

@lru_cache(maxsize=1)
def bindings(raw):
    assert H(Path(Current.__file__).read_bytes())==CURRENT_SHA
    source=body();old=Current.bindings(raw);b=old['bundle'];c={k:deepcopy(v)for k,v in old.items()if k!='bundle'}
    names=set(re.findall(r"r\('([A-Za-z0-9_]+)'",source+POLICY.read_text()+CONTROL.read_text()))
    for name in names:c['ram'][name]=W.address(b,name)
    for name in('GameLoop','ExpandedMovement','PitFlightUpdate','HandlePowerUpCollision','GuestBeginPowerup','GuestPowerupUpdate','EraseEnemyObject','SetupFloateyNumber'):
        c['hooks'][name]=Current.hook(b,name,8)
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==call];assert len(returns)==2 and returns[0]==12
    for i,n in enumerate(returns):
        bank=(at-16)//8192;c['hooks']['MainReturn'+str(i)]=dict(pc=pc+n,offset=at+n-16,bank=bank,bytes=list(raw[at+n:at+n+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=c['ram']['FloateyNum_Timer']
    needle=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    n=hits[0];bank=(at-16)//8192;c['hooks']['StockTimerDEC']=dict(pc=pc+n,offset=at+n-16,bank=bank,bytes=list(raw[at+n:at+n+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    h=c['hooks']['ExpandedMovement'];c['movement_hex']=raw[16+h['offset']:16+h['offset']+64].hex()
    return c

@lru_cache(maxsize=1)
def controller(raw,key='mushroom'):
    assert key=='mushroom';text='local C='+Text.lua(bindings(raw))+'\nlocal travel=(function()\n'+POLICY.read_text()+'\nend)()\n'+body()
    LuaRuntime().compile(text);assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='mushroom'):
    text=controller(raw,key)
    return dict(ROM_SHA256=H(raw),owner_role=Current.OWNERS[H(raw)],factory_SHA256=H(Path(__file__).read_bytes()),facade_SHA256=CURRENT_SHA,
        controller_SHA256=H(text.encode()),reference_only_sources={p.name:pin for p,pin in PINS.items()},
        hooks=bindings(raw)['hooks'],scope='Compiled GB Pit/raw6/variant1, authored firstM real emergence/mature physical collector/erase/cue/1000/60tier1 then25 returned ExpandedMovement+PitFlight at completedMain; no standaloneHP pool or otherstock/full claim',
        old_APIs_unchanged=True,gameplay_seeds=0,game_bytes_changed=0,outputs=0,Mesen=False)

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
