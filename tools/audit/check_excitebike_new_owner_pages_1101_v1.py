"""Current Tank/Metal/Shinobi cold carrier domains, plus bound body tables."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
import check_hogan_current_bounded_v1 as M
O=R/'build/excitebike-pose-1101-v3'


def labels(path):
    return {m[2]:int(m[1],16) for m in re.finditer(r'^al ([0-9A-Fa-f]+) \.(\S+)$',path.read_text(),re.M)}


def main():
    rom=R/'build/shinobi-camera-1101-v20/candidate.nes';b=scoped_load(rom)
    sh=labels(R/'build/shinobi-menu-1101-v13/resident.lbl')
    ms=labels(R/'build/metal-storm-shots-1101-v35/component.lbl')
    mt=labels(R/'build/mario-tank-visible-host-1101-v5/graft.lbl')
    mappings=[('ShMapRow',sh['ShMapRow'],65,9,3),('Ms8Map',ms['Ms8Map'],34,12,11),('MtMapCodeV4',mt['MtMapCodeV4'],82,1,11)]
    for name,pc,bank,rows,window in mappings:
        seg='audit_'+name;b['segs'][seg]={'start':str(pc),'ooffs':str(16+bank*8192+pc-0xa000)}
        b['syms'][name]={'val':str(pc),'seg':seg}
    seen={};seed=M.fresh(b)
    for name,pc,bank,rows,window in mappings:
        pages=[]
        for row in range(rows):
            m=M.fork(seed);M.put(m,R2=row)
            M.invoke(m,name)
            page=m.chr_latches[window]
            assert page not in range(728,740),(name,row,page)
            pages.append(page)
        seen[name]=pages
    assert seen['ShMapRow']==[506,507,508,509,510,513,515,516,517]
    assert seen['MtMapCodeV4']==[501]
    raw=b['raw']
    at=lambda bank,pc:16+bank*8192+(pc&8191)
    shlow=raw[at(65,sh['ShChrLow']):at(65,sh['ShChrLow'])+4]
    shupper=raw[at(65,sh['ShChrUpper']):at(65,sh['ShChrUpper'])+4]
    shbody=[lo+256*(hi&3) for lo,hi in zip(shlow,shupper)]
    assert shbody==[503,504,505,517]
    renderer=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024] for p in [831,500,494])
    lo=renderer[ms['MsBodyPhysicalLo']-0xcd00:ms['MsBodyPhysicalLo']-0xcd00+5]
    hi=renderer[ms['MsBodyPhysicalHi']-0xcd00:ms['MsBodyPhysicalHi']-0xcd00+5]
    msbody=[a+256*z for a,z in zip(lo,hi)];assert msbody==[495,496,497,498,499]
    report=dict(passed=True,ROM_SHA256=hashlib.sha256(raw).hexdigest(),
        actual_cold_map_rows=seen,Shinobi_body_table=shbody,Metal_body_table=msbody,
        Tank_own_carrier=501,Tank_own_art=502,Metal_shots=499,
        source_valid_domains_exclude_proposed_pages=True,
        scope='Actual real-ROM cold mapper leaves for22rows and actual emitted Shinobi/Metal body tables. Tank own art502 follows existing source grant; native Mario body remains native low-page domain. Not a complete gameplay or new-character admission test.')
    (O/'new-owner-pages.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
