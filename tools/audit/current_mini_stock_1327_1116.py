"""Strict actual1327 Mini; inverse00bb is metadata/reference only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json
import compose_jay_status_size_publication_00bb_1116 as Bridge
import inspect_mini_foundation_00bb_1116 as Inventory
import check_bub_current_budget_1113 as Frames

R,ROM,W,H,N=Inventory.R,Inventory.ROM,Inventory.W,Inventory.H,Inventory.W.N
PIN='13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d'
BRIDGE_SHA='7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c'
INVENTORY_SHA='275c7001e35ea6a83df6903ef1ae717345ae181147c176c30cbf21d4266e176b'
KERNEL_SHA='1167be90991080be8d47b09922e51083f78c12a6b987b2ed0bf4ecb6972627a6'
PAYLOAD_SHA='021e14f6ca810695ae3e4c744f7b9bdec60cd1608c12866cf609a982e8bf006b'
COOKIE=bytes.fromhex('a72901021e14f6ca810695ae3e4c744f')
CODE_AT=2033680


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN,'Exact actual1327 Mini only'
    assert H(Path(Bridge.__file__).read_bytes())==BRIDGE_SHA
    assert H(Path(Inventory.__file__).read_bytes())==INVENTORY_SHA
    parent=Bridge.inverse(raw);assert H(parent)==Inventory.PIN;return parent


@lru_cache(maxsize=1)
def bindings(raw):
    parent=reference(raw);proof=Inventory.inspect(parent);b=dict(W.Symbols.bundle(),raw=raw)
    assert b['raw']is raw and raw[CODE_AT:CODE_AT+7168]==parent[CODE_AT:CODE_AT+7168]
    assert H(raw[CODE_AT:CODE_AT+7168])==PAYLOAD_SHA and H(raw[CODE_AT:CODE_AT+5120])==KERNEL_SHA
    assert raw[536595:536611]==parent[536595:536611]==COOKIE
    hooks={}
    for name,pc in(('MiniMovementVector',0xa000),('MiniHostMain',0xae4d),('MiniStep',0xa3e5),('MiniHostFresh',0xaf11),('MiniHostBox',0xb255),('MiniHostPickup',0xb3da),('MiniHostPowerup',0xb3f1)):
        at=CODE_AT+pc-0xa000;assert raw[at:at+16]==parent[at:at+16]
        hooks[name]=dict(PC=pc,tag=3,first16_hex=raw[at:at+16].hex(),physical=3*8192+pc-0xa000)
    for name in('GameLoop','HandlePowerUpCollision','MarioSourcePowerupCollision','GuestBeginPowerup','GuestPowerupUpdate','PlayerMovementSubs'):
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        assert raw[at:at+16]==parent[at:at+16]
        hooks[name]=dict(PC=pc,tag=bank|128,file_offset=at,first16_hex=raw[at:at+16].hex(),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    banks=[]
    for bank in(1,3,10,11,26,65,89,124,126):
        at=16+bank*8192;actual,old=raw[at:at+8192],parent[at:at+8192]
        banks.append(dict(bank=bank,actual_SHA256=H(actual),reference_SHA256=H(old),changed_bytes=sum(a!=z for a,z in zip(actual,old,strict=True))))
    return dict(bundle=b,hooks=hooks,full_bank_pins=banks,metadata_reference_SHA256=Inventory.PIN,
        metadata_reference_receipt=H(json.dumps(proof,sort_keys=True,separators=(',',':')).encode()),actual_CPU_SHA256=PIN,bridge_SHA256=BRIDGE_SHA,
        payload_SHA256=PAYLOAD_SHA,kernel_SHA256=KERNEL_SHA,cookie=COOKIE.hex(),Mini962_968_and_cookie_exact=True,
        source_helpers_or_game_bytes_changed=False,outputs=0)


def metadata(raw):
    q=bindings(raw);return{k:v for k,v in q.items()if k!='bundle'}


def cold(raw,report=False):
    q=bindings(raw);b=q['bundle'];base=N.NesMPU;reads={};pending=[];counts={n:0 for n in('public movement','MiniStep')};returns=dict(counts);first={}
    code=raw[CODE_AT:CODE_AT+5120]
    class CPU(base):
        def step(self):
            m=self.memory
            for t in tuple(pending):
                if(self.pc,self.sp)==(t['returnPC'],t['returnSP']):
                    pending.remove(t);returns[t['name']]+=1
                    if t['name']not in first:first[t['name']]=dict(t,returned_epoch=m.ram[2][0x301],ready=m.ram[2][0x300])
            if self.pc>=0x8000:
                tag=m.rawtags[(self.pc-0x8000)//8192]
                if tag==3 and 0xa000<=self.pc<0xb400 and not reads:
                    assert bytes(m.ram[3][:5120])==code
                    assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])==COOKIE
                    reads.update(PC=self.pc,SP=self.sp,kernel_bytes=5120,kernel_SHA256=KERNEL_SHA,both16B_cookie=COOKIE.hex())
                if tag==3 and self.pc in(0xa000,0xa3e5):
                    name='MiniStep'if self.pc==0xa3e5 else'public movement';counts[name]+=1;sp=self.sp
                    pc=(m[256+((sp+1)&255)]+256*m[256+((sp+2)&255)]+1)&65535
                    pending.append(dict(name=name,PC=self.pc,SP=sp,returnPC=pc,returnSP=(sp+2)&255,epoch=m.ram[2][0x301]))
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
        cycle=[]
        for _ in range(8):
            W.UI.key(m,32);cycle.append(dict(name=W.UI.menu_name(m)[0],variant=N.get(m,'MarioVariant'),owner=N.get(m,'SelectedCharacter')))
        assert(W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'))==('MINI MARIO',41,8)
        assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
        start=W.UI.key(m,16);N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P']);N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;Frames.frame(m,cold=True)
        else:raise AssertionError('Actual1327 compiled Mini constructor bound')
        before=dict(counts)
        for _ in range(16):
            m.controller_pad=0;Frames.frame(m,whole_pass=True)
            assert(N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'),N.get(m,'PlayerStatus'),N.get(m,'NumberofLives'))==(41,8,0,2)
    assert m.bundle['raw']is raw and H(m.bundle['raw'])==PIN and reads and not pending and counts==returns
    assert all(counts[n]-before[n]==16 for n in counts)
    proof=dict(passed=True,actual_CPU_SHA256=PIN,metadata_reference_only_SHA256=Inventory.PIN,compiled_Select8=cycle,
        first_private_readback=reads,entries=counts,returns=returns,first_actual_returns=first,neutral_returned_updates=16,
        terminal={n:N.get(m,n)for n in('SelectedCharacter','MarioVariant','PlayerStatus','PlayerSize','NumberofLives','GameEngineSubroutine','Player_X_Position','Player_PageLoc','Player_Y_Position')},
        MiniReady=m.ram[2][0x300],MiniEpoch=m.ram[2][0x301],source_menu_vblank_limit=True,
        scope='Actual1327 compiled UI/cold and16 public+original MiniStep returns; inverse00bb metadata only, no item/fullstage/native/cadence claim',outputs=0,Mesen=False,gameplay_seeds=0)
    return(m,proof)if report else m
