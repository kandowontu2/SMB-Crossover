"""Private source-declared cold robot palette cache publication; no native."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import traceback
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D/'root-current-roster-composition-v1'
SHA = '3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def edit(path, old, new):
    raw=path.read_bytes();nl='\r\n' if b'\r\n' in raw else '\n'
    old,new=[x.replace('\n',nl).encode()for x in [old,new]]
    assert raw.count(old)==1,str(path);path.write_bytes(raw.replace(old,new))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(R);out.mkdir(parents=True,exist_ok=False)
    try:
        assert sha(P/'candidate.nes')==SHA
        manifest=json.loads((P/'source-manifest.json').read_text());source=out/'source'
        for rel,expected in manifest.items():
            old=P/'source'/rel;assert sha(old)==expected,rel
            target=source/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old,target)
        raw=(P/'candidate.nes').read_bytes();start=16+78*8192+0xb60;end=16+78*8192+0xc00
        assert raw[start:end]==bytes([255])*(end-start),'Actual bank78 AB60..ABFF must be unused'
        b=scoped_load(P/'candidate.nes')
        profiles=next(x for x in b['segs'].values()if x['name']=='"X5_PROFILES"')
        assert int(profiles['start'],0)+int(profiles['size'],0)==0xab58
        assert int(b['syms']['LuigiSourceClamp']['val'],0)==0xa745
        assert int(b['syms']['LuigiSourceClamp']['size'],0)==263
        edit(source/'src/x5_palette.s', '''SetVRAMOffset:
  sta VRAM_Buffer1_Offset  ;store as new vram buffer offset
  rts''', '''SetVRAMOffset:
  jsr RobotColdPaletteCommit ; Performs the original store and qualified cold cache.
  rts''')
        edit(source/'smb1base-mmc5-expanded.cfg','    X5_PROFILES: load=X5_NEW_4E,type=ro;\n',
             '    X5_PROFILES: load=X5_NEW_4E,type=ro;\n    ROBOT_COLD_PALETTE_CACHE: load=X5_NEW_4E,type=ro,start=$ab60,optional=yes;\n')
        entry=source/'src/entrypoint.s';data=entry.read_bytes();nl=b'\r\n' if b'\r\n' in data else b'\n'
        entry.write_bytes(data+nl+nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'.include "robot_cold_palette_cache.s"',b'.endif',b'']))
        helper='''; Tail is called only after the original legacy producer appended6+6+7 bytes.
; No new RAM or NMI work. Retain the genuine resident RTS/caller registers.
.pushseg
.segment "ROBOT_COLD_PALETTE_CACHE"
.proc RobotColdPaletteCommit
  sta VRAM_Buffer1_Offset
  php
  pha
  phx
  lda GameEngineSubroutine
  bne Done
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq Robot
  cmp #CHARACTER_BASS
  bne Done
  lda RlVariant
  bne Done
Robot:
  lda SelectedCharacter
  tax
  lda InvSelected,x
  bne Done
  lda GuestPowerupActive
  ora StarInvincibleTimer
  ora MmChargeFrames
  ora MmCharging
  bne Done
  lda VRAM_Buffer1_Offset
  cmp #19
  bcc Done
  cmp #84
  bcs Done
  ; Final19..83 implies initial0..64 and all19 command bytes plus terminator
  ; fit the declared84-byte native buffer without arithmetic wrapping.
  lda #1
  sta SsLastPalette
Done:
  plx
  pla
  plp
  rts
.endproc
.assert *-RobotColdPaletteCommit<=$a0,error,"Cold palette tail remains before AC00"
.popseg
'''
        (source/'src/robot_cold_palette_cache.s').write_text(helper)
        source_manifest={rel:sha(source/rel)for rel in manifest}
        source_manifest['src/robot_cold_palette_cache.s']=sha(source/'src/robot_cold_palette_cache.s')
        put(out/'source-manifest.json',source_manifest)
        changed=[rel for rel,h in manifest.items()if source_manifest[rel]!=h]+['src/robot_cold_palette_cache.s']
        patch=[]
        for rel in changed:
            old=P/'source'/rel
            patch+=list(difflib.unified_diff(old.read_text().splitlines(True)if old.exists()else[],(source/rel).read_text().splitlines(True),fromfile='3b/'+rel,tofile='private/'+rel))
        (out/'source.patch').write_text(''.join(patch))
        command=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(R/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
        run=subprocess.run(command,cwd=source,capture_output=True,text=True);put(out/'build.json',dict(command=command,exit=run.returncode,stdout=run.stdout,stderr=run.stderr))
        assert run.returncode==0,run.stdout+run.stderr
        oldq,newq=qualified(P/'candidate.nes'),qualified(out/'candidate.nes')
        assert all(newq.get(n)==v for n,v in oldq.items()),[(n,v,newq.get(n))for n,v in oldq.items()if newq.get(n)!=v]
        new=(out/'candidate.nes').read_bytes();deltas=[i for i,(x,y)in enumerate(zip(raw,new))if x!=y]
        assert len(raw)==len(new)and{(i-16)//8192 for i in deltas}=={78}
        assert all(i<16+128*8192 for i in deltas)
        put(out/'proof.json',dict(built=True,source_only=True,native_run=False,qualified=False,
            parent_ROM_sha256=SHA,ROM_sha256=sha(out/'candidate.nes'),changed_source=changed,
            changed_ROM_bytes=len(deltas),changed_banks=[78],all_old_qualified_symbols_exact=True,
            qualified_old_symbol_count=len(oldq),all_other_PRG_and_CHR_exact=True,new_RAM_bytes=0,NMI_code_changed=False,
            reserved_pool=dict(bank=78,start='AB60',end_exclusive='AC00',old_bytes_all_FF=True),
            source_manifest_sha256=sha(out/'source-manifest.json'),patch_sha256=sha(out/'source.patch'),tool_sha256=sha(__file__)))
        print((out/'proof.json').read_text())
    except BaseException as e:
        put(out/'failure.json',dict(native_run=False,error=repr(e),traceback=traceback.format_exc(),tool_sha256=sha(__file__)))
        shutil.copyfile(__file__,out/'failed-tool.py');raise


if __name__=='__main__':main()
