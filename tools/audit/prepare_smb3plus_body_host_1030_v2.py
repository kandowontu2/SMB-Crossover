"""Use retired constant CHR-high tables, preserving Rogue Dawn's audio.

All seven original high tables contain only2. Keep their pointer/register
outputs; replace the sole indirect read with LDA#2 of the same byte length.
Four now-unread81B table spans hold source palette/graphics helpers.
"""
from pathlib import Path
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_smb3plus_body_host_1030_v1 as P


def main():
    P.O=R/'build/smb3plus-body-host-1030-v3';P.J=P.O/'joint'
    original_write=P.B.write
    retired=[]

    def write(path,text):
        path=Path(path)
        if path==P.J/'src/smb3_mario_render.s':
            at=text.index(' lda M3ChrHiTableLo,x')
            end=text.index(' sta M3SpritePageHi',at)
            block=text[at:end]
            old=' lda (R0),y'
            new=' lda #2 ; All original high-table entries are2; pointer outputs retained.'
            assert (block.count(old),block.count(new)) in [(1,0),(0,1)]
            replacement=block.replace(old,new)
            text=text[:at]+replacement+text[end:]
        if path==P.J/'smb3plus_body_host.s':
            start=text.index('.proc MbPaletteIndex\n')
            original=text.index('Original:\n',start)
            end=text.index('.endproc',original)
            old_index=text[original+len('Original:\n'):end]
            new_index=text[start:original]+'Original:jmp MbOriginalPaletteIndex\n.endproc\n'
            old_index='.proc MbOriginalPaletteIndex\n'+old_index+'.endproc\n'
            start=text.index('.proc MbPaletteAndBody\n')
            end=text.index('.endproc',start)+len('.endproc')
            body=text[start:end]+'\n'
            start=text.index('MbPalettes:\n')
            end=text.index('MbBodyHostEnd:',start)
            palettes=text[start:end]
            target=P.J/'src/smb3_mario_art.inc';art=P.B.read(target)
            replacements=[new_index,old_index,body,palettes]
            for i,code in enumerate(replacements):
                pattern=rf'M3Form{i}ChrHi: \.byte ([0-9,]+)\n'
                match=re.search(pattern,art)
                assert match and [int(x)for x in match.group(1).split(',')]==[2]*81
                label=f'M3Form{i}ChrHi'
                new=label+':\n'+code+f' .res 81-(*-{label}),2\n'
                art=art[:match.start()]+new+art[match.end():]
                retired.append(dict(label=label,bytes=81,old_fill=2,sole_reader='M3SetFrame indirect high lookup replaced by same-length LDA#2'))
            original_write(target,art)
            text='; Helpers are source-emitted in the four retired constant-high tables in smb3_mario_art.inc.\n'
        if path==P.J/'private.cfg'and 'SMB3PLUS_BODY_CHR:'in text:
            line='    SMB3PLUS_BODY_CHR:load=UNALLOCATED_CHR_MEM,type=ro,start=$f2400;\n'
            assert text.count(line)==1
            text=text.replace(line,'')
            match=re.search(r'^    BENJ_MARIO_CHR:[^\n]+\n',text,re.M)
            assert match
            text=text[:match.end()]+line+text[match.end():]
        original_write(path,text)

    P.B.write=write
    try:P.main()
    finally:P.B.write=original_write
    path=P.O/'source-stage.json';d=json.loads(P.B.read(path))
    d['retired_constant_high_tables']=retired
    d['unchanged_indirect_pointer_register_outputs']=True
    d['preserved_audio_owners']=['ROGUE_AUDIO_PAGES_7 at90:AF00','ROGUE_AUDIO_UPPER_RAW_0 at91:D400']
    d['retained_resource_negative']='build/smb3plus-body-host-1030-v1/final-link.json'
    for p in [Path(__file__),P.J/'src/smb3_mario_art.inc',R/'build/smb3plus-body-host-1030-v1/final-link.json']:
        d['bindings'][str(p)]=P.B.sha(p)
    original_write(path,json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(candidate=d['candidate'],retired_bytes=324,audio_preserved=True,native=False,menu_unlocked=False)))


if __name__=='__main__':main()
