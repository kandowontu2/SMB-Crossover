"""Trace actual BT menu-to-gameplay identity and palette-marker writes."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address
O=R/'build/bub-menu-candidate-1102-v2'
PIN='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    rom=O/'combined-visible.nes';assert sha(rom)==PIN
    b=M.scoped_load(R/'build/wwf-death-1102-v2/candidate.nes');b=dict(b);b['raw']=rom.read_bytes()
    events=[];cursor=[None];phase=['setup'];tracked=[None]
    oldstep=M.NesMPU.step;oldset=M.Bus.__setitem__
    def step(c):
        pc=c.pc
        cursor[0]=(pc,c.memory.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1,
                   [c.memory[pc+i]for i in range(3)])
        return oldstep(c)
    def put(m,key,value):
        if m is tracked[0] and key==0x5fe8:
            c=cursor[0];pc=c[0] if c else 0
            if pc>=0x8000:
                tag=c[1]
                events.append(dict(phase=phase[0],PC=pc,bank=tag,old=m[key],new=value,
                    instruction=c[2]))
        return oldset(m,key,value)
    M.NesMPU.step=step;M.Bus.__setitem__=put
    try:
        m=M.fresh(b);tracked[0]=m
        M.put(m,CrossoverMenuIndex=23)
        phase[0]='cold-menu-Rash'
        for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:M.invoke(m,n)
        assert M.get(m,'SelectedCharacter')==33 and M.get(m,'FmGroups')==64
        phase[0]='simultaneous-Select+A'
        M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=160,SavedJoypad2Bits=0)
        start=M.invoke(m,'CrossoverMenuInput')
        start_groups=M.get(m,'FmGroups')
        assert start_groups==32 and M.get(m,'CrossoverMenuState')==0
        phase[0]='native-confirm-continuation'
        M.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        M.invoke(m,'PauseRoutine',a=0)
        phase[0]='native-cold-scene'
        for setup in range(600):
            if M.get(m,'OperMode_Task')==3 and M.get(m,'GameEngineSubroutine')==8:break
            M.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
            M.invoke(m,'GameLoop');M.consume(m)
        else:raise AssertionError('Actual BT cold scene did not enter active8')
        phase[0]='active-gameplay'
        for _ in range(180):
            M.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,NmiDisable=255)
            M.invoke(m,'GameLoop');M.consume(m)
        assert M.get(m,'SelectedCharacter')==33 and M.get(m,'FmGroups')==96
        assert m.ram[3][address(b,'BtHostReady')-0xa000]==1
        assert m.ram[3][address(b,'BtVariant')-0xa000]==32
        writes=[e for e in events if e['new']==96]
        assert writes and all(e['new']&32 for e in writes)
        assert any(e['bank']==3 and e['instruction']==[141,232,95]for e in writes)
        q=dict(passed=True,ROM_SHA256=PIN,ROM_changed=False,CPU_only=True,native_successor_pending=True,
            original_native_negative='native-visible-bt-start retained in bub-combined-native-v6 inputs.zip',
            conclusion='The menu boundary retains exact32. Existing BT body/lives color workers legitimately add palette lease64; gameplay96 retains alternate32 and private BtVariant32. Final exact equality32 is an observer error.',
            start_groups=start_groups,active_groups=M.get(m,'FmGroups'),private_variant=m.ram[3][address(b,'BtVariant')-0xa000],
            private_ready=m.ram[3][address(b,'BtHostReady')-0xa000],setup_iterations=setup,active_GameLoop_calls=180,
            source_writes=events[:32],total_writes=len(events),
            bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),rom,R/'tools/audit/prepare_battletoads_menu_lease_v7.py',R/'tools/audit/prepare_bt_lives_body_1031_v7.py',R/'tools/audit/bub_menu_qualification_1102_v2.lua']})
        target=O/'BT-Start-palette-CPU-v2.json';assert not target.exists();target.write_text(json.dumps(q,indent=2)+'\n')
        print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','source_writes']}))
    finally:M.NesMPU.step=oldstep;M.Bus.__setitem__=oldset

if __name__=='__main__':main()
