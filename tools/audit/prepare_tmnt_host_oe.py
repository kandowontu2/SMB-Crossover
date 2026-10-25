"""Build a private exact-record world renderer from the verified OD source ZIP."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'build/checkpoints/tmnt-host-render-od'
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-host-oe')
POSES=[60,61,62,63,72,73,74,75,76,80,81,82,83]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);a=p.parse_args()
    assert a.label and all(c.isalnum()or c in '-_'for c in a.label)
    out=OUT/a.label;out.mkdir(parents=True,exist_ok=False);m=json.loads((PARENT/'manifest.json').read_text())
    assert m['rom_sha256']=='89d8b2002ad0f471e1d4a782d52b681e5f641cba7843ba5f2eb019841b8cdf72'
    assert sha(PARENT/'source.zip')==m['source_zip_sha256'];source=out/'source'
    with zipfile.ZipFile(PARENT/'source.zip')as z:
        assert z.testzip()is None
        assert all((source/n).resolve().is_relative_to(source.resolve())for n in z.namelist());z.extractall(source)
    assert all(sha(source/n)==h for n,h in m['source_files'].items())
    syms={};segs={}
    for line in gzip.decompress((PARENT/'candidate.dbg.gz').read_bytes()).decode().splitlines():
        if not line.startswith(('sym\t','seg\t')):continue
        q=dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if '='in x)
        if line.startswith('seg\t'):segs[q['id']]=q
        elif 'val'in q:syms[q['name'].strip('"')]=q
    def loc(name):
        q=syms[name];s=segs[q['seg']]
        return int(s['ooffs'],0)+int(q['val'],0)-int(s['start'],0)
    raw=(PARENT/'candidate.nes').read_bytes();records={};hashes={}
    for face in ['R','L']:
        lo,hi=loc('TnWorld'+face+'Lo'),loc('TnWorld'+face+'Hi')
        for pose in POSES:
            ptr=raw[lo+pose]|raw[hi+pose]<<8;at=16+88*8192+ptr-0xc000;n=raw[at]
            assert n in [8,16] and 0xd1<=ptr>>8<=0xd3
            parts=[list(raw[at+j:at+j+4])for j in range(1,n+1,4)]
            for t,attr,y,x in parts:
                assert -8<=(x-256 if x&128 else x)<=0 and -24<=(y-256 if y&128 else y)<=0
                assert attr&32==0
            key=(ptr&255)^((ptr>>8<<2)&255);assert key not in hashes
            hashes[key]=ptr;records[ptr]=parts
    assert len(records)==26
    lines=['; Generated directly from all26 immutable source world descriptors.']
    for name,values in [
        ('TnWorldExpectedHigh',[f'${hashes[i]>>8:02x}'if i in hashes else'0'for i in range(256)]),
        ('TnWorldCodeLo',[f'<(TnWorldBaked{hashes[i]:04x}-1)'if i in hashes else'0'for i in range(256)]),
        ('TnWorldCodeHi',[f'>(TnWorldBaked{hashes[i]:04x}-1)'if i in hashes else'0'for i in range(256)])]:
        lines.extend([name+':',' .byte '+','.join(values)])
    for ptr,parts in records.items():
        lines.append(f'TnWorldBaked{ptr:04x}:')
        for tile,attr,y,x in reversed(parts):
            for offset,origin,target in [(x,'R4','Sprite_X_Position'),(y,'R6','Sprite_Y_Position')]:
                lines.append(' lda '+origin)
                if offset:lines.extend([' clc',f' adc #${offset:02x}'])
                lines.append(' sta '+target+',x')
            lines.extend([' lda R3',f' ora #${attr:02x}',' and #$f3',' sta Sprite_Attributes,x',
                          f' lda #${tile:02x}',' sta Sprite_Tilenumber,x',' inx',' inx',' inx',' inx'])
        lines.append(' jmp TnWorldBakedReturn')
    lines.extend(['TnWorldBakedReturn:',' clv',' txa',' ldy GuestOamRotationActive',' beq TnWorldBakedSave',
                  ' sec',' sbc RgOamRotation','TnWorldBakedSave:',' sta CurrentOAMOffset',' ldy #0',' sec',' rts'])
    changed={}
    for name,text in [('src/tmnt_world_baked_render.s',(ROOT/'tools/reference/tmnt_world_baked_oe.s').read_text()),
                      ('src/tmnt_world_baked_records.inc','\n'.join(lines)+'\n')]:
        p=source/name;assert not p.exists();p.write_text(text);changed[name]=dict(before=None,after=sha(p))
    p=source/'src/tmnt.s';before=sha(p);p.write_text(p.read_text()+'\n.include "tmnt_world_baked_render.s"\n')
    changed['src/tmnt.s']=dict(before=before,after=sha(p))
    p=source/'src/tmnt_equipment_draw.s';text=p.read_text();old=' jsr TnFastWorldRender\n jmp CallEnd\n';assert text.count(old)==1
    before=sha(p);p.write_text(text.replace(old,'::TnWorldBakedCall:\n jsr TnWorldBakedRender\n jmp CallEnd\n'))
    changed['src/tmnt_equipment_draw.s']=dict(before=before,after=sha(p))
    z=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=source,capture_output=True,text=True)
    (out/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2000:]
    new=(out/'candidate.nes').read_bytes();banks=[b for b in range(128)if raw[16+b*8192:16+(b+1)*8192]!=new[16+b*8192:16+(b+1)*8192]]
    assert banks==[87],banks;assert raw[16+1048576:]==new[16+1048576:]
    q=dict(passed=True,ROM_sha256=sha(out/'candidate.nes'),parent_ROM_sha256=m['rom_sha256'],source_changes=changed,
           changed_PRG_banks=banks,CHR_unchanged=True,records=len(records),parts=sum(len(v)for v in records.values()),
           live_source_unchanged=True,scope='Staged exact-record world renderer; ABI, interruption, native timing, physical items and route acceptance remain required.')
    (out/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
