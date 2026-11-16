"""Strict current91dc Excitebike ownership; inverse is reference only."""
from functools import lru_cache
from pathlib import Path
import re
from unittest.mock import patch
import compose_battletoads_mature8_1116 as BT
import check_ff_white_mushroom_current_1110 as W
import check_smb1_alts_full11_1114 as Runner

R,ROM,PIN,N,Frames,digest=BT.R,BT.ROM,BT.CANDIDATE,W.N,Runner.Frames,BT.digest
START=1048592+728*1024
COOKIE=536554
KERNEL='c9d92bfd61e73d413319408148b61379aab2084b66e24e55b28e2f3df5055e11'
META='6a35a9650d07daa537452734ec9d9204f75b3188957ab2621373f1cde3a5782b'
ART='084cc38b99f20c7cd630423feb1c59350fb35cc0975e69d026d6d9ed171e60fd'
COOKIE_HEX='a72503f6e4938f326baa12f2df77b97a'
LABELS=R/'build/excitebike-pose-1101-v3/heat-host.lbl'
NAV=[4,4,4,1,1,1,1,1]

@lru_cache(maxsize=1)
def reference(raw):return BT.inverse(raw)

@lru_cache(maxsize=1)
def preservation(raw):
    parent=reference(raw)
    extents=[('kernel',START,6144,KERNEL),('metadata',START+6144,2048,META),('art',START+8192,3072,ART)]
    for name,at,size,h in extents:assert digest(raw[at:at+size])==h and raw[at:at+size]==parent[at:at+size],name
    assert raw[COOKIE:COOKIE+16]==parent[COOKIE:COOKIE+16]==bytes.fromhex(COOKIE_HEX)
    assert raw[START+0x563:START+0x566]==bytes.fromhex('4c7aaf')
    assert raw[START+0xf7a:START+0xf8c]==bytes.fromhex('8d6a01a9998d6c01a9b28d6d01a98a4c5a01')
    assert raw[START+0xd18:START+0xd1d]==bytes.fromhex('4c8cafeaea')and raw[START+0xd65]==21
    assert raw[START+0xf8c:START+0xfa4]==bytes.fromhex('a203bd62ad9d4b01bda0af9de473ca10f14c28ad82828280')
    return dict(actual_execution_SHA256=PIN,strict_inverse_reference_6a3=digest(parent),
        Ex_extents=[dict(name=n,file=a,bytes=s,SHA256=h)for n,a,s,h in extents],full16_cookie=COOKIE_HEX,
        delivered_BT27_preserved=True,blank_alias_AF8C_preserved=True,game_bytes_changed=0,outputs=0)

@lru_cache(maxsize=1)
def bundle(raw):
    preservation(raw);b=dict(W.Symbols.bundle(),raw=raw);b['syms']=dict(b['syms'])
    # Only this retained owner's labels supplement the canonical native symbols.
    # The complete current kernel, metadata, art and cookie are pinned above.
    labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',LABELS.read_text(),re.M)}
    assert(labels['ExHostConstruct'],labels['ExHostMovement'],labels['ExMotorAll'],labels['ExAirLaunch'])==(0xa963,0xaa3e,0xa000,0xa388)
    for name,pc in labels.items():
        if name.startswith('Ex'):b['syms'][name]=dict(val=hex(pc))
    return b

def cold(raw,key='excitebike',report=False):
    assert key=='excitebike';b=bundle(raw);reads=[];base=N.NesMPU
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc==0xa963 and m.rawtags[1]==3 and not reads:
                assert bytes(m.ram[3][:6144])==raw[START:START+6144]
                assert bytes(m.ram[2][0x1000:0x1800])==raw[START+6144:START+8192]
                for bank in(2,3):assert bytes(m.ram[bank][0x1fe0:0x1ff0])==raw[COOKIE:COOKIE+16]
                reads.append(dict(PC=self.pc,SP=self.sp,kernel_bytes=6144,metadata_bytes=2048,both_full16_cookies=COOKIE_HEX))
            return super().step()
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in NAV:W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='EXCITEBIKE'and N.get(m,'CrossoverMenuIndex')==29 and N.get(m,'SelectedCharacter')==37
    assert N.get(m,'FmAlts')&16==0 and N.get(m,'CrossoverBehaviorVersion')==0
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    with patch.object(N,'NesMPU',CPU):
        for _ in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;Frames.frame(m,cold=True)
        else:raise AssertionError('Actual Excitebike compiled constructor bound')
    assert reads and m.ram[2][0x800]==0xa7 and N.get(m,'NumberofLives')==2 and N.get(m,'PlayerStatus')==0
    assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0 and m.bundle['raw']is raw
    q=dict(actual_ROM_SHA256=PIN,name='EXCITEBIKE',slot=29,raw_owner=37,Select_cycles=0,
        first_constructor_readback=reads[0],frontend='Compiled menu/Start/parser; source bus lacks real title vblank',outputs=0,Mesen=False)
    return(m,q)if report else m
