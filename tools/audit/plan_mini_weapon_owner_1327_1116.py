"""Detached owner-A restoration semantics; deliberately NOT a fitted patch.

Only flat list-backed primitive CPU memory is used. Virtual7000 is a test
address, not NES work RAM, a packet placement, or a physical resource grant.
"""
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import current_mini_stock_1327_1116 as Current

R,ROM,PIN,H,N=Current.R,Current.ROM,Current.PIN,Current.H,Current.N
BANK=79
GATE=bytes.fromhex('d00ec022d00dad5b074a05250526f0134c3db5c009f00cc01dd0f568a828ad6a0118604c42b5')
FOREIGN=bytes.fromhex('c9224c7ebf68a828ad6a013860eaea')
UNPLACED=bytes.fromhex('ad0260c9224c7ebf68a828ad6a013860')

def at(pc):return 16+BANK*8192+(pc&8191)

def cmp_flags(p,a,v):
    n=(a-v)&255
    return(p&~0x83)|(1 if a>=v else 0)|(2 if a==v else 0)|(n&128)

def proof(raw):
    Current.bindings(raw)
    assert raw[at(0xaada):at(0xab00)]==GATE and len(GATE)==38
    assert raw[at(0xb53d):at(0xb54c)]==FOREIGN and len(FOREIGN)==15
    assert raw[at(0xb53a):at(0xb53d)]==bytes.fromhex('4c4cb5')
    assert raw[at(0xb54c):at(0xb552)]==bytes.fromhex('ad0f5c850d60')
    assert raw[at(0xbf7e):at(0xbf85)]==bytes.fromhex('d02da99d4ccfbf')
    source=(R/'tools/reference/mini_mario_empty_draw.s').read_text()
    assert 'ConstantForeign:\n cmp #34\n jmp $bf7e' in source
    base=[0]*65536;base[0xa000:0xc000]=raw[16+BANK*8192:16+(BANK+1)*8192]
    old=list(base);new=list(base);new[0x7000:0x7010]=UNPLACED
    # DETACHED fixture bridges only. Nothing is mounted on a NesBus/ROM.
    new[0xaaea:0xaaed]=[0x4c,0x00,0x70]
    new[0xaafd:0xab00]=[0x4c,0x08,0x70]
    sentinel=0x7ffe
    def run(mem,owner,command,power,balls,flags,start=0xaada,A=None,P=None):
        mem[0x6002]=owner;mem[0x75b]=power;mem[0x25],mem[0x26]=balls;mem[0x16a]=0x73
        mem[0x1f0:0x1f4]=[0xa6,flags,(sentinel-1)&255,(sentinel-1)>>8]
        c=N.NesMPU(memory=mem,pc=start);c.a=owner if A is None else A;c.x=0x6d;c.y=command;c.sp=0xef;c.p=P if P is not None else cmp_flags(flags,owner,41)if start==0xaada else flags
        for _ in range(80):
            if c.pc in(sentinel,0xbf7e):break
            c.step()
        else:raise AssertionError(('Flat boundary bound',owner,command,power,balls,hex(c.pc)))
        return dict(PC=c.pc,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,stack=bytes(mem[0x1f0:0x1f4]).hex(),savedA=mem[0x16a])
    flags=(0x20,0x21,0x64,0xe5);shots=((0,0),(1,0),(0,1),(0x80,0),(0,0x81),(1,1))
    foreign=unchanged=corrected=0;samples=[]
    for owner,command,p in product(range(256),range(36),flags):
        if owner==41:continue
        a=run(old,owner,command,0,(0,0),p);b=run(new,owner,command,0,(0,0),p)
        assert a==b,(owner,command,a,b);foreign+=1
    for command,power,balls,p in product(range(36),range(3),shots,flags):
        a=run(old,41,command,power,balls,p);b=run(new,41,command,power,balls,p)
        active=command==34 and bool((power>>1)|balls[0]|balls[1])
        if active:
            assert a['PC']==b['PC']==0xbf7e and b['A']==41
            reference=run(old,41,command,power,balls,p,start=0xb53d,A=41,P=a['P'])
            assert b==reference,(command,power,balls,a,b,reference);corrected+=1
            if len(samples)<4:samples.append(dict(power=power,balls=balls,old=a,restored=b))
        else:assert a==b,(command,power,balls,a,b);unchanged+=1
    bank=raw[16+BANK*8192:16+(BANK+1)*8192]
    ingress={}
    for pc in(0xaada,0xb53d,0xb542):
        points=[]
        for i in range(8190):
            if bank[i]in(0x20,0x4c)and bank[i+1:i+3]==pc.to_bytes(2,'little'):points.append(dict(PC=0xa000+i,opcode=bank[i]))
        ingress[f'{pc:04X}']=points
    q=dict(passed=True,proposal_only=True,actual_input_SHA256=PIN,
        scope='Flat primitive actual MiniConstants/current foreign-owner selector. No gameplay/candidate/cold/ISR/native qualification.',
        actual_source_controller_negative='f233504928948b5579128764841d5092af6dcc70ba3fa2090a67f87c73beefd9',
        foreign_cases=foreign,Mini_unchanged_cases=unchanged,Mini_owner_restored_cases=corrected,samples=samples,
        owning_bank=BANK,gate=dict(start=0xaada,end=0xab00,bytes=38,preimage_hex=GATE.hex(),SHA256=H(GATE)),
        foreign_and_return=dict(start=0xb53d,end=0xb54c,capacity=15,preimage_hex=FOREIGN.hex(),SHA256=H(FOREIGN)),
        unplaced_helper=dict(bytes=16,hex=UNPLACED.hex(),SHA256=H(UNPLACED),funding_deficit=1,virtual_fixture_address=0x7000,virtual_is_physical_allocation=False),
        live_Roll_boundary=dict(start=0xb54c,hex=raw[at(0xb54c):at(0xb552)].hex(),borrowable=False),
        ingress=ingress,all36_commands_including_move_draw_menu=True,
        CPY34_rejected='BF7E is the Karnov raw-owner34 branch; Y is the command, not the owner.',
        current_Karnov_branch_hex=raw[at(0xbf7e):at(0xbf85)].hex(),
        current_bank79_SHA256=H(bank),Mini_payload_SHA256=Current.PAYLOAD_SHA,Mini_cookie=Current.COOKIE.hex(),
        cookie_change_required_for_native_bank79_only=False,
        predicted_whole_candidate_SHA256=None,fit=False,
        remaining='Fund exact one byte or an equivalent in-place layout, then root lease; candidate public-wrapper/cold/ISR and genuine two-shot gameplay still required.',
        files=0,ROM_composition=False,NesBus_overlay=False,Mesen=False)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':print(json.dumps(proof(ROM.read_bytes()),separators=(',',':')),flush=True)
