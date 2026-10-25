"""Stage source-identical Samus audio relocation to reserve a fixed TMNT drum."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);a=p.parse_args()
    assert a.label and all(c.isalnum()or c in '-_'for c in a.label)
    out=OUT/a.label;out.mkdir(parents=True,exist_ok=False)
    parent=ROOT/'build/checkpoints/tmnt-world-render-oa';m=json.loads((parent/'manifest.json').read_text())
    assert sha(parent/'candidate.nes')==m['rom_sha256']
    src=out/'source'
    with zipfile.ZipFile(parent/'source.zip')as z:
        assert z.testzip()is None
        assert all((src/n).resolve().is_relative_to(src.resolve())for n in z.namelist());z.extractall(src)
    assert all(sha(src/n)==h for n,h in m['source_files'].items())
    changes={}
    def replace(name,old,new):
        p=src/name;before=sha(p);text=p.read_text();assert text.count(old)==1,name
        p.write_text(text.replace(old,new));changes[name]=dict(before=changes.get(name,{}).get('before',before),after=sha(p))
    f=src/'src/samus_audio.s';text=f.read_text();start=text.index('.proc SamusAudioUpdate\n');end=text.index('.endproc',start)+len('.endproc')
    old=text[start:end];tail='  jsr CrossoverGraphicsBank\n  pla\n  BankPRGA a\n  rts\n.endproc'
    assert old.endswith(tail)
    cold=old.replace('.proc SamusAudioUpdate\n','.proc SamusAudioCold\n',1)
    cold=cold[:-len(tail)]+'  jmp SamusAudioFixedReturn\n.endproc'
    fixed='''.if ::ENABLE_MMC5_EXPANDED
.proc SamusAudioUpdate
  ; This code cannot live in A000: its native driver changes the A bank.
  ; C000 stays mapped until the fixed return selects the player art again.
  lda #.bank(SamusAudioCold)|MMC5_PRG_ROM
  sta a:CurrentBankC             ; Explicit size: this RAM symbol is defined later.
  sta MMC5_PRG_BANK_C
  jmp SamusAudioCold
  .res 65,$ea                   ; 11-byte entry; linked location asserted below.
::TnMusicDpcm:
  .incbin "audio/tmnt/native-drum.dmc"
::TnMusicDpcmEnd:
  .assert TnMusicDpcm=$e8c0,lderror,"Pinned aligned fixed drum location"
  .assert TnMusicDpcmEnd-TnMusicDpcm=129,error,"Original NSF DMC length"
  .res 505,$ea                  ; Preserve the eight-byte resident return.
::SamusAudioFixedReturn:
  jsr CrossoverGraphicsBank
  pla
  BankPRGA a
  rts
  .assert *-SamusAudioUpdate=718,error,"Keep all following fixed addresses"
.endproc
.else
'''+old+'\n.endif'
    # Keep the cold contribution last so all previous bank addresses stay put.
    replace('src/samus_audio.s',old,fixed)
    f=src/'src/tmnt_audio_samus_cold.s';assert not f.exists()
    f.write_text('; Relocated unmodified Metroid audio adapter; its bank-switching return stays fixed.\n.pushseg\n.segment "TMNT_SAMUS_AUDIO_COLD"\n'+cold+'\n.export SamusAudioCold\n.popseg\n')
    changes['src/tmnt_audio_samus_cold.s']=dict(before=None,after=sha(f))
    replace('src/entrypoint.s','.include "gradius_audio.s"\n','.include "gradius_audio.s"\n.include "tmnt_audio_samus_cold.s"\n')
    cfg=src/'smb1base-mmc5-expanded.cfg';line=next(x for x in cfg.read_text().splitlines(True)if x.strip().startswith('X5_NEW_7D:'))
    assert 'start=$a000'in line or 'start = $a000'in line,line
    replace('smb1base-mmc5-expanded.cfg',line,line.replace('$a000','$c000'))
    replace('smb1base-mmc5-expanded.cfg','SEGMENTS {\n','SEGMENTS {\n    TMNT_SAMUS_AUDIO_COLD:load=X5_NEW_7D,type=ro;\n')
    nsf=ROOT/'reference/new-roster-audio/tmnt/Teenage Mutant Ninja Turtles [Gekikame Ninja Den] (1989-05-12)(Konami).nsf'
    assert sha(nsf)=='f220e8d069e321f392526d41e46f5d0f72966d5a22e56d2b269607c678bd58d9'
    f=src/'audio/tmnt/native-drum.dmc';f.parent.mkdir();f.write_bytes(nsf.read_bytes()[128+0x4040:128+0x4040+129])
    assert f.stat().st_size==129;changes['audio/tmnt/native-drum.dmc']=dict(before=None,after=sha(f))
    z=subprocess.run([sys.executable,str(src/'tools/build_mmc5_expanded.py'),'--workspace',str(src),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=src,capture_output=True,text=True)
    (out/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
    old=(parent/'candidate.nes').read_bytes();new=(out/'candidate.nes').read_bytes()
    banks=[b for b in range(128)if old[16+b*8192:16+(b+1)*8192]!=new[16+b*8192:16+(b+1)*8192]]
    assert banks==[125,127],banks
    assert old[16+125*8192:16+126*8192]==bytes([255])*8192
    assert old[16+1048576:]==new[16+1048576:]
    q=dict(passed=True,ROM_sha256=sha(out/'candidate.nes'),parent_ROM_sha256=m['rom_sha256'],source_changes=changes,
           changed_PRG_banks=banks,CHR_unchanged=True,drum_source_CPU_address=0xc040,drum_bytes=129,
           source_NSF_sha256=sha(nsf),scope='Private space-reservation candidate only. No turtle music dispatch installed. Samus source/native equivalence and integration remain pending.')
    (out/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
