"""Qualify the linked loader, including its legitimate frontend target rebind."""
from pathlib import Path
import hashlib,json,re,sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

P=R/'build/smb2j-campaign-menu-source-1031-v7'
S=R/'build/smb2j-cache-loader-source-1031-v2'
O=R/'build/smb2j-cache-loader-qualified-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir()
    for recipe in ['main-build.json','carrier-build.json','final-link.json']:
        assert json.loads((S/recipe).read_text())['returncode']==0
    old,new=[scoped_load(p/'joint/candidate.nes')for p in [P,S]]
    a,z=old['raw'],new['raw']
    assert len(a)==len(z)and a[:10]==z[:10]and a[10]==9 and z[10]==10 and a[11:16]==z[11:16]
    first=location(old,'ProtoArtEnd');assert address(old,'ProtoArtEnd')==0xc738
    assert a[first:16+65*8192+0x1108]==bytes([255])*2512
    assert address(new,'J2CacheResidentStart')==0xc738 and address(new,'J2CacheResidentEnd')<=0xd108
    hook=location(old,'CrossoverMenuInput::FmStartReady')
    expect=bytearray(a[hook:hook+18]);target=address(new,'J2OpenCampaign')
    expect[4]=target&255;expect[9]=target>>8
    assert z[hook:hook+18]==expect,'Exact genuine frontend farcall target rebind'
    regions=[(10,11),(first,location(new,'J2CacheResidentEnd')),
             (location(new,'J2MenuStart'),location(new,'J2MenuEnd')),(hook,hook+18)]
    ranges=[(442,460),(563,571)]
    for x,y in ranges:
        lo,hi=1048592+x*1024,1048592+y*1024
        assert a[lo:hi]==bytes(hi-lo)
        regions.append((lo,hi))
    diff=[i for i,(b,c)in enumerate(zip(a,z))if b!=c]
    assert all(any(lo<=i<hi for lo,hi in regions)for i in diff)
    stable=0
    for n,sym in old['syms'].items():
        if n.split('::')[-1].startswith(('J2','LOCAL-MACRO_SYMBOL-'))or sym.get('type')!='lab'or'seg'not in sym or n not in new['syms']:continue
        assert address(old,n)==address(new,n),n
        if'ooffs'in old['segs'][sym['seg']]:assert location(old,n)==location(new,n),n
        stable+=1
    bound={}
    for receipt in [P/'source-stage.json',R/'build/smb2j-campaign-data-1031-v2/data-stage.json']:
        q=json.loads(receipt.read_text());assert q['passed']
        for name,h in q['bindings'].items():assert sha(name)==h,name;bound[name]=h
    dep=(S/'joint/main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    refs=[Path(p.replace('\\ ',' '))for p in re.split(r'(?<!\\)\s+',dep)if p]
    cmd=json.loads((S/'final-link.json').read_text())['command']
    refs += [Path(p)for p in cmd if p.endswith('.o')]
    refs += [p for p in S.rglob('*')if p.is_file()]
    refs += [Path(__file__),R/'tools/audit/prepare_smb2j_cache_loader_1031_v2.py',R/'tools/reference/smb2j_cache_loader_1031_v2.inc',R/'tools/reference/smb2j_campaign_menu_1031_v6.inc']
    bound.update({str(p.resolve()):sha(p)for p in refs})
    q=dict(passed=True,source_CPU=False,source=True,native=False,installed=False,
           source_component_only=True,SMB2J_campaign_still_declined=True,
           candidate=sha(S/'joint/candidate.nes'),parent=sha(P/'joint/candidate.nes'),
           matched_old_nonJ2_label_PCs=stable,changed_ROM_bytes=len(diff),exact_allowed_regions=regions,
           actual_resident_bytes=address(new,'J2CacheResidentEnd')-0xc738,
           private_resources=dict(data_CHR_pages=[442,460],art_CHR_pages=[563,571],
                                  resident_physical_bank=65,C_view=[0xc738,0xd108],
                                  volatile_WRAM_KiB=64,exclusive_cache_physical_bank=4,new_global_or_ZP_bytes=0),
           production_note='v2 emitted source/link successfully. Its final diff assertion omitted the existing18B frontend farcall whose private J2OpenCampaign target moved by7B. This qualification proves that exact emitted target relocation and every foreign byte/PC, without rebuilding or patching the linked bytes.',
           limits=['Uninstalled data-loader component. No2J gameplay or persistence.',
                   'Private header expansion and physical RAM4 still require source CPU/vector and actual cold mapper validation.'],bindings=bound)
    (O/'source-stage.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','exact_allowed_regions']}))


if __name__=='__main__':main()
