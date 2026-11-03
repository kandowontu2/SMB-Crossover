"""Differential actual renderer continuation and native descriptor consumers."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_prince_body_owner_1103_v178 as B
V=B.V;N,I=V.N,V.I;O=B.O


def patch(m):
    q=json.loads((O/'measurement.json').read_text())
    for row in q['patches']:
        bank,start=(3,0xa000)if row['region']=='runtime'else(2,0xc000)
        at=row['CPU']-start;old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
        assert bytes(m.ram[bank][at:at+len(old)])==old
        m.ram[bank][at:at+len(new)]=new
    return q


def main():
    e,seed,lab=V.first8();e['run'](seed,'GameLoop',lab)
    q=json.loads((O/'measurement.json').read_text());allow={2:set(),3:set()}
    for row in q['patches']:
        bank,start=(3,0xa000)if row['region']=='runtime'else(2,0xc000)
        allow[bank].update(range(row['CPU']-start,row['CPU']-start+len(bytes.fromhex(row['new_hex']))))
    art=json.loads((V.O/'source-art.json').read_text())
    original=(V.O/'prince-body-8x16.chr').read_bytes()
    old_lo=bytes(seed.ram[3][0xbda4-0xa000:0xbdc3-0xa000]);old_hi=bytes(seed.ram[3][0xbdc3-0xa000:0xbde2-0xa000])
    records=parts=patternbytes=0;pages=set();minimum=255;rows=[]
    for pose in art['poses']:
        old=N.fork(seed);new=N.fork(seed);patch(new)
        for m in [old,new]:
            # Standalone private leaf requires the same C2 mapping supplied
            # by PrSharedCall. WholeMain legitimately returned native C201.
            m.raw_page(2,2);N.put(m,CurrentBankC=2)
            m.ram[2][0x617]=pose['source_frame'];m.ram[2][0x615]=pose['source_facing']
            N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=1,RgOamRotation=0)
        first=I.invoke(old,3,lab['PpHostDraw'],(83,71,109,0x61))
        second=I.invoke(new,3,lab['PpHostDraw'],(83,71,109,0x61))
        assert first['regs']==second['regs'],(pose['source_frame'],'AXYP',first,second)
        assert bytes(old[3:11])==bytes(new[3:11])
        assert bytes(old[0x15a:0x17b])==bytes(new[0x15a:0x17b])
        assert bytes(old[0x200:0x300])==bytes(new[0x200:0x300])
        assert old.rawtags==new.rawtags
        for bank in [2,3]:
            diff=[i for i,(a,b)in enumerate(zip(old.ram[bank],new.ram[bank]))if a!=b and i not in allow[bank]]
            assert not diff,(pose['source_frame'],pose['source_facing'],bank,diff[:8])
        minimum=min(minimum,second.get('minimum_SP',255));records+=1
        # Test actual final publication, not merely cached CHR selectors.
        at=len(new.writes);N.invoke(new,'BankSwitchCHR',a=83,x=71,y=109,p=0x61)
        upper=0;banks={}
        for address,value in new.writes[at:]:
            if address==0x5130:upper=value&3
            elif 0x5120<=address<0x512c:banks[address-0x5120]=value+256*upper
        expected=sorted({p['pattern_pair']//32 for p in pose['parts_8x16']})
        for window,page in enumerate(expected):
            physical=old_lo[page]+256*old_hi[page];assert banks[window]==physical;pages.add(physical)
        for index,part in enumerate(pose['parts_8x16']):
            sprite=bytes(new[0x200+index*4:0x204+index*4]);tile=sprite[1]
            logical=(tile&1)*4096+(tile&254)*16;actual=bytearray()
            for byte in range(32):
                pp=logical+byte;physical=banks[pp//1024]
                off=1048592+physical*1024+pp%1024;actual.append(new.bundle['raw'][off])
            want=original[part['pattern_pair']*32:part['pattern_pair']*32+32]
            assert actual==want,(pose['source_frame'],pose['source_facing'],index,physical)
            parts+=1;patternbytes+=32
    assert records==408 and parts==2578
    # Real wholeMain stale native descriptor observed in177; no source result
    # or desired CHR bank is set. The same actual constructor/body path runs.
    old=N.fork(seed);new=N.fork(seed);patch(new)
    for m in [old,new]:N.put(m,ObjectMetasprite=0x91)
    e['run'](old,'GameLoop',lab);out=e['run'](new,'GameLoop',lab)
    assert N.get(old,'ObjectMetasprite')==0x91 and N.get(new,'ObjectMetasprite')==0
    assert N.get(new,'SmPosePtr')+256*N.get(new,'SmPosePtr',1)==I.address(new.bundle,'ObjectMetasprite')
    assert N.get(old,'PlayerChrBank')==64 and N.get(new,'PlayerChrBank')==85
    assert new.ram[2][0x6cf]==old.ram[2][0x6cf]==5 and N.get(new,'NumberofLives')==2
    N.invoke(new,'BankSwitchCHR',a=83,x=71,y=109,p=0x61)
    result=dict(passed=True,CPU_only=True,code_injected_fixture=True,source_backed_new_cold_pending=True,ROM_written=False,
                original_source_facing_poses=records,original_parts=parts,exact_original_published_pattern_bytes=patternbytes,
                published_physical_pages=sorted(pages),all_renderer_AXYP_R0_R7_SMC_maps_mutable_state_exact=True,
                upper_CV_scope='Changed helper C/V are not compared at arbitrary helper exit. Every complete original renderer continuation for all408legal poses returns exact AXYP and all mutable state, source OAM and published CHR versus159. Next flag dependency after page loop is explicit CLC in projection/geometry; final PLP restores original V and leafSEC/CLC establishes returnC.',
                actual_whole_Main=dict(stale_native_descriptor=0x91,old_final_low=64,new_final_low=85,stable_zero_header=True,HP=5,lives=2,minimum_SP=out['minSP']),
                required='Actual source-backed new codec/cookies/fullcold and current-owner/foreign/IRQ/FF/nested; actual hardware native fullbody probe. No actual graphics pass or private ROM emission claimed.',
                bindings={str(p.relative_to(R)):B.sha(p)for p in [Path(__file__),Path(B.__file__),O/'measurement.json',O/'body-owner.s',O/'body-owner.bin',O/'body-runtime.bin',O/'body-metadata.bin',V.O/'backdrop-manifest-v159.json',V.O/'source-art.json',V.O/'prince-body-8x16.chr']})
    (O/'renderer-CPU-v179.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        if not (O/'renderer-negative-v179.json').exists():
            (O/'renderer-negative-v179.json').write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n')
        raise
