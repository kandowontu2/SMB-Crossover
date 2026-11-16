"""Detached caller/real SFC proof; new arrays execute only at unit PCs."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import plan_contra_force_shared_tail_1115 as P

C,N,W=P.C,P.N,P.W
ROUTER,HELPER=0x5020,0x4099


class UnitMemory(list):
    def __init__(self,raw,router,helper,carrier,smc):
        super().__init__([0]*65536);self.raw=raw;self.tags=[254,215,2,255]
        self.ram=[bytearray(8192)for _ in range(4)]
        for i in(1,2,3):self.ram[i][:]=carrier[(i-1)*8192:i*8192]
        self[ROUTER:ROUTER+224]=router;self[HELPER:HELPER+175]=helper;self[0x15a:0x17b]=smc
        self.watch=False;self.writes=set();self.checks=Counter()
    def __getitem__(self,at):
        if not isinstance(at,int):return [self[i]for i in range(*at.indices(65536))]
        if at>=0x8000:
            tag=self.tags[(at-0x8000)//8192]
            return self.raw[16+(tag&127)*8192+(at&8191)]if tag&128 else self.ram[tag][at&8191]
        return super().__getitem__(at)
    def __setitem__(self,at,v):
        if not isinstance(at,int):
            for i,x in zip(range(*at.indices(65536)),v,strict=True):self[i]=x
            return
        if getattr(self,'watch',False):self.writes.add(at)
        if at>=0x8000:
            tag=self.tags[(at-0x8000)//8192];assert not tag&128,('Unit attempted immutable code write',at,tag)
            self.ram[tag][at&8191]=v
        else:
            super().__setitem__(at,v)
            if at==0x5115:self.tags[1]=v
            if at==0x5116:self.tags[2]=v


def run(raw,smoke=False):
    q,_=P.Prior.bindings(raw);b=q['bundle'];desc=P.descriptor(raw)
    router=bytearray(raw[716848:716848+224])
    assert router[:108]==bytes.fromhex('4c8eb0')*36
    for i in range(0,108,3):router[i+1:i+3]=(ROUTER+110).to_bytes(2,'little')
    needle=bytes.fromhex('a9998d6c01a9b78d6d01');assert router.count(needle)==1
    router=router.replace(needle,bytes.fromhex('a9998d6c01a9408d6d01'))
    target_index=router.index(bytes.fromhex('8d620168a868aa688d6a01284c5d01'));target_PC=ROUTER+target_index
    smc=bytes.fromhex(desc['actual_33byte_FarCall_source']['hex'])
    old=P.old_code(raw,HELPER);new,_=P.new_code(raw,HELPER)
    memories=[UnitMemory(raw,router,h,q['carrier'],smc)for h in(old,new)]
    cf_cookie=raw[W.location(b,'CfExternalCookie'):W.location(b,'CfExternalCookie')+16]
    bt_cookie=raw[W.location(b,'BtCookie'):W.location(b,'BtCookie')+16]
    bw_pc=W.address(b,'BwCheck');bw_bank=(W.location(b,'BwCheck')-16)//8192|128
    cycles=Counter();deltas={};cases=0;minimum=255;dead_stack=set();getter_entries=Counter();header_counts=Counter()
    def one(owner,slot,p,group=0,bad=None,mode=(1,3),a=85,x=71,y=37):
        nonlocal cases,minimum
        results=[]
        for m in memories:
            m.watch=False;m.writes.clear();m.checks.clear();m.tags[:]=[254,215,2,255]
            m[0x100:0x200]=[(i*29+p)&255 for i in range(256)];m[0x1e1:0x1e3]=[239,255]
            # The genuine SFC producer lives in page1, below the legal live
            # caller stack. Restore it after the synthetic dead-stack fill.
            m[0x15a:0x17b]=smc
            m[0x145]=215;m[0x7da1]=2;m[0x6002]=owner;m[0x5fe8]=group
            m[W.address(b,'OperMode')]=mode[0];m[W.address(b,'OperMode_Task')]=mode[1]
            m.ram[2][0x1fe0:0x1ff0]=cf_cookie;m.ram[2][0x1fe2]=(group>>3)&3
            m.ram[3][0x1fe0:0x1ff0]=bt_cookie
            if bad is not None:
                bank=2 if owner==31 else 3;m.ram[bank][0x1fe0+bad]^=1
            m[0x16a]=a;m[0x16c:0x16e]=(ROUTER+3*slot).to_bytes(2,'little')
            c=N.NesMPU(memory=m,pc=0x15a);c.a=215;c.x=x;c.y=y;c.p=p;c.sp=224
            armed=None;worker=None;gets=[];transport=[];m.watch=True
            for _ in range(2500):
                if c.pc==0xfff0:break
                if c.pc==HELPER:
                    ret=m[0x101+c.sp]+256*m[0x102+c.sp]
                    assert ret==0x16d and m[0x103+c.sp]==215,('Mandatory real SFC helper frame',ret,c.sp)
                    gets.append((c.a,c.x,c.y,c.p,c.sp))
                if c.pc==target_PC:armed=(c.a,m[0x16c]+256*m[0x16d])
                if c.pc==0x16b and len(transport)<16:
                    transport.append(dict(target=m[0x16c]+256*m[0x16d],bank=m.tags[1],SP=c.sp,A=c.a,X=c.x,Y=c.y))
                tag=m.tags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
                if(tag,c.pc)==(197,0xbf47):m.checks['CfOrBtCheck']+=1
                if(tag,c.pc)==(221,0xadc0):m.checks['BtCheck']+=1
                if(tag,c.pc)==(2,0xbe6e):m.checks['private_CF_router']+=1
                fixture=False
                if(tag,c.pc)==(bw_bank,bw_pc):
                    # Foreign Bowser header is unchanged. Both valid/reject
                    # results are explicit fixtures; CF/BT real checks run.
                    m.checks['unchanged_BwCheck_fixture']+=1;c.p=(c.p&254)|(0 if bad is not None else 1);fixture=True
                elif armed and((armed[0]==2 and(tag,c.pc)==(2,0xca0b))or(armed[0]!=2 and(tag,c.pc)==armed)):
                    assert worker is None
                    worker=(armed,(c.a,c.x,c.y,c.p,c.sp),bytes(m[0x101+c.sp:0x200]),tuple(m.tags))
                    c.a=a^167;c.x=(x+13)&255;c.y=y^128;c.p=(p^197)|32;fixture=True
                minimum=min(minimum,c.sp)
                if fixture:c.pc=(c.stPopWord()+1)&65535;c.processorCycles+=6
                else:
                    assert m[c.pc]!=0,('Detached caller BRK',owner,slot,p,bad,c.pc,m.tags)
                    try:c.step()
                    except AssertionError as error:
                        raise AssertionError(('Unit transport diagnostic',owner,slot,p,bad,c.pc,armed,gets,
                            dict(BwCheck_PC=bw_pc,BwCheck_bank=bw_bank),transport,str(error)))from error
            else:raise AssertionError(('Detached caller instruction bound',owner,slot,p,bad,c.pc,m.tags))
            m.watch=False
            assert c.sp==226
            results.append(dict(cpu=(c.a,c.x,c.y,c.p,c.sp),worker=worker,gets=gets,
                tags=tuple(m.tags),smc=bytes(m[0x15a:0x17b]),checks=dict(m.checks),cycles=c.processorCycles,m=m))
        l,r=results
        for name in('cpu','worker','gets','tags','smc','checks'):
            assert l[name]==r[name],('Caller mismatch',name,owner,slot,p,group,bad,mode,l[name],r[name])
        addresses=l['m'].writes|r['m'].writes
        assert all(l['m'][i]==r['m'][i]for i in addresses if not 0x100<=i<0x200),('Non-stack protocol difference',owner,slot,p,bad)
        assert all(l['m'].ram[i]==r['m'].ram[i]for i in range(4)),('Physical private RAM difference',owner,slot,p,bad)
        assert l['m'][0x1e1:0x200]==r['m'][0x1e1:0x200]
        dead_stack.update(i for i in addresses if 0x100<=i<0x1e1 and l['m'][i]!=r['m'][i])
        delta=l['cycles']-r['cycles'];cycles[owner,delta]+=1;deltas[owner,slot,mode,bad]=delta
        getter_entries[len(l['gets'])]+=1;header_counts[tuple(sorted(l['checks'].items()))]+=1;cases+=1
    statuses=(32,49,105,229)if smoke else tuple(p for p in range(256)if p&32)
    for owner in(27,29,31,33):
        for slot in range(36):
            for p in statuses:one(owner,slot,p)
        print('PROGRESS '+json.dumps(dict(owner=owner,cases=cases)),flush=True)
    basic=cases
    if not smoke:
        for owner in(27,29,31,33):
            for slot in range(36):
                for group in(0,1,5,6,7,32,255):
                    for mode in((0,0),(1,1)):
                        for p in(49,229):one(owner,slot,p,group=group,mode=mode)
        for owner in(31,33):
            for slot in range(36):
                for bad in range(16):one(owner,slot,105,bad=bad)
    return dict(cases=cases,all36_queries_four_legal_cohorts_all_hardware_status=basic,
        complete_caller_AXYP_SP_maps_callback_input_live_stack_all33SMC_and_nonstack_data_equal=True,
        actual_shared_FarCall33_and_Bw213_executed=True,actual_CF_outer_and_private_header_and_BT_full_header_executed=True,
        unchanged_other_handlers_represented_by_explicit_return_fixtures=True,
        helper_entry_actual_SFC_frame_acknowledged=True,callback_and_final_caller_live_stack_exact=True,
        discarded_getter_frame_dead_stack_addresses=sorted(dead_stack),
        dead_bytes_below_matched_callback_or_final_caller_stack_only=True,
        minimum_SP=minimum,helper_entry_counts=dict(getter_entries),header_count_signatures=len(header_counts),
        cycle_savings=[dict(owner=o,saved_cycles=d,cases=n)for(o,d),n in sorted(cycles.items())],
        CF_per_slot_savings=[dict(slot=s,saved_cycles=deltas[31,s,(1,3),None])for s in range(36)],
        no_NesBus_or_changed_game_PC_opcodes=True,detached_unit_PCs=dict(Router=ROUTER,helper=HELPER),
        no_whole_image_mount_native_or_delivery=True,outputs=0)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');args=ap.parse_args()
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    def deny(*a,**kw):raise AssertionError('Detached caller proof attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(raw,args.smoke)
    q.update(owning_ROM_SHA256=C.CANDIDATE,smoke=args.smoke)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
