"""Actual native row33 powerup/lifetime test in a private proposed-owner model.

HistoricalPrincev65+BB9cf shared proposal bytes are installed only in memory;
this does not mutate the ROM or authorize/publicly admit raw40.
"""
import collections,copy,json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    q=json.loads((O/'native-powerup-v26-layout.json').read_text());L=q['labels'];raw=bytearray(A.BASE.read_bytes());assert A.sha(raw)==A.PIN
    pp=R/'build/prince-actor-1101-v1/native-manifest-v65.json';pr=json.loads(pp.read_text())
    for p in pr['patches']:
        at=p['file_offset'];old=bytes.fromhex(p['old_hex']);assert raw[at:at+len(old)]==old;raw[at:at+len(old)]=bytes.fromhex(p['new_hex'])
    assert A.sha(raw)==pr['expected_memory_only_SHA256']
    bb=json.loads((R/'build/bub-menu-candidate-1102-v2/combined-current-landing.json').read_text())
    for p in bb['patches']:
        if len(bytes.fromhex(p['new']))==16:continue
        at=p['offset'];assert raw[at:at+len(bytes.fromhex(p['old']))]==bytes.fromhex(p['old']);raw[at:at+len(bytes.fromhex(p['new']))]=bytes.fromhex(p['new'])
    for pc,name in [(0xa740,'retire-selector-v18.bin'),(0xaaf7,'../../prince-actor-1101-v1/shared-frame-v22.bin'),(0xab72,'retire-extra-v18.bin'),(0xae00,'retire-owner-v18.bin')]:
        p=R/'build/prince-actor-1101-v1/shared-frame-v22.bin'if pc==0xaaf7 else O/name;part=p.read_bytes();at=16+65*8192+pc-0xa000;raw[at:at+len(part)]=part
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=bytes(raw)
    body=(O/'native-powerup-v26.bin').read_bytes();parts={k:(O/('native-powerup-'+k+'-v26.bin')).read_bytes()for k in ['pause','main','ports']}
    SL={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'retire-selector-v18.lbl').read_text(),re.M)}
    resident=(O/'retire-selector-v18.bin').read_bytes();cookie=resident[SL['DkCookie']-0xa740:SL['DkCookie']-0xa740+16];assert len(cookie)==16
    points={}
    for n in ['PlayerChangeSize','NrNativePowerupDispatch','HuPowerup','GuestPowerupUpdate','GetPlayerColors','HuColors','HuMovement']:
        points[W.address(b,n),((W.location(b,n)-16)//8192)|128]=n
    for n in ['DkNativePowerup','DkColors','DkNativeMain','DkPauseMain','DkjrFruitHit']:points[L[n],2 if L[n]>=0xc000 else 3]=n
    counts=collections.Counter();minsp=255;base=N.NesMPU;hit_entries=[]
    class Trace(base):
        def step(self):
            nonlocal minsp
            minsp=min(minsp,self.sp)
            if self.pc>=0x8000:
                n=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
                if n:counts[n]+=1
                if n=='DkjrFruitHit':hit_entries.append([self.memory[0xc066],self.memory[0xc068],list(self.memory.rawtags)])
            return super().step()
    N.NesMPU=Trace
    def direct(m,target):
        c=Trace(memory=m,pc=target);c.sp=224;c.stPushWord(0x5ffe)
        for _ in range(100000):
            if c.pc==0x5fff:break
            assert m[c.pc]!=0,('private powerup BRK',hex(c.pc));c.step()
        else:raise AssertionError('private powerup bound')
        assert c.sp==224
    try:
        m=N.Bus(b);m.ram[3][:len(body)]=body
        for kind,at in [('pause',0x1540),('main',0x165e),('ports',0x16a4)]:m.ram[2][at:at+len(parts[kind])]=parts[kind]
        for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=cookie
        m.raw_page(1,3);m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=40,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,AreaType=1,AreaPointer=0x25,WorldNumber=0,LevelNumber=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Player_X_Position=40,Player_Y_Position=176,Player_Y_HighPos=1,PlayerStatus=0,VRAM_Buffer1_Offset=0,NmiDisable=1,Mirror_PPUCTRL=160)
        direct(m,0xa02d);m.ram[2][0x68]=1;direct(m,L['DkNativeMain']);assert m.ram[2][0x440]and N.get(m,'TimerControl')==255
        source_timer=bytes(m.ram[2][8:10]);clock=m.ram[2][0x38];source_state=bytes(m.ram[2][:0x800]);flags=bytes(m[W.address(b,'Enemy_Flag'):W.address(b,'Enemy_Flag')+6])
        N.invoke(m,'GuestBeginPowerup');assert N.get(m,'GameEngineSubroutine')==9 and N.get(m,'GuestPowerupActive')==1
        for epoch in range(1,61):
            N.put(m,VRAM_Buffer1_Offset=0)
            N.invoke(m,'PlayerChangeSize')
            assert bytes(m.ram[2][:0x800])==source_state and m.ram[2][0x38]==clock and m.ram[2][0x68]==1
            assert bytes(m[W.address(b,'Enemy_Flag'):W.address(b,'Enemy_Flag')+6])==flags
            assert N.get(m,'TimerControl')==255
            if epoch<60:assert N.get(m,'GameEngineSubroutine')==9
        assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'GuestPowerupActive')==0 and N.get(m,'PlayerStatus')==1
        assert counts['DkNativePowerup']==60 and counts['GuestPowerupUpdate']==60 and counts['DkColors']>0
        N.invoke(m,'HuMovement');assert m.ram[2][8]==(source_timer[0]-1)&255 and m.ram[2][9]==source_timer[1]and m.ram[2][0x440]and N.get(m,'TimerControl')==255
        scope=dict(actual_native_powerup_updates=60,actual_native_engine9_to8=True,all2048_source_bytes_and_D1AE08_09_timer_pair_unchanged_during_native_powerup=True,native_completion_same_epoch_rearms_owned_pause=True,first_following_native_HuMovement_resumes_next_source_hit_tick=True,all_empty_tokens_still_held=True,minimum_CPU_SP=minsp,source_stack_SMC_overlap=minsp<0x7b)
        # Retire via the exact shared proposal after selecting a foreign owner.
        RL={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'retire-owner-v18.lbl').read_text(),re.M)}
        for name in ['CoRetire']:
            pc=RL[name];seg='DK_v27_'+name;b['segs'][seg]=dict(start=str(pc),ooffs=str(16+65*8192+pc-0xa000));b['syms'][name]=dict(val=str(pc),seg=seg)
        N.put(m,SelectedCharacter=28);N.invoke(m,'CoRetire');assert not m.ram[2][0x440]and N.get(m,'TimerControl')==0
        assert not any(m[W.address(b,'Enemy_Flag'):W.address(b,'Enemy_Flag')+6])
    finally:N.NesMPU=base
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,private_CPU_shared_proposal_only=True,source_base_SHA256=A.PIN,historical_Prince_reference=pr['expected_memory_only_SHA256'],Bub_reference=bb['expected_rebased_ROM_sha256'],checks=scope,actual_calls=dict(counts),
        remaining=['Real IRQ/lagNMI cuts, full native Scene/death lifecycle and all unfinished typed APIs.','Latest Prince successor fingerprint rebind before any image; this in-memory frame is historical v65 only.','Current DK auth cookie is an explicit matching-header CPU fixture, not final payload authentication or cold-loader qualification.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),A.BASE,pp,O/'native-powerup-v26-layout.json',O/'native-powerup-v26.bin',O/'native-powerup-ports-v26.bin',O/'retire-owner-v18.bin',O/'retire-selector-v18.bin',O/'retire-extra-v18.bin']})
    (O/'native-powerup-v27-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','checks','actual_calls']}))


if __name__=='__main__':main()
