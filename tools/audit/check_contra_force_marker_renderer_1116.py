"""Detached actual CF renderer/12-slot loop and consumed-stack proof."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import check_contra_force_p1_marker_detached_1116 as Base

C,P,N=Base.C,Base.P,Base.N


class Memory(bytearray):
    op=None
    def __init__(self,*args):super().__init__(*args);self.written=set();self.consumed=set()
    def __getitem__(self,at):
        value=super().__getitem__(at)
        if isinstance(at,int)and 0x100<=at<0x200 and self.op in(0x68,0x28,0x60,0x40):self.consumed.add(at)
        return value
    def __setitem__(self,at,value):
        if isinstance(at,int)and 0x100<=at<0x200 and self.op is not None:
            self.written.add(at);self.consumed.discard(at)
        return super().__setitem__(at,value)


def run(raw):
    old,new,s,d=Base.seed(raw);newlabels=d['fragments'][0]['labels'];cases=0;minimum=255;dead=Counter();cost=Counter();paths=Counter()
    cursor=s['CurrentOAMOffset'];entry_sp=224
    def one(kind,frame=0,p=32,body=25,shot=0,where=0,slot=10,invalid=0,offset=0,rotation=0):
        nonlocal cases,minimum
        pair=[]
        for version,image in enumerate((old,new)):
            m=Memory(image);m[0x100:0x200]=bytes((i*13+p+frame)&255 for i in range(256));m[0x1e1:0x1e3]=(0x4fff).to_bytes(2,'little')
            for i in range(64):m[512+i*4:516+i*4]=bytes((248,i*3&255,(i*7)&231,i*5&255))
            m[0xc023]=frame;m[0xc31a]=body;m[0xc334]=0;m[0xc2df]=72 if version else 8
            m[s['MmDeathFlag']]=int(kind=='loop');m[s['InjuryTimer']]=0;m[s['FrameCounter']]=0
            m[cursor]=offset;m[s['GuestOamRotationActive']]=bool(rotation);m[s['RgOamRotation']]=rotation
            for name,value in(('Player_X_Position',(40,0,250)[where%3]),('Player_PageLoc',0),('ScreenLeft_X_Pos',16 if where==1 else 0),
                ('ScreenLeft_PageLoc',0),('Player_Y_Position',176 if where<3 else 250),('Player_Y_HighPos',1 if where<4 else 0)):
                m[s[name]]=value
            if kind=='shot':
                for i in range(22):m[0xc382+i]=0
                m[0xc382+slot]=0 if invalid==1 else 10;m[0xc334+slot]=0 if invalid==2 else 28
                m[0xc31a+slot]=shot;m[0xc34e+slot]=96 if where==0 else 255;m[0xc368+slot]=128 if where==0 else 245
                m[0xc300+slot]=where*8
            entries=[];target=s['CfHostRenderShot']if kind=='shot'else s['CfHostRenderAll']
            if version and kind=='shot':target=newlabels[f'Old_{target:04X}']
            c=N.NesMPU(memory=m,pc=target);c.a=p^165;c.x=slot;c.y=p^91;c.p=p;c.sp=entry_sp
            shot_pc=s['CfHostRenderShot']if version==0 else newlabels[f'Old_{s["CfHostRenderShot"]:04X}']
            for _ in range(30000):
                if c.pc==0x5000:break
                if c.pc==shot_pc:entries.append(c.x)
                m.op=bytearray.__getitem__(m,c.pc);assert m.op!=0,('Renderer BRK',kind,frame,body,shot,version,c.pc)
                minimum=min(minimum,c.sp);c.step()
            else:raise AssertionError(('Renderer instruction bound',kind,frame,body,shot,version,c.pc))
            m.op=None;pair.append((c,m,entries))
        a,b=pair
        assert(a[0].a,a[0].x,a[0].y,a[0].p,a[0].sp)==(b[0].a,b[0].x,b[0].y,b[0].p,b[0].sp),(kind,frame,p,body,shot,where,slot,invalid,offset,rotation,'public AXYP/SP')
        assert a[2]==b[2]
        if kind!='shot':assert a[2]==[10+(frame%12+i)%12 for i in range(12)],(frame,a[2])
        assert a[1][:0x100]==b[1][:0x100]and a[1][0x200:0x8000]==b[1][0x200:0x8000],('Renderer RAM/OAM',kind,body,shot)
        assert a[1][0xc000:0xc2df]==b[1][0xc000:0xc2df]and a[1][0xc2e0:0xe000]==b[1][0xc2e0:0xe000],('Renderer private RAM',kind,body,shot)
        assert a[1][0xc2df]^b[1][0xc2df]==64,('Only intended pending-work marker differs',kind,body,shot)
        for at in range(0x100,0x200):
            if a[1][at]==b[1][at]:continue
            assert at<=0x100+entry_sp,('Renderer live caller stack changed',at)
            for _,memory,_ in pair:
                assert at not in memory.written or at in memory.consumed,('Renderer discarded unconsumed stack publication',at,kind)
            dead[at]+=1
        cost[kind,a[0].processorCycles-b[0].processorCycles]+=1;paths[kind]+=1;cases+=1
    # Exact full modulo/flags cross-product with body absent and12 real
    # inactive Shot handlers. No handler-return fixture is used.
    for frame in range(256):
        for p in range(32,256):
            if p&32:one('loop',frame=frame,p=p)
    for body in range(192):
        for where in(0,1,2,3,4):
            for p in(32,255):one('body',frame=body,p=p,body=body,where=where,offset=(0,192,220,248)[body%4],rotation=(0,224)[body%2])
    for shot in range(139):
        for where in range(4):
            for p in(32,255):one('shot',p=p,shot=shot,where=where,offset=(0,192,220,248)[shot%4],rotation=(0,224)[shot%2])
    for slot in(0,9,10,21,22,255):
        for invalid in(0,1,2):
            for shot in(139,255):
                for p in(32,33,128+32,255):one('shot',slot=slot,invalid=invalid,shot=shot,p=p)
    return dict(cases=cases,paths=dict(paths),all256_modulo_frames_cross_all128_hardware_status=True,
        all192_body_frames_and139_shot_frames_both_encoded_facings_clip_rotation_capacity_paths=True,
        invalid_slot_state_type_frame_paths=True,actual_unmodified_flat_C2_publisher_and_CF_records=True,
        exact12_slot_order_finalTurn_Slot_X_AXYP_SP_OAM_and_all_data_except_pending40=True,
        every_differing_dead_stack_cell_last_write_consumed_by_actual_PLA_PLP_RTS=True,
        exact_dead_stack_cells=[dict(address=at,cases=n)for at,n in sorted(dead.items())],
        every_live_caller_byte_compared=True,minimum_SP=minimum,
        cycle_savings=[dict(path=path,cycles=cy,cases=n)for(path,cy),n in sorted(cost.items())],
        incoming_internal_shot_A_C_dead_before_first_use=True,
        intermediate_Turn_changes_still_require_actual_reached_ISR_reader_proof=True,
        actual_NesBus_header_ISR_full_route_gates_not_replaced=True,outputs=0)


if __name__=='__main__':
    raw=C.load_current_image()
    def deny(*a,**kw):raise AssertionError('Renderer unit attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    q.update(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,native=False,new_whole_ROM_or_NesBus_mount=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
