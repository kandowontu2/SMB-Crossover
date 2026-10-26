"""Canonical staged admission/icon source changes in verified A87 tail only."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,sha

BASE='1d741cfa4c502b22906eb8fb74296c12899f34cf03be86e0eb31131fc77e353e'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['parent','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--stage',choices=['admission','icons'],required=True);a=p.parse_args()
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    old=load(a.parent/'candidate.nes');a.output.mkdir(parents=True);s=a.output/'source'
    shutil.copytree(a.parent/'source',s,ignore=shutil.ignore_patterns('__pycache__'));changes=[];records=[]
    target=s/'src/tmnt_equipment_draw.s';text=target.read_text()
    if a.stage=='admission':
        assert sha(a.parent/'candidate.nes')==BASE
        anchor=' lda TnGearSelected\n ora TnShotKind\n';assert text.count(anchor)==1
        text=text.replace(anchor,' lda TnGearSelected\n bne RenderActors\n ora TnShotKind\n')
        anchor=' bne RenderActors\n lda #0\n sta TnDrawSlot\n';assert text.count(anchor)==1
        text=text.replace(anchor,' bne RenderActors\n ; The complete OR result is already zero, including its N/Z flags.\n sta TnDrawSlot\n')
        changes=['src/tmnt_equipment_draw.s']
    else:
        assert(a.parent/'fast-preparation.json').exists()
        prep=json.loads((a.parent/'fast-preparation.json').read_text());assert prep['stage']=='admission'
        off=16+87*8192;assert old['raw'][off+0x1700:off+0x2000]==bytes([255])*0x900
        assert int(old['syms']['TnExpansionFlushFast']['size'],0)>0
        assert all(int(g['start'],0)+int(g['size'],0)<=0xd700 for g in old['segs'].values()if g.get('name')=='"TN_SWEEP_C87"')
        cfg=s/'smb1base-mmc5-expanded.cfg';ct=cfg.read_text();anchor='TN_SWEEP_C87_MEM: start=$d500, size=$0b00, type=ro, file=%O, fill=yes, fillval=$ff, bank=$57;'
        assert ct.count(anchor)==1;ct=ct.replace(anchor,anchor.replace('$0b00','$0200')+'\n    TN_EQUIP_FAST_MEM: start=$b700, size=$0900, type=ro, file=%O, fill=yes, fillval=$ff, bank=$57;')
        anchor='TN_SWEEP_C87:load=TN_SWEEP_C87_MEM,type=ro;';assert ct.count(anchor)==1
        cfg.write_text(ct.replace(anchor,anchor+'\n    TN_EQUIP_FAST:load=TN_EQUIP_FAST_MEM,type=ro;'))
        anchor=' lda #128\n sta R4\n';start=text.index(anchor);end=text.index('Ammo:jsr TnAmmoHud',start)
        block=text[start:end];assert block.count('jsr TnWorldDraw')==1
        text=text[:start]+block.replace('jsr TnWorldDraw','jsr TnExactIconRender')+text[end:]
        tmnt=s/'src/tmnt.s';tt=tmnt.read_text();anchor='.include "tmnt_hud_world.s"';assert tt.count(anchor)==1
        tmnt.write_text(tt.replace(anchor,anchor+'\n.include "tmnt_equipment_icon_fast.s"'))
        body=['; Private icon-call entry: the caller retains the exact original',
            '; fixed coordinates/palette/page setup. Original fallback is literal.',
            '.pushseg','.segment "TN_EQUIP_FAST"','.proc TnExactIconRender',
            ' lda R1',' cmp #$d1',' bne Legacy',' lda R0']
        base=16+88*8192-0xc000;lo=location(old,'TnWorldRLo');hi=location(old,'TnWorldRHi')
        for i,pose in enumerate(range(80,84)):
            ptr=old['raw'][lo+pose]+256*old['raw'][hi+pose];assert ptr>>8==0xd1
            pos=base+ptr;n=old['raw'][pos];assert n==16
            parts=[list(old['raw'][pos+j:pos+j+4])for j in range(1,n+1,4)]
            assert all(v[2]==240 and v[3]in[0,248]for v in parts)
            records.append(dict(pose=pose,pointer=ptr,parts=parts))
            body += [f' cmp #${ptr&255:02x}',f' beq Icon{i}Gate']
        body += ['Legacy:',' jmp TnWorldDraw']
        for i,row in enumerate(records):
            body += [f'Icon{i}Gate:',f' jmp Icon{i}']
        for i,row in enumerate(records):
            body += [f'Icon{i}:',' ldx CurrentOAMOffset',' lda #16',' clc',' adc CurrentOAMOffset',' bcc :+',' jmp TnWorldDraw',':',
                ' lda GuestOamRotationActive',f' beq Draw{i}',' txa',' clc',' adc RgOamRotation',' tax',f'Draw{i}:']
            for tile,attr,y,x in reversed(row['parts']):
                body += [f' lda #{(128+x)&255}',' sta Sprite_X_Position,x',' lda #7',' sta Sprite_Y_Position,x',
                    f' lda #{attr&0xf3}',' sta Sprite_Attributes,x',f' lda #{tile}',' sta Sprite_Tilenumber,x',
                    ' inx',' inx',' inx',' inx']
            body += [' clv',' txa',' ldy GuestOamRotationActive',f' beq Save{i}',' sec',' sbc RgOamRotation',f'Save{i}:',
                ' sta CurrentOAMOffset',' ldy #0',' ora #0',' sec',' BankPRGC #.bank(TnWorldArtStart)',' rts',
                f'Legacy{i}:',' jmp TnWorldDraw']
        body += ['.endproc','.assert TnExactIconRender=$b700,lderror,"Only declared new A87 tail"',
            '.assert *<=$c000,lderror,"Keep fixed bank layout"','.export TnExactIconRender','.popseg','']
        (s/'src/tmnt_equipment_icon_fast.s').write_text('\n'.join(body))
        changes=['src/tmnt_equipment_draw.s','src/tmnt.s','src/tmnt_equipment_icon_fast.s','smb1base-mmc5-expanded.cfg']
    target.write_text(text)
    cmd=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(cmd,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-5000:]
    prep_path=a.parent/'preparation.json'
    if prep_path.exists():
        inherited=json.loads(prep_path.read_text());inherited['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
        (a.output/'preparation.json').write_text(json.dumps(inherited,indent=2)+'\n')
    new=load(a.output/'candidate.nes');before=old['raw'];after=new['raw'];bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    delta={n:sum(x!=y for x,y in zip(bank(before,n),bank(after,n)))for n in range(128)};delta={n:v for n,v in delta.items()if v}
    assert set(delta)=={87}and before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert qualified(a.parent/'candidate.nes').items()<=qualified(a.output/'candidate.nes').items()
    if a.stage=='icons':assert bank(before,87)[0x1500:0x1700]==bank(after,87)[0x1500:0x1700]
    manifest={};patch=''
    for n in changes:
        p=a.parent/'source'/n;q=s/n;manifest[n]=dict(before_sha256=sha(p)if p.exists()else None,after_sha256=sha(q))
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True)if p.exists()else[],q.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch)
    q=dict(prepared=True,source_only=True,native_run=False,accepted=False,stage=a.stage,parent_ROM_sha256=sha(a.parent/'candidate.nes'),
        candidate_ROM_sha256=sha(a.output/'candidate.nes'),changed_PRG_bytes=delta,all_old_qualified_symbols_exact=True,
        original_icon_record_bindings=records,source_changes=manifest,checker_sha256=sha(Path(__file__)))
    (a.output/'fast-preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
