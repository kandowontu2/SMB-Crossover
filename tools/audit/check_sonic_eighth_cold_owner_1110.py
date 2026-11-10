"""Current-a5 derivative: packed eighth330 cold owner, RAM/stdout only.

Historical coarse FF carrier pins are not silently reused: two changed pages
are rebound by complete reachable writer closure and exact a5 reconstruction.
No ROM, public selector, runtime service table or build artifact is produced.
"""
import argparse
from collections import Counter
from hashlib import sha256
import inspect
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from contextlib import redirect_stdout
from unittest.mock import patch

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import check_sonic_seventh_cold_owner_1110 as S
import check_sonic_fairy_funding_1110 as Alias
import check_ff_mux_unused_tail_1110 as FF
import sonic_sms_native_eighth_payload_1110 as Payload

C,O,N=S.C,S.O,S.N
PIN='a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa'
PARENT='4f205d9d67e40c50adfd383c8318f7c557a4e8a8ce657d7f2d1f40cec6e11de1'
OLD7='d07012de9762e93ca76cb283ba84e9b8a9a7bd532364fd94ce4ca6101687cb72'
PAGE330_PIN='a0d0f990b24bea911ebcfaeaaf4f3b6a4f3a3805b7cb271b6d318a897edadbfa'
CHR=S.CHR
digest=lambda raw:sha256(raw).hexdigest()


