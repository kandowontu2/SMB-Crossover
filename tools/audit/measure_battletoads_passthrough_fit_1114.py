"""Exact unallocated BT dispatch fragments, generated independently of a ROM image."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch
from py65.devices.mpu6502 import MPU

import compose_battletoads_camera_handoff_1114 as C
import check_battletoads_camera_candidate_1114 as Cold
import current_battletoads_dispatch_input_1114 as Input

W,N=Cold.W,Cold.N


class Code:
    def __init__(self,base):self.base=base;self.code=bytearray();self.labels={};self.fix=[]
    @property
    def pc(self):return self.base+len(self.code)
    def mark(self,label):assert label not in self.labels;self.labels[label]=self.pc
    def emit(self,value):self.code.extend(bytes.fromhex(value))
    def absolute(self,op,target):
        self.code.append(op)
        if isinstance(target,str):self.fix.append((len(self.code),target,False));self.code.extend(b'\0\0')
        else:self.code.extend(target.to_bytes(2,'little'))
    def branch(self,op,target):self.code.append(op);self.fix.append((len(self.code),target,True));self.code.append(0)
    def done(self):
        for pos,label,rel in self.fix:
            value=self.labels[label]
            if rel:
                delta=value-(self.base+pos+1);assert-128<=delta<128;(self.code.__setitem__)(pos,delta&255)
            else:self.code[pos:pos+2]=value.to_bytes(2,'little')
        return bytes(self.code)


def router():
    a=Code(0xb020)
    for _ in range(36):a.absolute(0x4c,'Router')
    a.mark('Unavailable');a.emit('1860');a.mark('Router');a.emit('08488a489848ad026038e91bc907')
    a.branch(0xb0,'No');a.emit('2901');a.branch(0xd0,'No');a.emit('ad6c0138e920aaad0260c921')
    a.branch(0xd0,'Common');a.emit('8a29b3c913');a.branch(0xf0,'No')
    a.emit('e033');a.branch(0xf0,'Portrait');a.emit('e04e');a.branch(0xd0,'Common')
    a.emit('a991');a.branch(0xd0,'Cold');a.mark('Portrait');a.emit('a911')
    a.mark('Cold');a.emit('8d6c01a9b08d6d01a9c8');a.branch(0xd0,'Target')
    a.mark('Common');a.emit('8a8d6a01a99d8d6c01a9b78d6d01a9e0205a01');a.branch(0x90,'No')
    a.mark('Target');a.emit('8d620168a868aa688d6a01284c5d01')
    a.mark('No');a.emit('68a868aa688d6a01281860');out=a.done()
    assert len(out)==224 and a.labels['Router']==0xb08e
    return out,a.labels


def head():
    a=Code(0xe49a);a.emit('ad0260c921');a.branch(0xf0,'Native');a.emit('c902');a.branch(0xb0,'Slow')
    a.mark('Native');a.absolute(0x4c,0x9587);a.mark('Slow');a.absolute(0x4c,0xe60f)
    a.mark('SidePrefix');a.emit('a9048d6c014c5bed');out=a.done()
    assert len(out)==25 and a.labels['SidePrefix']==0xe4ab
    return out,a.labels


def side():
    a=Code(0xbea2);a.emit('08a9b08d6c01a9bf8d6d01ad0260');a.branch(0xd0,'Rejected')
    a.emit('a99c205a01');a.branch(0x90,'Legacy');a.emit('a9558d6c01a9b78d6d0128a9024c5a01')
    a.mark('High');a.emit('c921');a.branch(0xf0,'Native');a.emit('c92a');a.branch(0xf0,'Native')
    a.mark('Source');a.emit('6828a9588d6c01a9bc8d6d01a9d94c5a01')
    a.mark('Legacy');a.emit('ad6a01');a.mark('LegacySide');a.emit('48ad0260c904');a.branch(0xf0,'Source')
    a.emit('c90b');a.branch(0xb0,'High');a.mark('Native');a.emit('68284c38bf')
    a.mark('Rejected');a.emit('8d7901a99c8d6201');a.branch(0xd0,'Legacy');out=a.done()
    assert len(out)==94 and a.labels['High']==0xbec9
    return out,a.labels


def literal_edges(raw,target):
    """Literal census only; each edge still needs instruction/data/bank closure."""
    result=[];prg=raw[16:1048592]
    for opcode in(0x20,0x4c,0x6c):
        pattern=bytes((opcode,target&255,target>>8));at=0
        while(at:=prg.find(pattern,at))>=0:
            result.append(dict(PRG=at//8192,CPU=(0xa000 if at//8192<126 else 0x8000 if at//8192==126 else 0xe000)+(at&8191),file=16+at,opcode=opcode));at+=1
    return result


def epilogue_units(old,new):
    rows=0
    for p in range(256):
        if not p&32:continue
        for av,x,y in((0,0,0),(85,7,91),(255,255,255),(128,1,254)):
            pair=[]
            for code in(old,new):
                memory=[0]*65536;memory[0x4000:0x4000+len(code)]=code
                cpu=MPU(memory=memory,pc=0x4000);cpu.sp=236;cpu.stPushWord(0x5aff)
                cpu.stPush(p|16);cpu.stPush(av);cpu.stPush(x);cpu.stPush(y)
                cpu.a=17;cpu.x=19;cpu.y=23;cpu.p=0xe5
                for _ in range(32):
                    if(cpu.pc,cpu.sp)==(0x5b00,236):break
                    cpu.step()
                else:raise AssertionError('Epilogue return bound')
                pair.append((cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,memory[0x16a]))
            assert pair[0]==pair[1]==(av,x,y,p&0xee|32,236,av),(p,pair);rows+=1
    return rows


def branch_units(raw):
    """Detached code/ABI units; external native/source queries are terminal contracts."""
    counts={};intentional={}
    for name,prg,pc,n,recipe in(('head',127,0xe49a,25,head),('side',33,0xbea2,94,side)):
        at=16+prg*8192+(pc&8191);programs=(raw[at:at+n],recipe()[0]);count=0;changed=0
        for owner in range(256):
            for p in range(32,256):
                if not p&32:continue
                for admitted in((False,True)if owner==0 and name=='side'else(False,)):
                    results=[]
                    for code in programs:
                        memory=[0]*65536;memory[pc:pc+len(code)]=code;memory[0x6002]=owner;memory[0x16a]=85
                        c=MPU(memory=memory,pc=pc);c.a=85;c.x=7;c.y=91;c.p=p;c.sp=236;c.stPushWord(0x5aff)
                        callbacks=0
                        for _ in range(96):
                            if c.pc in(0x9587,0xe60f,0xbf38):break
                            if c.pc==0x15a:
                                target=memory[0x16c]+256*memory[0x16d]
                                if target!=0xbfb0:break
                                # Public predicate contract only: AXYP retained except C.
                                c.a=memory[0x16a];c.p=(c.p&~1)|int(admitted);c.pc=c.stPopWord()+1;callbacks+=1;continue
                            c.step()
                        else:raise AssertionError((name,owner,p,hex(c.pc)))
                        assert c.pc in(0x9587,0xe60f,0xbf38,0x15a)
                        results.append((c.pc,c.a,c.x,c.y,c.p&0xef,c.sp,memory[0x16a],memory[0x16c],memory[0x16d],memory[0x162],memory[0x179],callbacks))
                    if owner==33:
                        assert results[1][0]==(0x9587 if name=='head' else 0xbf38)
                        changed+=1
                    else:assert results[0]==results[1],(name,owner,p,admitted,results)
                    count+=1
        counts[name]=count;intentional[name]=changed
    return dict(detached_units=True,external_queries_terminal_not_stubbed_gameplay=True,
        public_raw0_predicate_contract='AXYP retained except returned C; both outcomes tested',
        all_owner_all128_valid_status_cases=counts,selected33_intentional_native_routes=intentional,
        every_foreign_owner_exact_AXYP_SP_SMC_and_terminal=True,no_ROM_code_placement=True)


def measure(raw,abi=False):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    b=dict(W.Symbols.bundle(),raw=raw);rows=[]
    for name,prg,pc,n,recipe in(('router',87,0xb020,224,router),):
        at=16+prg*8192+(pc&8191);old=raw[at:at+n];new,labels=recipe()
        rows.append(dict(name=name,PRG=prg,CPU_half_open=[pc,pc+n],file_half_open=[at,at+n],old_hex=old.hex(),
            old_SHA256=sha256(old).hexdigest(),proposed_hex=new.hex(),proposed_SHA256=sha256(new).hexdigest(),labels=labels))
    r=rows[0];old=bytes.fromhex(r['old_hex']);new=bytes.fromhex(r['proposed_hex'])
    assert old[-17:]==bytes.fromhex('68a868aa688d6a016829fe48ad6a012860')
    count=epilogue_units(old[-17:],new[-11:])
    valid=[3*x for x in range(36)];selected=[x for x in valid if x&0xb3==0x13];assert selected==[27,87]
    cache=bytearray(raw[C.BASE:C.BASE+8192]);metadata=[]
    for slot,old_target,target in((10,0xb2d9,0x9587),(14,0xb2eb,0x958b)):
        pos=3*slot;assert cache[pos:pos+3]==bytes((0x4c,old_target&255,old_target>>8))
        old=bytes(cache[pos+1:pos+3]);new=target.to_bytes(2,'little');cache[pos+1:pos+3]=new
        metadata.append(dict(slot=slot,file_half_open=[C.BASE+pos+1,C.BASE+pos+3],old_hex=old.hex(),proposed_hex=new.hex(),
            original_full_validation_retained=True,target_fixed_PRG=126,target_CPU=target))
    digest=sha256(cache).hexdigest();cookie=raw[765863:765867]+bytes.fromhex(digest)[:12]
    native=[]
    for name,prg,pc,n,recipe in(('head',127,0xe49a,25,head),('side',33,0xbea2,94,side)):
        at=16+prg*8192+(pc&8191);old=raw[at:at+n];new,labels=recipe()
        native.append(dict(name=name,PRG=prg,CPU_half_open=[pc,pc+n],file_half_open=[at,at+n],
            old_hex=old.hex(),old_SHA256=sha256(old).hexdigest(),proposed_hex=new.hex(),proposed_SHA256=sha256(new).hexdigest(),labels=labels))
    callers=literal_edges(raw,0xe4a7);assert[(r['PRG'],r['file'])for r in callers]==[(119,978271),(120,986463),(125,1027423),(127,1043807)]
    for row in callers:
        at=row['file'];assert raw[at:at+3]==bytes.fromhex('4ca7e4')
        row.update(operand_file=at+1,old_hex='a7',proposed_hex='ab',current_instruction='4ca7e4',proposed_instruction='4cabe4')
    return dict(ROM_SHA256=C.CANDIDATE,fragments=rows,whole_ROM_image_composed=False,opcode_placement=False,
        smaller_validated_alternative=dict(private_API_operand_proposals=metadata,proposed_8192_payload_SHA256=digest,
            existing_cookie_proposal=dict(file_half_open=[765867,765879],old_hex=raw[765867:765879].hex(),proposed_hex=cookie[4:].hex(),full_cookie=cookie.hex()),
            session16608_optimistic_cycles_saved=1950,preferred_larger_contract=False),
        router_funding=dict(new_guard_bytes=6,old_epilogue=17,new_epilogue=11,net_growth=0,all224_bytes_used=True,
            all128_valid_status_epilogue_cases=count,SafeA_and_AXYP_SP_exact=True,
            legal_public_target_domain=['B020+3*slot',0,35],mask_matches_offsets=selected,
            illegal_unaligned_router_offsets=[x for x in range(256)if x&0xb3==0x13 and x not in valid],
            selected33_only=True,following_CMP_to_CPX_same_width=True,all_cookie_APIs_unchanged=True),
        cache_independent_native_contract_research=dict(prior_fault_negative='50126 all17bad-header/absent-cache states intentionally change old rejection ABI',
            fragments=native,head_prefix_operand_consumers=callers,
            side_envelope=[278194,278288],side_moved_literal_inbound={hex(pc):literal_edges(raw,pc)for pc in(0xbecd,0xbede,0xbee2,0xbeef,0xbef4)},
            detached_branch_ABI=branch_units(raw)if abi else'Use --abi',allocation_granted=False,placement=False),
        source_proposal_only=True,allocation_granted=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--abi',action='store_true');args=ap.parse_args()
    raw,input_info=Input.load()
    def forbid(*args,**kwargs):raise RuntimeError('BT fit attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Runner.Native,'run',forbid):q=measure(raw,args.abi)
    q.update(input_info);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
