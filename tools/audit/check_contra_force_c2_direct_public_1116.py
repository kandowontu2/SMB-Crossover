"""Small actual-opcode public transport smoke; liveness differences stay open."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import contra_force_c2_direct_model_1116 as M
from check_contra_force_checked_public_1116 import Memory

C,N,W=M.C,M.N,M.W


def run(parent):
    image,_=C.proposal(parent);b=M.symbols(parent);labels=M.private_labels(parent)
    at=W.location(b,'FarCallCommon');smc=parent[at:at+33]
    assert W.address(b,'FarCallCommon')==0x15a and smc[9:15]==bytes.fromhex('8d45018d1551')
    payloads=[raw[2006032:2030608]for raw in(parent,image)]
    bw_at=W.location(b,'BwCookie');bw_cookie=parent[bw_at:bw_at+16]
    bwseg=next(s for s in b['segs'].values()if s['name'].strip('"')=='BW_STREAM')
    bw_at=int(bwseg['ooffs'],0);bw_payload=parent[bw_at:bw_at+8192]
    bt=C.Base.BT;bt_cookie=parent[bt.COOKIE:bt.COOKIE+16]
    lo=8192+(labels['CfOwnLo']&8191);hi=8192+(labels['CfOwnHi']&8191)
    targets=[payloads[0][lo+i]+256*payloads[0][hi+i]for i in range(36)]
    memories=[Memory(raw,smc)for raw in(parent,image)]
    old_at=0xb020+parent[716848:717072].index(bytes.fromhex('8d620168a868aa688d6a01'))
    targetPCs=[old_at,C.Base.Plan.router(parent[716848:717072])[1]['Target']]
    count=0;cycles=Counter();SP=Counter();smc_fields=Counter();private_fields=Counter();stacks=Counter();minimum=255;examples=[];checks=Counter()
    def one(owner,slot,p=105,group=0,oldC=2,poison=None,mismatch=False):
        nonlocal count,minimum
        outcomes=[]
        for version,m in enumerate(memories):
            m.watch=False;m.tags[:]=[254,215,oldC,255]
            for tag in(1,2,3):m.ram[tag][:]=payloads[version][(tag-1)*8192:tag*8192]
            if owner==27:m.ram[3][:]=bw_payload
            elif owner==33:m.ram[3][:]=parent[bt.CACHE:bt.CACHE+8192]
            cookie=bytearray(m.raw[573373:573389]);cookie[2]=(group>>3)&3
            if mismatch:cookie[2]^=1
            if poison is not None:cookie[poison]^=1
            m.ram[2][0x1fe0:0x1ff0]=cookie
            if owner in(27,33):m.ram[3][0x1fe0:0x1ff0]=bw_cookie if owner==27 else bt_cookie
            m[0x100:0x200]=[(i*29+p)&255 for i in range(256)];m[0x15a:0x17b]=smc;m[0x1e1:0x1e3]=[239,255]
            m[0x145]=215;m[0x7da1]=oldC;m[0x6002]=owner;m[0x5fe8]=group
            m[W.address(b,'OperMode')]=1;m[W.address(b,'OperMode_Task')]=3
            m[0x16a]=85;m[0x16c:0x16e]=(0xb020+3*slot).to_bytes(2,'little')
            m.header.clear();m.writes.clear();m.private=0;m.lastread.clear();m.lastwrite.clear();m.tick=0
            cpu=N.NesMPU(memory=m,pc=0x15a);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=215,71,37,p,224
            m.cpu=cpu;m.watch=True;armed=None;worker=None;outer=0;new_helper=0
            for _ in range(7000):
                if cpu.pc==0xfff0:break
                tag=m.tags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
                m.op=m[cpu.pc];m.tick+=1
                if(tag,cpu.pc)==(197,0xbf47):outer+=1
                if owner==31 and tag==2:
                    assert all(m.header['outer',i]for i in range(16)),('Private before full16',version,slot,oldC,poison,cpu.pc)
                    m.private+=1
                    if cpu.pc==0xbf91:new_helper+=1
                if(tag,cpu.pc)==(215,targetPCs[version])and cpu.p&1:armed=(cpu.a,m[0x16c]+256*m[0x16d])
                dest=(3,targets[slot])if armed and armed[0]==2 else armed
                if dest and(tag,cpu.pc)==dest and worker is None:
                    worker=dict(target=dest,AXYP=(cpu.a,cpu.x,cpu.y,cpu.p),SP=cpu.sp,maps=tuple(m.tags),SMC=bytes(m[0x15a:0x17b]),
                        native_live=bytes(m[0x1e3:0x200]),C2Args=bytes(m.ram[2][0x2ec:0x2f1]))
                    if dest not in((224,0xb2cb),(224,0xb2cd)):
                        # Explicit effect-handler return fixture: this qualifies
                        # transport only. Natural gameplay uses actual workers.
                        # B/U are canonical status-copy bits, not persistent
                        # hardware flags. Toggle all meaningful fixture flags.
                        cpu.a,cpu.x,cpu.y,cpu.p=242,84,165,(p^197)|48
                        cpu.pc=(cpu.stPopWord()+1)&65535;cpu.processorCycles+=6;continue
                assert m[cpu.pc],('Public BRK',version,owner,slot,oldC,poison,hex(cpu.pc),m.tags)
                minimum=min(minimum,cpu.sp);cpu.step()
            else:raise AssertionError(('Public bound',version,owner,slot,oldC,poison,hex(cpu.pc)))
            m.watch=False;assert cpu.sp==226
            outcomes.append(dict(AXYPSP=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp),worker=worker,maps=tuple(m.tags),cycles=cpu.processorCycles,
                outer=outer,private=m.private,new_helper=new_helper))
        a,z=outcomes
        for key in('AXYPSP','maps'):assert a[key]==z[key],('Public semantic mismatch',owner,slot,p,oldC,poison,key,a,z)
        assert bool(a['worker'])==bool(z['worker'])
        if a['worker']:
            for key in('target','AXYP','maps','native_live'):
                assert a['worker'][key]==z['worker'][key],('Callback mismatch',key,owner,slot,p,oldC,poison,a,z)
            SP[owner,z['worker']['SP']-a['worker']['SP']]+=1
            for i,(x,y)in enumerate(zip(a['worker']['SMC'],z['worker']['SMC'],strict=True)):
                if x!=y:smc_fields['callback',0x15a+i]+=1
        if owner==31 and(poison is not None or mismatch):
            assert not a['private']and not z['private']
            if a['worker']:assert a['worker']['target'][0]>=128,'Cold fallback must be the actual ROM handler, never private CF'
        if owner==31 and oldC!=2 and poison is None and not mismatch:assert z['new_helper']==1 and z['outer']==2
        private_diff=[]
        for tag in range(4):
            for offset,(x,y)in enumerate(zip(memories[0].ram[tag],memories[1].ram[tag],strict=True)):
                if x==y:continue
                if tag==2 and(0x1f91<=offset<0x1fcb or 0x1fe0<=offset<0x1ff0):
                    # Exact declared code/header fixtures are checked against
                    # their own owning inputs; never executed as normalized.
                    if offset<0x1fcb:assert x==payloads[0][8192+offset]and y==payloads[1][8192+offset]
                    else:assert offset>=0x1fe4
                    continue
                private_fields[tag,offset]+=1;private_diff.append((tag,offset,x,y))
        assert all(tag==2 and off in(0x2ef,0x2f0)for tag,off,x,y in private_diff),('New private-state obligation',owner,slot,oldC,private_diff)
        diffs=[i for i in memories[0].writes|memories[1].writes if i<0x8000 and memories[0][i]!=memories[1][i]]
        external=[i for i in diffs if not 0x100<=i<0x200 or 0x15a<=i<0x17b]
        assert all(i in(0x162,0x16c,0x16d)for i in external),('New final RAM/SMC obligation',owner,slot,oldC,external)
        for i in external:smc_fields['final',i]+=1
        assert bytes(memories[0][0x1e3:0x200])==bytes(memories[1][0x1e3:0x200])
        for i in diffs:
            if 0x100<=i<0x1e3 and not 0x15a<=i<0x17b:stacks[i]+=1
        if len(examples)<8 and(a['worker']and oldC==2 or oldC!=2):
            examples.append(dict(owner=owner,slot=slot,oldC=oldC,old_SP=a['worker']['SP']if a['worker']else None,
                new_SP=z['worker']['SP']if z['worker']else None,private_differences=private_diff,final_SMC=external,
                outer_checks=[a['outer'],z['outer']],cycles_saved=a['cycles']-z['cycles']))
        cycles[owner,oldC,a['cycles']-z['cycles']]+=1;checks[owner,oldC,a['outer'],z['outer']]+=1;count+=1
    for group in(0,8,16,24):
        for slot in range(36):
            for p in(32,105):one(31,slot,p,group)
    for oldC in(0,1,3):
        for slot in range(36):one(31,slot,105,oldC=oldC)
    for group in(0,8,16,24):
        for poison in range(16):one(31,14,105,group,poison=poison)
        for slot in(15,18,19):one(31,slot,105,group,poison=0)
        one(31,14,105,group,mismatch=True)
    for owner in(0,27,29,33,255):
        for slot in(0,9,12,13,15,18,19,35):one(owner,slot)
    for group in(6,7):
        for slot in(0,12,35):one(29,slot,group=group)
    q=dict(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,cases=count,minimum_SP=minimum,
        actual_public_and_callback_AXYP_CVID_native_live_stack_maps_semantics_equal=True,
        all36_all4_classes_and_nonC2_fault_fallback_smoke=True,effect_handlers_are_explicit_return_fixtures_not_gameplay=True,
        callback_SP_delta=[dict(owner=o,delta=d,cases=n)for(o,d),n in sorted(SP.items())],
        SMC_differences_requiring_actual_liveness=[dict(when=w,address=at,cases=n)for(w,at),n in sorted(smc_fields.items())],
        private_Arg_differences_requiring_actual_liveness=[dict(tag=t,offset=at,cases=n)for(t,at),n in sorted(private_fields.items())],
        dead_stack_difference_addresses=dict(stacks),examples=examples,
        cycles_saved=[dict(owner=o,oldC=c,cycles=d,cases=n)for(o,c,d),n in sorted(cycles.items())],
        outer_checks=[dict(owner=o,oldC=c,old=a,new=z,cases=n)for(o,c,a,z),n in sorted(checks.items())],
        full_stack_SMC_private_liveness_and_ISR_qualification_complete=False,no_native_or_gameplay_claim=True,outputs=0)
    q['earlier_fixture85263_B0_normalization_negative_retained']=True
    q['effect_return_fixture_uses_hardware_status_copy_BU_ones_no_meaningful_flag_mask']=True
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    parent=C.load_current_image();assert C.H(parent)==C.PIN
    def deny(*a,**kw):raise AssertionError('Public smoke attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
