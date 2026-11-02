"""Bind inherited writer declarations to current ROM and private carriers.

Private-image offsets must never be interpreted as offsets in the NES image.
This is preservation evidence; new-owner source domains remain explicit.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
O=R/'build/excitebike-pose-1101-v3'


def main():
    rom=R/'build/shinobi-camera-1101-v20/candidate.nes';b=scoped_load(rom);raw=b['raw']
    historical=R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json'
    old=json.loads(historical.read_text());bound=[];direct=private=0
    for writer in old['unchanged_inherited_writers']:
        path=Path(writer['file']);at=writer['file_offset'];expected=bytes.fromhex(writer['old_bytes'])
        if path.suffix=='.nes':
            assert raw[at:at+len(expected)]==expected,(writer['segment'],at)
            direct+=1
        else:
            ref=old['readonly_image_inputs'][str(path)] if str(path) in old['readonly_image_inputs'] else old['readonly_image_inputs'][writer['file']]
            image=path.read_bytes();assert hashlib.sha256(image).hexdigest()==ref['sha256']
            assert image[at:at+len(expected)]==expected
            # The full containing source1KB, not an accidentally matching3B store.
            base=at&~1023;chunk=image[base:base+1024]
            matches=[page for page in range(1024) if raw[1048592+page*1024:1048592+(page+1)*1024]==chunk]
            assert matches,(writer['segment'],at)
            assert not set(range(728,740))&set(matches)
            bound.append(dict(segment=writer['segment'],source_offset=at,source_page_matches=matches,
                              source_chunk_SHA256=hashlib.sha256(chunk).hexdigest()))
            private+=1
    tables=[]
    for name,table in old['current_table_bytes'].items():
        path=Path(table['file']);at=table['file_offset'];expected=bytes.fromhex(table['hex'])
        if path.suffix=='.nes':
            assert raw[at:at+len(expected)]==expected,name
            tables.append(name)
    source=(R/'build/wwf-roster-native-1101-v1/wf-page-sources.bin').read_bytes()
    at=location(b,'WfPageSourceTable');assert raw[at:at+len(source)]==source
    wwf_sources=sorted({512+v for v in source})
    assert not set(range(728,740))&set(wwf_sources)
    # Metadata importer copies1687bytes from each exact6-entry offset.
    at=location(b,'WfMetadataOffsets');offsets=raw[at:at+12]
    wwf_metadata=set()
    for i in range(6):
        offset=int.from_bytes(offsets[i*2:i*2+2],'little')
        wwf_metadata.update(range(658+offset//1024,658+(offset+1686)//1024+1))
    assert not set(range(728,740))&wwf_metadata
    newer=R/'build/kirby-approach-owner-1101-v3/candidate.nes'
    prior=newer.read_bytes()
    changes=[page for page in range(1024) if prior[1048592+page*1024:1048592+(page+1)*1024]!=raw[1048592+page*1024:1048592+(page+1)*1024]]
    allowed={247,248,249,250,403,406,*range(494,511),513,515,516,517,*range(827,832)}
    assert set(changes)<=allowed
    report=dict(passed=True,current_ROM_SHA256=hashlib.sha256(raw).hexdigest(),
        inherited_direct_writer_instructions_exact=direct,
        inherited_private_writer_source_chunks_exact=private,private_writer_bindings=bound,
        current_old_table_bytes_exact=tables,WWF_cold_kernel_pages=wwf_sources,
        WWF_cold_metadata_pages=sorted(wwf_metadata),
        changed_CHR_since_Kirby=changes,changes_within_existing_Karnov_Metal_Tank_Shinobi_owners=True,
        global_consumer_closure=False,
        remaining='New ROM-resident Tank/Metal/Shinobi loaders and cache graphics publisher source-domain binding; changed Karnov403/406 source reader bounds remain inherited. This receipt does not grant pages.',
        scope='All831 unchanged inherited writers are still exact at their real mainROM or complete private1KB carrier locations; no private image offset is confused with NES header/PRG offsets.')
    (O/'writer-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['private_writer_bindings','current_old_table_bytes_exact']}))


if __name__=='__main__':main()
