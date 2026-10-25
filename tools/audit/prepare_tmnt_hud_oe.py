"""Stage only exact source HUD icon admission, preserving every other draw path."""
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


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--probe-gates',action='store_true')
    p.add_argument('--mac-visibility',action='store_true');a=p.parse_args();assert not a.mac_visibility or a.probe_gates
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
    raw=(PARENT/'candidate.nes').read_bytes();high={};records=[]
    for face in ['R','L']:
        lo,hi=loc('TnWorld'+face+'Lo'),loc('TnWorld'+face+'Hi')
        for pose in [80,81,82,83]:
            ptr=raw[lo+pose]|raw[hi+pose]<<8;at=16+88*8192+ptr-0xc000
            assert raw[at]==16 and ptr&255 not in high
            parts=[list(raw[at+j:at+j+4])for j in range(1,17,4)]
            assert all(y==240 and x in [0,248]and attr&32==0 for tile,attr,y,x in parts)
            high[ptr&255]=ptr>>8;records.append(dict(face=face,pose=pose,pointer=ptr,parts=parts))
    lines=['; Eight original four-part HUD records; all other entries reject.','TnHudWorldHigh:',
           ' .byte '+','.join(f'${high[i]:02x}'if i in high else'0'for i in range(256))]
    changed={}
    for name,text in [('src/tmnt_hud_world.s',(ROOT/'tools/reference/tmnt_hud_world_oe.s').read_text()),
                      ('src/tmnt_hud_world_high.inc','\n'.join(lines)+'\n')]:
        p=source/name;assert not p.exists();p.write_text(text);changed[name]=dict(before=None,after=sha(p))
    p=source/'src/tmnt.s';before=sha(p);p.write_text(p.read_text()+'\n.include "tmnt_hud_world.s"\n')
    changed['src/tmnt.s']=dict(before=before,after=sha(p))
    p=source/'src/tmnt_fast_render.s';text=p.read_text();old=' lda R6\n cmp #24\n bcc Legacy\n';assert text.count(old)==1
    before=sha(p);p.write_text(text.replace(old,' lda R6\n cmp #24\n::TnHudWorldBranch:\n bcc TnHudWorldRender\n'))
    changed['src/tmnt_fast_render.s']=dict(before=before,after=sha(p))
    if a.mac_visibility:
        p=source/'src/little_mac_terrain.s';text=p.read_text();old=' jsr BlockBufferColli_Side\n bne Restore\n';assert text.count(old)==1
        before=sha(p);text=text.replace(old,'::LmVisibleSideCall:\n jsr LmVisibleSideProbe\n bne Restore\n')
        lower='Lower:ldy LmSavedY\n jsr BlockBufferColli_Side\n';assert text.count(lower)==1
        text=text.replace(lower,'Lower:ldy LmSavedY\n::LmVisibleLowerCall:\n jsr LmVisibleSideProbe\n');p.write_text(text)
        changed['src/little_mac_terrain.s']=dict(before=before,after=sha(p))
        native_wrapper=(ROOT/'tools/reference/mac_visible_side_oe.s').read_text()
        p=source/'src/mac_visible_side.s';assert not p.exists()
        p.write_text('.pushseg\n.segment "LM_CORE"\n'+native_wrapper.replace('MAC_VISIBLE_NAME','LmVisibleSideProbe')+'.popseg\n')
        changed['src/mac_visible_side.s']=dict(before=None,after=sha(p))
        p=source/'src/entrypoint.s';text=p.read_text();at=text.rfind('\n.endif');assert at>0 and not text[at:].strip()[len('.endif'):].strip()
        before=sha(p);p.write_text(text[:at]+'\n.include "mac_visible_side.s"\n'+text[at:])
        changed['src/entrypoint.s']=dict(before=before,after=sha(p))
    if a.probe_gates:
        # Mac's original native bodies use only resident getters and their
        # existing private RAM. Copy those exact source bodies into this bank
        # so his probes also avoid a redundant bank trip; no mechanics change.
        terrain=(source/'src/little_mac_terrain.s').read_text();bodies=[]
        for oldname,newname,marker in [('LmHeadGate','TnMacHeadProbe',' LmGate JnHeadDispatch\n'),
                                       ('LmSideGate','TnMacSideProbe','Own:pla\n plp\n')]:
            at=terrain.index('.proc '+oldname+'\n');end=terrain.index('.endproc',at);body=terrain[at:end]
            assert body.count(marker)==1;body=body.split(marker,1)[1]
            assert all('BlockBufferColli_'in line or'VisibleSideProbe'in line for line in body.splitlines()if'jsr 'in line)
            assert 'farcall'not in body
            if a.mac_visibility:
                body=body.replace('jsr LmVisibleSideProbe','jsr TnMacVisibleSideProbe').replace('::LmVisibleSideCall:','::TnMacVisibleSideCall:').replace('::LmVisibleLowerCall:','::TnMacVisibleLowerCall:')
            bodies.append('.proc '+newname+'\n'+body+'.endproc\n.export '+newname+'\n')
        if a.mac_visibility:bodies.append(native_wrapper.replace('MAC_VISIBLE_NAME','TnMacVisibleSideProbe'))
        p=source/'src/tmnt_mac_probes.inc';assert not p.exists();p.write_text('; Exact native Little Mac probe bodies, copied without mechanical edits.\n'+''.join(bodies))
        changed['src/tmnt_mac_probes.inc']=dict(before=None,after=sha(p))
        p=source/'src/tmnt_probe_gates.s';assert not p.exists();p.write_text((ROOT/'tools/reference/tmnt_probe_gates_oe.s').read_text())
        changed['src/tmnt_probe_gates.s']=dict(before=None,after=sha(p))
        p=source/'src/tmnt.s';p.write_text(p.read_text()+'\n.include "tmnt_probe_gates.s"\n');changed['src/tmnt.s']['after']=sha(p)
        for name,old,new in [('src/characters.s','  farcall LmSideGate,jmp\n','  farcall TnFastSideGate,jmp\n'),
                             ('src/expanded.s','  farcall LmHeadGate,jmp\n','  farcall TnFastHeadGate,jmp\n')]:
            p=source/name;text=p.read_text();assert text.count(old)==1;before=sha(p);p.write_text(text.replace(old,new))
            changed[name]=dict(before=before,after=sha(p))
    z=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=source,capture_output=True,text=True)
    (out/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2000:]
    new=(out/'candidate.nes').read_bytes();banks=[b for b in range(128)if raw[16+b*8192:16+(b+1)*8192]!=new[16+b*8192:16+(b+1)*8192]]
    expected=[87,89,93,127]if a.mac_visibility else([87,89,127]if a.probe_gates else[87])
    assert banks==expected and raw[16+1048576:]==new[16+1048576:]
    q=dict(passed=True,ROM_sha256=sha(out/'candidate.nes'),parent_ROM_sha256=m['rom_sha256'],source_changes=changed,
           changed_PRG_banks=banks,CHR_unchanged=True,records=records,live_source_unchanged=True,
           scope='Staged HUD-only fast admission for eight source records atY16..23. ABI, native performance, OAM/IRQ/item and route acceptance pending.')
    (out/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='records'},indent=2))


if __name__=='__main__':main()
