"""Compare the exact local All Night Nippon campaign with original1/2J data."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
from audit_smb2j_campaign_source_1031_v1 import disk_files

O=R/'build/smbann-campaign-audit-1031-v1'
S=R/'build/smbann-original-source-1031-v1'
DONOR=Path('C:/NES/fds/All Night Nippon Super Mario Bros. (Japan) (Promo).fds')
SMB1=Path('C:/NES/Super Mario Bros. (World).nes')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda b:hashlib.sha256(b).hexdigest()


def labels(path):
    scopes,syms={},[]
    for line in path.read_text().splitlines():
        if '\t'not in line:continue
        kind,body=line.split('\t',1)
        f={k:v.strip('"')for k,v in re.findall(r'(\w+)=("[^"]*"|[^,]+)',body)}
        if kind=='scope':scopes[f['id']]=f.get('name','')
        if kind=='sym'and f.get('type')=='lab'and'val'in f:syms.append(f)
    out={}
    for f in syms:
        scope=scopes.get(f.get('scope'),'')
        if scope.startswith('FILE_SM2'):out.setdefault(scope[5:],{})[f['name']]=int(f['val'],0)
    return out


def stream(image,start,enemy=False):
    at=start+(0 if enemy else 2)
    records=[]
    while image[at]!=(255 if enemy else 253):
        n=3 if enemy and image[at]&15==14 else 2
        records.append(tuple(image[at:at+n]));at+=n
        assert at-start<2048
    raw=bytes(image[start:at+1])
    return dict(address=start,bytes=len(raw),sha256=digest(raw),header=list(raw[:2])if not enemy else [],records=records)


def semantic(records,game):
    # Decode the original object protocol. This deliberately preserves raw
    # positions/page bits/lengths. Names provide a comparable object identity;
    # closest-match scores are similarities, never a byte-equality assertion.
    common=['pipe','style','brick-row','solid-row','coin-row','brick-column','solid-column','pipe',
            'hole','rope-pulley','bridge-high','bridge-mid','bridge-low','water-hole','question-row-high','question-row-low',
            'rope-endless','rope-balance','castle','stairs','exit-pipe','flag-balls']
    if game!='SMB1':common+=['pipe-inverted-high','pipe-inverted-low']
    small={
        'SMB1':['q-power','q-coin','hidden-coin','hidden-1up','brick-power','brick-vine','brick-star','brick-coins','brick-1up','water-pipe','empty-block','spring'],
        'ANN':['q-power','q-coin','hidden-coin','hidden-1up','hidden-power','brick-power','brick-vine','brick-star','brick-coins','brick-1up','water-pipe','empty-block','spring'],
        'SMB2J':['q-power','q-coin','hidden-coin','q-poison','hidden-1up','hidden-power','hidden-poison','brick-power','brick-vine','brick-star','brick-poison','brick-coins','brick-1up','water-pipe','empty-block','spring'],
    }[game]
    row13=['intro-pipe','flagpole','axe','chain','castle-bridge','warp-lock','scroll-lock','scroll-lock','frenzy-cheep','frenzy-bill','frenzy-stop','maze-loop']
    if game=='SMB2J':row13+=['wind-on','wind-off']
    result=[]
    for a,b in records:
        row=a&15
        if row==13 and not b&64:result.append(('page',b&31));continue
        if row==14:result.append(('attributes',a>>4,b&127));continue
        if row==13:
            number=b&63
            name=row13[number]if number<len(row13)else'unknown-control-'+str(number)
            result.append((name,a>>4,b&128));continue
        if row in [12,15]:
            number=(8 if row==12 else 16)+((b>>4)&7)
            name=common[number]if number<len(common)else'unknown-large-'+str(number)
            result.append((name,a>>4,b&15,b&128));continue
        if b&112:
            number=(b>>4)&7
            if number==7 and b&8:number=0
            result.append((common[number],a,b&15,b&128))
        else:
            number=b&15
            result.append((small[number]if number<len(small)else'unknown-small-'+str(number),a,b&128))
    return result


def main():
    assert not O.exists()
    O.mkdir()
    assert sha(DONOR)==sha(S/'original/original.fds')=='a762d0a90d16c84b5f2b014816b37675cf5115320be7e815effbb64d91b2014d'
    files=disk_files(DONOR.read_bytes());sym=labels(S/'original/original.dbg')
    originals=[]
    # Locate both complete original SMB1 tables by their actual cartridge bytes.
    raw=SMB1.read_bytes();assert raw[:4]==b'NES\x1a'and raw[4]==2
    image1=bytearray(65536);image1[0x8000:]=raw[16:32784]
    world=bytes([0,5,10,14,19,23,27,32])
    areas=bytes.fromhex('25 29 c0 26 60 28 29 01 27 62 24 35 20 63 22 29 41 2c 61 2a 31 26 62 2e 23 2d 60 33 29 01 27 64 30 32 21 65')
    w=raw.find(world+areas);assert w>=16 and raw.find(world+areas,w+1)==-1
    candidates=[]
    for at in range(0x8000,0xff00):
        if image1[at:at+4]==bytes([31,6,28,0])and image1[at+72:at+76]==bytes([0,3,25,28]):candidates.append(at)
    assert len(candidates)==1,candidates
    enemy=candidates[0];terrain=enemy+72
    for i in range(8):
        start,stop=world[i],world[i+1]if i<7 else 36
        stage=0
        for pointer in areas[start:stop]:
            kind,num=(pointer>>5)&3,pointer&31
            idx=image1[terrain+kind]+num
            ptr=image1[terrain+4+idx]+256*image1[terrain+38+idx]
            q=stream(image1,ptr)
            # Pipe-intro headers have entry selector6 or7, not a numbered stage.
            if (q['header'][0]>>3)&7 in [6,7]:continue
            stage+=1;originals.append(dict(game='SMB1',stage=f'{i+1}-{stage}',**q))
        assert stage==4
    audit2=json.loads((R/'build/smb2j-campaign-audit-1031-v1/source-audit.json').read_text())
    files2=disk_files(Path('C:/NES/fds/Super Mario Bros. 2 (Japan) (En).fds').read_bytes())
    for profile in audit2['profiles']:
        image=bytearray(65536)
        for n in profile['original_load_order']:
            f=files2[n];image[f['load']:f['load']+f['bytes']]=f['payload']
        counts={}
        for row in [x for x in audit2['routes']if x['profile']==profile['profile']]:
            q=stream(image,row['terrain']['address'])
            if (q['header'][0]>>3)&7 in [6,7]:continue
            world=row['world'];counts[world]=counts.get(world,0)+1
            originals.append(dict(game='SMB2J',stage=f'{world}-{counts[world]}',**q))
    routes=[]
    for profile,chain,table,indices,names in [
        ('worlds1-4',['NSMMAIN'],'SM2MAIN',range(4),'1234'),
        ('worlds5-8',['NSMMAIN','NSMDATA2'],'SM2MAIN',range(4,8),'5678'),
        ('worldsA-D',['NSMMAIN','NSMDATA4'],'SM2DATA4',range(4),'ABCD')]:
        image=bytearray(65536)
        for n in chain:
            f=files[n];image[f['load']:f['load']+f['bytes']]=f['payload']
        lab=sym[table];worlds=lab['WorldAddrOffsets'];area=lab['AreaAddrOffsets']
        for index,name in zip(indices,names):
            start=image[worlds+index]
            stop=image[worlds+index+1]if index<(3 if table=='SM2DATA4'else 7)else(18 if table=='SM2DATA4'else 36)
            numbered=0
            for order,pointer in enumerate(image[area+start:area+stop]):
                kind,num=(pointer>>5)&3,pointer&31
                pointers=[]
                for offsets,addrs,enemy in [('AreaDataHOffsets','AreaDataAddrs',False),('EnemyAddrHOffsets','EnemyDataAddrs',True)]:
                    idx=image[lab[offsets]+kind]+num
                    ptr=int.from_bytes(image[lab[addrs]+2*idx:lab[addrs]+2*idx+2],'little')
                    pointers.append(stream(image,ptr,enemy))
                q,e=pointers;intro=(q['header'][0]>>3)&7 in [6,7]
                if not intro:numbered+=1
                matches=[];qs=semantic(q['records'],'ANN')
                for ref in originals:
                    ratio=difflib.SequenceMatcher(None,qs,semantic(ref['records'],ref['game']),autojunk=False).ratio()
                    matches.append(dict(game=ref['game'],stage=ref['stage'],similarity=round(ratio,6),
                                        raw_terrain_byte_exact=q['sha256']==ref['sha256'],
                                        header_exact=q['header']==ref['header']))
                matches.sort(key=lambda x:(x['similarity'],x['raw_terrain_byte_exact'],x['header_exact']),reverse=True)
                routes.append(dict(profile=profile,original_load_order=chain,world=name,native_world=index,
                                   ordered_area=order,stage=None if intro else f'{name}-{numbered}',
                                   pipe_intro=intro,area_pointer=pointer,terrain=q,enemy=e,
                                   nearest_terrain_matches=matches[:6],
                                   same_number_SMB1=next((m for m in matches if m['game']=='SMB1'and m['stage']==f'{name}-{numbered}'),None)))
            assert numbered==4,(name,numbered)
    stages=[q for q in routes if q['stage']]
    assert len(stages)==48
    report=dict(passed=True,source_only=True,installed=False,campaign_implemented=False,
        donor_sha256=sha(DONOR),rebuilt_disk_byte_exact=True,compared_bytes=65500,
        source_repository='https://github.com/threecreepio/smbann-disassembly',
        source_commit='b70a0ad9e28facabd7b9d899f9c6cab7a45967f6',
        source_credit='doppelganger; All Night Nippon conditional disassembly by threecreepio',
        worlds=12,numbered_stages=48,world9_not_in_ANN_world_tables=True,
        ordered_area_entries=len(routes),routes=routes,
        comparison_limit='Nearest matches compare decoded object identities, coordinates, page flags and lengths. Similarity is not a complete rendered-level/physics assertion; raw equality and headers are separate.',
        additional_functions=['Distinct ANN graphics and rescued characters/ending.','Original star/save count and letter worlds.','ANN-specific parser/control differences from2J; do not enable poison/wind solely because its engine derives from2J.'],
        bindings={str(p.resolve()):sha(p)for p in [Path(__file__),DONOR,SMB1,S/'original/original.fds',S/'original/original.dbg',S/'assemble.json',S/'link.json',*sorted((S/'original').glob('*.asm')),R/'build/smb2j-campaign-audit-1031-v1/source-audit.json']})
    (O/'source-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    summary=[]
    for q in stages:
        if q['world']in'ABCD'or q['same_number_SMB1']['similarity']<0.9:
            summary.append(dict(stage=q['stage'],nearest=q['nearest_terrain_matches'][:2],same_number_SMB1=q['same_number_SMB1']))
    (O/'changes-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,byte_exact=True,worlds=12,stages=48,ordered_areas=len(routes),largest_changes=summary)))


if __name__=='__main__':main()
