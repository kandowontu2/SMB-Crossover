"""Genuine sparse full link for the skin-only Mario alternate; no installation."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/kamikaze-mario-host-v4"
BASE = ROOT / "build/roster-shared-celeste-small-chr-v1.nes"


def binding(path):
    p=Path(path);b=p.read_bytes()
    return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/"build.json").exists(),"Keep qualified build immutable"
    assert binding(BASE)["sha256"]=="f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9"
    raw=BASE.read_bytes()
    assert raw[16+62*8192+0x9c0:16+62*8192+0xa00]==b'\xff'*64
    assert raw[16+62*8192+0x1690:16+63*8192]==b'\xff'*2416
    assert raw[16+124*8192+0xdce:16+124*8192+0xe00]==b'\xff'*50
    assert raw[16+81*8192+0x1f60:16+82*8192]==b'\xff'*160
    assert raw[16+1048576+696*1024:16+1048576+704*1024]==bytes(8192)
    overlay=OUT/"overlay";(overlay/"src").mkdir(parents=True,exist_ok=True)
    entry=(ROOT/"src/entrypoint.s").read_text()
    (overlay/"src/entrypoint.s").write_text(entry+'\n.include "kamikaze_mario.s"\n.if ::ENABLE_MMC5_EXPANDED\n.include "kamikaze_mario_render_v2.inc"\n.endif\n')
    # Exact eight-byte source slot; all following public publisher PCs stay
    # fixed. No occupied physical4 metasprite tail is consumed.
    publisher=(ROOT/"src/mmc5_expanded.s").read_text()
    publisher=once(publisher,'X5Direct0:\n  and #3\n  sta $5130\n  lda CurrentCHRBank+0\n',
        'X5Direct0:\n  jsr KmNmiSlot0\n  jmp X5Write0\n  .res 2,$ea\n')
    (overlay/"src/mmc5_expanded.s").write_text(publisher)
    nr=(ROOT/"src/new_roster_dispatch.s").read_text()
    old=''' lda MarioVariant
 beq NrToLuigi
 cmp #1
 beq NrToCeleste
 lda #0
 beq NrMarioPublish
NrToLuigi:lda #1
 bne NrMarioPublish
NrToCeleste:lda #4
'''
    new=''' jsr KmNextVariant
 jmp NrMarioPublish
 .res 7,$ea
NrToLuigi: .res 4,$ea
NrToCeleste: .res 2,$ea
'''
    nr=once(nr,old,new)
    (overlay/"src/new_roster_dispatch.s").write_text(nr)
    menu=(ROOT/"src/character_select.s").read_text()
    menu=once(menu,'farcall NrQueueSelectName,jmp','farcall KmQueueName,jmp')
    (overlay/"src/character_select.s").write_text(menu)
    player=(ROOT/'src/player.s').read_text()
    player=once(player,'  cmp #4\n  bne :+\n  farcall CmHostGraphics,jmp\n:\n.endif\n  lda SelectedCharacter',
        '  cmp #3\n  bcc :+\n  farcall KmGraphics,jmp\n:\n.endif\nKmNativeGraphics:\n  lda SelectedCharacter')
    (overlay/'src/player.s').write_text(player)
    ui=(ROOT/'src/x5_menu_ui.s').read_text()
    ui=once(ui,'farcall CmHostPortraitRender,jmp','farcall KmPortrait,jmp')
    (overlay/'src/x5_menu_ui.s').write_text(ui)
    resident=(ROOT/'src/samus.s').read_text();start=resident.index('  ; Same resident68B capsule');end=resident.index('.else\n  lda SelectedCharacter',start)
    replacement='''  ; Same68B resident capsule, no shared NMI mapper scratch.
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bcc Small
  jmp ExpandedGraphicsBank
Small:
  cmp #CHARACTER_BILL
  bcc First
  jmp RosterGraphicsBank
First:
  cmp #CHARACTER_SAMUS
  beq Samus
  ; First is reachable only for0/1/2; Samus2 already branched above.
  lsr
  bcs Mega
  lda MarioVariant
  cmp #4
  beq Celeste
  cmp #3
  beq Kamikaze
Native:
  clc
  lda #.bank(MmMM_HAIR_STANDRight)|MMC5_PRG_ROM
  bne Publish
Mega:
  lda ObjectMetasprite
  cmp #METASPRITE_SAMUS_BODY
  bne Native
  lda #.bank(SsMegaTHROWRight)|MMC5_PRG_ROM
  bne Publish
Samus:
  lda #.bank(SmP0_STANDRight)|MMC5_PRG_ROM
  bne Publish
Celeste:
  lda #.bank(CmArtStart)|MMC5_PRG_ROM
  bne Publish
Kamikaze:
  lda #62|MMC5_PRG_ROM
Publish:
  BankPRGC a
  rts
  .res 0,$ea
  .assert *-CrossoverGraphicsBank=68,error,"Resident graphics ABI capsule"
'''
    resident=resident[:start]+replacement+resident[end:]
    (overlay/'src/samus.s').write_text(resident)
    cfg=(ROOT/"smb1base-mmc5-expanded.cfg").read_text()
    cfg=once(cfg,'    CHR:        load = CHR,     type = ro;',
        '    CHR:        load = CHR,     type = ro;\n    KAMIKAZE_CHR: load=LM_UNUSED_CHR_MEM,type=ro,start=$ae000,optional=yes;')
    cfg=once(cfg,'    ICE_CLIMBERS_CORE: load=X5_NEW_3E,type=ro,start=$a2b7,optional=yes;',
        '    ICE_CLIMBERS_CORE: load=X5_NEW_3E,type=ro,start=$a2b7,optional=yes;\n    KAMIKAZE_NMI: load=X5_NEW_3E,type=ro,start=$a9c0,optional=yes;\n    KAMIKAZE_CORE: load=X5_NEW_3E,type=ro,start=$b690,optional=yes;')
    (overlay/"smb1base-mmc5-expanded.cfg").write_text(cfg)
    # A genuine separate ASM object keeps this art out of the main object's
    # 256-segment limit, including the forthcoming four-segment Rogue unit.
    asset=OUT/"kamikaze_chr.s"
    asset.write_text('''; Genuine separately linked NMI helper and original artwork.
.import CurrentCHRBank
.export KmNmiSlot0
.segment "KAMIKAZE_NMI"
KmNmiSlot0:
 php
 cmp #$84
 beq Skin
 and #3
 sta $5130
 lda CurrentCHRBank
 plp
 ora #0
 rts
Skin:
 lda #2
 sta $5130
 lda CurrentCHRBank
 clc
 adc #168
 plp
 ora #0
 rts
.assert * <= $aa00,lderror,"Kamikaze NMI exceeds verified62A9C0 gap"
.segment "KAMIKAZE_CHR"
.incbin "chr/characters/kamikaze-mario-source-v2.chr"
''')
    builder=(ROOT/"tools/build_mmc5_expanded.py").read_text()
    builder=once(builder,"a=p.parse_args(); root=a.workspace.resolve(); overlay=(a.source_overlay or root).resolve()",
        "a=p.parse_args(); root=a.workspace.resolve(); overlay=(a.source_overlay or root).resolve(); sys.path.insert(0,str(root/'tools'))")
    builder=once(builder,"command += [str(objects/'main.c'),str(objects/'entrypoint.s')]",
        "command += [str(objects/'main.c'),str(objects/'entrypoint.s')]\n if flag: command += ["+repr(str(asset.resolve()))+"]")
    private=OUT/"private_builder.py";private.write_text(builder)
    command=[sys.executable,'-B',str(private),'--workspace',str(ROOT),
             '--source-overlay',str(overlay),'--output',str(OUT/'candidate.nes')]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (OUT/"build.log").write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stdout+result.stderr
    proof=dict(status="PRIVATE_LINK_ONLY_NOT_NATIVE_OR_INSTALLED",parent=binding(BASE),
               candidate=binding(OUT/'candidate.nes'),command=command,
               bindings=[binding(p)for p in[Path(__file__),ROOT/'src/kamikaze_mario.s',
                   ROOT/'chr/characters/kamikaze-mario-source-v2.chr',ROOT/'tools/build_mmc5_expanded.py',
                   ROOT/'build/kamikaze-mario-art-v2/source-art.json',ROOT/'src/kamikaze_mario_render_v2.inc',ROOT/'src/kamikaze_mario_source_art_v2.inc',private,asset,
                   *sorted(overlay.rglob('*.*'))]],
               scope="Skin-only MarioVariant3; native Mario/physics/abilities unchanged. Full actual source/caller/pixel/native qualification remains open.")
    (OUT/"build.json").write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(candidate=proof['candidate'],status=proof['status'])))


if __name__=='__main__':main()
