"""Build a private gameplay route for the qualified original Chip music player."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = D/'root-chip-native-adapter-v1'
PARENT = D/'root-chip-native-relocation-v5'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


ADAPTER = '''; Private original Rescue Rangers music adapter; no shared farcall/SMC.
.pushseg
ChNativeSavedPointer=XgLzHistory+$a4
ChNativePending=XgLzHistory+$a8
ChNativeResume=XgLzHistory+$a9
ChNativePrivatePointer=XgLzHistory+$aa
.segment "CHIP_NATIVE_SERVICE"
ChNativeService:
  lda RgAudioRequest
  beq Play
  sec
  sbc #1
  jsr ChNativeSourceInit
  rts
Play:
  jmp ChNativeSourcePlay
.assert * <= $ae00,lderror,"Chip service stays before original data"
.segment "CHIP_NATIVE_BRIDGE"
ChNativeMacTail:
  BankPRGA #.bank(LmNativeMusicUpdate)
  jmp LmNativeMusicUpdate
ChNativeBridge:
  lda CurrentBank
  pha
  lda #.bank(ChNativeService)|MMC5_PRG_ROM
  sta CurrentBank
  sta MMC5_PRG_BANK_A
  jsr ChNativeService
  pla
  sta CurrentBank
  sta MMC5_PRG_BANK_A
  rts
.assert * <= $e000,lderror,"Chip bridge stays inside existing C94 tail"
.segment "CHIP_NATIVE_ADAPTER"
.proc ChNativeAudioUpdate
  ; The caller saved its A bank. C94 contains the data/roundtrip bridge.
  BankPRGC #.bank(ChNativeBridge)
  lda SelectedCharacter
  cmp #15
  beq MacTail
  lda #.bank(ChNativeAudioUpdate)|MMC5_PRG_ROM
  sta CurrentBank
  lda #0
  sta RgAudioRequest
  lda XgAudioCharacter
  cmp #$f8
  beq Initialized
  lda #$f8
  sta XgAudioCharacter
  lda #0
  sta RgAudioSong
  sta RgAudioSilenced
  sta XgAudioEvent
  sta ChNativeResume
  lda #2
  sta ChNativePending
Initialized:
  lda OperMode
  jeq Mute
  lda AreaMusicQueue
  ora EventMusicQueue
  and #Silence
  beq Area
  lda #1
  sta RgAudioSilenced
Area:
  lda AreaMusicQueue
  and #$7f
  beq Event
  ldx #0
FindArea:
  lsr
  bcs AreaFound
  inx
  bne FindArea
AreaFound:
  lda Areas,x
  sta ChNativePending
  lda #0
  sta RgAudioSilenced
  sta XgAudioEvent
Event:
  lda EventMusicQueue
  and #$7f
  beq Pause
  ldx #0
FindEvent:
  lsr
  bcs EventFound
  inx
  bne FindEvent
EventFound:
  lda Events,x
  sta ChNativePending
  lda #0
  sta RgAudioSilenced
  lda #1
  sta XgAudioEvent
Pause:
  lda GamePauseStatus
  and #1
  jne Mute
  lda RgAudioSilenced
  jne Mute
  lda ChNativePending
  sta RgAudioRequest
  beq Resume
  sta RgAudioSong
  inc XgAudioSong
  lda #0
  ldx #$a3
ClearSource:
  sta XgLzHistory,x
  dex
  bpl ClearSource
  ldx #3
ClearPrivatePointer:
  sta ChNativePrivatePointer,x
  dex
  bpl ClearPrivatePointer
  ldx #15
ClearImage:
  sta GuestNativeApu,x
  lda #1
  sta GuestNativeDirty,x
  lda #0
  dex
  bpl ClearImage
  sta ChNativePending
Resume:
  lda ChNativeResume
  beq Borrow
  lda #0
  sta ChNativeResume
  ldx #15
  lda #1
RestoreImage:
  sta GuestNativeDirty,x
  dex
  bpl RestoreImage
  lda #15
  jsr GuestNativeStatusSTA
Borrow:
 .macro BorrowPointer Address,Offset
  lda Address
  sta ChNativeSavedPointer+Offset
  lda ChNativePrivatePointer+Offset
  sta Address
 .endmacro
  BorrowPointer ChNativePointer,0
  BorrowPointer ChNativePointer+1,1
  BorrowPointer ChNativeMappedC5,2
  BorrowPointer ChNativeMappedC5+1,3
  ldx #0
  ldy #0
  jsr ChNativeBridge
 .macro RestorePointer Address,Offset
  lda Address
  sta ChNativePrivatePointer+Offset
  lda ChNativeSavedPointer+Offset
  sta Address
 .endmacro
  RestorePointer ChNativePointer,0
  RestorePointer ChNativePointer+1,1
  RestorePointer ChNativeMappedC5,2
  RestorePointer ChNativeMappedC5+1,3
  jmp Queues
Mute:
  lda #1
  sta ChNativeResume
  lda #0
  jsr GuestNativeStatusSTA
Queues:
  lda #0
  sta AreaMusicQueue
  sta EventMusicQueue
  sta Square1SoundQueue
  sta Square2SoundQueue
  sta NoiseSoundQueue
  rts
MacTail:
  jmp ChNativeMacTail
Areas: .byte 2,4,5,8,12,13,14
Events:.byte 15,16,11,11,16,11,10
.endproc
.popseg
'''


def main():
    assert not OUT.exists()
    assert sha(PARENT/'candidate.nes') == '2a116f44a768d0ab9a94c88df0191144f0a85ae377211263dabdceb43ede12f6'
    source = OUT/'source'
    shutil.copytree(PARENT/'source', source)
    old = '''::LmNativeMusicGate:
  lda SelectedCharacter
  cmp #15
  bne LmNativeMusicLegacy
  BankPRGA #.bank(LmNativeMusicUpdate)
  jmp LmNativeMusicUpdate
LmNativeMusicLegacy:
  jmp ExpandedAudioTick'''
    new = '''::LmNativeMusicGate:
  ; Closed entry: real VgAudioDispatch supplies A=character,C=(character>=18),
  ; except Vic alternatives supply A=variant1..3,C=1. Only14/15 map into0/1.
  sbc #13
  cmp #2
  bcs LmNativeMusicLegacy
  BankPRGA #.bank(ChNativeAudioUpdate)
  jmp ChNativeAudioUpdate
LmNativeMusicLegacy:
  jmp ExpandedAudioTick
  nop ; retain original18-byte entry span and following DMC gate PCs'''
    p = source/'src/collision.s'
    text = (ROOT/'src/collision.s').read_text()
    assert text.count(old) == 1
    p.write_text(text.replace(old,new))
    p = source/'src/entrypoint.s'
    with p.open('a') as stream:
        stream.write('\n.if MAPPER_MMC5 .and ENABLE_MMC5_EXPANDED\n.include "chip_native_adapter.s"\n.endif\n')
    (source/'src/chip_native_adapter.s').write_text(ADAPTER)
    cfg = source/'smb1base-mmc5-expanded.cfg'
    text = cfg.read_text()
    assert text.count('\n}\nSYMBOLS {') == 1
    cfg.write_text(text.replace('\n}\nSYMBOLS {','''
    CHIP_NATIVE_SERVICE:load=X5_NEW_3E,type=ro,start=$add0;
    CHIP_NATIVE_BRIDGE:load=X5_NEW_5E,type=ro,start=$dfe0;
    CHIP_NATIVE_ADAPTER:load=X5_NEW_4E,type=ro,start=$a500;
}
SYMBOLS {'''))
    result = subprocess.run([sys.executable,'-B',str(ROOT/'tools/build_mmc5_expanded.py'),
                             '--source-overlay',str(source),'--output',str(OUT/'candidate.nes')],
                            cwd=ROOT,capture_output=True,text=True)
    (OUT/'build.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        print(result.stdout+result.stderr)
        raise SystemExit(result.returncode)
    proof = dict(prepared=True,accepted=False,native_run=False,
                 parent_ROM_sha256=sha(PARENT/'candidate.nes'),
                 candidate_ROM_sha256=sha(OUT/'candidate.nes'),
                 generator_sha256=sha(__file__),
                 limitations='Unqualified new gameplay route. Full adapter state/APU, all-other-character equivalence, closed gate inputs, actual IRQ, flagoff and native cadence still required.')
    (OUT/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
