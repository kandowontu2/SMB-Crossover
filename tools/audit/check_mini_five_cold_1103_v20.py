"""Actual five-owner fullcold/retire/auth/faults for the payload-derived cookie."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_mini_owner_payload_1103_v19 as P
import check_mini_existing_owners_1103_v17 as Q
import build_storage_guard_v1 as G
O=P.O;N,I,C=Q.N,Q.I,Q.C


def image():
    q=json.loads((O/'payload-manifest-v19.json').read_text())
    for name,digest in q['bindings'].items():assert P.M.sha((R/name).read_bytes())==digest,name
    bundle,_=C.M.image();raw=bytearray(P.M.BASE.read_bytes())
    for row in q['patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new
    assert P.M.sha(raw)==q['memory_SHA256']
    return dict(bundle,raw=bytes(raw)),q


def blank(base,owner):
    m=N.fresh(base)
    for bank in [2,3]:m.ram[bank][:]=bytes([0x9d])*8192;m.ram[bank][0x1fe0:0x1ff0]=bytes(16)
    C.C.fields(m,owner)
    return m


def main():
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=2,fresh=True)
    base,q=image();fit=json.loads((O/'owner-fit-v15.json').read_text());seeds={};rows=[]
    cookie=bytes.fromhex(q['Mini_cookie']);kernel=(P.R/'build/mini-mario-host-1103-v22/mini-host-v22.bin').read_bytes();code=kernel+bytes([255])*(5120-len(kernel));meta=(O/'metadata-v19.bin').read_bytes()
    header_events=[]
    # Install a read-only header-write observer on the actual existing bus.
    sample,_=C.C.cold(base,37);bus=type(sample);original=bus.__setitem__
    def observed(m,at,value):
        if isinstance(at,int)and at>=0x8000:
            bank=m.rawtags[(at-0x8000)//8192]
            if not bank&128 and bank&3 in [2,3]and(at&8191)==0x1fe0:
                header_events.append(dict(bank=bank&3,value=value,PPU_reads=m.ppu_reads))
        return original(m,at,value)
    bus.__setitem__=observed
    try:
        for owner in range(37,42):
            print('Actual final fiveowner cold',owner,flush=True)
            header_events.clear();m,out=C.C.cold(base,owner)
            if owner==41:
                assert bytes(m.ram[3][:5120])==code and bytes(m.ram[2][0x1000:0x1400])==meta
                assert bytes(m.ram[2][:0x900])==bytes(0x900)
                assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])==cookie
                events=list(header_events);published=[x for x in events if x['value']]
                assert [x['bank']for x in published]==[3,2]and all(x['value']==0xa7 for x in published)
                assert all(x['PPU_reads']==published[0]['PPU_reads']for x in published)
                mini_trace=dict(header_byte0_writes=events,all_copy_readback_before_validity=True,source_init_not_called=True)
            seeds[owner]=m;rows.append(dict(owner=owner,CPU=out['CPU'],minimum_SP=out['minSP']))
    finally:bus.__setitem__=original
    transitions=[]
    for before in range(37,42):
        for owner in range(37,42):
            print('Actual final transition',before,owner,flush=True)
            m=N.fork(seeds[before]);C.C.fields(m,owner);out=I.invoke(m,193,0xae00,(83,71,109,0x21))
            assert out['regs'][3]&1 and out['regs'][:3]==[83,71,109]and out['regs'][4]==224
            assert all(bytes(m.ram[k][0x1fe0:0x1ff0])==bytes(seeds[owner].ram[k][0x1fe0:0x1ff0])for k in [2,3])
            if owner==41:assert bytes(m.ram[3][:5120])==code and bytes(m.ram[2][0x1000:0x1400])==meta
            transitions.append(dict(previous=before,owner=owner,CPU=out['CPU'],minimum_SP=out['minSP']))
        m=N.fork(seeds[before]);N.put(m,SelectedCharacter=0);out=I.invoke(m,193,fit['labels']['CoRetire'],(83,71,109,0x21))
        assert out['regs']==[83,71,109,0x21,224]and not m.ram[2][0x1fe0]and not m.ram[3][0x1fe0]
    poisoned=0
    for owner in range(37,42):
        for bank in [2,3]:
            for index in range(16):
                m=N.fork(seeds[owner]);m.ram[bank][0x1fe0+index]^=1;state=[bytes(x)for x in m.ram]
                out=I.invoke(m,193,0xb08c,(83,71,109,0x21))
                assert not out['regs'][3]&1 and state==[bytes(x)for x in m.ram]
                poisoned+=1
    faults=[]
    for name,corrupt,locked in [('protection',None,True),('state',(2,0),False),('metadata',(2,0x1000),False)]+[(f'code-row{i}',(3,i*1024),False)for i in range(5)]:
        m=blank(base,41);m.corrupt_at=corrupt
        if locked:m.protection=[0,0]
        out=I.invoke(m,193,0xae00,(83,71,109,0x21))
        assert not out['regs'][3]&1 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0,name
        faults.append(dict(name=name,CPU=out['CPU'],minimum_SP=out['minSP']))
    guards=[]
    for name,values in [('foreign',dict(SelectedCharacter=42)),('title',dict(OperMode=0)),('uncommitted',dict(FamilyMainCommit=0)),('visible',dict(DisableScreenFlag=0)),('PPU',dict(Mirror_PPUMASK=24)),('NMIzero',dict(NmiDisable=0)),('NMIpositive',dict(NmiDisable=1))]:
        m=blank(base,41);N.put(m,**values);before=[bytes(x)for x in m.ram];reads=m.ppu_reads
        out=I.invoke(m,193,0xae00,(83,71,109,0x21))
        assert not out['regs'][3]&1 and reads==m.ppu_reads and before==[bytes(x)for x in m.ram],name
        guards.append(name)
    result=dict(passed=True,CPU_only=True,ROM_written=False,kernel_Main_CPU_qualification=False,
        memory_SHA256=q['memory_SHA256'],Mini_cookie=q['Mini_cookie'],cold=rows,transitions=transitions,
        foreign_selected_retirements=5,individual_header_poisons=poisoned,copy_verify_faults=faults,cold_guards=guards,
        mini_source_images_exact=True,mini_state_C000_C900_zero=True,mini_commit=mini_trace,
        remaining=['Source deadA/upper-latch continuation closure and actualcold/parser/hot IRQ/genuineFF/nested.','Root currentkernel source/Main/native-ingress proof and final scene/menu/gate composition review before ROM.'],
        bindings={p.relative_to(R).as_posix():P.M.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(Q.__file__),O/'payload-manifest-v19.json',O/'owner-final-v19.s',O/'cold-v19.s',O/'cold-v19.bin',O/'metadata-v19.bin',O/'existing-owner-CPU-v17.json',R/'docs/qa/allocations/mini-mario-private-resources-1103-v24.json']})
    (O/'five-cold-CPU-v20.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','transitions']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'five-cold-negative-v20.json').write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n');raise
