"""Existing-code075B1/2 consumer units, never earned/candidate gameplay proof."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_full_fresh_current_1115 as C

N,W,Game,Frames=C.Base.N,C.Base.Candidate.W,C.Base.Candidate.Game,C.Base.Candidate.Frames
PIN='7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79'


def snapshot(m):
    names=('SelectedCharacter','PlayerStatus','PlayerSize','GameEngineSubroutine','OperMode','OperMode_Task',
        'TimerControl','FireballCounter','MegaManShotPose','Square1SoundQueue','Square2SoundQueue',
        'GuestPowerupActive','GuestPowerupTarget','GuestPowerupOld','VRAM_Buffer1_Offset','VRAM_Buffer_AddrCtrl',
        'NumberofLives','InjuryTimer','AreaType','GamePauseStatus')
    q={name:N.get(m,name)for name in names if name in m.bundle['syms']}
    q.update(private_HP=m.ram[2][0x6cf],private_Sword=m.ram[2][0x6ee],private_Ready=m.ram[2][0xab],
        maps=list(m.rawtags),latches=list(m.chr_latches),
        fireballs=[N.get(m,'Fireball_State',i)for i in range(2)])
    for name,size in(('VRAM_Buffer1',256),('VRAM_Buffer2',256)):
        if name in m.bundle['syms']:
            at=W.address(m.bundle,name);data=bytes(m[at:at+size]);q[name]=list(data)
    return q


def run(raw):
    assert sha256(raw).hexdigest()==PIN
    # Explicit exact owning image for this cold model only. No old API is
    # widened; the public native routines tested below are the actual bytes.
    def parent(image):assert image==raw;return raw
    with patch.object(Game,'proof_parent',parent):m,opening=Game.cold(raw)
    for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert N.get(m,'SelectedCharacter')==38 and m.ram[2][0x6cf]==5 and m.ram[2][0x6ee]==0
    rows=[];base_cpu=N.NesMPU
    calls=('NrObjectWeaponTail','ProcFireball_Bubble','GetPlayerColors','NrColors','SetupIntermediate',
        'InventorySupported','InventoryHas','RemainingPower','NrInjuryStatus','ForceInjury',
        'PwrUpJmp','KillPlayer','NativeRareRunGameOverCore::ContinueGame','NrFullPower')
    for name in calls:
      if name not in m.bundle['syms']:
        rows.append(dict(name=name,missing_symbol=True));continue
      pc=W.address(m.bundle,name);at=W.location(m.bundle,name)
      for tier in(1,2):
        b=N.fork(m);N.put(b,PlayerStatus=tier)
        # Declared ordinary-button precondition for the two weapon leaves.
        if name in('NrObjectWeaponTail','ProcFireball_Bubble'):
            N.put(b,A_B_Buttons=64,PreviousA_B_Buttons=0,SavedJoypad1Bits=64,SavedJoypadBits=64)
        before=snapshot(b);access=[]
        class CPU(base_cpu):
            def step(self):
                pc0=self.pc;model=self.memory
                if pc0>=0x8000 and bytes(model[pc0+1:pc0+3])==b'\x5b\x07':
                    access.append(dict(PC=pc0,SP=self.sp,tag=model.rawtags[(pc0-0x8000)//8192],
                        bytes=bytes(model[pc0:pc0+3]).hex(),A=self.a,X=self.x,Y=self.y,P=self.p))
                    assert len(access)<64,'Bounded current consumer path'
                return super().step()
        error=None;result=None
        try:
            with patch.object(N,'NesMPU',CPU):result=N.invoke(b,name,a=0,x=5 if name=='PwrUpJmp'else 0,y=0,p=0x21)
        except (AssertionError,KeyError,IndexError)as failure:error=repr(failure)
        after=snapshot(b)
        rows.append(dict(name=name,tier=tier,entry=dict(PC=pc,physical=at,bytes=raw[at:at+12].hex()),
            before=before,after=after,result=result,error=error,actual075B_accesses=access))
    # Actual compiled menu Select from Prince to its Excitebike sibling.
    bundle=dict(W.Symbols.bundle(),raw=raw);prior=N.Bus;N.Bus=W.ControllerBus
    try:menu=W.UI.seed(bundle,29)
    finally:N.Bus=prior
    W.UI.key(menu,32);assert N.get(menu,'SelectedCharacter')==38
    N.put(menu,PlayerStatus=2);menu_before=dict(character=N.get(menu,'SelectedCharacter'),tier=N.get(menu,'PlayerStatus'))
    W.UI.key(menu,32);menu_after=dict(character=N.get(menu,'SelectedCharacter'),tier=N.get(menu,'PlayerStatus'))
    q=dict(diagnostic_complete=True,ROM_SHA256=PIN,opening=opening,units=rows,
        actual_compiled_Select=dict(before=menu_before,after=menu_after),
        declared_unit_inputs='Only native075B1/2 and ordinary weapon button fields on clones of actual cold Prince; explicit public routine calls. No earned tier2 or candidate/gameplay claim.',
        mounted_code=0,ROM_modified=False,source_mask_used=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Tier2 units attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
