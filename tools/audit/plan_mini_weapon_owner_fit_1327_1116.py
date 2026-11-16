"""Detached exact18B owner-helper fit, funded by reached Roll exit flags.

No NesBus overlay, whole candidate image, game CPU, ROM file or allocation.
New bytes execute only in a flat primitive address space for comparison.
"""
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import plan_mini_weapon_owner_1327_1116 as Previous

R,ROM,PIN,H,N=Previous.R,Previous.ROM,Previous.PIN,Previous.H,Previous.N
BASE_SHA='6f344918d03a92bd234433d814ff642e5801d512e4eca220333a3d5fcf1c3cc6'
OLD=bytes.fromhex('4c4cb5c9224c7ebf68a828ad6a013860eaea')
NEW=bytes.fromhex('3010ad0260c9224c7ebf68a828ad6a013860')

def patch_descriptor(raw):
    assert H(Path(Previous.__file__).read_bytes())==BASE_SHA
    Previous.Current.bindings(raw)
    assert len(OLD)==len(NEW)==18
    rows=[]
    for pc,old,new in((0xaaeb,b'\x3d',b'\x3c'),(0xaafe,b'\x42',b'\x44'),(0xb53a,OLD,NEW)):
        at=Previous.at(pc);assert raw[at:at+len(old)]==old
        rows.append(dict(bank=79,PC=pc,file_offset=at,length=len(old),old_hex=old.hex(),new_hex=new.hex(),old_SHA256=H(old),new_SHA256=H(new),changed=sum(a!=b for a,b in zip(old,new))))
    return rows

def predicted_hash(raw,rows):
    h=sha256();last=0
    for q in sorted(rows,key=lambda q:q['file_offset']):
        at=q['file_offset'];h.update(raw[last:at]);h.update(bytes.fromhex(q['new_hex']));last=at+q['length']
    h.update(raw[last:]);return h.hexdigest()

def flat_proof(raw,rows):
    base=[0]*65536;base[0xa000:0xc000]=raw[16+79*8192:16+80*8192]
    old=list(base);new=list(base)
    for q in rows:new[q['PC']:q['PC']+q['length']]=bytes.fromhex(q['new_hex'])
    sentinel=0x7ffe
    def run(mem,owner,command,power,balls,flags,start=0xaada,A=None,P=None,X=0x6d,Y=None,slot=0,stop=None):
        mem[0x6002]=owner;mem[0x75b]=power;mem[0x25],mem[0x26]=balls;mem[0x16a]=0x73;mem[0x6897]=slot
        mem[0x1f0:0x1f4]=[0xa6,flags,(sentinel-1)&255,(sentinel-1)>>8]
        c=N.NesMPU(memory=mem,pc=start);c.a=owner if A is None else A;c.x=X;c.y=command if Y is None else Y;c.sp=0xef;c.p=P if P is not None else Previous.cmp_flags(flags,owner,41)if start==0xaada else flags
        for _ in range(80):
            if c.pc in((stop,)if stop else(sentinel,0xbf7e)):break
            c.step()
        else:raise AssertionError(('Flat boundary bound',owner,command,power,balls,hex(c.pc)))
        return dict(PC=c.pc,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,stack=bytes(mem[0x1f0:0x1f4]).hex(),savedA=mem[0x16a],cycles=c.processorCycles)
    flags=(0x20,0x21,0x64,0xe5);shots=((0,0),(1,0),(0,1),(0x80,0),(0,0x81),(1,1))
    foreign=unchanged=corrected=0
    def semantic(q):return{k:v for k,v in q.items()if k!='cycles'}
    for owner,command,p in product(range(256),range(36),flags):
        if owner==41:continue
        a=run(old,owner,command,0,(0,0),p);b=run(new,owner,command,0,(0,0),p)
        assert semantic(a)==semantic(b),(owner,command,a,b);foreign+=1
    for command,power,balls,p in product(range(36),range(3),shots,flags):
        a=run(old,41,command,power,balls,p);b=run(new,41,command,power,balls,p)
        if command==34 and bool((power>>1)|balls[0]|balls[1]):
            reference=run(old,41,command,power,balls,p,start=0xb53d,A=41,P=a['P'])
            assert semantic(b)==semantic(reference),(command,power,balls,a,b,reference);corrected+=1
        else:assert semantic(a)==semantic(b),(command,power,balls,a,b);unchanged+=1
    roll=0
    for p,A,X,Y in product(range(128,256),(0,1,64,128,255),(0,127,128,254,255),(0,127,255)):
        a=run(old,0,0,0,(0,0),p,start=0xb53a,A=A,P=p,X=X,Y=Y,stop=0xb54c)
        b=run(new,0,0,0,(0,0),p,start=0xb53a,A=A,P=p,X=X,Y=Y,stop=0xb54c)
        assert a==b and a['cycles']==3,(a,b);roll+=1
    predecessor=0
    for p,A,Y in product(range(256),(0,1,128,255),(0,127,255)):
        a=run(old,0,0,0,(0,0),p,start=0xb534,A=A,P=p,Y=Y,slot=0,stop=0xb54c)
        b=run(new,0,0,0,(0,0),p,start=0xb534,A=A,P=p,Y=Y,slot=0,stop=0xb54c)
        assert a==b and a['X']==255 and a['P']&128 and a['cycles']==11,(a,b);predecessor+=1
    return dict(foreign_exact=foreign,Mini_unchanged_exact=unchanged,Mini_restored_owner=corrected,
        Roll_N1_direct_exact=roll,Roll_actual_LDX_DEX_BPL_exit_exact=predecessor,
        Roll_skip_cycles_old_and_new=3,Roll_instruction_PC_after_skip=0xb54c,
        scope='Flat CPU only; primitive seeds, no gameplay/ISR/native qualification')

