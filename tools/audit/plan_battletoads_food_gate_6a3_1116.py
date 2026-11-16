"""Detached three-byte mature-admission plan. No ROM composition or mount."""
from pathlib import Path
from itertools import product
from collections import Counter
import argparse,json
import current_battletoads_stock_6a3_1116 as Current

R,ROM,PIN,W,N=Current.R,Current.ROM,Current.PIN,Current.W,Current.N
ENTRY,ACTIVE,UNAVAILABLE=0xa045,0xae3e,0xb546

def proposal(raw):
    Current.preservation(raw);b=Current.bundle(raw);old=raw[Current.CACHE:Current.CACHE+8192]
    assert W.address(b,'BtActive')==ACTIVE and W.address(b,'BtUnavailable')==UNAVAILABLE
    before=bytes.fromhex('4c46b5');after=b'\x4c'+ACTIVE.to_bytes(2,'little')
    assert old[ENTRY&8191:(ENTRY&8191)+3]==before and old[UNAVAILABLE&8191:(UNAVAILABLE&8191)+2]==b'\x18\x60'
    assert old[0x1fe0:0x1ff0]==bytes(16)
    new=old[:ENTRY&8191]+after+old[(ENTRY&8191)+3:]
    cookie=raw[Current.COOKIE:Current.COOKIE+16];assert cookie[4:]==bytes.fromhex(Current.digest(old))[:12]
    new_cookie=cookie[:4]+bytes.fromhex(Current.digest(new))[:12]
    header=raw[Current.HEADER:Current.HEADER+487];delta=Current.COOKIE-Current.HEADER
    new_header=header[:delta]+new_cookie+header[delta+16:]
    rows=[dict(name='BtCacheServices slot23',CPU=[ENTRY,ENTRY+3],file=[Current.CACHE+(ENTRY&8191),Current.CACHE+(ENTRY&8191)+3],old=before.hex(),new=after.hex()),
          dict(name='Existing full16 Bt cookie',file=[Current.COOKIE,Current.COOKIE+16],old=cookie.hex(),new=new_cookie.hex())]
    for row in rows:
        row.update(old_SHA256=Current.digest(bytes.fromhex(row['old'])),new_SHA256=Current.digest(bytes.fromhex(row['new'])))
    assert sum(a!=b for a,b in zip(old,new,strict=True))==2
    return old,new,dict(owning_parent_SHA256=PIN,detached_only=True,ROM_composed=False,mounted=False,outputs=0,
        spans=rows,owned_bytes=19,changed_bytes=2+sum(a!=b for a,b in zip(cookie,new_cookie,strict=True)),
        old_packet_SHA256=Current.digest(old),proposed_packet_SHA256=Current.digest(new),
        old_header487_SHA256=Current.digest(header),proposed_header487_SHA256=Current.digest(new_header),
        only_private_service23_and_existing_cookie=True,existing_Active_body=old[ACTIVE&8191:(ACTIVE&8191)+41].hex(),
        no_new_code_RAM_carrier_art_physics_helper_capacity=True)

def inspect(raw):
    old,new,q=proposal(raw);b=Current.bundle(raw);m,opening=Current.cold(raw,'rash',True)
    q['actual_parent_cold']=opening
    q['actual_SMC']=dict(first=0x15a,bytes=bytes(m[0x15a:0x17b]).hex(),
        FarCallCommon=W.address(b,'FarCallCommon'),SafecallA_SMC=W.address(b,'SafecallA_SMC'),
        FarcallJmpTarget_SMC=W.address(b,'FarcallJmpTarget_SMC'))
    q['symbols']={n:dict(PC=W.address(b,n),file=W.location(b,n))for n in b['syms']if n.startswith('Bt')and('Cookie'in n or n in('BtCheck','BtServiceVeneers','BtActive','BtUnavailable'))}
    for n in('PowerUpObjHandler','BtCheck'):
        pc,at=W.address(b,n),W.location(b,n)
        if n.startswith('Bt')and n!='BtCheck':continue
        q[n]=dict(PC=pc,file=at,bytes=raw[at:at+256].hex())
    return q

