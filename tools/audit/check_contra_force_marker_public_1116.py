"""Actual full public CF guard/fault/foreign and ordinary loan retirement."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import contra_force_p1_work_marker_model_1116 as M

C,N,W,Frames=M.C,M.N,M.W,M.Frames


def guards(raw):
    seed=M.cold(raw);d=C.Plan.descriptor(M.parent(raw));ranges=[tuple(f['CPU_half_open'])for f in d['fragments']]
    base=N.NesMPU;entries=Counter();ctx={}
    class Observe(base):
        def step(self):
            m=self.memory
            if self.pc>=0xa000 and m.rawtags[(self.pc-0x8000)//8192]==3 and any(lo<=self.pc<hi for lo,hi in ranges):entries[ctx['case']]+=1
            return super().step()
    rows=[];minimum=255
    for case in list(range(16))+['old-warm']+['foreign-'+str(i)for i in range(256)if i!=31]:
        z=N.fork(seed);ctx['case']=str(case)
        if isinstance(case,int):z.ram[2][0x1fe0+case]^=1
        elif case=='old-warm':
            parent=M.parent(raw);carrier=parent[C.Plan.Audit.P.CHR+935*1024:C.Plan.Audit.P.CHR+959*1024]
            z.ram[1][:]=carrier[:8192];z.ram[3][:]=carrier[16384:24576];z.ram[2][0x1fe0:0x1ff0]=C.OLD_COOKIE
        else:N.put(z,SelectedCharacter=int(case.split('-')[1]))
        before_OAM=bytes(z[512:768]);before_CF=[bytes(z.ram[i])for i in(1,2,3)]
        with patch.object(N,'NesMPU',Observe):result=N.invoke(z,'NrDraw',a=0x53,x=0x17,y=0x8d,p=0x21)
        assert entries[str(case)]==0,('Invalid/foreign public guard entered new CF code',case)
        if bytes(z[512:768])!=before_OAM or[bytes(z.ram[i])for i in(1,2,3)]!=before_CF:
            detail=dict(case=case,public_result=result,
                OAM_differences=[dict(offset=i,before=x,after=y)for i,(x,y)in enumerate(zip(before_OAM,bytes(z[512:768])))if x!=y][:8],
                private_differences=[dict(bank=k,offset=i,before=x,after=y)for k in(1,2,3)for i,(x,y)in enumerate(zip(before_CF[k-1],bytes(z.ram[k])))if x!=y][:8])
            print('NEGATIVE '+json.dumps(detail,separators=(',',':')),flush=True)
            raise AssertionError((case,'Rejected CF may still have admitted foreign native behavior; requires parent comparison'))
        rows.append(dict(case=case,carry=result['P']&1,new_private_instructions=0))
    # The valid owning public draw reaches the new renderer. Its actual
    # phase-status callback then executes the unchanged complete packet path.
    z=N.fork(seed);ctx['case']='valid-public'
    with patch.object(N,'NesMPU',Observe):
        draw=N.invoke(z,'NrDraw',a=0x53,x=0x17,y=0x8d,p=0x21)
        assert entries['valid-public']>0 and z.ram[2][0x2df]&128
        status=N.invoke(z,'NrInjuryStatus',a=0x53,x=0x17,y=0x8d,p=0x20)
    assert not z.ram[2][0x2df]&128 and not any(z[514+i*4]&24 for i in range(64))
    assert z[W.address(z.bundle,'SmFreezeLastBlue')]==192
    return dict(cache_header_faults=16,foreign_selected_values=255,old_warm_full_code_header_rejected=True,
        all_fault_foreign_no_new_CF_instruction_or_OAM_private_write=True,
        owning_valid_public_draw_and_phase_status_actual_packet=True,
        valid_public_draw_carry=draw['P']&1,valid_status_carry=status['P']&1,
        no_weakened_full_header_or_foreign_admission=True,total_rejected_cases=len(rows))


def retire(raw):
    result=[]
    for key in M.IDENTITIES:
        m=M.cold(raw,key);b=m.bundle;last_blue=W.address(b,'SmFreezeLastBlue');pending=W.address(b,'SmFreezePalettePending');packet=W.address(b,'SmFreezePalettePacket')
        turn=m[W.address(b,'SmFreezeTurn')];loan=0;first_native=None
        for age in range(32):
            m.controller_pad=4|(64 if age>=6 and age%8 in(6,7)else 0);Frames.frame(m,whole_pass=True)
            if m.ram[2][0x2fb]==1:
                loan+=1;assert m[last_blue]==193 and m[pending]==128
                assert bytes(m[packet:packet+7])==bytes.fromhex('3f150320381600')
        assert loan>0
        for age in range(180):
            m.controller_pad=0;Frames.frame(m,whole_pass=True)
            assert N.get(m,'NumberofLives')==2 and N.get(m,'PlayerStatus')==0
            assert not any(m[514+i*4]&24 for i in range(64))
            if not any(m.ram[2][0x382+i]for i in range(10,22)):
                first_native=age+1;break
        assert first_native is not None,(key,'Ordinary projectiles did not retire')
        for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
        assert m.ram[2][0x2fb]==0 and m.ram[2][0x2df]==0 and m[last_blue]==192 and m[pending]==192
        assert m[W.address(b,'SmFreezeTurn')]==turn
        control=m[W.address(b,'SmFreezePaletteControl')];area=N.get(m,'AreaType')
        index=control if 1<=control<=4 else 2 if control==8 else area+1 if area<4 else 2
        colors=((16,26,28,28),(48,48,54,54),(39,39,23,23))
        expected=bytes((63,21,3,*(c[index-1]for c in colors),0));assert bytes(m[packet:packet+7])==expected
        row=dict(identity=key,ordinary_loan_Main=loan,neutral_Main_until_all_shots_retired=first_native,
            four_more_completed_native_packet_updates=True,packet_hex=expected.hex(),Pending=192,LastBlue=192,Choice=0,marker=0,Turn_unchanged=True,
            lives=N.get(m,'NumberofLives'),x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'))
        result.append(row);print('PROGRESS '+json.dumps(row,separators=(',',':')),flush=True)
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--guards',action='store_true');ap.add_argument('--retire',action='store_true');args=ap.parse_args()
    assert args.guards or args.retire
    parent=C.load_current_image();raw,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Public/protocol source gate attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=dict(candidate_SHA256=C.CANDIDATE,outputs=0,native=False,gameplay_seeds=0)
        if args.guards:q['guards']=guards(raw)
        if args.retire:q['ordinary_all4_loan_to_native_packet']=retire(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
