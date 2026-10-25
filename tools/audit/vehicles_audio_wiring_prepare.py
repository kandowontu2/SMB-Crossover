"""Restage verified native TMNT music on an exact current frozen baseline."""
from pathlib import Path
import argparse, difflib, hashlib, json, re, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
HELD=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-oc')
EXPECTED='859b51acb503dde2b9f57ef45a6a6d2bc22a98aa726a331897ef0af6cc4ff587'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True)
    a=p.parse_args();out=a.packet.resolve();source=out/'source'
    manifest=json.loads((out/'frozen-source.json').read_text())
    assert sha(out/'baseline.nes')==EXPECTED
    assert all(sha(source/n)==v for n,v in manifest.items())
    command=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
             '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe')]
    subprocess.run(command+['--output',str(out/'rebuilt-baseline.nes')],check=True)
    assert sha(out/'rebuilt-baseline.nes')==EXPECTED
    proof=json.loads((HELD/'work-packet-v1/manifest.json').read_text())
    held=HELD/'candidate-v7/source'
    assert proof['accepted'] is False and proof['ROM_sha256']=='dde53bc1bdb02489230dcd561b96496d1551cdc2b0b684c98cede6d3ca5c3fff'
    before={};dependency={}
    def write(name,text):
        f=source/name;before.setdefault(name,f.read_text()if f.exists()else '')
        f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text)
    def replace(name,old,new):
        text=(source/name).read_text();assert text.count(old)==1,name
        write(name,text.replace(old,new))
    for name in ['src/tmnt_audio.s','src/tmnt_audio_writers.s','src/tmnt-native.inc',
                 'src/tmnt_audio_samus_cold.s','src/tmnt_audio_resident.s','audio/tmnt/native-drum.dmc']:
        f=held/name;assert sha(f)==proof['source_files'][name],name;dependency[name]=sha(f)
        target=source/name;assert not target.exists(),name
        target.parent.mkdir(parents=True,exist_ok=True)
        if name.endswith('.dmc'):
            shutil.copyfile(f,target)
        else:
            text=f.read_text()
            if name.endswith('resident.s'):
                # This task restores music; retain all current foreground hot
                # gates instead of importing historical graphics replacements.
                text=text.split('; Exact-ID foreground admissions')[0]
            write(name,text)
    samus=(source/'src/samus_audio.s').read_text()
    start=samus.index('.proc SamusAudioUpdate\n');end=samus.index('.endproc\n',start)+len('.endproc\n')
    original=samus[start:end]
    cold=(source/'src/tmnt_audio_samus_cold.s').read_text()
    cold_proc=cold[cold.index('.proc SamusAudioCold\n'):cold.index('.endproc\n')+len('.endproc\n')]
    expected_cold=original.replace('.proc SamusAudioUpdate','.proc SamusAudioCold').replace(
        '  jsr CrossoverGraphicsBank\n  pla\n  BankPRGA a\n  rts\n','  jmp SamusAudioFixedReturn\n')
    assert cold_proc==expected_cold,'Do not import an obsolete Metroid adapter'
    held_samus=(held/'src/samus_audio.s').read_text()
    stage_start=held_samus.index('.if ::ENABLE_MMC5_EXPANDED\n.proc SamusAudioUpdate\n')
    stage_end=held_samus.index('.else\n.proc SamusAudioUpdate\n',stage_start)
    replacement=held_samus[stage_start:stage_end]+'.else\n'+original+'.endif\n'
    write('src/samus_audio.s',samus[:start]+replacement+samus[end:])
    replace('src/gradius_audio.s','Legacy:\n  jmp ExpandedAudioTick\n','Legacy:\n  jmp TnAudioDispatch\n')
    replace('src/guest_audio.s','DmcEnded:\n  lda #0\n  sta BassDmcActive\n  sta $4011\nDmcOff:',
        'DmcEnded:\n.if ::ENABLE_MMC5_EXPANDED\n  jmp TnDmcEnded\n  .res 5,$ea\n.else\n  lda #0\n  sta BassDmcActive\n  sta $4011\n.endif\nDmcOff:')
    replace('src/music_drivers/audio.s','.proc AudioInit\n  lda #0\n  sta PauseModeFlag\n',
        '.proc AudioInit\n.if ::ENABLE_MMC5_EXPANDED\n  jsr TnAudioInitGate\n  nop\n  nop\n.else\n  lda #0\n  sta PauseModeFlag\n.endif\n')
    replace('src/music_drivers/audio.s','.proc AudioUpdate\n.if ::ENABLE_CROSSOVER\n  lda OperMode\n',
        '.proc AudioUpdate\n.if ::ENABLE_CROSSOVER\n.if ::ENABLE_MMC5_EXPANDED\n  jsr TnAudioGlobalGate\n.else\n  lda OperMode\n.endif\n')
    # Append to avoid shifting pre-existing contributors or farcall identifiers.
    text=(source/'src/entrypoint.s').read_text()
    write('src/entrypoint.s',text+'\n.if ::ENABLE_MMC5_EXPANDED\n.include "tmnt_audio_samus_cold.s"\n.include "tmnt_audio.s"\n.endif\n')
    cfg=(source/'smb1base-mmc5-expanded.cfg').read_text()
    line=next(v for v in cfg.splitlines(True)if v.strip().startswith('X5_NEW_7B:'))
    replacement='    TN_AUDIO_PREFIX_MEM:start=$a000,size=$002c,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7b;\n    TN_AUDIO_WRITERS_MEM:start=$a02c,size=$05e6,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7b;\n'+line.replace('start=$a000, size=$2000','start=$a612, size=$19ee')
    cfg=cfg.replace(line,replacement)
    for bank in ['7C','7D']:
        line=next(v for v in cfg.splitlines(True)if v.strip().startswith('X5_NEW_'+bank+':'))
        cfg=cfg.replace(line,line.replace('$a000','$c000'))
    cfg=cfg.replace('SEGMENTS {\n','SEGMENTS {\n    TMNT_NATIVE_AUDIO_PREFIX:load=TN_AUDIO_PREFIX_MEM,type=ro;\n    TMNT_NATIVE_AUDIO_WRITERS:load=TN_AUDIO_WRITERS_MEM,type=ro;\n    TMNT_NATIVE_AUDIO_A:load=X5_NEW_7B,type=ro;\n    TMNT_NATIVE_AUDIO_B:load=X5_NEW_7C,type=ro;\n    TMNT_SAMUS_AUDIO_COLD:load=X5_NEW_7D,type=ro;\n',1)
    write('smb1base-mmc5-expanded.cfg',cfg)
    patch=''
    for name,old in before.items():
        new=(source/name).read_text()
        patch+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (out/'implementation.patch').write_text(patch)
    subprocess.run(command+['--output',str(out/'candidate.nes')],check=True)
    sys.path.insert(0,str(ROOT/'tools/audit'))
    from check_tmnt_audio_fallback_oc import qualified
    old,new=(out/'baseline.nes').read_bytes(),(out/'candidate.nes').read_bytes()
    assert old[16+1048576:]==new[16+1048576:]
    oldq,newq=qualified(out/'baseline.nes'),qualified(out/'candidate.nes')
    moved={str(n):[v,newq.get(n)]for n,v in oldq.items()if newq.get(n)!=v}
    assert all(len(n)>1 and n[0]=='SamusAudioUpdate'for n,v in oldq.items()if newq.get(n)!=v),moved
    changed=[bank for bank in range(128)if old[16+bank*8192:16+(bank+1)*8192]!=new[16+bank*8192:16+(bank+1)*8192]]
    assert changed==[38,123,124,125,127],changed
    report=dict(prepared=True,accepted=False,base_ROM_sha256=EXPECTED,ROM_sha256=sha(out/'candidate.nes'),
                changed_PRG_banks=changed,CHR_unchanged=True,new_RAM_allocations=0,
                existing_named_symbols_checked=len(oldq),only_moved_symbols=moved,
                held_dependencies=dependency,held_manifest_sha256=sha(HELD/'work-packet-v1/manifest.json'),
                changes={n:sha(source/n)for n in before}|{'audio/tmnt/native-drum.dmc':sha(source/'audio/tmnt/native-drum.dmc')},
                scope='Private restoration of the previously held verified native TMNT driver; current shared mixer and foreground gates preserved. Current-hash CPU/native/performance qualification pending.')
    (out/'prepare.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k not in ['only_moved_symbols','changes','held_dependencies']},indent=2))


if __name__=='__main__':main()
