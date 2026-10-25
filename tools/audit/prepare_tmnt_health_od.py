"""Stage an exact four-cell health renderer on the frozen native-audio work."""
from pathlib import Path
import argparse
import hashlib
import gzip
import json
import re
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
PARENT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-oc/work-packet-v1')
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-render-od')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True)
    p.add_argument('--base',choices=['oa','oc'],default='oc')
    p.add_argument('--native-duration',action='store_true');p.add_argument('--body-render',action='store_true')
    p.add_argument('--movement-gate',action='store_true');a=p.parse_args()
    assert a.base=='oc' or not(a.native_duration or a.body_render)
    parent=PARENT if a.base=='oc' else ROOT/'build/checkpoints/tmnt-world-render-oa'
    parent_path=parent/('roundtrip.nes'if a.base=='oc'else'candidate.nes')
    assert a.label and all(c.isalnum()or c in '-_'for c in a.label)
    out=OUT/a.label;out.mkdir(parents=True,exist_ok=False);m=json.loads((parent/'manifest.json').read_text())
    parent_hash=m.get('ROM_sha256',m.get('rom_sha256'));assert parent_hash==sha(parent_path)
    assert parent_hash==('dde53bc1bdb02489230dcd561b96496d1551cdc2b0b684c98cede6d3ca5c3fff'if a.base=='oc'else'06908a38ac7c658c40f6c064b82e71f84ecc0b5f4617ed8b9a17fba6ad677701')
    assert sha(parent/'source.zip')==m['source_zip_sha256'];source=out/'source'
    with zipfile.ZipFile(parent/'source.zip')as z:
        assert z.testzip()is None
        assert all((source/n).resolve().is_relative_to(source.resolve())for n in z.namelist());z.extractall(source)
    assert all(sha(source/n)==h for n,h in m['source_files'].items())
    changed={}
    for name,old,new in [
        ('src/tmnt.s','.include "tmnt_fast_render.s"\n','.include "tmnt_fast_render.s"\n.include "tmnt_health_render.s"\n'),
        ('src/tmnt_draw.s',' lda #7\n sta R6\n jsr Draw\nDone:\n',' lda #7\n sta R6\n::TnHealthDrawCall:\n jsr TnHealthRender\nDone:\n')]:
        p=source/name;text=p.read_text();assert text.count(old)==1,name
        before=sha(p);p.write_text(text.replace(old,new));changed[name]=dict(before=before,after=sha(p))
    p=source/'src/tmnt_health_render.s';assert not p.exists();p.write_text((ROOT/'tools/reference/tmnt_health_render_od.s').read_text())
    changed['src/tmnt_health_render.s']=dict(before=None,after=sha(p))
    p=source/'src/inventory.s';text=p.read_text()
    old='  farcall RlSupportedDispatch,jmp\n  .res 28,$ea\n'
    assert text.count(old)==1
    before=sha(p);p.write_text(text.replace(old,(ROOT/'tools/reference/inventory_supported_od.s').read_text()))
    changed['src/inventory.s']=dict(before=before,after=sha(p))
    p=source/'src/x5_bounce.s';text=p.read_text();old='  farcall RlUiDispatch,jmp\n'
    assert text.count(old)==1;before=sha(p)
    text=text.replace(old,'::X5OwnUiCall:\n  jmp X5OwnInventoryUi\n  .res 15,$ea\n')
    text+='\n'+(ROOT/'tools/reference/own_inventory_ui_od.s').read_text()
    p.write_text(text);changed['src/x5_bounce.s']=dict(before=before,after=sha(p))
    # Decode the parent's actual immutable31-entry facing tables. Do not
    # substitute hand-redrawn weapon shapes or change their pixel/OAM data.
    dbg=(parent/'roundtrip.dbg').read_text()if a.base=='oc' else gzip.decompress((parent/'candidate.dbg.gz').read_bytes()).decode();syms={};segs={}
    for line in dbg.splitlines():
        if not line.startswith(('sym\t','seg\t')):continue
        q=dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if '='in x)
        if line.startswith('seg\t'):segs[q['id']]=q
        elif 'val'in q:syms[q['name'].strip('"')]=q
    def loc(name):
        q=syms[name];s=segs[q['seg']]
        return int(s['ooffs'],0)+int(q['val'],0)-int(s['start'],0)
    parent_rom=parent_path.read_bytes();ptrs=[];records={}
    for face in ['R','L']:
        lo,hi=loc('TnWeapon'+face+'Lo'),loc('TnWeapon'+face+'Hi');assert hi-lo==31
        for i in range(31):
            ptr=parent_rom[lo+i]|parent_rom[hi+i]<<8;pos=16+88*8192+ptr-0xc000;n=parent_rom[pos]
            assert n%4==0 and n<=16
            parts=[list(parent_rom[pos+j:pos+j+4])for j in range(1,n+1,4)]
            for t,at,y,x in parts:
                assert -20<=(x-256 if x&128 else x)<=12 and -24<=(y-256 if y&128 else y)<=8
            ptrs.append(ptr);records[ptr]=parts
        ptrs.append(ptrs[-31]) # Unused index31/63; X>=31 falls back before lookup.
    lines=['; Baked from the pinned parent TMNT weapon descriptors.']
    for label,values in [('TnPrimaryPtrLo',[f'<${p:04x}'for p in ptrs]),('TnPrimaryPtrHi',[f'>${p:04x}'for p in ptrs]),
                         ('TnPrimaryCodeLo',[f'<(TnPrimary{p:04x}-1)'for p in ptrs]),('TnPrimaryCodeHi',[f'>(TnPrimary{p:04x}-1)'for p in ptrs])]:
        lines.extend([label+':',' .byte '+','.join(values)])
    for ptr,parts in records.items():
        lines.append(f'TnPrimary{ptr:04x}:')
        for t,at,y,x in reversed(parts):
            lines.extend([f' lda #${x:02x}',' clc',' adc R4',' sta Sprite_X_Position,x',f' lda #${y:02x}',' clc',' adc R6',' sta Sprite_Y_Position,x',
                          f' lda #${at&0xf3:02x}',' sta Sprite_Attributes,x',f' lda #${t:02x}',' sta Sprite_Tilenumber,x',' inx',' inx',' inx',' inx'])
        lines.append(' jmp TnPrimaryReturn')
    lines.extend(['TnPrimaryReturn:',' clv',' txa',' ldy GuestOamRotationActive',' beq TnPrimarySave',' sec',' sbc RgOamRotation',
                  'TnPrimarySave:',' sta CurrentOAMOffset',' ldy #0',' ora #0',' sec',' rts'])
    p=source/'src/tmnt_primary_records.inc';assert not p.exists();p.write_text('\n'.join(lines)+'\n')
    changed['src/tmnt_primary_records.inc']=dict(before=None,after=sha(p))
    p=source/'src/tmnt_primary_render.s';assert not p.exists();p.write_text((ROOT/'tools/reference/tmnt_primary_render_od.s').read_text())
    changed['src/tmnt_primary_render.s']=dict(before=None,after=sha(p))
    for name,old,new in [('src/tmnt.s','.include "tmnt_health_render.s"\n','.include "tmnt_health_render.s"\n.include "tmnt_primary_render.s"\n'),
                         ('src/tmnt_draw.s',' sta R6\n jsr Draw\nHealth:\n',' sta R6\n::TnPrimaryDrawCall:\n jsr TnPrimaryRender\nHealth:\n')]:
        p=source/name;text=p.read_text();assert text.count(old)==1
        p.write_text(text.replace(old,new));changed[name]['after']=sha(p)
    if a.native_duration:
        # Prove no original branch/call or known pointer enters the replaced
        # duration block midway. Shared entry8C75 has an external caller8CFB;
        # keep it as the patch entry, and keep the bytecode reader8C71 intact.
        p=source/'src/tmnt-native.inc';text=p.read_text();nsf=ROOT/'reference/new-roster-audio/tmnt/Teenage Mutant Ninja Turtles [Gekikame Ninja Den] (1989-05-12)(Konami).nsf'
        raw=nsf.read_bytes();assert hashlib.sha256(raw).hexdigest()=='f220e8d069e321f392526d41e46f5d0f72966d5a22e56d2b269607c678bd58d9'
        def rb(pc):return raw[128+pc-0x8000]
        for pc in map(lambda s:int(s,16),re.findall(r'Original instruction offset ([0-9a-f]{4})',text)):
            op=rb(pc);target=None
            if op in [0x20,0x4c]:target=rb(pc+1)|rb(pc+2)<<8
            elif op in [0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0]:target=(pc+2+(rb(pc+1)-256 if rb(pc+1)&128 else rb(pc+1)))&65535
            if target is not None and not 0x8c75<=pc<0x8c89:assert not 0x8c75<target<0x8c89,(hex(pc),hex(target))
        coverage=json.loads((ROOT/'reference/new-roster-audio/tmnt/coverage-ob.json').read_text())if(ROOT/'reference/new-roster-audio/tmnt/coverage-ob.json').exists()else json.loads(Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob/probe-v2/coverage.json').read_text())
        for word in list(coverage['pointer_words'])+[0x9014]:assert not 0x8c75<(rb(word)|rb(word+1)<<8)<0x8c89
        start=text.index('  .assert *=$ac75,lderror,"Original instruction offset 8c75"')
        end=text.index('  .assert *=$ac89,lderror,"Original instruction offset 8c89"')
        before=sha(p);p.write_text(text[:start]+'  .assert *=$ac75,lderror,"Original shared duration entry8C75"\n  jsr ::TnNativeDuration\n  jmp $ac89\n  .res 14,$ea\n'+text[end:])
        changed['src/tmnt-native.inc']=dict(before=before,after=sha(p))
        p=source/'src/tmnt_duration.s';assert not p.exists();p.write_text((ROOT/'tools/reference/tmnt_duration_od.s').read_text())
        changed['src/tmnt_duration.s']=dict(before=None,after=sha(p))
        p=source/'src/entrypoint.s';text=p.read_text();old='.include "tmnt_audio.s"\n';assert text.count(old)==1;before=sha(p)
        p.write_text(text.replace(old,old+'.include "tmnt_duration.s"\n'));changed['src/entrypoint.s']=dict(before=before,after=sha(p))
    if a.body_render:
        p=source/'src/tmnt_body_render.s';assert not p.exists();p.write_text((ROOT/'tools/reference/tmnt_body_render_od.s').read_text())
        changed['src/tmnt_body_render.s']=dict(before=None,after=sha(p))
        p=source/'src/tmnt.s';text=p.read_text();p.write_text(text+'\n.include "tmnt_body_render.s"\n');changed['src/tmnt.s']['after']=sha(p)
        p=source/'src/tmnt_audio_resident.s';before=sha(p)
        text=p.read_text()+'''
    ::TnBodyGate:
     php
     pha
     lda a:SelectedCharacter
     cmp #19
     bne TnBodyLegacy
     lda a:CurrentBankC
     cmp #$d8
     bne TnBodyLegacy
     pla
     plp
     jmp TnBodyRender
    ::TnBodyLegacy:
     pla
     plp
     jmp MetaspriteRenderLoop
    .export TnBodyGate
    '''
        p.write_text(text);changed['src/tmnt_audio_resident.s']=dict(before=before,after=sha(p))
        p=source/'src/native_goomba_draw.s';text=p.read_text();old='Slow:\n  jmp MetaspriteRenderLoop\n';assert text.count(old)==1;before=sha(p)
        p.write_text(text.replace(old,'Slow:\n::TnBodyFallbackCall:\n  jmp TnBodyGate\n'));changed['src/native_goomba_draw.s']=dict(before=before,after=sha(p))
    if a.movement_gate:
        p=source/'src/x5_bounce.s';text=p.read_text();old='  farcall LmMovementGate\n';assert text.count(old)==1
        text=text.replace(old,'::X5OwnMovementCall:\n  jsr X5OwnMovement\n  .res 15,$ea\n')
        p.write_text(text+'\n'+(ROOT/'tools/reference/own_movement_od.s').read_text());changed['src/x5_bounce.s']['after']=sha(p)
    z=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=source,capture_output=True,text=True)
    (out/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2000:]
    old=parent_path.read_bytes();new=(out/'candidate.nes').read_bytes()
    banks=[b for b in range(128)if old[16+b*8192:16+(b+1)*8192]!=new[16+b*8192:16+(b+1)*8192]]
    expected_banks=sorted([59,86,89]+([123]if a.native_duration else[])+([4,88,127]if a.body_render else[]))
    assert banks==expected_banks,banks;assert old[16+1048576:]==new[16+1048576:]
    q=dict(passed=True,ROM_sha256=sha(out/'candidate.nes'),parent_ROM_sha256=parent_hash,
           source_changes=changed,changed_PRG_banks=banks,CHR_unchanged=True,live_source_unchanged=True,
           scope='Staged renderer optimization; linked ABI/ordered stores, native performance, replay, item and interrupt acceptance pending. Native-music performance remains unaccepted until measured clean.')
    (out/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
