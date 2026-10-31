"""Rebuild menu artwork/names only, keeping every gameplay instruction intact."""
from pathlib import Path
from collections import Counter
from itertools import groupby
import difflib
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_current_rcr_misc_chr_fix_1030_v1 as B

P=R/'build/functional-roster-ready54-v1/joint'
O=R/'build/roster-visual-fixes-1030-v1'
sha=B.sha
save=B.save


def decode(data):
    return [[((data[y]>>(7-x))&1)+2*((data[y+8]>>(7-x))&1) for x in range(8)] for y in range(8)]


def encode(pixels):
    return bytes(sum(((pixels[y][x]>>plane)&1)<<(7-x) for x in range(8)) for plane in range(2) for y in range(8))


def main():
    assert not O.exists()
    parent=json.loads((P.parent/'handoff.json').read_text())
    assert all(sha(f)==v for f,v in parent['bindings'].items())
    assert sha(P/'candidate.nes')=='08f1a75fb13f1974270bf9c6732d050f778f7f5b8b8a3361683416c242a176f3'
    O.mkdir()
    for p in P.rglob('*'):
        if p.is_file() and p.suffix in {'.s','.inc','.cfg','.bin','.chr','.nam','.rle'}:
            q=O/p.relative_to(P);q.parent.mkdir(parents=True,exist_ok=True)
            q.write_bytes(p.read_bytes())
    raw,syms,address,location,_=B.linked(P/'candidate.nes')
    entry=(O/'entrypoint.s').read_text()
    packed=Path(re.findall(r'\.incbin "([^"]+/packed\.chr)"',entry)[0])
    preview=Path(re.findall(r'\.incbin "([^"]+/pending-previews\.chr)"',entry)[0])
    select=(O/'src/character_select.s').read_text()
    rle=Path(re.findall(r'\.incbin "([^"]+/menu\.rle)"',select)[0])
    oldpacked=packed.read_bytes();oldpreview=preview.read_bytes()
    assert raw[1048592:1048592+len(oldpacked)]==oldpacked
    assert raw[1048592+700*1024:1048592+704*1024]==oldpreview
    nam=bytearray()
    encoded=rle.read_bytes();i=0
    while encoded[i]:
        count,v=encoded[i:i+2];nam.extend([v]*count);i+=2
    assert len(nam)==1024 and i==len(encoded)-1
    oldnam=bytes(nam);oldbg=oldpacked[4096:8192];bg=bytearray(oldbg)
    def grid(slot):
        top,col=4+slot//8*4,4+slot%8*3
        return [[decode(oldbg[oldnam[(top+y//8)*32+col+x//8]*16:][:16])[y%8][x%8] for x in range(16)] for y in range(24)]
    images={slot:[list(reversed(row)) for row in grid(slot)] for slot in (13,23,25,26)}
    # Decode the exact already-recognizable colored DK preview into24x24.
    # Keep its24px width; the old16px fit discarded the facial detail.
    dk=[[0]*24 for _ in range(32)]
    at=location('FmDkPreviewOam');parts=[raw[at+j:at+j+4] for j in range(0,24,4)]
    for y,t,attr,x in reversed(parts):
        data=oldpreview[(t&254)*16:(t&254)*16+32]
        for yy in range(16):
            for xx in range(8):
                sy=15-yy if attr&128 else yy;sx=7-xx if attr&64 else xx
                k=sy//8*16+sy%8
                v=((data[k]>>(7-sx))&1)+2*((data[k+8]>>(7-sx))&1)
                if v:dk[y-159+yy][x-116+xx]=[0,3,2,1][v]
    ys=[y for y,row in enumerate(dk) if any(row)]
    assert max(ys)-min(ys)+1<=24
    cropped=dk[min(ys):max(ys)+1]
    images[27]=[[0]*24 for _ in range(24-len(cropped))]+cropped
    affected=set()
    for slot,pixels in images.items():
        top,col=4+slot//8*4,4+slot%8*3
        affected.update((top+y)*32+col+x for y in range(3) for x in range(len(pixels[0])//8))
    protected={v for i,v in enumerate(oldnam[:960]) if i not in affected}
    available=sorted(set(range(64,252))-protected)
    patterns={bytes(oldbg[t*16:(t+1)*16]):t for t in sorted(protected)}
    allocations=[]
    for slot,pixels in images.items():
        top,col=4+slot//8*4,4+slot%8*3
        for ty in range(3):
            for tx in range(len(pixels[0])//8):
                data=encode([row[tx*8:tx*8+8] for row in pixels[ty*8:ty*8+8]])
                if data not in patterns:
                    assert available,'Menu background pool exhausted'
                    tile=available.pop(0);patterns[data]=tile;bg[tile*16:(tile+1)*16]=data
                    allocations.append(tile)
                nam[(top+ty)*32+col+tx]=patterns[data]
    assert all(bg[t*16:(t+1)*16]==oldbg[t*16:(t+1)*16] for t in protected)
    # The old preview rectangle assigned palette3 to row18 of the roster.
    # Align its top with row20 so DK/Bowser/WWF bottom tiles retain palette0.
    for col in (3,4):
        assert nam[960+4*8+col]==0xf0;nam[960+4*8+col]=0
    for col in range(12,20):
        assert nam[19*32+col]==254;nam[19*32+col]=36
    newpacked=bytearray(oldpacked);newpacked[4096:8192]=bg
    (O/'packed.chr').write_bytes(newpacked)
    (O/'menu.nam').write_bytes(nam)
    stream=bytearray()
    for v,g in groupby(nam):
        count=len(list(g))
        while count:
            n=min(count,255);stream.extend([n,v]);count-=n
    stream.append(0);(O/'menu.rle').write_bytes(stream)
    # Mirror pending colored Bowser/Thomas previews in their existing8 pairs.
    tiletable=location('FmPreviewTiles')
    rows=[list(raw[tiletable+4*j:tiletable+4*j+4]) for j in range(33)]
    used={t//2 for j,row in enumerate(rows) if j not in (15,17,32) for t in row}
    used.update(range(100,116));used.update((66,67,126,127))
    free=sorted(set(range(128))-used)
    pool={oldpreview[j*32:(j+1)*32]:j for j in sorted(used)}
    newpreview=bytearray(oldpreview)
    for index in (15,32):
        pixels=[[0]*16 for _ in range(32)]
        for j,t in enumerate(rows[index]):
            pair=oldpreview[t*16:t*16+32]
            for half in range(2):
                tile=decode(pair[half*16:(half+1)*16])
                for y in range(8):pixels[j//2*16+half*8+y][j%2*8:j%2*8+8]=tile[y]
        pixels=[list(reversed(row)) for row in pixels]
        result=[]
        for j in range(4):
            pair=b''.join(encode([line[j%2*8:j%2*8+8] for line in pixels[j//2*16+h*8:j//2*16+h*8+8]]) for h in range(2))
            if pair not in pool:
                assert free;pairid=free.pop(0);pool[pair]=pairid;newpreview[pairid*32:(pairid+1)*32]=pair
            result.append(pool[pair]*2)
        rows[index]=result
    assert all(newpreview[j*32:(j+1)*32]==oldpreview[j*32:(j+1)*32] for j in used)
    (O/'pending-previews.chr').write_bytes(newpreview)
    p=O/'src/full_roster_menu_art.inc';old=p.read_text();new=old
    for name in ('ARTHUR','QUICK MAN'):
        assert new.count('*'+name)==1;new=new.replace('*'+name,' '+name)
    begin=new.index('FmPreviewTiles:');end=new.index('FmPreviewColors:')
    new=new[:begin]+'FmPreviewTiles:\n'+''.join(' .byte '+','.join(map(str,row))+'\n' for row in rows)+new[end:]
    p.write_text(new)
    patches=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='parent/src/full_roster_menu_art.inc',tofile='new/src/full_roster_menu_art.inc'))
    entry=entry.replace(str(packed),str(O/'packed.chr')).replace(packed.as_posix(),(O/'packed.chr').as_posix())
    entry=entry.replace(str(preview),str(O/'pending-previews.chr')).replace(preview.as_posix(),(O/'pending-previews.chr').as_posix())
    (O/'entrypoint.s').write_text(entry)
    select=select.replace(str(rle),str(O/'menu.rle')).replace(rle.as_posix(),(O/'menu.rle').as_posix())
    (O/'src/character_select.s').write_text(select)
    (O/'source.patch').write_text(''.join(patches))
    p=O/'private.cfg';p.write_text(p.read_text().replace(str(P),str(O)).replace(P.as_posix(),O.as_posix()))
    compile_cmd=[v.replace(str(P),str(O)) for v in json.loads((P.parent/'compile-main.json').read_text())['command']]
    compile_cmd[1:1]=['--bin-include-dir',str(P),'--bin-include-dir',str(P/'src')]
    link_cmd=[v.replace(str(P/'candidate'),str(O/'candidate')).replace(str(P/'private.cfg'),str(O/'private.cfg')).replace(str(P/'main.o'),str(O/'main.o')) for v in json.loads((P.parent/'final-link.json').read_text())['command']]
    inputs={Path(v):sha(v) for v in link_cmd if v.endswith('.o') and Path(v)!=O/'main.o'}
    B.O=O;B.run(compile_cmd,'compile-main');B.run(link_cmd,'link');B.prepare(R,O/'candidate.nes')
    assert all(sha(f)==v for f,v in inputs.items())
    after,news,_,_,_=B.linked(O/'candidate.nes')
    assert all(name in news and q['val']==news[name]['val'] for name,q in syms.items())
    named=location('FmNames');table=location('FmPreviewTiles');start=location('SelectNameTable')
    end=start+len(encoded)+1024 # Tightened below using actual source padding boundary.
    limit=location('CrossoverMenuInput')+0xc8c
    assert start+len(stream)<=limit
    legal={named+j*16+k for j in (30,31) for k in range(16)}|set(range(table+15*4,table+16*4))|set(range(table+32*4,table+33*4))|set(range(start,limit))
    prgdiff=[i for i,(a,b) in enumerate(zip(raw[:1048592],after[:1048592])) if a!=b]
    assert all(i in legal for i in prgdiff) and raw[:16]==after[:16]
    for i,(a,b) in enumerate(zip(raw[1048592:],after[1048592:])):
        if a!=b:assert 4096<=i<8192 or 700*1024<=i<704*1024
    for f,v in parent['bindings'].items():assert sha(f)==v,f
    files={Path(__file__),P.parent/'handoff.json',packed,preview,rle}|set(inputs)|{p for p in O.rglob('*') if p.is_file()}
    proof=dict(passed=True,native=False,installed=False,parent=sha(P/'candidate.nes'),candidate=sha(O/'candidate.nes'),ready=54,pending=26,
        grayscale_flipped_slots=[13,23,25,26],DK_slot=27,DK_source='Exact colored six-part DK menu preview, retained at24px width, grayscale24x24.',
        DK_pixels_not_rescaled=True,preview_overlap_removed_rows=[18,19],pending_colored_flipped_indices=[15,32],markers_removed=['Arthur','Quick Man'],
        background_allocated_tiles=allocations,background_tiles_remaining=len(available),preview_pairs_remaining=len(free),
        all_foreign_background_patterns_and_preview_pairs_exact=True,all_prior_symbol_values_exact=True,
        all_gameplay_instructions_WRAM_payloads_header_other_CHR_exact=True,PRG_changed_bytes=len(prgdiff),new_RLE_bytes=len(stream),old_RLE_bytes=len(encoded),
        limits=['Source-only menu data successor; native menu view pending user-owned Mesen slot.','Goku/Gimmick gameplay facing corrections are separate source work.'],
        bindings={str(p):sha(p) for p in sorted(files)})
    save(O/'source-proof.json',proof)
    print(json.dumps({k:proof[k] for k in ['passed','candidate','PRG_changed_bytes','new_RLE_bytes','background_tiles_remaining','preview_pairs_remaining']}))


if __name__=='__main__':main()
