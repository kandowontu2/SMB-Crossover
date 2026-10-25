"""Build a separate native-TMNT-audio integration from the verified OB packet."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OB=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-oc')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);a=p.parse_args()
    assert a.label and all(c.isalnum()or c in '-_'for c in a.label)
    out=OUT/a.label;out.mkdir(parents=True,exist_ok=False)
    packet=OB/'work-packet-v1';manifest=json.loads((packet/'manifest.json').read_text())
    assert sha(packet/'space-prerequisite-source.zip')==manifest['source_zip_sha256']
    for n in ['space-v3/CPU-v2/proof.json','driver-v3/golden-v1/proof.json','original-mesen-proof-v1/proof.json']:
        assert json.loads((OB/n).read_text())['passed']
    source=out/'source'
    with zipfile.ZipFile(packet/'space-prerequisite-source.zip')as z:
        assert z.testzip()is None
        assert all((source/n).resolve().is_relative_to(source.resolve())for n in z.namelist());z.extractall(source)
    assert all(sha(source/n)==h for n,h in manifest['source_files'].items())
    changed={}
    def replace(name,old,new):
        p=source/name;before=sha(p);text=p.read_text();assert text.count(old)==1,name
        p.write_text(text.replace(old,new));changed[name]=dict(before=changed.get(name,{}).get('before',before),after=sha(p))
    def create(name,text):
        p=source/name;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        changed[name]=dict(before=None,after=sha(p))
    for name in ['adapter','resident','writers']:
        filename='src/tmnt_audio.s'if name=='adapter'else f'src/tmnt_audio_{name}.s'
        create(filename,(ROOT/f'tools/reference/tmnt_audio_{name}_oc.s').read_text())
    driver=(OB/'driver-v3/tmnt-native.inc').read_text()
    assert sha(OB/'driver-v3/raw-test.bin')==manifest['source_engine_raw_binary_sha256']
    old='.segment "TMNT_NATIVE_AUDIO_A"\nTnNativeImageStart:';assert driver.count(old)==1
    driver=driver.replace(old,'.segment "TMNT_NATIVE_AUDIO_PREFIX"\nTnNativeImageStart:')
    old='  .res $5e6,$ff\nTnNativeSourceBegin:';assert driver.count(old)==1
    driver=driver.replace(old,'.segment "TMNT_NATIVE_AUDIO_A"\nTnNativeSourceBegin:')
    # Only instruction operands are changed. Immediate constants and data bytes
    # are never matched. The driver's per-instruction location assertions retain
    # every original addressing width and branch/ROM-pointer location.
    zero_page=[]
    def zp_operand(m):
        op,prefix,value,suffix=m.groups();offset=int(value,16)-0xe0
        zero_page.append(dict(instruction=m.group(0).strip(),offset=offset))
        return '  '+op+' '+prefix+'::TnAudioZp+$'+f'{offset:02x}'+suffix
    driver=re.sub(r'(?m)^  ([A-Z]{3}) (\(?)\$(00e[0-9a-d]|e[0-9a-d])(\)?(?:,[XY])?)$',zp_operand,driver)
    assert len(zero_page)>100,len(zero_page)
    driver=driver.replace('; CPU page1 channel state moves to owned history; E0..ED remain borrowed ZP.',
        '; CPU page1 channel state moves to owned history; E0..ED map to inactive decoder ZP.')
    create('src/tmnt-native.inc',driver)
    replace('src/entrypoint.s','.include "tmnt_audio_samus_cold.s"\n','.include "tmnt_audio_samus_cold.s"\n.include "tmnt_audio.s"\n')
    replace('src/samus_audio.s','  .res 505,$ea                  ; Preserve the eight-byte resident return.\n',
        'TnResidentBegin:\n.include "tmnt_audio_resident.s"\nTnResidentEnd:\n  .res 505-(TnResidentEnd-TnResidentBegin),$ea\n')
    replace('src/gradius_audio.s','Legacy:\n  jmp ExpandedAudioTick\n','Legacy:\n  jmp TnAudioDispatch\n')
    replace('src/guest_audio.s','DmcEnded:\n  lda #0\n  sta BassDmcActive\n  sta $4011\nDmcOff:',
        'DmcEnded:\n.if ::ENABLE_MMC5_EXPANDED\n  jmp TnDmcEnded\n  .res 5,$ea\n.else\n  lda #0\n  sta BassDmcActive\n  sta $4011\n.endif\nDmcOff:')
    replace('src/music_drivers/audio.s','.proc AudioInit\n  lda #0\n  sta PauseModeFlag\n',
        '.proc AudioInit\n.if ::ENABLE_MMC5_EXPANDED\n  jsr TnAudioInitGate\n  nop\n  nop\n.else\n  lda #0\n  sta PauseModeFlag\n.endif\n')
    replace('src/music_drivers/audio.s','.proc AudioUpdate\n.if ::ENABLE_CROSSOVER\n  lda OperMode\n',
        '.proc AudioUpdate\n.if ::ENABLE_CROSSOVER\n.if ::ENABLE_MMC5_EXPANDED\n  jsr TnAudioGlobalGate\n.else\n  lda OperMode\n.endif\n')
    replace('src/player.s','    farcall RlGraphicsDispatch\n',
        '::TnFastGraphicsSpan:\n    jsr TnFastGraphicsGate\n    jmp TnFastGraphicsResume\n    .res 12,$ea\n::TnFastGraphicsResume:\n')
    replace('src/metasprite_engine.s','  farcall RlSpecialDrawDispatch\n',
        '::TnFastSpecialSpan:\n  jsr TnFastSpecialGate\n  jmp TnFastSpecialResume\n  .res 12,$ea\n::TnFastSpecialResume:\n')
    replace('src/metasprite_engine.s','  jsr KbDrawDispatch\n',
        '::TnFastDrawSpan:\n  jsr TnFastDrawGate\n')
    cfg=source/'smb1base-mmc5-expanded.cfg';text=cfg.read_text()
    line=next(s for s in text.splitlines(True)if s.strip().startswith('X5_NEW_7B:'))
    replacement='    TN_AUDIO_PREFIX_MEM:start=$a000,size=$002c,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7b;\n    TN_AUDIO_WRITERS_MEM:start=$a02c,size=$05e6,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7b;\n'+line.replace('start=$a000, size=$2000','start=$a612, size=$19ee')
    assert replacement!=line;replace('smb1base-mmc5-expanded.cfg',line,replacement)
    line=next(s for s in text.splitlines(True)if s.strip().startswith('X5_NEW_7C:'))
    replace('smb1base-mmc5-expanded.cfg',line,line.replace('$a000','$c000'))
    replace('smb1base-mmc5-expanded.cfg','SEGMENTS {\n','SEGMENTS {\n    TMNT_NATIVE_AUDIO_PREFIX:load=TN_AUDIO_PREFIX_MEM,type=ro;\n    TMNT_NATIVE_AUDIO_WRITERS:load=TN_AUDIO_WRITERS_MEM,type=ro;\n    TMNT_NATIVE_AUDIO_A:load=X5_NEW_7B,type=ro;\n    TMNT_NATIVE_AUDIO_B:load=X5_NEW_7C,type=ro;\n')
    z=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=source,capture_output=True,text=True)
    (out/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2600:]
    old=(ROOT/'build/checkpoints/tmnt-world-render-oa/candidate.nes').read_bytes();new=(out/'candidate.nes').read_bytes()
    banks=[b for b in range(128)if old[16+b*8192:16+(b+1)*8192]!=new[16+b*8192:16+(b+1)*8192]]
    assert banks==[1,4,38,123,124,125,127],banks
    assert old[16+1048576:]==new[16+1048576:]
    q=dict(passed=True,ROM_sha256=sha(out/'candidate.nes'),parent_ROM_sha256=manifest['live_ROM_sha256'],
           prerequisite_ROM_sha256=manifest['prerequisite_ROM_sha256'],source_changes_from_OB_packet=changed,
           changed_PRG_banks=banks,CHR_unchanged=True,scope='Private integrated candidate; exact linked/native source, DMC, ownership, IRQ, performance and gameplay acceptance pending.')
    q['native_zero_page_operand_relocations']=zero_page
    (out/'preparation.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k!='native_zero_page_operand_relocations'},indent=2))


if __name__=='__main__':main()
