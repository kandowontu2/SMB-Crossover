"""Six exact two-layer shuriken records; original caller clipping fallback."""
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

PARENT='4c591d1420e84989f0c56579224f39ce79bebe4ec09fb25c843f7fa75ceb33ee'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['parent','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert sha(a.parent/'candidate.nes')==PARENT
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    old=load(a.parent/'candidate.nes');end=address(old,'TnExactIconRender')+int(old['syms']['TnExactIconRender']['size'],0)
    assert old['raw'][16+87*8192+end-0xa000:16+88*8192]==bytes([255])*(0xc000-end)
    a.output.mkdir(parents=True);s=a.output/'source';shutil.copytree(a.parent/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    p=s/'src/tmnt_equipment_draw.s';text=p.read_text();start=text.index('ShotPointer:');stop=text.index('NextShot:',start)
    block=text[start:stop];assert block.count('jsr TnWorldDraw')==1
    p.write_text(text[:start]+block.replace('jsr TnWorldDraw','jsr TnExactShurikenRender')+text[stop:])
    p=s/'src/tmnt.s';text=p.read_text();anchor='.include "tmnt_equipment_icon_fast.s"';assert text.count(anchor)==1
    p.write_text(text.replace(anchor,anchor+'\n.include "tmnt_equipment_shuriken_fast.s"'))
    rows=[];base=16+88*8192-0xc000
    for face in['R','L']:
        lo=location(old,'TnWorld'+face+'Lo');hi=location(old,'TnWorld'+face+'Hi')
        for pose in range(73,76):
            ptr=old['raw'][lo+pose]+256*old['raw'][hi+pose];pos=base+ptr;assert old['raw'][pos]==8
            parts=[list(old['raw'][pos+j:pos+j+4])for j in[1,5]];assert all(v[2:]==[248,252]for v in parts)
            rows.append(dict(face=face,pose=pose,pointer=ptr,parts=parts))
    body=['; Private source ShotPointer caller sets attr0/page1 and restores C88.',
        '; Exact original two palette layers; all unknown/edge/capacity paths legacy.',
        '.pushseg','.segment "TN_EQUIP_FAST"','.proc TnExactShurikenRender',
        ' lda R5',' bne Legacy',' lda R7',' cmp #1',' bne Legacy',
        ' lda R4',' cmp #8',' bcc Legacy',' lda R6',' cmp #24',' bcc Legacy',
        ' lda R3',' bne Legacy',' lda R1',' cmp #$d1',' beq Right',' cmp #$d2',' bne Legacy',' lda R0']
    for i in range(3,6):body += [f' cmp #${rows[i]["pointer"]&255:02x}',f' beq Record{i}Gate']
    body += [' jmp Legacy','Right:',' lda R0']
    for i in range(3):body += [f' cmp #${rows[i]["pointer"]&255:02x}',f' beq Record{i}Gate']
    body += ['Legacy:',' jmp TnWorldDraw']
    for i in range(6):body += [f'Record{i}Gate:',f' jmp Record{i}']
    for i,row in enumerate(rows):
        body += [f'Record{i}:',' ldx CurrentOAMOffset',' lda #8',' clc',' adc CurrentOAMOffset',' bcc :+',' jmp TnWorldDraw',':',
            ' lda GuestOamRotationActive',f' beq Draw{i}',' txa',' clc',' adc RgOamRotation',' tax',f'Draw{i}:']
        for tile,attr,y,x in reversed(row['parts']):
            body += [' lda R4',' sec',' sbc #4',' sta Sprite_X_Position,x',
                ' lda R6',' sec',' sbc #8',' sta Sprite_Y_Position,x',f' lda #{attr&0xf3}',' sta Sprite_Attributes,x',
                f' lda #{tile}',' sta Sprite_Tilenumber,x',' inx',' inx',' inx',' inx']
        body += [' clv',' txa',' ldy GuestOamRotationActive',f' beq Save{i}',' sec',' sbc RgOamRotation',f'Save{i}:',
            ' sta CurrentOAMOffset',' ldy #0',' sec',' BankPRGC #.bank(TnWorldArtStart)',' rts']
    body += ['.endproc',f'.assert TnExactShurikenRender=${end:04x},lderror,"Append only verified A87 tail"',
        '.assert *<=$c000,lderror,"Keep fixed layout"','.export TnExactShurikenRender','.popseg','']
    (s/'src/tmnt_equipment_shuriken_fast.s').write_text('\n'.join(body))
    cmd=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(cmd,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-4000:]
    new=load(a.output/'candidate.nes');before=old['raw'];after=new['raw'];bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    delta={n:sum(x!=y for x,y in zip(bank(before,n),bank(after,n)))for n in range(128)};delta={n:v for n,v in delta.items()if v}
    assert set(delta)=={87}and before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert qualified(a.parent/'candidate.nes').items()<=qualified(a.output/'candidate.nes').items()
    assert bank(before,87)[0x1500:0x1700]==bank(after,87)[0x1500:0x1700]
    prep=json.loads((a.parent/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
    (a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n');manifest={};patch=''
    for n in['src/tmnt_equipment_draw.s','src/tmnt.s','src/tmnt_equipment_shuriken_fast.s']:
        p=a.parent/'source'/n;q=s/n;manifest[n]=dict(before_sha256=sha(p)if p.exists()else None,after_sha256=sha(q))
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True)if p.exists()else[],q.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch)
    q=dict(prepared=True,stage='shuriken',source_only=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,
        candidate_ROM_sha256=sha(a.output/'candidate.nes'),changed_PRG_bytes=delta,all_old_qualified_symbols_exact=True,
        literal_original_fallback=True,original_record_bindings=rows,new_helper_PC=end,source_changes=manifest,checker_sha256=sha(Path(__file__)))
    (a.output/'fast-preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
