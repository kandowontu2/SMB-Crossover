"""Actual80-menu regression plus exact pixel witnesses for menu-only data edits."""
from pathlib import Path
import json
import sys
from PIL import Image

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import arthur_quick_functional_admission_v1 as A
import prepare_roster_visual_fixes_1030_v1 as B

O=B.O


def thumb(nam,chrdata,slot,width=16):
    top,col=4+slot//8*4,4+slot%8*3
    return [[B.decode(chrdata[nam[(top+y//8)*32+col+x//8]*16:][:16])[y%8][x%8] for x in range(width)] for y in range(24)]


def main():
    proof=json.loads((O/'source-proof.json').read_text())
    assert all(B.sha(f)==v for f,v in proof['bindings'].items())
    rows=[]
    for slot,count in enumerate(A.COUNTS):
        pair=[A.fresh(p,slot) for p in [B.P,O]]
        for m in pair:A.call(m,'MenuResolveCharacter');A.call(m,'QueueSelection')
        for variant in range(count):
            if variant:
                for m in pair:A.button(m,32)
            pending=[A.call(m,'FmPending')[0] for m in pair]
            assert pending[0]==pending[1]
            assert pair[0].get('SelectedCharacter')==pair[1].get('SelectedCharacter')
            packets=[[q for q in A.commands(m) if q['address']==0x2328] for m in pair]
            if (slot,variant) in [(9,2),(31,0)]:
                assert len(packets[0])==len(packets[1])==1
                old=packets[0][0]['data'];new=packets[1][0]['data']
                assert old.count(0x3f)==1 and new.count(0x3f)==0
                assert new==[0x24 if v==0x3f else v for v in old]
            else:assert packets[0]==packets[1],(slot,variant)
            rows.append(dict(slot=slot,variant=variant,pending=bool(pending[1]['P']&1),
                selected=pair[1].get('SelectedCharacter'),name_packets=packets[1]))
    assert len(rows)==80 and sum(not x['pending'] for x in rows)==54
    old=Path('build/expanded-playable-menu-parent-1030-v1/joint')
    oldnam=(old/'menu.nam').read_bytes();oldchr=(old/'packed.chr').read_bytes()[4096:8192]
    nam=(O/'menu.nam').read_bytes();newchr=(O/'packed.chr').read_bytes()[4096:8192]
    for slot in range(32):
        if slot in (13,23,25,26):assert thumb(nam,newchr,slot)==[list(reversed(row)) for row in thumb(oldnam,oldchr,slot)]
        elif slot!=27:assert thumb(nam,newchr,slot)==thumb(oldnam,oldchr,slot),slot
    newdk=thumb(nam,newchr,27,24)
    assert any(any(row) for row in newdk)
    # Full grayscale source thumbnails. A source-pixel witness, not a PPU capture.
    sheet=Image.new('RGB',(576,216),'#101725')
    colors=[(16,23,37),(72,72,72),(160,160,160),(248,248,248)]
    for col,(label,pixels) in enumerate([('old',thumb(oldnam,oldchr,27)),('new',newdk)]):
        sprite=Image.new('RGB',(len(pixels[0]),24))
        for y,row in enumerate(pixels):
            for x,v in enumerate(row):sprite.putpixel((x,y),colors[v])
        sprite=sprite.resize((len(pixels[0])*8,192),Image.Resampling.NEAREST)
        sheet.paste(sprite,(24+col*288,12))
    sheet.save(O/'DK-old-left-new-right-source-preview.png')
    controls=dict(passed=True,native=False,candidate=proof['candidate'],actual_menu_profiles=80,
        ready=54,pending=26,actual_Quick_Arthur_names_have_no_coming_soon_marker=True,
        all_foreign_name_packets_and_pending_decisions_exact=True,
        unchanged_other_27_grid_thumbnails=True,exact_four_complete_grayscale_mirrors=True,
        DK_width=24,DK_pixels_not_resampled=True,source_pixel_preview_sha256=B.sha(O/'DK-old-left-new-right-source-preview.png'),
        rows=rows,limits=['Source menu/bitmap checks; native menu view pending user-owned Mesen.','No gameplay instruction or runtime facing change in this data-only successor.'])
    B.save(O/'menu-controls.json',controls)
    print(json.dumps({k:controls[k] for k in ['passed','candidate','actual_menu_profiles','ready','pending']}))


if __name__=='__main__':main()
