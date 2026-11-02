"""Compose the private source cache, retaining pending menu admission."""
from pathlib import Path
import hashlib,json,os,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
O=R/'build/excitebike-pose-1101-v3'
BASE=R/'build/shinobi-camera-1101-v20/candidate.nes'


def main():
    raw=bytearray(BASE.read_bytes());basehash=hashlib.sha256(raw).hexdigest()
    names=['publication-CPU-controls.json','upper2-finite-domains.json','smb3-pages.json',
           'writer-preservation.json','new-owner-pages.json','owner-assembly.json']
    receipts={name:json.loads((O/name).read_text()) for name in names}
    for name,q in receipts.items():
        assert q['passed'],name
        digest=next((q[k] for k in ('current_ROM_sha256','ROM_sha256','ROM_SHA256','current_ROM_SHA256','baseline_SHA256') if k in q),None)
        assert digest==basehash,(name,digest)
    targets=set(range(728,740))
    domains=dict(receipts['upper2-finite-domains.json']['domains'])
    # The old label-based SMB3 record walks retired tables. Replace it with
    # actual execution of the live factored selector on this exact ROM.
    del domains['SMB3 seven forms81frames']
    domains['SMB3 actual current selector']=receipts['smb3-pages.json']['pages']
    historical=json.loads((R/'build/metal-storm-chr-closure-1101-v10/source-domains.json').read_text())
    for name,domain in historical['exact_source_domains'].items():
        if name!='WWF every input byte':domains[name]=domain['physical_pages']
    w=receipts['writer-preservation.json'];n=receipts['new-owner-pages.json']
    domains['WWF source code']=w['WWF_cold_kernel_pages']
    domains['WWF metadata']=w['WWF_cold_metadata_pages']
    domains.update(n['actual_cold_map_rows'])
    domains['Shinobi body']=n['Shinobi_body_table'];domains['Metal body']=n['Metal_body_table']
    domains['Tank source/body art']=[501,502]
    assert all(not targets&set(pages) for pages in domains.values())
    assert w['inherited_direct_writer_instructions_exact']+w['inherited_private_writer_source_chunks_exact']==831
    closure=dict(passed=True,source_valid_consumer_domains_disjoint=True,baseline_ROM_SHA256=basehash,
        reclaimed_pages=list(range(728,739)),unused_page=739,domains=domains,
        inherited_source_scope='Existing classified direct/indirect/array writer ABI and Karnov owner proof retained; current831 writer bytes/chunks and linked tables checked. Original native-low/upper1/upper3 publishers cannot select upper2 pages728..739. All upper2 typed body, cold loader and current transient publication domains are refined here.',
        substitutions=['WWF full-byte superset replaced by actual195 metadata records and all clamped selectors.',
                       'Retired SMB3 table labels replaced by1134 actual current selector executions.'],
        limits=['Source-valid owner/index/scene contracts only; arbitrary corrupt RAM not covered.',
                'Recheck after any new loader, CHR publisher, source table or menu ownership change.',
                'This resource closure does not qualify Excitebike gameplay, menu unlock or native execution.'],
        bindings={str((O/name).relative_to(R)):hashlib.sha256((O/name).read_bytes()).hexdigest() for name in names})
    (O/'consumer-closure.json').write_text(json.dumps(closure,indent=2)+'\n')
    start=16+65*8192+0xe00;loader=(O/'owner-loader.bin').read_bytes()
    assert raw[start:start+776]==bytes([255])*776
    raw[start:start+len(loader)]=loader
    payload=(O/'owner-actor.bin').read_bytes()+(O/'owner-metadata.bin').read_bytes()+(O/'body-native.chr').read_bytes()
    for i,page in enumerate(range(728,739)):
        at=1048592+page*1024;assert raw[at:at+1024]==bytes(1024)
        raw[at:at+1024]=payload[i*1024:(i+1)*1024]
    labels={m[2]:int(m[1],16) for m in re.finditer(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'owner-loader.lbl').read_text(),re.M)}
    # Both real Shinobi foreign-scene/menu retirement calls run Excitebike's
    # authenticated retirement first; all original Shinobi logic still runs.
    lo,hi=16+65*8192+0x800,16+65*8192+0xe00
    old=bytes.fromhex('2049a8');positions=[];cursor=lo
    while (cursor:=raw.find(old,cursor,hi))>=0:
        positions.append(cursor);cursor+=3
    assert positions==[16+65*8192+0xc2c,16+65*8192+0xda6],positions
    target=labels['ExRetireBoth']
    for at in positions:raw[at:at+3]=bytes([0x20,target&255,target>>8])
    candidate=O/'candidate.nes';candidate.write_bytes(raw)
    for suffix in ['.dbg','.lbl']:
        dest=candidate.with_suffix(suffix)
        if not dest.exists():os.link(BASE.with_suffix(suffix),dest)
    b=scoped_load(candidate);seed=M.fresh(b)
    # A native menu transition retires either cache, while foreign cache
    # bytes survive the new authentication check unchanged.
    cookies=[(O/'excitebike-cookie.bin').read_bytes(),
             raw[16+65*8192+0xa78:16+65*8192+0xa78+16]]
    for cookie in cookies:
        m=M.fork(seed)
        for bank in [2,3]:m.ram[bank][8160:8176]=cookie
        M.put(m,CrossoverMenuIndex=0,FmAlts=0)
        M.invoke(m,'MenuResolveCharacter')
        assert m.ram[2][8160]==m.ram[3][8160]==0
    m=M.fork(seed)
    for bank in [2,3]:m.ram[bank][8160:8176]=bytes([0x6d])*16
    M.put(m,CrossoverMenuIndex=0,FmAlts=0);M.invoke(m,'MenuResolveCharacter')
    assert all(bytes(m.ram[bank][8160:8176])==bytes([0x6d])*16 for bank in [2,3])
    result=dict(passed=True,ROM_SHA256=hashlib.sha256(raw).hexdigest(),base_ROM_SHA256=basehash,
        resident_bytes=len(loader),menu_unlock=False,native_verified=False,installed=False,
        both_owner_menu_retirement_passed=True,foreign_headers_unchanged=True,
        retirement_hook_offsets=positions,
        limitation='Private storage/retirement successor only. No Excitebike movement/render/gameplay ingress. Base is private Shinobi v20 and does not yet include Metal v41 optimization.')
    (O/'composition.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
