"""Join genuine SMB3+ body art/palettes privately; do not unlock the menu.

Kick/float and special-form movement remain required before admission.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location

P=R/'build/peach-palette-fix-1030-v1'
A=R/'build/smb3plus-original-characters-1030-v1'
O=R/'build/smb3plus-body-host-1030-v1';J=O/'joint'


def once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def main():
    assert not O.exists()
    h=json.loads(B.read(P/'handoff.json'));B.bound(h)
    art=json.loads(B.read(A/'source-proof.json'));B.bound(art)
    assert h['candidate']=='f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78'
    old=load(P/'joint/candidate.nes')
    shutil.copytree(P/'joint',J)
    def rt(text):return text.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file()and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
    source=J/'src/smb3_mario_render.s';text=B.read(source)
    a=text.index(' lda M3RenderForm\n',text.index('.proc M3Palette\n'))
    z=text.index(' lda #$3f\n',a)
    original_index=text[a:z]
    # Measure the original assembled span, preserving every following entry.
    at=location(old,'M3Palette');data=old['raw'][at:at+180]
    needle=bytes([0xad,address(old,'M3RenderForm')&255,address(old,'M3RenderForm')>>8,0xc9,2])
    begin=data.index(needle);end=data.index(bytes.fromhex('a8a93f9d'),begin)+1
    span=end-begin
    text=text[:a]+f' jsr MbPaletteIndex\n .res {span}-3,$ea\n'+text[z:]
    for offset in ['', '+1', '+2']:
        text=once(text,' lda M3NativePalettes'+offset+',y',' lda MbPalettes'+offset+',y')
    text=once(text,'Palette:jsr M3PaletteCached','Palette:jsr MbPaletteAndBody')
    B.write(source,text)
    palettes=json.loads(B.read(A/'palette-consumers.json'))
    original_palette=old['raw'][location(old,'M3NativePalettes'):location(old,'M3NativePalettes')+24]
    colors=list(original_palette)
    for char in [2,3]:
        for form in range(8):
            colors+=next(q['visible_colors']for q in palettes if q['character']==char and q['player']==0 and q['form']==form)
    assert len(colors)==72
    helper='''; Genuine donor graphics/normal-form palette integration only.
.pushseg
.segment "M3_LOGIC"
.proc MbPaletteIndex
 lda M3Variant
 cmp #2
 bcc Original
 cmp #4
 bcs Original
 lda M3RenderForm
 cmp #5
 bne Form
 ldy M3Native::Player_Statue
 beq Form
 lda #7
Form:sta M3Scratch
 asl
 clc
 adc M3Scratch
 clc
 adc #24
 ldy M3Variant
 cpy #3
 bne Index
 clc
 adc #24
Index:tay
 rts
Original:
'''+original_index+''' rts
.endproc
.proc MbPaletteAndBody
 php
 pha
 phx
 phy
 lda M3Variant
 cmp #2
 bcc Done
 cmp #4
 bcs Done
 lda SmChrBank
 sec
 sbc #12
 tax
 lda M3RenderForm
 cmp #4
 bne Root
 lda M3RenderFrame
 cmp #$39
 bcc Root
 cmp #$3c
 bcs Root
 ldx #20
Root:txa
 clc
 adc #<969
 ldy M3Variant
 cpy #3
 bne Publish
 clc
 adc #25
Publish:
 sta SmChrBank
 lda #>969
 sta M3SpritePageHi
Done:
 ply
 plx
 pla
 plp
 jmp M3PaletteCached
.endproc
MbPalettes:
 .byte '''+','.join('$%02x'%v for v in colors)+'''
MbBodyHostEnd:
.assert MbBodyHostEnd<=$c000,lderror,"SMB3+ helpers stay in existing M3 logic bank"
.popseg
'''
    B.write(J/'smb3plus_body_host.s',helper)
    B.write(J/'entrypoint.s',B.read(J/'entrypoint.s')+'\n.include "smb3plus_body_host.s"\n')
    for name in ['toad','peach']:
        shutil.copy2(A/(name+'-all-original-body-pages.chr'),J/(name+'-smb3plus-body.chr'))
    B.write(J/'smb3plus-chr.s','.segment "SMB3PLUS_BODY_CHR"\n.incbin "toad-smb3plus-body.chr"\n.incbin "peach-smb3plus-body.chr"\n')
    B.write(J/'private.cfg',once(B.read(J/'private.cfg'),'    BENJ_MARIO_CHR:',
        '    SMB3PLUS_BODY_CHR:load=UNALLOCATED_CHR_MEM,type=ro,start=$f2400;\n    BENJ_MARIO_CHR:'))
    recipes=[]
    for label in ['main-build','union-build']:
        recipes.append((label,[rt(x)for x in json.loads(B.read(P/(label+'.json')))['command']]))
    ca=R/'tools/Windows/cc65/bin/ca65.exe'
    recipes.append(('chr-build',[str(ca),'--cpu','6502x','--bin-include-dir',str(J),'-o',str(J/'smb3plus-chr.o'),str(J/'smb3plus-chr.s')]))
    link=[rt(x)for x in json.loads(B.read(P/'final-link.json'))['command']]+[str(J/'smb3plus-chr.o')]
    recipes.append(('final-link',link))
    for label,command in recipes:
        validate(command,J,cwd=R)
        result=subprocess.run(command,cwd=R,capture_output=True,text=True)
        B.write(O/(label+'.json'),json.dumps(dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr),indent=2)+'\n')
        assert result.returncode==0,(label,result.stderr)
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes')
    new=load(J/'candidate.nes')
    for name in old['syms']:
        if name.startswith('M3')and old['syms'][name].get('type')=='lab':
            assert address(old,name)==address(new,name),name
    assert new['raw'][:16]==old['raw'][:16]
    base=16+128*8192
    assert new['raw'][base:base+969*1024]==old['raw'][base:base+969*1024]
    assert new['raw'][base+1019*1024:]==old['raw'][base+1019*1024:]
    d=dict(source=True,native=False,installed=False,menu_unlocked=False,
        status='PRIVATE_SMB3PLUS_BODY_PALETTE_HOST_BUILT_NOT_ADMITTED',candidate=B.sha(J/'candidate.nes'),
        parent=h['candidate'],source_art_sha256=B.sha(A/'source-proof.json'),
        CHR_pages=[969,1019],M3_public_entries_preserved=True,
        limits=['Kick/float and source movement are not joined.',
            'Growth, slide and ground-pound special-form source consumers remain incomplete.',
            'No menu admission, native gameplay or full1-1/every-powerup claim.'],
        bindings={str(p):B.sha(p)for p in [Path(__file__),P/'handoff.json',A/'source-proof.json',
            source,J/'smb3plus_body_host.s',J/'entrypoint.s',J/'private.cfg',J/'smb3plus-chr.s',
            J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',*[O/(label+'.json')for label,_ in recipes]]})
    B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items()if k!='bindings'},indent=2))


if __name__=='__main__':main()
