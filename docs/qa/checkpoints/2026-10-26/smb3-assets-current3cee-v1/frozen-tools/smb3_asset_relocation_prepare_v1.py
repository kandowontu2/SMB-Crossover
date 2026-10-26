"""Private config-only asset relocation on frozen adopted3cee; no active driver."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
from link_pit_rygar_sophia_audit_cpu import scoped_load

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'root-chip-hud-composed-v1'
SHA='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    assert sha(BASE/'candidate.nes')==SHA
    files=json.loads((BASE/'source-manifest.json').read_text())
    for n,h in files.items():assert sha(BASE/'source'/n)==h,n
    source=out/'source';source.mkdir()
    for n in files:
        target=source/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/'source'/n,target)
    cfg=source/'smb1base-mmc5-expanded.cfg';raw=cfg.read_bytes();nl=b'\r\n'if b'\r\n'in raw else b'\n'
    def edit(a,b):
        nonlocal raw
        a=a.encode();b=b.replace('\n',nl.decode()).encode()
        assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
    edit('X5_NEW_5F: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$5f;',
         'X5_NEW_5F: start=$a000, size=$0340, type=ro, file=%O, fill=yes, fillval=$ff, bank=$5f;\n    SMB3_ASSET_C95: start=$c340, size=$1cc0, type=ro, file=%O, fill=yes, fillval=$ff, bank=$5f;')
    edit('MIKE_GFX:load=X5_NEW_61,type=ro;','MIKE_GFX:load=SMB3_ASSET_C95,type=ro,start=$c6c0;')
    edit('Z2_GFX: load=X5_NEW_46,type=ro,optional=yes;','Z2_GFX: load=SMB3_ASSET_C95,type=ro,start=$c340,optional=yes;')
    edit('BILL_ORBIT_2: load=XG_AUDIO_MEM, type=ro, optional=yes; # Existing C000 FF tail; all prior data fixed.',
         'BILL_ORBIT_2: load=X5_NEW_55, type=ro, start=$cbe8, optional=yes; # Same CPU addresses; real label bank expressions reassemble.')
    edit('VG_AUDIO_DISPATCH:load=XG_AUDIO_MEM,type=ro;','VG_AUDIO_DISPATCH:load=XG_AUDIO_MEM,type=ro,start=$dfe8;')
    cfg.write_bytes(raw)
    newfiles={n:sha(source/n)for n in files};changed=[n for n in files if files[n]!=newfiles[n]]
    assert changed==['smb1base-mmc5-expanded.cfg'],changed
    (out/'source-manifest.json').write_text(json.dumps(newfiles,indent=2)+'\n')
    b=scoped_load(BASE/'candidate.nes')
    def segment(bundle,name):
        q=next(g for g in bundle['segs'].values()if g['name'].strip('"')==name)
        offset=int(q['ooffs'],0);n=int(q['size'],0)
        return dict(name=name,bank=(offset-16)//8192,offset=(offset-16)%8192,CPU=int(q['start'],0),bytes=n,end_exclusive=int(q['start'],0)+n)
    chips=[]
    for name in ['root-chip-native-adapter-v6','chip-hot-control-v5']:
        rom=D/name/'candidate.nes';q=segment(scoped_load(rom),'CHIP_NATIVE_ADAPTER')
        assert(q['bank'],q['CPU'],q['bytes'])==(78,0xa500,409)
        chips.append(dict(ROM=str(rom),sha256=sha(rom),segment=q,debug_sha256=sha(rom.with_suffix('.dbg'))))
    bounce=segment(b,'X5_BOUNCE');assert bounce['bank']==86 and bounce['end_exclusive']==0xa746
    def blank(bank,lo,hi):
        at=16+bank*8192+lo;assert b['raw'][at:at+hi-lo]==bytes([255])*(hi-lo)
        for g in b['segs'].values():
            if 'ooffs'not in g:continue
            start=int(g['ooffs'],0);size=int(g['size'],0)
            assert not size or start+size<=at or start>=at+hi-lo,(bank,lo,hi,g)
    blank(86,0x800,0xa00)
    for bank in [78,86,90,93,95,96,98,118,119]:blank(bank,0x1000,0x2000)
    assert all(q['segment']['end_exclusive']<=0xb000 for q in chips)
    plan=dict(parent_ROM_sha256=SHA,held_Chip_adapters=chips,
              reserved_banks=[62,63,94,99,123,124,125,126,127],
              reservation='Full Chip A78:A500..A698 kept; A62/C94, Tn63/99/124, Mac123, CV3/shared125, resident126/fixed127 excluded.',
              future_cold_pool=dict(bank=86,CPU=0xa800,bytes=512,allocated=False),
              current_bounce=bounce,
              future_intact_payload_pages=[dict(page=i,bank=q,physical_offset=0x1000,bytes=4096,allocated=False)for i,q in enumerate([78,86,90,93,95,96,98,118,119])],
              conflict_resolution='The old A78:A500512B cold proposal conflicts with 409B held Chip adapter. Future pool instead fits86:A800..A9FF after current A745 highwater. Chip stays below raw page B000. No future pools/pages/SMB3 core/samples are installed here.')
    (out/'revised-storage-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    cmd=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--source-overlay',str(source),'--output',str(out/'candidate.nes')]
    run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    (out/'build-command.json').write_text(json.dumps(dict(command=cmd,exit=run.returncode,stdout=run.stdout,stderr=run.stderr),indent=2)+'\n')
    assert run.returncode==0,run.stdout+run.stderr
    new=scoped_load(out/'candidate.nes')
    segments={name:segment(new,name)for name in ['Z2_GFX','MIKE_GFX','BILL_ORBIT_2','VG_AUDIO_DISPATCH','LM_COMBAT','X5_BOUNCE']}
    assert[(segments[n]['bank'],segments[n]['CPU'],segments[n]['bytes'])for n in ['Z2_GFX','MIKE_GFX','BILL_ORBIT_2']]==[(95,0xc340,886),(95,0xc6c0,863),(85,0xcbe8,5120)]
    assert new['raw'][16+128*8192:]==b['raw'][16+128*8192:]
    moved=[];unchanged=0
    for name,s in b['syms'].items():
        if name not in new['syms']:raise AssertionError(('removed',name))
        if 'seg'in s and b['segs'][s['seg']]['name'].strip('"')in ['Z2_GFX','MIKE_GFX']:
            d=0x340 if b['segs'][s['seg']]['name']=='"Z2_GFX"'else 0x6c0
            assert int(new['syms'][name]['val'],0)==int(s['val'],0)+d,name
            moved.append(dict(name=name,old=int(s['val'],0),new=int(new['syms'][name]['val'],0)))
        else:
            assert new['syms'][name]['val']==s['val'],(name,s,new['syms'][name]);unchanged+=1
    changes={}
    for bank in range(128):
        a=16+bank*8192;points=[i for i in range(8192)if b['raw'][a+i]!=new['raw'][a+i]]
        if points:changes[str(bank)]=dict(bytes=len(points),first=min(points),last=max(points))
    proof=dict(passed=True,private=True,native_run=False,active_SMB3_driver=False,
               parent_ROM=str(BASE/'candidate.nes'),parent_ROM_sha256=SHA,ROM=str(out/'candidate.nes'),ROM_sha256=sha(out/'candidate.nes'),
               changed_source=changed,segments=segments,unchanged_qualified_symbols=unchanged,genuine_relocated_data_symbols=moved,
               CHR_exact=True,ROM_changed_banks=changes,source_manifest_sha256=sha(out/'source-manifest.json'),
               revised_storage_plan_sha256=sha(out/'revised-storage-plan.json'),tool_sha256=sha(__file__),
               limits='Build/storage/symbol check only. Renderer/caller/IRQ and ordinary/canonical comparisons remain separate.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in ['passed','ROM_sha256','changed_source','ROM_changed_banks','unchanged_qualified_symbols']},indent=2))

if __name__=='__main__':main()