def current_authority(old,current):
    assert digest(old)==C.PIN and digest(current)==PIN
    reproduced,*_=FF.proposal(old)
    assert reproduced==current,'Entire current a5 must be exact source reconstruction'
    prior=json.loads((R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json').read_text())
    normalized=bytearray(current);exact=0;rebound=[]
    for row in prior['inherited_private_writer_chunks_exact']:
        candidates=[p for p in row['pages'] if digest(Alias.page_bytes(old,p))==row['SHA256']]
        assert len(candidates)==1,(row,candidates)
        page=candidates[0]
        if Alias.page_bytes(current,page)==Alias.page_bytes(old,page):exact+=1;continue
        assert page in (898,900),(page,row)
        at=CHR+page*1024
        normalized[at:at+1024]=old[at:at+1024]
        changes=[i for i,(a,b)in enumerate(zip(old[at:at+1024],current[at:at+1024]))if a!=b]
        rebound.append(dict(page=page,changed_offsets=changes,current_SHA256=digest(Alias.page_bytes(current,page)),
                            historical_SHA256=row['SHA256']))
    assert exact==13 and {r['page']for r in rebound}=={898,900}
    # Retain every legacy finite table/native map/weapon/SMB3 binding.  Only
    # coarse FF pages are normalized for this historical part of the audit.
    legacy=Alias.Authority.chr_authority(bytes(normalized))
    assert legacy.pop('private_writer_chunks_exact')==15
    bundle=C.Current.W.bundle(current)
    base=CHR+893*1024
    kernels=[q[base:base+8192]for q in(old,current)]
    roots0=FF.Funding.gateways(old,C.Current.W.bundle(old))
    roots1=FF.Funding.gateways(current,bundle)
    assert roots0==roots1 and len(roots0)==37
    flows=[FF.Funding.walk(q,[target for _,target in roots0])for q in kernels]
    assert not any(indirect for _,_,indirect in flows)
    chrbyte=Alias.address(bundle,'SmChrBank')
    def writers(kernel,flow):
        result={};indirect={}
        for pc,row in flow[0].items():
            op,mode=row['mnemonic'],row['mode']
            if op not in('STA','STX','STY','INC','DEC','ASL','LSR','ROL','ROR')or mode=='acc':continue
            blob=kernel[pc-0xa000:pc-0xa000+row['bytes']]
            if mode in('inx','iny','ind'):indirect[pc]=blob;continue
            if mode not in('abs','abx','aby'):continue
            operand=int.from_bytes(blob[1:],'little');hi=operand+(255 if mode in('abx','aby')else 0)
            if operand<=chrbyte<=hi or any(operand<=b and a<=hi for a,b in((0x2000,0x2007),(0x5000,0x5207))):
                result[pc]=blob
        return result,indirect
    before,after=[writers(k,f)for k,f in zip(kernels,flows,strict=True)]
    assert before==after,'Current direct CHR/MMIO and all indirect writer sites/operands must remain exact'
    # The source records and the complete body decoder/publication functions
    # are retained; new priority/head/OAM-tail code owns no pattern publisher.
    ranges=((0xb443,0xb620),(0xb68b,0xb6fe),(0xbb60,0xbcef))
    assert all(kernels[0][lo-0xa000:hi-0xa000]==kernels[1][lo-0xa000:hi-0xa000]for lo,hi in ranges)
    assert old[16+93*8192:16+94*8192]==current[16+93*8192:16+94*8192]
    return dict(**legacy,current_private_writer_scopes_rebound=15,coarse_private_pages_exact=exact,
        changed_coarse_pages_rebound=rebound,current_complete_ROM_source_reproduced=True,
        actual_FF_gateway_roots=37,actual_FF_reachable_instructions=[len(f[0])for f in flows],
        exact_direct_CHR_MMIO_writer_sites=len(before[0]),exact_indirect_writer_sites=len(before[1]),
        exact_body_mux_pickup_ranges=[list(r)for r in ranges],exact_source_record_bank93=True,
        qualification='13 whole pages exact; two FF page hashes differ. Their current reachable CHR/MMIO and indirect writer sites/operands, full body/publication/pickup ranges and source record bank rebound exactly. Legacy normalized carrier census is separately labeled.')


def finite_current(old,current):
    authority=current_authority(old,current)
    # Derivative retains the actual sole bounded Z2 reader and finite source
    # assertions, substituting the explicitly rebound writer-scope predicate.
    source=inspect.getsource(Alias.finite_sources)
    needle="current['private_writer_chunks_exact'] == 15"
    assert source.count(needle)==1
    source=source.replace(needle,"current['current_private_writer_scopes_rebound'] == 15")
    scope=dict(Alias.__dict__)
    scope['Authority']=SimpleNamespace(chr_authority=lambda raw:authority)
    exec(compile(source,'<current a5 finite source authority>','exec'),scope)
    result=scope['finite_sources'](current,C.Current.W.bundle(current))
    assert Alias.page_bytes(current,330)==Alias.page_bytes(current,320)
    assert digest(Alias.page_bytes(current,330))==PAGE330_PIN
    return result


def alias_poison(old,current):
    """Reuse the exact frozen CPU/NMI/negative fixture on this a5 authority."""
    authority=finite_current(old,current)
    target=R/'build/sonic-fairy-funding-audit-1110'
    assert not target.exists()
    text=io.StringIO()
    # Downloads lies outside R.  Preserve every CPU assertion; the sole main
    # source edit displays absolute binding paths instead of relative paths.
    source=inspect.getsource(Alias.main);needle='str(p.relative_to(R))'
    assert source.count(needle)==1;source=source.replace(needle,'str(p.resolve())')
    scope=dict(Alias.__dict__);scope.update(ROM=Path('C:/Users/kando/Downloads')/'SMB-Crossover-Latest-WIP-MMC5.nes',
        PIN=PIN,finite_sources=lambda raw,b:authority)
    exec(compile(source,'<current a5 alias poison fixture absolute bindings>','exec'),scope)
    with patch.object(sys,'argv',[str(Path(Alias.__file__)),'--output',str(target)]),redirect_stdout(text):
        scope['main']()
    report=json.loads(text.getvalue().splitlines()[-1])
    assert report['passed']and report['all27_table_indices_seen']and report['wrong_unaliased_poison_negative_detected']
    assert report['parent_SHA256']==PIN and not target.exists()
    return report


def proposal(old,current,*,audit=True):
    assert digest(current)==PIN and digest(old)==C.PIN
    old7,program,_,patches,rows,sh=S.proposal(old)
    assert digest(old7)==OLD7
    ff={i for i,(a,b)in enumerate(zip(old,current))if a!=b}
    sonic={i for i,(a,b)in enumerate(zip(old,old7))if a!=b}
    assert len(ff)==155 and len(sonic)==8319 and not ff&sonic
    parent=bytearray(old7)
    for i in ff:parent[i]=current[i]
    assert digest(parent)==PARENT
    authority=finite_current(old,current)if audit else None
    alias=json.loads((R/'docs/qa/allocations/sonic-sms-fairy-repack-1110.json').read_text())['mandatory_atomic_source_change']
    a=alias['file_offset'];assert a==574138
    assert current[a:a+27]==bytes.fromhex(alias['old_hex'])
    assert parent[a:a+27]==bytes.fromhex(alias['new_hex'])
    packet=Payload.build();image=bytearray(parent)
    for index,page in enumerate(packet['code_pages']):
        if page==330:
            assert digest(Alias.page_bytes(parent,page))==PAGE330_PIN
        at=CHR+page*1024
        image[at:at+1024]=packet['kernel'][1024*index:1024*(index+1)]
    at=CHR+328*1024;image[at:at+1024]=packet['metadata']
    at=C.off(126,0x88d8);assert image[at:at+3]==bytes((0xa7,43,1))
    image[at:at+16]=packet['cookie']
    assert all(image[i]==current[i]for i in ff)
    assert Alias.page_bytes(image,329)==Alias.page_bytes(parent,329)
    assert all(Alias.page_bytes(image,p)==Alias.page_bytes(parent,p)for p in(319,320,335))
    changes={i for i,(a,b)in enumerate(zip(parent,image))if a!=b}
    allowed={*range(at,at+16)}
    for p in(*packet['code_pages'],328):allowed.update(range(CHR+1024*p,CHR+1024*(p+1)))
    assert changes<=allowed
    return bytes(image),program,packet,rows,dict(authority=authority,parent_SHA256=PARENT,
        changed_from_combined_parent=len(changes),FF155_preserved=True,Prince329_preserved=True,
        retained_pages=[319,320,335],mandatory_atomic_alias=alias,page330_preimage_SHA256=PAGE330_PIN,
        page330_file_offset=CHR+330*1024,conditional_only=True)


def owned(m,packet):
    assert O.headers(m)==(packet['cookie'],packet['cookie'])
    assert bytes(m.ram[2][:0x900])==bytes(0x900)
    assert bytes(m.ram[2][0x1000:0x1400])==packet['metadata']
    assert bytes(m.ram[3][:0x1fe0])==packet['kernel'][:0x1fe0]


def eighth(trial,program,packet,seeds):
    counts=Counter();own=O.blank(trial);before=tuple(bytes(row)for row in own.ram)
    result=C.cold(own,43,program['new']);owned(own,packet)
    assert result['PPU_reads']==18386,result
    assert result['descriptor_offsets']==[0,1,2,3,4]
    assert bytes(own.ram[3][0x1ff0:])==before[3][0x1ff0:]
    assert bytes(own.ram[2][0x900:0x1000])==before[2][0x900:0x1000]
    assert bytes(own.ram[2][0x1400:0x1fd0])==before[2][0x1400:0x1fd0]
    assert bytes(own.ram[2][0x1fd0:0x1fd3])==before[2][0x1fd0:0x1fd3]
    # No startup write reaches the cold-header region.  Common worker alone
    # invalidates/publishes the two authenticated16-byte headers afterward.
    commits=[(b,v)for b,a,v in own.ram_writes if a==0x1fe0]
    assert commits[-2:]==[(3,0xa7),(2,0xa7)]and all(v==0 for _,v in commits[:-2])
    assert C.invoke(own,O.AUTH)['P']&1
    O.clear_logs(own);warm=S.slim_fork(own)
    assert C.cold(warm,43,program['new'])['PPU_reads']==0 and warm.ram==own.ram
    counts.update(Sonic_cold=1,Sonic_warm=1)
    for bank in(2,3):
        for index in range(16):
            m=S.slim_fork(own);m.ram[bank][0x1fe0+index]^=1
            assert not C.invoke(m,O.AUTH)['P']&1 and not m.ram_writes
            counts['Sonic_header_poisons']+=1
    faults=('write-protection',(2,0x1000),(2,0x13e8),*((3,i)for i in(0,1023,1024,4095,6144,7167,7168,8159)))
    for fault in faults:
        m=O.blank(trial)
        if fault=='write-protection':m.protection=[0,0]
        else:m.corrupt_at=fault
        C.cold(m,43,program['new'],expect_success=False)
        assert O.headers(m)==(bytes(16),bytes(16))and not C.invoke(m,O.AUTH)['P']&1
        counts['Sonic_readback_faults']+=1
    for fields in(dict(SelectedCharacter=44),dict(OperMode=0),dict(FamilyMainCommit=0),dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)):
        m=O.blank(trial);O.scene(m,43);N.put(m,**fields);O.clear_logs(m)
        saved=[bytes(row)for row in m.ram]
        assert not C.invoke(m)['P']&1 and saved==[bytes(row)for row in m.ram]and not m.ram_writes
        counts['Sonic_guard_cases']+=1
    m=S.slim_fork(own)
    assert not C.invoke(m,0xb08c)['P']&1 and not m.ram_writes
    counts['Sonic_public_selector_still_rejects']=1
    for source,(_,seeded)in seeds.items():
        m=S.slim_fork(seeded);C.cold(m,43,program['new']);owned(m,packet)
        C.cold(m,source,program['new']);assert O.headers(m)==O.headers(seeded)
        for bank in(2,3):
            writes={at for b,at,_ in m.ram_writes if b==bank}
            assert all(m.ram[bank][at]==seeded.ram[bank][at]for at in writes)
        assert C.invoke(m,O.AUTH)['P']&1
        counts['Sonic_roundtrip_owner_transitions']+=1
    m=S.slim_fork(own);N.put(m,SelectedCharacter=0);C.invoke(m,O.RETIRE)
    assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0 and not C.invoke(m,O.AUTH)['P']&1
    counts['Sonic_foreign_retire']=1
    return counts,result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--static-only',action='store_true');p.add_argument('--alias-poison',action='store_true');args=p.parse_args()
    assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    old=C.ROM.read_bytes();current=(Path('C:/Users/kando/Downloads')/'SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    if args.alias_poison:
        report=alias_poison(old,current)
        print(json.dumps(dict(passed=True,source_SHA256=digest(Path(__file__).read_bytes()),
            source_only=True,outputs_written=0,current_alias_poison=report),sort_keys=True),flush=True)
        return
    image,program,packet,rows,authority=proposal(old,current)
    receipt=dict(passed=True,source_only=True,outputs_written=0,ROM_written=False,current_parent_SHA256=PIN,
        in_memory_SHA256=digest(image),source_SHA256=digest(Path(__file__).read_bytes()),authority=authority,
        payload_SHA256=digest(packet['kernel']),metadata_SHA256=digest(packet['metadata']),cookie=packet['cookie'].hex(),
        startup_bytes=len(packet['startup']['image']),copy_bytes=packet['copy_bytes'],source_payload_bytes=packet['source_payload_bytes'],
        remaining_before_header=packet['remaining_before_header'],service_base=packet['proposed_service_base'],relocation=packet['relocation'])
    if not args.static_only:
        base,trial=C.Current.W.bundle(current),C.Current.W.bundle(image)
        counts,seeds=S.six_regressions(base,trial,program,rows)
        extra,cold=eighth(trial,program,packet,seeds);counts.update(extra)
        assert C.Current.inventory(current)==C.Current.inventory(image)
        receipt.update(actual_CPU=dict(counts),Sonic_cold_result=cold,all100_menu_entries_exact=True)
    assert not args.output.exists();print(json.dumps(receipt,sort_keys=True),flush=True)


if __name__=='__main__':main()
