"""Bound an explicit final Mini kernel; no ROM output or hard-coded host revision."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_mini_owner_payload_1103_v19 as P
import check_mini_five_cold_1103_v20 as F
import build_storage_guard_v1 as G
O=P.O;N,I,C=F.N,F.I,F.C


def qualify(kernel_path,expected_sha256,metadata_path=None,art_path=None):
    """Return qualified final memory bundle and disjoint recipe, without emit."""
    kernel_path=Path(kernel_path).resolve();metadata_path=Path(metadata_path or O/'metadata-v19.bin').resolve();art_path=Path(art_path or R/'build/mini-mario-art-1103-v12/body.chr').resolve()
    kernel=kernel_path.read_bytes();meta=metadata_path.read_bytes();art=art_path.read_bytes()
    base,q=P.compose(kernel,meta,art,expected_sha256)
    fit=json.loads((O/'owner-fit-v15.json').read_text());cookie=bytes.fromhex(q['Mini_cookie'])
    code=kernel+bytes([255])*(5120-len(kernel));mini,out=C.C.cold(base,41)
    assert bytes(mini.ram[3][:5120])==code and bytes(mini.ram[2][0x1000:0x1400])==meta
    assert bytes(mini.ram[2][:0x900])==bytes(0x900)
    assert all(bytes(mini.ram[k][0x1fe0:0x1ff0])==cookie for k in [2,3])
    transitions=[]
    for owner in [37,38,39,40]:
        previous,_=C.C.cold(base,owner)
        for before,destination in [(previous,41),(mini,owner)]:
            m=N.fork(before);C.C.fields(m,destination);call=I.invoke(m,193,0xae00,(83,71,109,0x21))
            assert call['regs'][:3]==[83,71,109]and call['regs'][3]&1 and call['regs'][4]==224
            expected=mini if destination==41 else previous
            assert all(bytes(m.ram[k][0x1fe0:0x1ff0])==bytes(expected.ram[k][0x1fe0:0x1ff0])for k in [2,3])
            if destination==41:assert bytes(m.ram[3][:5120])==code and bytes(m.ram[2][0x1000:0x1400])==meta
            transitions.append(dict(previous=owner if destination==41 else 41,owner=destination,CPU=call['CPU'],minimum_SP=call['minSP']))
    for bank in [2,3]:
        for index in range(16):
            m=N.fork(mini);m.ram[bank][0x1fe0+index]^=1;before=[bytes(x)for x in m.ram]
            call=I.invoke(m,193,0xb08c,(83,71,109,0x21))
            assert not call['regs'][3]&1 and before==[bytes(x)for x in m.ram]
    faults=[]
    for name,corrupt,locked in [('protection',None,True),('state',(2,0),False),('metadata',(2,0x1000),False)]+[(f'code-row{i}',(3,i*1024),False)for i in range(5)]:
        m=F.blank(base,41);m.corrupt_at=corrupt
        if locked:m.protection=[0,0]
        call=I.invoke(m,193,0xae00,(83,71,109,0x21))
        assert not call['regs'][3]&1 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
        faults.append(name)
    m=N.fork(mini);N.put(m,SelectedCharacter=0);call=I.invoke(m,193,fit['labels']['CoRetire'],(83,71,109,0x21))
    assert call['regs'][:3]==[83,71,109]and call['regs'][3]&0xef==0x21 and call['regs'][4]==224
    assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
    q.update(passed=True,CPU_only=True,ROM_written=False,final_Mini_cold_qualified=True,
        Mini_cold=dict(CPU=out['CPU'],minimum_SP=out['minSP'],code_metadata_exact=True,state_C000_C900_zero=True),
        actual_to_from_current_owners=transitions,Mini_individual_header_poisons=32,copy_verify_faults=faults,foreign_selected_Mini_retire=True,
        unchanged_shared_source='Exactv15 manager/extra/selector/73BSh and35Bmap. Only finalMini code carriers and16Bhashcookie differ from positivev22; cookie ownerbytesA7/41/1 stayunique from currentfour. Copier113B/meta/art remain explicitinputs.',
        reuse_scope='Currentfour complete source/private/AXYP/SP/SMC parity from17 and all25 transitions/160poisons/7guards from22. This parameter run additionally copies/verifies finalMini bytes and actual8to/from transitions, own32poisons,8readback/protectionfaults and foreignretire.',
        remaining='Root currentkernel/native ingress/sharedlifetime review plus root scene/menu/gates/nativeMesen before nightly. This is not sourceStep or nativegraphics qualification.',
        bindings={p.relative_to(R).as_posix():P.M.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(F.__file__),kernel_path,metadata_path,art_path,O/'owner-fit-v15.json',O/'existing-owner-CPU-v17.json',O/'five-cold-CPU-v22.json',R/'docs/qa/allocations/mini-mario-private-resources-1103-v24.json']})
    return base,q


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kernel',type=Path,required=True);ap.add_argument('--sha256',required=True);a=ap.parse_args()
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=4,fresh=True)
    base,q=qualify(a.kernel,a.sha256)
    fit=json.loads((O/'owner-fit-v15.json').read_text());source=(O/'owner-v15.s').read_text()
    before='MiniCookie:\n .byte '+','.join('$%02x'%v for v in bytes.fromhex(fit['Mini_cookie_placeholder']))
    after='MiniCookie:\n .byte '+','.join('$%02x'%v for v in bytes.fromhex(q['Mini_cookie']))
    assert source.count(before)==1
    (O/'owner-final-v24.s').write_text(source.replace(before,after))
    (O/'final-payload-v24.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings','actual_to_from_current_owners']}))


if __name__=='__main__':main()
