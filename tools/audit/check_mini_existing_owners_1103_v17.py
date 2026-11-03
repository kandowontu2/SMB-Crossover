"""Actual existing-owner constructors and header/retirement on fifth-owner fit."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_mini_private_owner_1103_v15 as M
import check_prince_body_cold_1103_v181 as C
import build_storage_guard_v1 as G
O=M.O;N,I=C.N,C.I


def image():
    fit=json.loads((O/'owner-fit-v15.json').read_text())
    for name,digest in fit['bindings'].items():assert M.sha((R/name).read_bytes())==digest,name
    base,_=C.M.image();raw=bytearray(M.BASE.read_bytes());assert M.sha(raw)==M.PIN
    patches=[]
    def put(bank,pc,new,role,old_prefix=None):
        at=16+bank*8192+pc-0xa000;old=bytes(raw[at:at+len(new)])
        if old_prefix is not None:assert old.startswith(old_prefix),(bank,hex(pc))
        patches.append(dict(physical_PRG=bank,CPU=pc,file_offset=at,bytes=len(new),old_hex=old.hex(),new_hex=new.hex(),role=role))
        raw[at:at+len(new)]=new
    for stem,oldname,pc in [('owner-v15','combined-auth-v83',0xae00),('owner-v15-extra','combined-auth-v83-extra',0xab72),('owner-v15-Sh','combined-auth-v83-Sh',0xa800),('selector-v15','combined-auth-v83-selector',0xa740)]:
        new=(O/(stem+'.bin')).read_bytes();old=(M.P/(oldname+'.bin')).read_bytes()
        put(65,pc,new,stem,old)
    old=(R/'build/bubble-bobble-source-1101-v1/common-split-map.bin').read_bytes()
    put(123,0xb9d6,(O/'common-v15-map.bin').read_bytes(),'Cold-only map+six-byte Mini descriptor',old)
    for row in fit['retired_entry_rebind']:
        put(65,row['CPU'],bytes.fromhex(row['new_hex']),'Source-derived native retired-entry import',bytes.fromhex(row['old_hex']))
    return dict(base,raw=bytes(raw)),fit,patches


def main():
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=3,fresh=True)
    base,fit,patches=image();parent=dict(base,raw=M.BASE.read_bytes());seeds={};rows=[]
    for owner in [37,38,39,40]:
        print('Actual existing fullcold on fiveowner proposal',owner,flush=True)
        new,out=C.C.cold(base,owner);old,ref=C.C.cold(parent,owner)
        assert out['regs']==ref['regs'],(owner,out['regs'],ref['regs'])
        assert all(bytes(a)==bytes(b)for a,b in zip(new.ram,old.ram)),('Complete privateRAM',owner)
        assert new.rawtags==old.rawtags and new.chr_latches==old.chr_latches
        assert bytes(new[3:11])==bytes(old[3:11]) and bytes(new[0x15a:0x17b])==bytes(old[0x15a:0x17b])
        seeds[owner]=new;rows.append(dict(owner=owner,CPU=out['CPU'],minimum_SP=out['minSP'],full_AXYP_SP_RAM_SMC_map_parity=True))
    transitions=[]
    for previous in [37,38,39,40]:
        for owner in [37,38,39,40]:
            print('Actual fiveowner existing transition',previous,owner,flush=True)
            m=N.fork(seeds[previous]);C.C.fields(m,owner);out=I.invoke(m,193,0xae00,(83,71,109,0x21))
            assert out['regs'][3]&1
            assert all(bytes(m.ram[k][0x1fe0:0x1ff0])==bytes(seeds[owner].ram[k][0x1fe0:0x1ff0])for k in [2,3])
            transitions.append(dict(previous=previous,owner=owner,CPU=out['CPU'],minimum_SP=out['minSP']))
        m=N.fork(seeds[previous]);N.put(m,SelectedCharacter=0)
        out=I.invoke(m,193,fit['labels']['CoRetire'],(83,71,109,0x21))
        assert out['regs'][:3]==[83,71,109]and out['regs'][3]&1 and out['regs'][4]==224
        assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
    rejects=0
    for owner in [37,38,39,40]:
        for bank in [2,3]:
            for index in range(16):
                m=N.fork(seeds[owner]);m.ram[bank][0x1fe0+index]^=1;before=[bytes(x)for x in m.ram]
                out=I.invoke(m,193,0xb08c,(83,71,109,0x21))
                assert not out['regs'][3]&1 and before==[bytes(x)for x in m.ram]
                rejects+=1
    result=dict(passed=True,CPU_only=True,ROM_written=False,final_Mini_payload_qualified=False,
        parent_SHA256=M.PIN,memory_proposal_SHA256=M.sha(base['raw']),cold=rows,transitions=transitions,
        foreign_selected_retirements=4,individual_header_poisons=rejects,
        existing_all_four_complete_private_RAM_AXYP_SP_scratch_SMC_maps_exact=True,
        source_stage='Measured proposal with source-fit Mini cookie only; current37..40 actual payloads used unchanged, not injected.',
        remaining=['Actual complete Mini fifth cold/failure/readback before finalcookie.','Source-bound lost-A/upper-latch continuation and all foreign/public/current-owner IRQ/genuineFF/nested.','Exact41 scene/menu gate proposal remains root-owned.'],
        patches=patches,bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),Path(M.__file__),Path(C.__file__),O/'owner-fit-v15.json',O/'owner-v15.s',O/'owner-v15.bin',O/'owner-v15-extra.bin',O/'owner-v15-Sh.bin',O/'selector-v15.s',O/'selector-v15.bin',O/'common-v15.s',O/'common-v15-map.bin',R/'docs/qa/allocations/mini-mario-private-resources-1103-v24.json']})
    (O/'existing-owner-CPU-v17.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ['patches','bindings','transitions']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'existing-owner-negative-v17.json').write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n');raise
