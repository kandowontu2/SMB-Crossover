"""Stage the confirmed item/side fixes on accepted PS, retaining its music."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];PARENT=ROOT/'build/checkpoints/contact-pause-ps'
MIDDLE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-combined-pu/candidate-v12/source/src/tmnt_middle_probe.s')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(PARENT/'candidate.nes')=='646baef6cbcbe9ebc3c0a57c182592b3e777970c13b9c89eda6765f446915bb6'
 parent=json.loads((PARENT/'manifest.json').read_text());assert sha(PARENT/'source.zip')==parent['source_zip_sha256'];s=a.output/'source'
 with zipfile.ZipFile(PARENT/'source.zip')as z:
  assert z.testzip()is None and all((s/n).resolve().is_relative_to(s.resolve())for n in z.namelist());z.extractall(s)
 def replace(n,old,new):
  f=s/n;v=f.read_text();assert v.count(old)==1,(n,old);f.write_text(v.replace(old,new))
 replace('src/inventory.s','farcall InventoryLegacyLeaf,jmp','farcall InventoryLegacyItemLeaf,jmp')
 f=s/'src/inventory_legacy_leaf.s';f.write_text(f.read_text()+'''
; Item queries/spending pass their requested local ID in A. The existing
; mode leaf publishes a character/alternate ID in A; retain its boolean C
; and X result while restoring the caller's requested item for the lookup.
.pushseg
.segment "INVENTORY_ITEM_RETURN"
.proc InventoryLegacyItemLeaf
 pha
 jsr InventoryLegacyLeaf
 pla
 rts
.endproc
.export InventoryLegacyItemLeaf
.popseg
''')
 replace('src/tmnt_dispatch.s','Shift:clc\n adc Player_Y_Position\n sta Player_Y_Position\n ldy TnSavedY\n jsr BlockBufferColli_Side','Shift:clc\n adc Player_Y_Position\n sta Player_Y_Position\n ldy TnSavedY\n::TnMiddleProbeSpan:\n jsr TnSideMiddleProbe')
 f=s/'src/tmnt.s';f.write_text(f.read_text()+'\n.include "tmnt_middle_probe.s"\n');(s/'src/tmnt_middle_probe.s').write_bytes(MIDDLE.read_bytes())
 replace('src/guest_audio.s','  lda GuestMixMask\n  ora GuestMixChanged\n  bne MixedChannels','''  lda GuestMixMask
.if ::ENABLE_MMC5_EXPANDED
::X5NativeNoiseSpan:
  jsr X5NativeNoiseMask
.else
  ora GuestMixChanged
.endif
  bne MixedChannels''')
 f=s/'src/guest_audio.s';f.write_text(f.read_text()+'''
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "X5_AUDIO_MIX"
; Pulse effects are already flushed on the separate MMC5 voices.
; Only native-noise ownership/change needs the ordinary APU owner loop.
.proc X5NativeNoiseMask
 ora GuestMixChanged
 and #8
 rts
.endproc
.export X5NativeNoiseMask
.popseg
.endif
''')
 replace('smb1base-mmc5-expanded.cfg','    HOT_RENDER_GATE: load=X5_NEW_42,type=ro;','    HOT_RENDER_GATE: load=X5_NEW_42,type=ro;\n    INVENTORY_ITEM_RETURN: load=X5_NEW_42,type=ro,optional=yes;')
 replace('smb1base-mmc5-expanded.cfg','    CHAR_SELECT:     load = PRG_EXTRA, type = ro, optional=yes;','    CHAR_SELECT:     load = PRG_EXTRA, type = ro, optional=yes;\n    X5_AUDIO_MIX: load=PRG_EXTRA,type=ro,optional=yes;')
 z=subprocess.run([sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2500:]
 q=dict(prepared=True,accepted=False,goal_complete=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=parent['rom_sha256'],scope='Confirmed item-ID preservation and native middle-side sample repair; same existing music, plus byte/output-equivalent MMC5 mixer shortcut. Native TMNT music PU remains a separate held candidate.')
 (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(q['ROM_sha256'])
if __name__=='__main__':main()
