"""Leased whole-public SFC components on actual91dc/44b opcodes."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import contra_force_checked_resolver_model_1116 as M

C,N,W=M.C,M.N,M.W


class Memory(list):
    def __init__(self,raw,smc):
        super().__init__([0]*65536);self.raw=raw;self.tags=[254,215,2,255]
        self.ram=[bytearray(8192)for _ in range(4)];self.smc=smc;self.watch=False;self.cpu=None
        self.writes=set();self.header=Counter();self.private=0;self.lastread={};self.lastwrite={};self.tick=0;self.op=0
    def __getitem__(self,at):
        if not isinstance(at,int):return[self[i]for i in range(*at.indices(65536))]
        if self.watch and self.cpu is not None:
            if 0x100<=at<0x200 and not 0x15a<=at<0x17b:self.lastread[at]=(self.tick,self.op)
            if at>=0x8000 and self.tags[(at-0x8000)//8192]==2 and 0x1fe0<=at&8191<0x1ff0:
                tag=self.tags[(self.cpu.pc-0x8000)//8192]if self.cpu.pc>=0x8000 else-1
                if tag==197:self.header['outer',(at&8191)-0x1fe0]+=1
                elif tag==2:self.header['inner',(at&8191)-0x1fe0]+=1
        if at>=0x8000:
            tag=self.tags[(at-0x8000)//8192]
            return self.raw[16+(tag&127)*8192+(at&8191)]if tag&128 else self.ram[tag][at&8191]
        return super().__getitem__(at)
    def __setitem__(self,at,value):
        if not isinstance(at,int):
            for i,v in zip(range(*at.indices(65536)),value,strict=True):self[i]=v
            return
        if self.watch:self.writes.add(at);self.lastwrite[at]=self.tick
        if at>=0x8000:
            tag=self.tags[(at-0x8000)//8192];assert not tag&128,('Immutable ROM write',at,tag)
            self.ram[tag][at&8191]=value
        else:
            super().__setitem__(at,value)
            if at==0x5115:self.tags[1]=value
            elif at==0x5116:self.tags[2]=value


def run(parent,smoke=False,groups_only=False):
    candidate,_=C.proposal(parent);b=M.symbols(parent)
    at=W.location(b,'FarCallCommon');smc=parent[at:at+33];assert W.address(b,'FarCallCommon')==0x15a
    assert smc[9:15]==bytes.fromhex('8d45018d1551')
    cf=parent[2006032:2030608];cf_cookie=parent[573373:573389]
    bw_at=W.location(b,'BwCookie');bw_cookie=parent[bw_at:bw_at+16]
    bt_cookie=parent[C.BT.COOKIE:C.BT.COOKIE+16]
    bwseg=next(s for s in b['segs'].values()if s['name'].strip('"')=='BW_STREAM')
    bw_at=int(bwseg['ooffs'],0);bw_payload=parent[bw_at:bw_at+8192]
    labels=C.Plan.Rejected.Source.M.C.Plan.inputs(C.reference(parent))[1]
    targets=[cf[8192+(labels['CfOwnLo']&8191)+i]+256*cf[8192+(labels['CfOwnHi']&8191)+i]for i in range(36)]
    memories=[Memory(raw,smc)for raw in(parent,candidate)];cycles=Counter();headercounts=Counter();dead=Counter();opaque=Counter();cases=0;minimum=255
    targetPCs=[0xb020+parent[716848:717072].index(bytes.fromhex('8d620168a868aa688d6a01')),
               C.Plan.router(parent[716848:717072])[1]['Target']]
    def one(owner,slot,p,group=0,poison=None,mismatch=False,oldC=2):
        nonlocal cases,minimum
        out=[]
        for side,m in enumerate(memories):
            m.watch=False;m.tags[:]=[254,215,oldC,255]
            for i in(1,2,3):m.ram[i][:]=cf[(i-1)*8192:i*8192]
            if owner==33:m.ram[3][:]=parent[C.BT.CACHE:C.BT.CACHE+8192]
            elif owner==27:m.ram[3][:]=bw_payload
            m.ram[2][0x1fe0:0x1ff0]=cf_cookie;m.ram[2][0x1fe2]=(group>>3)&3
            if mismatch:m.ram[2][0x1fe2]^=1
            if owner in(27,33):m.ram[3][0x1fe0:0x1ff0]=bw_cookie if owner==27 else bt_cookie
            if poison is not None:m.ram[2 if owner==31 else 3][0x1fe0+poison]^=1
            m[0x100:0x200]=[(i*29+p)&255 for i in range(256)];m[0x15a:0x17b]=smc;m[0x1e1:0x1e3]=[239,255]
            m[0x145]=215;m[0x7da1]=oldC;m[0x6002]=owner;m[0x5fe8]=group
            m[W.address(b,'OperMode')]=1;m[W.address(b,'OperMode_Task')]=3
            m[0x16a]=85;m[0x16c:0x16e]=(0xb020+3*slot).to_bytes(2,'little')
            m.header.clear();m.private=0;m.writes.clear();m.lastread.clear();m.lastwrite.clear();m.tick=0
            cpu=N.NesMPU(memory=m,pc=0x15a);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=215,71,37,p,224
            armed=None;worker=None;checks=Counter();m.cpu=cpu;m.watch=True
            for _ in range(6000):
                if cpu.pc==0xfff0:break
                tag=m.tags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
                m.op=m[cpu.pc];m.tick+=1
                if(tag,cpu.pc)==(197,0xbf47):checks['CfOrBtCheck']+=1
                if(tag,cpu.pc)==(221,0xadc0):checks['BtCheck']+=1
                if tag==2:
                    assert all(m.header['outer',i]for i in range(16)),('Private opcode before full16',owner,slot,p,poison,cpu.pc)
                    m.private+=1
                if(tag,cpu.pc)==(215,targetPCs[side])and cpu.p&1:
                    armed=(cpu.a,m[0x16c]+256*m[0x16d])
                destination=(3,targets[slot])if armed and armed[0]==2 else armed
                if destination and(tag,cpu.pc)==destination and worker is None:
                    worker=dict(destination=destination,registers=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp),
                        live_stack=bytes(m[0x101+cpu.sp:0x200]),maps=tuple(m.tags),SMC33=bytes(m[0x15a:0x17b]))
                    if destination not in((224,0xb2cb),(224,0xb2cd)):
                        # Explicit callback return fixture, not a gameplay run.
                        cpu.a=242;cpu.x=84;cpu.y=165;cpu.p=(p^197)|32
                        cpu.pc=(cpu.stPopWord()+1)&65535;cpu.processorCycles+=6;continue
                assert m[cpu.pc],('Public component BRK',owner,slot,p,poison,side,hex(cpu.pc),m.tags)
                minimum=min(minimum,cpu.sp);cpu.step()
            else:raise AssertionError(('Public component bound',owner,slot,p,poison,side,cpu.pc))
            m.watch=False;assert cpu.sp==226
            out.append(dict(registers=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp),worker=worker,maps=tuple(m.tags),
                cycles=cpu.processorCycles,checks=dict(checks),private=m.private,header=dict(m.header)))
        a,z=out
        for key in('registers','worker','maps'):assert a[key]==z[key],('Public mismatch',key,owner,slot,p,poison,a,z)
        l,r=memories;assert all(l.ram[i]==r.ram[i]for i in range(4)),('Private RAM mismatch',owner,slot,p,poison)
        differences=[at for at in l.writes|r.writes if l[at]!=r[at]]
        nonstack=[at for at in differences if not 0x100<=at<0x200 or 0x15a<=at<0x17b]
        assert set(nonstack)<={0x162},('Unqualified nonstack difference',owner,slot,p,group,poison,
            [(hex(at),l[at],r[at])for at in nonstack],a['registers'],a['worker'])
        if 0x162 in nonstack:opaque[owner,slot]+=1
        assert bytes(l[0x1e3:0x200])==bytes(r[0x1e3:0x200])
        for at in differences:
            if 0x100<=at<0x1e3 and not 0x15a<=at<0x17b:dead[at]+=1
        if owner==31 and(poison is not None or mismatch):assert not a['private']and not z['private']
        headercounts[owner,a['checks'].get('CfOrBtCheck',0),z['checks'].get('CfOrBtCheck',0)]+=1
        cycles[owner,a['cycles']-z['cycles']]+=1;cases+=1
    statuses=(32,49,105,229)if smoke else tuple(p for p in range(256)if p&32)
    for owner in(()if groups_only else(31,27,29,33)):
        for group in((0,8,16,24)if owner==31 else(0,)):
            for slot in range(36):
                for p in statuses:one(owner,slot,p,group)
        print('PROGRESS '+json.dumps(dict(owner=owner,cases=cases)),flush=True)
    for group in(()if groups_only else(0,8,16,24)):
        for slot in range(36):
            for poison in range(16):one(31,slot,105,group,poison)
            one(31,slot,229,group,mismatch=True)
    if not smoke:
        for owner in(()if groups_only else range(256)):
            if owner in(27,29,31,33):continue
            for slot in(0,12,35):
                for p in(32,49,105,229):one(owner,slot,p)
        for group in(1,2,3,4,5,6,7,32,255):
            for slot in range(36):
                for p in(32,105):one(29,slot,p,group)
        for oldC in(()if groups_only else(0,1,3)):
            for slot in range(36):one(31,slot,105,oldC=oldC)
    opaque_by_owner=Counter()
    for(owner,slot),count in opaque.items():opaque_by_owner[owner]+=count
    q=dict(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,smoke=smoke,cases=cases,minimum_SP=minimum,
        public_callback_AXYP_SP_CVID_maps_live_stack_and_full_private_exact=True,
        actual_CF_outer_inner_and_BT_BW_checks_executed=True,all36_all4CFclass_queries=True,
        unchanged_real_handlers_are_explicit_return_fixtures_not_gameplay=True,
        header_counts=[dict(owner=o,old=a,new=b,cases=n)for(o,a,b),n in sorted(headercounts.items())],
        cycle_savings=[dict(owner=o,cycles=d,cases=n)for(o,d),n in sorted(cycles.items())],
        opaque_NextBank0162_total=sum(opaque.values()),opaque_NextBank_owner_count=len(opaque_by_owner),
        opaque_NextBank0162_top_owners=[dict(owner=o,cases=n)for o,n in opaque_by_owner.most_common(8)],
        dead_stack_difference_addresses=dict(dead),dead_stack_ledger_and_first_consumer_proof_still_pending=True,
        no_actor_health_or_terrain_fixture=True,no_cold_lifecycle_native_or_FPS_claim=True,outputs=0)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');ap.add_argument('--groups-only',action='store_true');args=ap.parse_args()
    parent=C.load_current_image();assert C.H(parent)==C.PIN
    def deny(*a,**kw):raise AssertionError('Public source component attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent,args.smoke,args.groups_only)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