def flat_call(cache,smc,b,values,*,a=0,x=5,y=0,p=0x32):
    # Explicit isolated flat CPU fixture. No NesBus, mapper, gameplay or ROM
    # object is mounted. The real RAM farcall code runs with bank writes inert;
    # the sole target is the actual private service entry and existing leaf.
    m=[0]*65536;m[0x100:0x180]=smc;m[0xa000:0xc000]=cache
    for name,value in values.items():m[W.address(b,name)]=value
    m[W.address(b,'SafecallA_SMC')+1]=a
    at=W.address(b,'FarcallJmpTarget_SMC');m[at+1]=ENTRY&255;m[at+2]=ENTRY>>8
    m[W.address(b,'CurrentBank')]=252
    before=m[:];c=N.NesMPU(memory=m,pc=W.address(b,'FarCallCommon'));c.a=3;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    minimum=c.sp
    for _ in range(160):
        if c.pc==0x5b00:break
        assert m[c.pc],('Flat service BRK',hex(c.pc));minimum=min(minimum,c.sp);c.step()
    else:raise AssertionError(('Flat service bound',c.pc,c.sp))
    assert c.sp==224 and m[W.address(b,'CurrentBank')]==252
    assert all(m[W.address(b,n)]==v for n,v in values.items())
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,minimum_SP=minimum,CPU=c.processorCycles)

def flat_check(header,cookie,b,*,owner=33,p=0x31,bank=193):
    # Actual unchanged BtCheck instructions. DFE0 is its declared private
    # cookie read view; mapper-register writes are inert in this flat fixture.
    m=[0]*65536;m[0xadc0:0xafa7]=header;m[0xdfe0:0xdff0]=cookie
    m[W.address(b,'SelectedCharacter')]=owner;m[0x7da1]=bank
    c=N.NesMPU(memory=m,pc=0xadc0);c.a=85;c.x=7;c.y=91;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    minimum=c.sp
    for _ in range(200):
        if c.pc==0x5b00:break
        assert m[c.pc],('Flat actual BtCheck BRK',hex(c.pc));minimum=min(minimum,c.sp);c.step()
    else:raise AssertionError(('Flat actual BtCheck bound',c.pc))
    assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)and m[0x7da1]==bank
    return dict(P=c.p,A=c.a,X=c.x,Y=c.y,SP=c.sp,minimum_SP=minimum)

