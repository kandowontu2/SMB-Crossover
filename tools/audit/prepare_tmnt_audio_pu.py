"""Three-way restage the held native soundtrack onto the accepted PS source."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from workspace_storage import locate
OC=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-oc')
GAME=['audio/tmnt/native-drum.dmc','src/tmnt_audio_samus_cold.s','src/tmnt_audio.s',
 'src/tmnt_audio_resident.s','src/tmnt_audio_writers.s','src/tmnt-native.inc',
 'src/entrypoint.s','src/samus_audio.s','src/gradius_audio.s','src/guest_audio.s',
 'src/music_drivers/audio.s','src/player.s','src/metasprite_engine.s','smb1base-mmc5-expanded.cfg']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(data):return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT.resolve());a.output.mkdir(parents=True,exist_ok=False)
    parent=ROOT/'build/checkpoints/contact-pause-ps';pm=json.loads((parent/'manifest.json').read_text())
    assert sha(parent/'candidate.nes')==pm['rom_sha256']=='646baef6cbcbe9ebc3c0a57c182592b3e777970c13b9c89eda6765f446915bb6'
    assert sha(parent/'source.zip')==pm['source_zip_sha256']
    old=ROOT/'build/checkpoints/tmnt-world-render-oa';om=json.loads(locate(old/'manifest.json').read_text());oz=locate(old/'source.zip')
    assert sha(oz)==om['source_zip_sha256'] and om['rom_sha256']=='06908a38ac7c658c40f6c064b82e71f84ecc0b5f4617ed8b9a17fba6ad677701'
    staged=OC/'candidate-v7';work=json.loads((OC/'work-packet-v1/manifest.json').read_text())
    assert sha(staged/'candidate.nes')==work['ROM_sha256']=='dde53bc1bdb02489230dcd561b96496d1551cdc2b0b684c98cede6d3ca5c3fff'
    source=a.output/'source'
    with zipfile.ZipFile(parent/'source.zip')as z:
        assert z.testzip()is None and all((source/n).resolve().is_relative_to(source.resolve())for n in z.namelist());z.extractall(source)
    assert all(sha(source/n)==h for n,h in pm['source_files'].items())
    changes={};conflicts=[];resolved=[];merges=a.output/'merges';merges.mkdir()
    with zipfile.ZipFile(oz)as z:
        for name in GAME:
            upstream=(staged/'source'/name).read_bytes();assert digest(upstream)==work['source_files'][name],name
            base=z.read(name)if name in z.namelist()else None
            target=source/name;ours=target.read_bytes()if target.exists()else None
            if base is None:
                assert ours in [None,upstream],name;merged=upstream;mode='new'
            elif ours==base:merged=upstream;mode='unchanged-parent'
            elif upstream==base:merged=ours;mode='retain-current'
            elif ours==upstream:merged=ours;mode='identical'
            else:
                assert ours is not None and b'\0'not in ours+base+upstream,name
                directory=merges/name.replace('/','_');directory.mkdir()
                for n,data in [('ours',ours),('base',base),('upstream',upstream)]:(directory/n).write_bytes(data)
                result=subprocess.run(['git','merge-file','-p',str(directory/'ours'),str(directory/'base'),str(directory/'upstream')],capture_output=True)
                assert result.returncode in [0,1],result.stderr.decode(errors='replace')
                merged=result.stdout;mode='three-way'
                if result.returncode:
                    (directory/'conflict').write_bytes(merged)
                    if name=='src/player.s':
                        text=merged.decode();start=text.index('<<<<<<< ');end=text.index('\n',text.index('>>>>>>> ',start))+1
                        block=text[start:end].replace('\r\n','\n');ours_text=block.split('\n',1)[1].split('=======\n')[0]
                        theirs=block.split('=======\n')[1].split('>>>>>>> ')[0]
                        assert ours_text=='    farcall HotPlayerGraphics\n'
                        assert theirs=='::TnFastGraphicsSpan:\n    jsr TnFastGraphicsGate\n    jmp TnFastGraphicsResume\n    .res 12,$ea\n::TnFastGraphicsResume:\n'
                        ending='\r\n'if '\r\n'in text else '\n'
                        merged=(text[:start]+theirs.replace('\n',ending)+text[end:]).encode();resolved.append(name)
                    else:conflicts.append(name)
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(merged)
            changes[name]=dict(before=digest(ours)if ours is not None else None,after=sha(target),merge=mode)
    if 'src/player.s'in resolved:
        target=source/'src/tmnt_audio_resident.s';v=target.read_text();old='farcall RlGraphicsDispatch,jmp'
        assert v.count(old)==1;target.write_text(v.replace(old,'farcall HotPlayerGraphics,jmp'))
        changes['src/tmnt_audio_resident.s']['after']=sha(target)
    report=dict(prepared=False,accepted=False,goal_complete=False,parent_ROM_sha256=pm['rom_sha256'],held_ROM_sha256=work['ROM_sha256'],
      parent_source_sha256=sha(parent/'source.zip'),held_source_sha256=sha(OC/'work-packet-v1/source.zip'),changes=changes,conflicts=conflicts,resolved_with_current_render_target=resolved)
    (a.output/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    if conflicts:print(json.dumps(dict(conflicts=conflicts)),flush=True);return 1
    args=[sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
      '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(args,cwd=source,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-2500:]
    report.update(prepared=True,ROM_sha256=sha(a.output/'candidate.nes'));(a.output/'preparation.json').write_text(json.dumps(report,indent=2)+'\n');print(report['ROM_sha256'],flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
