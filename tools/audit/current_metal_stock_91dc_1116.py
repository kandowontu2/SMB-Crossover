"""Strict actual91dc Metal carriers and genuine compiled cold/publication."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json,re,zipfile
import inspect_metal_stock_foundation_91dc_1116 as Inventory

R,ROM,PIN,W,N,digest=Inventory.R,Inventory.ROM,Inventory.PIN,Inventory.W,Inventory.N,Inventory.digest
Frames=Inventory.Current.Frames
GRANT=R/'docs/qa/allocations/metal-natural-sl-source-root-1116.json'
GRANT_SHA='972e1232e1fabc2b08e329e588a7a7c098555b995df50f374f2aaec7c760c9cc'
INSPECTOR_SHA='1b4be4a9d5f340c2182c7961f2097e4bc7bd0928e2896f4c8558c15501b8a712'
COOKIE=bytes.fromhex('a7232e7f64f1695d30762600e8451a6c')
NAV=(1,1,1,4,32)


@lru_cache(maxsize=1)
def lease():
    assert digest(GRANT.read_bytes())==GRANT_SHA and digest(Path(Inventory.__file__).read_bytes())==INSPECTOR_SHA
    q=json.loads(GRANT.read_text());assert q['actual_ROM_SHA256']==PIN and q['source_in_memory_gameplay_authorized']
    assert not q['game_byte_or_capacity_changes_authorized']and not q['physical_ROM_native_or_Downloads_authorized']
    assert q['output_root']=='build/metal-natural-sl-source-1116';return q


@lru_cache(maxsize=1)
def labels():
    assert digest(Inventory.PACKET.read_bytes())==Inventory.PACKET_SHA
    with zipfile.ZipFile(Inventory.PACKET)as z:text=z.read('component.lbl')
    assert digest(text)=='2486ea414abcde510d52260e2aad250a29916a2087d7e11eb5b5d9712ae69d1c'
    return{n:int(a,16)for a,n in re.findall(r'^al ([0-9a-fA-F]+) \.(\S+)[ \t\r]*$',text.decode(),re.M)}


@lru_cache(maxsize=1)
def payload(raw):
    lease();assert isinstance(raw,bytes)and digest(raw)==PIN,'Only actual91dc Metal payload'
    q=Inventory.inspect(raw)
    actor=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in Inventory.ACTOR_PAGES)
    renderer=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in Inventory.RENDER_PAGES)
    page=1048592+499*1024;extra=raw[page:page+1024]
    assert extra==Inventory.Current.reference(raw)[page:page+1024]
    return actor,renderer,extra,q


@lru_cache(maxsize=1)
def bundle(raw):
    payload(raw);b=dict(W.Symbols.bundle(),raw=raw);b['syms']=dict(b['syms'])
    for n,pc in labels().items():
        if n.startswith('Ms'):b['syms'][n]=dict(val=hex(pc))
    return b


def check_loaded(m,raw,*,published):
    actor,renderer,extra,_=payload(raw)
    headers=[bytes(m.ram[i][0x1fe0:0x1ff0])for i in(2,3)]
    if published:assert headers==[COOKIE,COOKIE],'Both exact native16 headers before first guest opcode'
    else:
        assert all(h[1:]==COOKIE[1:]and h[0]in(0,0xa7)for h in headers),'Both complete tails before release'
    expected=bytearray(actor);expected[0x1fe0:0x1ff0]=headers[1]
    assert bytes(m.ram[3])==bytes(expected),'All8192 actual actor carrier bytes including declared header cell'
    assert bytes(m.ram[2][0xd00:0x1900])==renderer,'All3072 actual renderer bytes'
    assert bytes(m.ram[2][0x1900:0x1d00])==extra,'All1024 actual extra carrier bytes'
    return dict(actor_bytes=8192,renderer_bytes=3072,extra_carrier_bytes=1024,extra_active_bytes=352,
        actor_SHA256=digest(actor),renderer_SHA256=digest(renderer),extra_carrier_SHA256=digest(extra),both16_headers=[h.hex()for h in headers])


def cold(raw,key='metal',report=False):
    assert key=='metal';b=bundle(raw);lab=labels();base=N.NesMPU;reads={};events=[]
    finish=raw[817022:817022+135];needle=bytes.fromhex('a9a78de0df');assert finish.count(needle)==1
    release=0xb76e+finish.index(needle)+2
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc>=0x8000:
                tag=m.rawtags[(self.pc-0x8000)//8192]
                if(tag,self.pc)==(99|128,release):
                    assert self.a==0xa7
                    witness=check_loaded(m,raw,published=False)
                    if len(events)<2:events.append(dict(PC=self.pc,SP=self.sp,CurrentBankC=N.get(m,'CurrentBankC'),**witness))
                if tag in(2,3)and N.get(m,'SelectedCharacter')==35 and'first_private'not in reads:
                    reads['first_private']=dict(PC=self.pc,SP=self.sp,bank=tag,**check_loaded(m,raw,published=True))
                if(tag,self.pc)==(2,lab['Ms12Movement'])and'first_movement'not in reads:
                    reads['first_movement']=dict(PC=self.pc,SP=self.sp,bank=2,both16_headers=[bytes(m.ram[i][0x1fe0:0x1ff0]).hex()for i in(2,3)])
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
        for pad in NAV:W.UI.key(m,pad)
        assert(W.UI.menu_name(m)[0],N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'),N.get(m,'X5ChrMode'))==('METAL STORM',11,35,0,130)
        assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
        start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            active=tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)
            if active and reads.get('first_movement')and m.ram[2][0x800]==0xa7:break
            m.controller_pad=0;Frames.frame(m,whole_pass=True)if active else Frames.frame(m,cold=True)
        else:raise AssertionError('Actual compiled Metal cold/first worker bound')
    assert events and reads.get('first_private')and reads.get('first_movement')
    assert N.get(m,'SelectedCharacter')==35 and N.get(m,'NumberofLives')==2
    assert all(bytes(m.ram[i][0x1fe0:0x1ff0])==COOKIE for i in(2,3))
    q=dict(actual_ROM_SHA256=PIN,compiled_menu=dict(name='METAL STORM',slot=11,owner=35,variant=0,chr_mode=130,navigation=list(NAV),Easy=0,cheats=[0,0]),
        before_header_release=events,readback=reads,source_title_vblank_limit=True,
        source_state=dict(ready=m.ram[2][0x800],epoch=m.ram[2][0x801],armor=m.ram[2][0x5d0],weapon=m.ram[2][0x718],saved_life=m.ram[2][0x83e]),
        outputs=0,Mesen=False,gameplay_seeds=0)
    return(m,q)if report else m
