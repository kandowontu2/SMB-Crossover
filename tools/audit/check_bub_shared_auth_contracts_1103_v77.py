"""Changed Sh/raw39 auth, cold/fault/lifetime contracts; no cartridge output."""
import json
from pathlib import Path
import measure_bub_shared_auth_funding_1103_v76 as P
from measure_bub_full_auth_helper_1103_v73 import parity
O,R,N,Q,address,sha=P.O,P.R,P.N,P.Q,P.address,P.sha
C,I=P.F.D.C,P.F.D.C.I


def public(m,target,a=83,x=71,y=109,p=0x21):
    z=I.invoke(m,193,target,(a,x,y,p))
    return dict(zip(['A','X','Y','P'],z['regs'][:4]),CPU=z['CPU'],SP=z['regs'][4],minimum_SP=z['minSP'])


def cold(bb,owner,fault=None):
    N.Bus=C.cold.__globals__['C'].C.V.ControllerBus;m=N.fresh(bb)
    for k in [2,3]:m.ram[k][:]=bytes([0x9d])*8192;m.ram[k][0x1fe0:0x1ff0]=bytes(16)
    C.fields(m,owner)
    if fault=='protected':m.protection=[0,0]
    elif fault=='NMI-enabled':N.put(m,NmiDisable=0)
    elif fault:m.corrupt_at=fault
    z=public(m,0xae00 if owner!=36 else (0xa87f if fault else 0xac1d))
    C.clear(m)
    return m,z