def ingress(raw):
    bank=raw[16+79*8192:16+80*8192];direct={}
    for pc in(0xaada,0xb53a,0xb53c,0xb53d,0xb542,0xb544,0xb54c):
        direct[f'{pc:04X}']=[dict(PC=0xa000+i,opcode=bank[i])for i in range(8190)if bank[i]in(0x20,0x4c)and bank[i+1:i+3]==pc.to_bytes(2,'little')]
    assert direct['AADA']==[dict(PC=0xb83d,opcode=0x4c)]
    assert direct['B53A']==direct['B53C']==direct['B544']==[]
    assert direct['B53D']==[dict(PC=0xaaea,opcode=0x4c)]and direct['B542']==[dict(PC=0xaafd,opcode=0x4c)]
    assert direct['B54C']==[dict(PC=0xb53a,opcode=0x4c)]
    assert raw[Previous.at(0xb534):Previous.at(0xb53d)]==bytes.fromhex('ae9768ca10c74c4cb5')
    source=(R/'src/roll_weapons.s').read_text();assert 'Next:ldx MmSlot\n dex\n bpl Loop\n'in source and'.res 18,$ea\n lda RlSavedObject\n sta ObjectOffset\nDone:rts'in source
    # Explicit 16B native farcall packets cannot name an interior here.
    far=[]
    for pc in range(0xb53a,0xb54c):
        needle=bytes((0xa9,pc&255,0x8d,0x6c,1,0xa9,pc>>8,0x8d,0x6d,1,0xa9,0xcf))
        start=0
        while True:
            at=raw.find(needle,start)
            if at<0:break
            far.append(dict(target=pc,file_offset=at));start=at+1
    assert not far
    return dict(bank79_absolute_machine_references=direct,current_native_farcall_packets_to_owned_interior=far,
        live_predecessor_PC=0xb534,live_predecessor_hex='ae9768ca10c7',
        exit_predicate='B538 BPL not taken immediately after B537 DEX implies N=1 for every reachable fallthrough to B53A.',
        publication='The18B post-loop source reservation has no label/export; Mini Foreign/Handled are local labels in mini_mario_empty_draw.s.',
        closure_limit='No complete arbitrary data/decoded-container indirect-call claim; exact source ownership plus local direct/farcall census is supplied for root review.')

def plan(raw):
    rows=patch_descriptor(raw);a=Previous.at(0xb54c);assert raw[a:a+6]==bytes.fromhex('ad0f5c850d60')
    q=dict(passed=True,proposal_only=True,source_gameplay_overlay=False,ROM_composed=False,fit=True,
        parent_SHA256=PIN,predicted_whole_SHA256=predicted_hash(raw,rows),spans=rows,
        owned_bytes=sum(p['length']for p in rows),changed_bytes=sum(p['changed']for p in rows),
        envelope=dict(gate=[0xaada,0xab00],helper=[0xb53a,0xb54c],helper_bytes=18,
            Roll_skip=[0xb53a,0xb53c],Foreign=[0xb53c,0xb544],Handled=[0xb544,0xb54c]),
        funding='3B JMP B54C ->2B same-page BMI B54C under immediately reached N=1;3cycles unchanged. Frees1B plus original2EA for universal owner reload.',
        primitive=flat_proof(raw,rows),ingress=ingress(raw),
        Mini_payload_SHA256=Previous.Current.PAYLOAD_SHA,Mini_cookie=Previous.Current.COOKIE.hex(),Mini_code_metadata_cookie_changes=0,
        header_changes=0,new_resources=0,live_Roll_B54C_preserved=True,
        required_after_lease=['Full caller/owner routing and header-fault proof','Reached IRQ/busyNMI and foreign/lifecycle regression','Genuine earnedF then2live slots/third rejection/motion+bounce'],
        files=0,gameplay_claim=False,Mesen=False)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':print(json.dumps(plan(ROM.read_bytes()),separators=(',',':')),flush=True)
