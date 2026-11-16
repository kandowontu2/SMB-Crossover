"""Actual compiled Mini selection/cold/16 neutral public returns, no item route."""
from pathlib import Path
from unittest.mock import patch
import json
import inspect_mini_foundation_00bb_1116 as Inventory
import check_bub_current_budget_1113 as Frames
import run_stdout_mesen_1110 as Native

W,N,R,H=Inventory.W,Inventory.W.N,Inventory.R,Inventory.H


def run(raw):
    assert H(raw)==Inventory.PIN
    b=dict(W.Symbols.bundle(),raw=raw);base=N.NesMPU;reads={};entries=0;returns=0;pending=[];first=None
    step_entries=0;step_returns=0;first_step=None
    code_at=1048592+962*1024;code=raw[code_at:code_at+5120];cookie=raw[536595:536611]
    assert code[0x3e5:0x3e9]==bytes.fromhex('ad49c249'),'Actual original MiniStep entry preimage'
    target=int.from_bytes(code[1:3],'little')
    class CPU(base):
        def step(self):
            nonlocal entries,returns,first,step_entries,step_returns,first_step
            m=self.memory
            for q in tuple(pending):
                if(self.pc,self.sp)==(q['returnPC'],q['returnSP']):
                    pending.remove(q)
                    if q['name']=='MiniStep':
                        step_returns+=1
                        if first_step is None:first_step=dict(q,sourceX16=int.from_bytes(m.ram[2][0x250:0x252],'little'),sourceY16=int.from_bytes(m.ram[2][0x252:0x254],'little'))
                    else:
                        returns+=1
                        if first is None:first=dict(q,returned_epoch=m.ram[2][0x301],ready=m.ram[2][0x300])
            if self.pc>=0x8000:
                tag=m.rawtags[(self.pc-0x8000)//8192]
                if tag==3 and 0xa000<=self.pc<0xb400 and not reads:
                    assert bytes(m.ram[3][:5120])==code,'Actual first loaded Mini code before SMC'
                    assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])==cookie,'Both full actual Mini headers'
                    reads.update(PC=self.pc,SP=self.sp,kernel_bytes=5120,kernel_SHA256=H(code),both16B_cookie=cookie.hex())
                if tag==3 and self.pc in(0xa000,0xa3e5):
                    name='MiniStep'if self.pc==0xa3e5 else'public movement'
                    if name=='MiniStep':step_entries+=1
                    else:entries+=1
                    sp=self.sp;pc=(m[256+((sp+1)&255)]+256*m[256+((sp+2)&255)]+1)&65535
                    pending.append(dict(name=name,PC=self.pc,SP=sp,target=target if name!='MiniStep'else self.pc,returnPC=pc,returnSP=(sp+2)&255,epoch=m.ram[2][0x301]))
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
        else:raise AssertionError('Mini actual compiled constructor bound')
        before=entries;before_step=step_entries
        for _ in range(16):
            m.controller_pad=0;Frames.frame(m,whole_pass=True)
            assert N.get(m,'SelectedCharacter')==41 and N.get(m,'MarioVariant')==8 and N.get(m,'PlayerStatus')==0 and N.get(m,'NumberofLives')==2
    assert reads and not pending and entries==returns and entries-before==16
    assert step_entries==step_returns and step_entries-before_step==16
    return dict(passed=True,ROM_SHA256=Inventory.PIN,compiled_Select8=cycle,first_private_readback=reads,
        public_movement_PC=0xa000,actual_target_PC=target,entries=entries,returns=returns,neutral_returned_updates=16,first_actual_return=first,
        MiniStep_PC=0xa3e5,MiniStep_entries=step_entries,MiniStep_returns=step_returns,first_original_step_return=first_step,
        terminal={n:N.get(m,n)for n in('SelectedCharacter','MarioVariant','PlayerStatus','PlayerSize','NumberofLives','GameEngineSubroutine','Player_X_Position','Player_PageLoc','Player_Y_Position')},
        MiniReady=m.ram[2][0x300],MiniEpoch=m.ram[2][0x301],source_menu_vblank_limit=True,
        scope='Actual compiled UI/constructor and16 neutral public Mini movement plus original MiniStep calls with dynamic PC/SP returns; no item/fullstage/native/physical cadence claim',
        outputs=0,Mesen=False,gameplay_seeds=0)


if __name__=='__main__':
    def deny(*args,**kw):raise AssertionError('Mini cold foundation attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Native,'run',deny):q=run(Inventory.ROM.read_bytes())
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