def main():
    dst=O/'shared-auth-v77-contracts.json';assert not dst.exists()
    old,new,route,q,manifest,ol,nl,patches,refs=P.build();seeds={};coldrows=[];faults=[];transitions=[];retire=[]
    for owner in [36,37,38,39,40]:
        pair=[];out=[]
        for bb in [old,new]:
            m,z=cold(bb,owner);pair.append(m);out.append(z)
        parity(*pair,out);assert out[0]['P']&1,(owner,'actual cold')
        fresh=[N.invoke(m,'HuFresh',a=83,x=0,y=109,p=0x21)for m in pair]
        parity(*pair,fresh);assert fresh[0]['P']&1,(owner,'real Fresh')
        for m in pair:C.clear(m)
        seeds[owner]=[N.fork(m)for m in pair]
        coldrows.append(dict(owner=owner,baseline=out[0],proposal=out[1]))
        reads=[m.ppu_reads for m in pair]
        warm=[public(m,0xae00 if owner!=36 else 0xac1d)for m in pair]
        parity(*pair,warm);assert [m.ppu_reads for m in pair]==reads and warm[0]['P']&1
        # Current source fault mechanisms affect actual copy/readback, not
        # a synthetic outcome or mocked native collector.
        for fault in ['protected','NMI-enabled',(3,100),(2,0x1005)]:
            pp=[];zz=[]
            for bb in [old,new]:
                m,z=cold(bb,owner,fault);pp.append(m);zz.append(z)
            parity(*pp,zz)
            if fault in ['protected','NMI-enabled',(3,100)]:assert not zz[0]['P']&1,(owner,fault,zz)
            faults.append(dict(owner=owner,fault=fault,returned_C=zz[0]['P']&1))
        pp=[N.fork(m)for m in seeds[owner]];zz=[]
        for m in pp:N.put(m,SelectedCharacter=0);zz.append(public(m,0xae0b))
        parity(*pp,zz)
        assert pp[0].ram[2][0x1fe0]==pp[0].ram[3][0x1fe0]==0
        retire.append(owner)
    for before in [37,38,39,40]:
        for after in [37,38,39,40]:
            pair=[N.fork(m)for m in seeds[before]];out=[]
            for m in pair:C.fields(m,after);out.append(public(m,0xae00))
            parity(*pair,out);assert out[0]['P']&1
            transitions.append([before,after])
    # Exact ShCheckCode AXYP/CurrentC/R0..7 and raw36-only predicate.
    checks=0;poisons=0;foreign=0
    for a in [0,1,83,128,255]:
        for y in [0,109,255]:
            for p in [0x20,0x21,0x71,0xf1]:
                pair=[N.fork(m)for m in seeds[36]];out=[public(m,0xa800,a,71,y,p)for m in pair]
                parity(*pair,out);assert out[0]['P']&1;checks+=1
    for bank in [2,3]:
        for offset in range(16):
            pair=[N.fork(m)for m in seeds[36]];out=[]
            for m in pair:m.ram[bank][0x1fe0+offset]^=1;out.append(public(m,0xa800))
            parity(*pair,out);assert not out[0]['P']&1;poisons+=1
    for raw in range(256):
        if raw==36:continue
        pair=[N.fork(m)for m in seeds[36]];out=[]
        for m in pair:N.put(m,SelectedCharacter=raw);out.append(public(m,0xa800))
        parity(*pair,out);assert not out[0]['P']&1;foreign+=1
    # Complete published rows, with each original owner genuinely loaded.
    rows=0
    for owner in [36,37,38,39,40]:
        for row in range(37):
            pair=[N.fork(m)for m in seeds[owner]];out=[]
            for m in pair:
                target=(0xaa88 if owner==36 else 0xb08c)+row*3
                y=6 if row==10 else 9 if row==14 else 109
                try:out.append(public(m,target,83,0,y,0x21))
                except Exception as error:raise AssertionError((owner,row,'actual public caller fixture',repr(error)))from error
            parity(*pair,out);rows+=1
    CPU=N.NesMPU;maincases=[]
    for identity in [0,1]:
        for phase,keys in [('idle',0),('walk',1),('left',2),('jump',129),('bubble',64)]:
            pair=[Q.Q.fresh(bb,route,identity)for bb in [old,new]];outputs=[];traces=[];auth=[]
            for index,m in enumerate(pair):
                Q.L.E.main_fields(m);trace=[];count=0
                class Trace(CPU):
                    def step(self):
                        nonlocal count
                        pc=self.pc;mm=self.memory;bank=mm.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                        if bank==193 and pc==(ol if index==0 else nl)['CoCheckCode']:count+=1
                        if bank in [2,3]and not(bank==3 and pc in [0xa01b,0xa02a,0xa066,0xb57c,0xb57d]):
                            trace.append((bank,pc,self.a,self.x,self.y,self.p,self.sp))
                        return super().step()
                N.NesMPU=Trace
                try:
                    out=[]
                    for epoch in range(12):
                        held=(keys&127)|(128 if keys&128 and epoch==1 else 0)
                        N.put(m,FrameCounter=epoch,SavedJoypadBits=held,SavedJoypad1Bits=held,VRAM_Buffer1_Offset=0)
                        out.append(N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31))
                    outputs.append(out)
                finally:N.NesMPU=CPU
                traces.append(trace);auth.append(count)
            parity(*pair,[x[-1]for x in outputs]);assert traces[0]==traces[1]and auth==[156,156]
            for a,z in zip(*outputs):assert [a[k]for k in ['A','X','Y','P']]==[z[k]for k in ['A','X','Y','P']]
            before=sum(z['CPU']for z in outputs[0])/12;after=sum(z['CPU']for z in outputs[1])/12
            item=dict(identity=identity,phase=phase,baseline_CPU=before,proposal_CPU=after,saving_CPU=before-after,
                full_auth_calls=auth,remaining_private_instruction_AXYP_SP_exact=True)
            maincases.append(item);print(json.dumps(item),flush=True)
    result=dict(passed=True,CPU_only=True,CPU_qualified=False,candidate_allowed=False,ROM_written=False,
        current_source_proposal=sha(O/'shared-auth-v76-funding.json'),cold=coldrows,warm_all_owners=5,
        actual_copy_fault_cases=faults,ordered_common_owner_transitions=transitions,
        foreign_selected_retirement=retire,Sh_full_AXYP_check_cases=checks,Sh_header_byte_rejections=poisons,
        Sh_foreign_raw_rejections=foreign,actual_all_owner_public_row_cases=rows,Main_cases=maincases,
        source_fit_keeps_cookie_addresses_bytes_and_15B_end_pad=True,
        remaining=['Actual typed-contact virtual37 requires its native caller context, not an arbitrary direct public call; qualify with populated trapped-native-AI retirement.',
            'Exact current-public/cold/SMC/header/cookie reference census.',
            'Actual IRQ/FF/NMI cuts over changed Sh/raw39/cold/Fresh/retire code and nested deepest genuine contexts.',
            'Pending Prince/DK changes still require exact composition/rebind; no native candidate permission.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(P.__file__),
            O/'shared-auth-v76-funding.json',O/'shared-auth-v76.s',O/'shared-auth-v76.bin',
            O/'shared-auth-v76-extra.bin',O/'shared-auth-v76-Sh.bin',O/'shared-auth-v76.lbl']})
    dst.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
