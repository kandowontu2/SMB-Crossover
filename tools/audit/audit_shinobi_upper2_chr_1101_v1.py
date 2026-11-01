"""Read actual current finite art tables, including all six WWF metadata sets."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
O=R/'build/shinobi-chr-closure-1101-v1'
ROM=R/'build/kirby-approach-owner-1101-v3/candidate.nes'
TARGETS=set(range(503,511))|{513,515,516,517}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    b=scoped_load(ROM);raw=b['raw'];sources=[Path(__file__),ROM];domains={};tables={}
    wf=R/'build/wwf-roster-native-1101-v1/runtime.s'
    sources.append(wf)
    source=wf.read_text()
    for clause in [
        'lda WfState+$32\n cmp WfHoganMetadata\n bcc GroupValid\n lda #0',
        'lda WfState+$34\n cmp R3\n bcc FrameValid\n lda #0',
        'FrameValid:\n clc\n adc WfPoseIndex',
        'lda WfHoganMetadata+1,y\n pha\n and #7',
        'ldy #0\n lda (R0),y\n sta WfPosePage',
    ]:
        assert clause in source,clause
    historical=json.loads((R/'build/metal-storm-chr-closure-1101-v10/source-domains.json').read_text())
    source_key=next(k for k in historical['source_bindings'] if k.replace('\\','/').endswith('/wwf-roster-native-1101-v1/runtime.s'))
    assert sha(wf)==historical['source_bindings'][source_key]['sha256']
    prior=R/'build/kirby-owner-main-1101-v2/candidate.nes'
    sources.append(prior)
    offset=location(b,'WfBuildPose');bank=(offset-16)//8192;bankstart=16+8192*bank
    assert raw[bankstart:bankstart+8192]==prior.read_bytes()[bankstart:bankstart+8192]
    def table(name,n):
        p=location(b,name);v=raw[p:p+n];assert len(v)==n
        tables[name]=dict(offset=p,bytes=n,sha256=hashlib.sha256(v).hexdigest())
        return v
    for name,file,base in [('TnBodyChr','tmnt_art.inc',512),('IcPosePage','ice_climbers_art.inc',712),('MacRosterChrLow','mac_roster_data.inc',512),('SunnyChrLow','sunny_art.inc',512)]:
        p=R/'src'/file;sources.append(p)
        text=p.read_text().split(name+':',1)[1];values=[]
        for line in text.splitlines():
            line=line.strip()
            if not line:continue
            if not line.startswith('.byte '):break
            values.extend(int(x) for x in line[6:].split(','))
        assert values and table(name,len(values))==bytes(values),name
        domains[name]=sorted({base+x for x in values})
    domains['Mike body and weapons']=list(range(708,712))
    domains['CV3 nonzero alternates weapons']=list(range(518,524))
    domains['Mac world']= [704]
    domains['FinalFantasy body and preview']=list(range(756,788))
    recovered={}
    def require(relative,clauses):
        p=R/relative
        if p.exists():sources.append(p);text=p.read_text()
        else:
            key=next(k for k in historical['source_bindings'] if k.replace('\\','/').endswith('/'+relative))
            digest=historical['source_bindings'][key]['sha256']
            with zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip') as z:data=z.read('objects/'+digest)
            assert hashlib.sha256(data).hexdigest()==digest
            recovered[key]=digest;text=data.decode()
        for clause in clauses:assert clause in text,(relative,clause)
    require('src/mike_jones_state.inc',['JN_FIRST_CHR=708'])
    require('src/mike_jones_core.s',['lda #<JN_FIRST_CHR\n sta SmChrBank'])
    require('src/mike_jones_render.s',['lda #<(JN_FIRST_CHR+2)','lda #<(JN_FIRST_CHR+3)'])
    require('src/final_fantasy_state.inc',['FF_FIRST_CHR=756'])
    require('src/final_fantasy_render.s',['and #31\n sta FfRenderPage'])
    require('build/current-character-composition-v1/joint/preview.s',['and #31\n sta FfRenderPage'])
    require('build/bt-ready-menu-1031-v2/joint/src/cv3_core.s',[
        'lda Cv3Variant\n  jeq No\n  cmp #4\n  jcs No'])
    require('build/bt-ready-menu-1031-v2/joint/src/cv3_draw.s',[
        'farcall Cv3IsActive\n bcs Native\n farcall RosterDrawShots,jmp\nNative:jmp Cv3DrawShots',
        'adc #<516','adc #<517'])
    m3=set()
    for i in range(7):
        low=table(f'M3Form{i}ChrLo',81);high=table(f'M3Form{i}ChrHi',81)
        m3.update(lo+256*hi for lo,hi in zip(low,high))
    domains['SMB3 seven forms81frames']=sorted(m3)
    offsets=table('WfMetadataOffsets',12);pages=set();records=0;selector_cases=0
    chrstart=16+1048576
    for variant in range(6):
        off=int.from_bytes(offsets[2*variant:2*variant+2],'little')
        data=raw[chrstart+658*1024+off:chrstart+658*1024+off+1687]
        groups,frames=data[:2];assert 0<groups<64 and 0<frames<128
        pointers=2+groups*2
        # Mirror the assembly's two clamps and byte-sized pointer arithmetic.
        # Enumerate all state bytes, including invalid groups and frames.
        for requested_group in range(256):
            group=requested_group if requested_group<groups else 0
            start=data[2+2*group]
            end=data[4+2*group] if group+1<groups else frames
            assert 0<=start<end<=frames
            for requested_frame in range(256):
                frame=requested_frame if requested_frame<end-start else 0
                index=start+frame
                assert index<frames and pointers+2*index+1<256
                selector_cases+=1
        for frame in range(frames):
            low,high=data[pointers+2*frame:pointers+2*frame+2]
            ptr=low+256*(high&7);cells=high>>3
            assert 0<cells<=31 and ptr+1+3*cells<=len(data)
            pages.add(data[ptr]);records+=1
    assert max(pages)<140,sorted(pages)
    def mapped(a):
        return 546+a if a<58 else 442+a-58 if a<76 else 629+a-76
    domains['WWF actual metadata']=sorted({mapped(a) for a in pages})
    domains['WWF cold portraits']=[mapped(a) for a in table('WfIdlePages',6)]
    collision={k:sorted(set(v)&TARGETS)for k,v in domains.items()if set(v)&TARGETS}
    assert not collision,collision
    result=dict(passed=True,ROM_sha256=sha(ROM),proposed_pages=sorted(TARGETS),
        resource_granted=False,complete_consumer_closure=False,domains=domains,tables=tables,
        WWF_metadata_records=records,WWF_selector_cases=selector_cases,
        WWF_source_clamps_bound=True,WWF_code_bank_unchanged=bank,
        WWF_legal_page_indices=sorted(pages),
        limits=['Finite table/domain extension only; typed selector, writer preservation and publication proof must also hold.','IRQ may publish512; it is deliberately excluded.','251 was rejected by a real native-menu publication test and is not proposed.'],
        recovered_source_objects=recovered,bindings={str(p):sha(p)for p in sources})
    (O/'upper2-finite-domains.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,WWF_records=records,WWF_pages=sorted(pages),domains=len(domains))))

if __name__=='__main__':main()
