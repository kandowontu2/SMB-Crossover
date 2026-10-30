"""Compact authenticated pose data; no host PRG/CHR lease is assigned."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'build/arthur-source-v1';WIN=ROOT/'build/arthur-projected-leaf-v2';OUT=ROOT/'build/arthur-projected-leaf-v3'
BIN=ROOT/'tools/Windows/cc65/bin';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    source=json.loads((BASE/'art-source.json').read_text());windowed=json.loads((WIN/'windowed-art-proof.json').read_text())
    maps={pose:(g['relative_page'],{int(k):v for k,v in g['source_tile_to_even_local_tile'].items()})for g in windowed['pages']for pose in g['poses']}
    layouts={}
    for r in source['records']:
        if len(r['coordinates'])>len(layouts.get(r['layout'],[])):layouts[r['layout']]=r['coordinates']
    layoutids=sorted(layouts);uni=[];posemap=[255]*256;entries={}
    for r in source['records']:
        assert layouts[r['layout']][:len(r['coordinates'])]==r['coordinates']
        page,mapping=maps[r['pose']]
        # Five local-pair bits, H/V bits5/6, hidden part bit7.
        parts=[128 if p['tile']==255 else(mapping[p['tile']]//2)|((p['attribute']>>6)<<5)for p in r['parts']]
        raw=bytes([len(parts)|(page<<4),layoutids.index(r['layout'])]+parts)
        if raw not in uni:uni.append(raw)
        posemap[r['pose']]=uni.index(raw);entries[r['pose']]=raw
    a=['; Abstract original-source pose data. No physical host lease.','.segment "ARTHUR_COMPACT_ART"',
       '.export ArCompactArtStart,ArCompactArtEnd,ArPoseIndex,ArRecordLo,ArRecordHi,ArLayoutLo,ArLayoutHi','ArCompactArtStart:','ArPoseIndex:']
    for i in range(0,256,16):a.append(' .byte '+','.join(str(n)for n in posemap[i:i+16]))
    for name,prefix,count in[('ArRecordLo','<ArRecord',len(uni)),('ArRecordHi','>ArRecord',len(uni)),
       ('ArLayoutLo','<ArLayout',len(layoutids)),('ArLayoutHi','>ArLayout',len(layoutids))]:
        a += [name+':',' .byte '+','.join(prefix+str(i)for i in range(count))]
    for i,raw in enumerate(uni):a += [f'ArRecord{i}:',' .byte '+','.join(str(n)for n in raw)]
    for i,k in enumerate(layoutids):a += [f'ArLayout{i}:',' .byte '+','.join(str(n)for n in layouts[k])]
    a += ['ArCompactArtEnd:','.assert ArCompactArtEnd-ArCompactArtStart=1554,error,"Source compact metadata changed"']
    (OUT/'compact-art.s').write_text('\n'.join(a)+'\n')
    (OUT/'compact-art.cfg').write_text('MEMORY { A:start=$C000,size=$0800,type=ro,file=%O; }\nSEGMENTS { ARTHUR_COMPACT_ART:load=A,type=ro; }\n')
    commands=[[str(BIN/'ca65.exe'),'-g','-o',str(OUT/'compact-art.o'),str(OUT/'compact-art.s')],
       [str(BIN/'ld65.exe'),'-C',str(OUT/'compact-art.cfg'),'-o',str(OUT/'compact-art.bin'),'-Ln',str(OUT/'compact-art.lbl'),
        '--dbgfile',str(OUT/'compact-art.dbg'),str(OUT/'compact-art.o')]]
    for cmd in commands:subprocess.run(cmd,check=True,cwd=ROOT)
    assert (OUT/'compact-art.bin').stat().st_size==1554
    cases=[]
    for r in source['records']:
        header,layout,*parts=entries[r['pose']];count=header&15;page=header>>4
        assert count==len(r['parts'])and page==maps[r['pose']][0]
        xy=layouts[layoutids[layout]];assert xy[:count*2]==r['coordinates']
        for key,row in r['attribute_rows'].items():
            key=int(key);expected=next(v for v in windowed['records']if v['pose']==r['pose']and v['attribute_row']==key)
            got=[]
            for i,encoded in enumerate(parts):
                # The original rows0..3 are constant; row8 is2,1,1,... .
                palette=(2 if i==0 else 1)if key==8 else key
                assert palette==row['values'][i]
                if encoded&128:assert r['parts'][i]['tile']==255;continue
                attr=((encoded>>5)&3)<<6|palette
                x,y=xy[i*2:i*2+2];x=x if x<128 else x-256;y=y if y<128 else y-256
                window=6 if page==3 else 0;local=(encoded&31)*2
                got.append(dict(tile=local|(0x81 if window==6 else 0),local_tile=local,attribute=attr,x=x,
                  y=y-(8 if attr&128 else 0),height=16,relative_page=page,hardware_window=window))
            assert got==expected['parts'],(r['pose'],key)
            cases.append(dict(pose=r['pose'],attribute_row=key,exact_decoded_parts=True,
               source_index_alpha_priority_plane_sha256=expected['exact_index_alpha_priority_plane_sha256']))
    result=dict(status='PASS_ABSTRACT1554B_METADATA_EXACT84POSES420PALETTE_CASES',commands=commands,
       metadata_sha256=sha(OUT/'compact-art.bin'),metadata_bytes=1554,pose_index_bytes=256,
       unique_records=len(uni),record_bytes=sum(map(len,uni)),layout_count=len(layoutids),layout_bytes=sum(map(len,layouts.values())),
       pointer_bytes=(len(uni)+len(layoutids))*2,attribute_rows='Original0/1/2/3 constant; row8 first2 then1, explicitly compared in all420cases.',
       cases=cases,CHR=dict(path=str((WIN/'arthur-windowed.chr').resolve()),sha256=sha(WIN/'arthur-windowed.chr'),bytes=4096),
       bindings={str(p.resolve()):sha(p)for p in[Path(__file__),BASE/'art-source.json',WIN/'windowed-art-proof.json',
          WIN/'arthur-windowed.chr',OUT/'compact-art.s',OUT/'compact-art.cfg',OUT/'compact-art.bin',BIN/'ca65.exe',BIN/'ld65.exe']},
       limits='Abstract metadata linked atC000 only for pointer proof. No host PRG/CHR allocation, palette quantization or native gameplay claim.')
    target=OUT/'compact-art-proof.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],bytes=1554,records=len(uni),layouts=len(layoutids),proof_sha256=sha(target))))
if __name__=='__main__':main()