def finite(raw):
    old,new,q=proposal(raw);b=Current.bundle(raw);seed,opening=Current.cold(raw,'rash',True)
    smc=list(seed[0x100:0x180]);base=dict(BtHostReady=1,SelectedCharacter=33,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0)
    rows=[];minimum=255;changed_noncarry=Counter()
    def compare(values,expected,**regs):
        nonlocal minimum
        left=flat_call(old,smc,b,values,**regs);right=flat_call(new,smc,b,values,**regs)
        assert left['P']&1==0 and bool(right['P']&1)==expected
        assert(left['X'],left['Y'],left['SP'])==(right['X'],right['Y'],right['SP'])
        # Do not mask these changes: Active changes A/N/Z. Caller liveness
        # below must establish that those outputs are dead at this boundary.
        changed_noncarry[left['A']!=right['A'],bool((left['P']^right['P'])&0x82)]+=1
        assert(left['P']^right['P'])&0x4c==0,'I/D/V preserved'
        minimum=min(minimum,left['minimum_SP'],right['minimum_SP'])
        return left,right
    abi=0
    for a,p,x,y in product((0,85,255),range(256),(0,5),(0,23)):
        compare(base,True,a=a,p=p,x=x,y=y);abi+=1
    guards=0
    for field in base:
        for value in range(256):
            values=dict(base,**{field:value})
            expected=values['BtHostReady']==1 and values['SelectedCharacter']==33 and values['OperMode']==1 and values['GameEngineSubroutine']==8 and values['GamePauseStatus']&1==0 and values['TimerControl']==0
            compare(values,expected);guards+=1
    for variant,health,death,engine in product((0,32),(0,4,47),(0,0xc0),(8,11)):
        values=dict(base,BtVariant=variant,BtSrc_Objects_Life=health,BtSrc_Objects_death_timer=death,GameEngineSubroutine=engine)
        compare(values,engine==8)
    # Guard semantics are deliberately explicit: Active uses native engine,
    # not raw HP. Original underflow sets deathC0 and synchronously KillPlayer;
    # exact zeroHP alone is an original live donor state, not death.
    values=dict(base);left,right=compare(values,True)
    rows.append(dict(case='Actual mature caller A0/P32/X5/Y0',old=left,new=right))
    pc,at=W.address(b,'PowerUpObjHandler'),W.location(b,'PowerUpObjHandler');code=raw[at:at+256]
    tail=bytes.fromhex('205a0190032096a44c04a5');hits=[i for i in range(len(code)-len(tail)+1)if code[i:i+len(tail)]==tail];assert len(hits)==1
    return_pc=pc+hits[0]+3;assert code[hits[0]+3:hits[0]+5]==b'\x90\x03'
    remaining=W.address(b,'RemainingNormalPlayerCollision');rat=W.location(b,'RemainingNormalPlayerCollision')
    assert remaining==0xa496 and raw[rat:rat+6]==bytes.fromhex('b517c92ef01b')
    # Actual caller's first consumer is BCC. The taken collision callee then
    # immediately overwrites A/N/Z and CMP overwrites C. X/Y and I/D/V survive.
    caller_cases=0
    for a,p in product(range(256),range(256)):
        m=[0]*65536;m[remaining:remaining+6]=raw[rat:rat+6];m[W.address(b,'Enemy_ID')+5]=46
        c=N.NesMPU(memory=m,pc=remaining);c.a=a;c.x=5;c.y=0;c.p=p
        c.step();c.step();c.step()
        assert c.pc==remaining+6+0x1b and c.a==46 and c.x==5 and c.y==0
        assert c.p&0x4c==p&0x4c and c.p&0x83==3
        caller_cases+=1
    old_header=raw[Current.HEADER:Current.HEADER+487];delta=Current.COOKIE-Current.HEADER
    old_cookie=raw[Current.COOKIE:Current.COOKIE+16];new_cookie=bytes.fromhex(q['spans'][1]['new'])
    new_header=old_header[:delta]+new_cookie+old_header[delta+16:];header_cases=0
    for header,cookie in((old_header,old_cookie),(new_header,new_cookie)):
        for owner in range(256):
            out=flat_check(header,cookie,b,owner=owner);assert bool(out['P']&1)==(owner==33);header_cases+=1
        for p in range(256):
            out=flat_check(header,cookie,b,p=p);assert out['P']&1 and(out['P']^p)&0xce==0;header_cases+=1
        for i in range(16):
            wrong=bytearray(cookie);wrong[i]^=1;out=flat_check(header,wrong,b);assert out['P']&1==0;header_cases+=1
        assert flat_check(header,bytes(16),b)['P']&1==0;header_cases+=1
    assert flat_check(old_header,new_cookie,b)['P']&1==0 and flat_check(new_header,old_cookie,b)['P']&1==0
    header_cases+=2
    q.update(passed=True,actual_parent_cold=opening,flat_primitive_only=True,no_NesBus_modified_code_mount=True,
        actual_RAM_farcall_and_existing_Active_executed=True,ABI_cases=abi,all256_each_guard_cases=guards,minimum_SP=minimum,
        changed_A_NZ_explicit=[dict(A_changed=a,NZ_changed=z,cases=n)for(a,z),n in changed_noncarry.items()],representative_ABI=rows,
        caller=dict(native_returnPC=return_pc,bytes=tail[3:].hex(),first_consumer='BCC carry only',
            collision_callee=remaining,first6=raw[rat:rat+6].hex(),all65536_A_P_liveness_cases=caller_cases,
            X_Y_and_I_D_V_retained=True,A_N_Z_C_overwritten_before_collision_logic=True),
        full16_actual_BtCheck_flat_cases=header_cases,retired_each_byte_corrupt_and_cross_cookie_reject=True,
        no_claim_all_public_clients_preserve_A_P=True,source_model_or_native_gameplay_qualification=False)
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inspect',action='store_true');a=p.parse_args()
    q=inspect(ROM.read_bytes())if a.inspect else finite(ROM.read_bytes());q['receipt_SHA256']=Current.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
