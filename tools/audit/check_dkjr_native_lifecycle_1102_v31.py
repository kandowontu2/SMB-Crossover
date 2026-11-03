"""Actual injury/death/life ingress versus original DK damage/defeat epochs.

Historical v65 owner model only. Native and original terrain fixtures are
explicit identical source-format floor rectangles, not authored SMB levels.
"""
import collections,json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W;D=W.P.D


def fixture():
    q=json.loads((O/'native-lifecycle-v30-layout.json').read_text());L=q['labels']
    raw=bytearray(A.BASE.read_bytes());assert A.sha(raw)==A.PIN
    pr=json.loads((R/'build/prince-actor-1101-v1/native-manifest-v65.json').read_text())
    for p in pr['patches']:
        at=p['file_offset'];old=bytes.fromhex(p['old_hex']);assert raw[at:at+len(old)]==old
        raw[at:at+len(old)]=bytes.fromhex(p['new_hex'])
    assert A.sha(raw)==pr['expected_memory_only_SHA256']
    bb=json.loads((R/'build/bub-menu-candidate-1102-v2/combined-current-landing.json').read_text())
    for p in bb['patches']:
        if len(bytes.fromhex(p['new']))==16:continue
        at=p['offset'];old=bytes.fromhex(p['old']);assert raw[at:at+len(old)]==old
        raw[at:at+len(old)]=bytes.fromhex(p['new'])
    for pc,path in [(0xa740,O/'retire-selector-v18.bin'),(0xaaf7,R/'build/prince-actor-1101-v1/shared-frame-v22.bin'),(0xab72,O/'retire-extra-v18.bin'),(0xae00,O/'retire-owner-v18.bin')]:
        part=path.read_bytes();at=16+65*8192+pc-0xa000;raw[at:at+len(part)]=part
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=bytes(raw)
    SL={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'retire-selector-v18.lbl').read_text(),re.M)}
    resident=(O/'retire-selector-v18.bin').read_bytes();cookie=resident[SL['DkCookie']-0xa740:SL['DkCookie']-0xa740+16]
    m=N.Bus(b);body=(O/'native-lifecycle-v30.bin').read_bytes();m.ram[3][:len(body)]=body
    for kind,at in [('pause',0x1540),('main',0x165e),('ports',0x16a4)]:
        part=(O/f'native-lifecycle-{kind}-v30.bin').read_bytes();m.ram[2][at:at+len(part)]=part
    for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=cookie
    m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=40,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,AreaType=1,AreaPointer=0x25,WorldNumber=0,LevelNumber=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Player_X_Position=40,Player_Y_Position=176,Player_Y_HighPos=1,PlayerStatus=0,VRAM_Buffer1_Offset=0,NmiDisable=1,Mirror_PPUCTRL=160,NumberofLives=2)
    return b,m,L,q


def direct(m,entry):
    c=N.NesMPU(memory=m,pc=entry);c.sp=224;c.stPushWord(0x5ffe)
    for _ in range(100000):
        if c.pc==0x5fff:break
        assert m[c.pc]!=0,('private lifecycle BRK',hex(c.pc));c.step()
    else:raise AssertionError(('private lifecycle bound',hex(entry),hex(c.pc)))
    assert c.sp==224
    return c


def original_call(oracle,entry,terminal=False):
    c=D.T.NesMPU(memory=oracle,pc=entry);c.sp=224;c.stPushWord(0x5ffe)
    for _ in range(100000):
        if c.pc==0xcf62 and terminal:return True
        if c.pc==0x5fff:return False
        assert oracle[c.pc]!=0,('original lifecycle BRK',hex(c.pc));c.step()
    raise AssertionError(('original lifecycle bound',hex(entry),hex(c.pc)))


def main():
    b,seed,L,q=fixture();direct(seed,L['DkConstruct'])
    points={}
    for name in ['InjurePlayer','GuestInjuryStatus','HuInjuryStatus','HuInjury','PlayerDeath','HuDeath','HuDeathStart','UnionDeathStartCore','PlayerLoseLife']:
        points[W.address(b,name),((W.location(b,name)-16)//8192)|128]=name
    for name in ['DkNativeInjury','DkNativeInjuryStatus','DkNativeDeathStart','DkNativeDeath','DkjrDefeatTick','DkjrNativeLifeTerminal','DkjrDamage']:
        points[L[name],3]=name
    counts=collections.Counter();minimum=255;old=N.NesMPU
    class Trace(old):
        def step(self):
            nonlocal minimum
            minimum=min(minimum,self.sp)
            if self.pc>=0x8000:
                name=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
                if name:counts[name]+=1
            return super().step()
    N.NesMPU=Trace
    results=[]
    try:
        for mode in ['native-contact-injury','native-forced-death']:
            m=N.fork(seed);oracle=D.Bus();oracle[:2048]=bytes(m.ram[2][:2048])
            if mode=='native-contact-injury':
                N.invoke(m,'InjurePlayer',a=85,x=0,y=0,p=0x31)
                assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'TimerControl')==0
            else:
                N.invoke(m,'MegaManDeathStart')
                # PlayerDeath's engine11/TimerFF are the genuine native pit/
                # KillPlayer continuation inputs, not a replacement source timer.
                N.put(m,GameEngineSubroutine=11,TimerControl=255)
            original_call(oracle,0xd405)
            differences=[(i,oracle[i],m.ram[2][i])for i in range(4,0x800)if not 0x100<=i<0x200 and oracle[i]!=m.ram[2][i]]
            assert not differences,(mode,differences[:12],dict(counts))
            # Both query engines read these exact floor rectangles. Original
            # stage table pointers are substituted read-only, as in v2 proof.
            lists=[bytes([0,208,239,239,255]),bytes([255]),bytes([255])]
            for table,orig,private,data in zip([0xc440,0xc448,0xc450],[0x700,0x740,0x780],[0x800,0x840,0x880],lists):
                oracle[orig:orig+len(data)]=data;m.ram[2][private:private+len(data)]=data
                for i in range(4):
                    list.__setitem__(oracle,table+2*i,orig&255);list.__setitem__(oracle,table+2*i+1,orig>>8)
            direct(m,L['DkjrUseNativeGeometry']);m.ram[2][0x8da]=0
            # Keep fixture rectangle storage out of the compared donor actor;
            # C700 was original scratch in this native adaptation, not its list.
            ignored=set(range(0x700,0x781))
            for epoch in range(1,500):
                terminal=original_call(oracle,0xcf37,True)
                N.invoke(m,'HuMovement'if mode=='native-contact-injury'else'PlayerDeath')
                if terminal:
                    assert N.get(m,'GameEngineSubroutine')==6 and N.get(m,'TimerControl')==0 and m.ram[2][0x8f8]==1
                    assert N.get(m,'NumberofLives')==2
                    break
                assert N.get(m,'GameEngineSubroutine')==(8 if mode=='native-contact-injury'else 11)
                differences=[(i,oracle[i],m.ram[2][i])for i in range(4,0x800)if i not in ignored and not 0x100<=i<0x200 and oracle[i]!=m.ram[2][i]]
                assert not differences,(mode,epoch,differences[:12])
            else:raise AssertionError((mode,'no original terminal'))
            N.invoke(m,'PlayerLoseLife');assert N.get(m,'NumberofLives')==1 and N.get(m,'SelectedCharacter')==40 and N.get(m,'OperMode')==1
            # Fresh is the sole re-construction after native life bookkeeping.
            N.put(m,GameEngineSubroutine=8,OperMode_Task=3,Player_X_Position=40,Player_Y_Position=176,Player_Y_HighPos=1)
            N.invoke(m,'HuFresh');assert m.ram[2][0x6b]==1 and m.ram[2][0x65]==36 and m.ram[2][0x8f8]==0 and m.ram[2][0x8fe]==1
            results.append(dict(mode=mode,original_defeat_epochs=epoch,one_native_life_lost=True,identity40_retained=True,genuine_Fresh_reconstructed=True))
        # Earned D1AE pause owns its no-contact source phase. Repeated native
        # injury requests must not reset its08/09 counters or discard tokens.
        m=N.fork(seed);m.ram[2][0x68]=1;direct(m,L['DkNativeMain']);before=bytes(m.ram[2][:0x900]);timer=N.get(m,'TimerControl')
        for _ in range(3):N.invoke(m,'InjurePlayer')
        assert bytes(m.ram[2][:0x900])==before and N.get(m,'TimerControl')==timer==255
        # The real public Reset owns CoRetire rather than dispatching private
        # row19. Its authenticated callback thaws, then invalidates both full
        # headers. Old constructed bytes are unreachable until a later Fresh.
        N.invoke(m,'HuReset');assert not m.ram[2][0x440]and N.get(m,'TimerControl')==0
        assert all(m.ram[bank][0x1fe0]==0 for bank in [2,3])
        assert not any(m[W.address(b,'Enemy_Flag'):W.address(b,'Enemy_Flag')+6])
        before=bytes(m.ram[2]);assert not N.invoke(m,'HuMovement')['P']&1 and bytes(m.ram[2])==before
        direct(m,L['DkNativeReset']);assert not m.ram[2][0x8fe]
    finally:N.NesMPU=old
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,historical_v65_matching_header_fixture=True,checks=results,
        source_hit_injury_requests_do_not_reset_pause=True,actual_public_Reset_thaws_and_invalidates_both_headers=True,private_Reset_leaf_invalidates_constructed_state=True,actual_calls=dict(counts),minimum_CPU_SP=minimum,
        remaining=['Actual complete scene/header authentication and latest Prince rebind, full native GameCore/IRQ foreign closure.','Remaining21 public rows and native art/fruit/points/name admission; isolated floor fixtures are not a stage clear.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-lifecycle-v30-layout.json',O/'native-lifecycle-v30.bin',O/'native-lifecycle-ports-v30.bin',O/'retire-owner-v18.bin',O/'retire-selector-v18.bin']})
    (O/'native-lifecycle-v31-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','checks','actual_calls','minimum_CPU_SP']}))


if __name__=='__main__':main()
