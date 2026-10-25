"""Privately restore Rygar's unused world palette without moving existing code."""
from pathlib import Path
import argparse, configparser, hashlib, json, shutil, subprocess

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/world-palette-fu'
C=O/'source'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    global O,C
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tag',default='world-palette-fu');args=parser.parse_args()
    O=R/'build/verification'/args.tag;C=O/'source'
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/hud-numbers-fl/manifest.json').read_text())
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==h for m,h in parent['ROMs'].items())
    C.mkdir(parents=True)
    seed=json.loads((R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json').read_text())
    names=set(seed['source_hashes'])|{p.relative_to(R).as_posix()for p in(R/'src').rglob('*')if p.is_file()}
    before={n:sha(R/n)for n in names}
    for name in names:
        dst=C/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,dst)
    for name in seed['generated11']:
        dst=C/'build/generated'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'build/generated'/name,dst)
    path=C/'src/characters.s';text=path.read_text();start=text.index('  ldy #0\n',text.index('.proc QueueMegaManFacePalette\n'));end=text.index('Guest:\n',start)
    text=text[:start]+'''PaletteSelector:
  jsr GuestWorldPaletteIndex
  jmp Guest
  .res 20-(*-PaletteSelector), $ea
'''+text[end:];path.write_text(text)
    path=C/'src/entrypoint.s';text=path.read_text();anchor='.include "hud_tail.s"\n';assert text.count(anchor)==1
    path.write_text(text.replace(anchor,anchor+'.include "world_sprite_palette.s"\n'))
    path=C/'smb1base.cfg';text=path.read_text();anchor='    HUD_TAIL_COLD: load=PRGA_03, type=ro, optional=yes, start=$be97;';assert text.count(anchor)==1
    path.write_text(text.replace(anchor,anchor+'\n    WORLD_SPRITE_PALETTE: load=PRGA_03, type=ro, optional=yes, start=$bf91;'))
    (C/'src/world_sprite_palette.s').write_text('''; Rygar's body, disk and chain use palette0; he has no2.02 inventory.
; Retain the area's native palette3 for bricks, debris and world actors.
; Other guests still require their face/special palette until their own
; artwork has a verified allocation. No extra OAM or CHR is introduced.
.pushseg
.segment "WORLD_SPRITE_PALETTE"
.proc GuestWorldPaletteIndex
  php
  ldy #0
  lda SelectedCharacter
  beq Mario
  cmp #CHARACTER_RYGAR
  bne Guest
  jsr NativeIndex
Guest:
  plp                           ; Preserve the old guest entry C/V/I/D.
  rts
Mario:
  plp
NativeIndex:
  lda AreaType
  asl
  sta R0
  asl
  clc
  adc R0
  adc #6
  tay
  rts
.endproc
.assert * <= $c000,error,"World palette helper exceeds bank3 tail"
.popseg
''')
    report=dict(status='BUILDING_PRIVATE_RYGAR_WORLD_PALETTE',parent_ROMs=parent['ROMs'],new_RAM_bytes=0,new_OAM_parts=0,new_CHR_bytes=0,
                scope='Rygar only: native world palette in every area. Other guests remain unchanged pending complete artwork ownership review.',goal_complete=False)
    (O/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(C/'build_options.ini');opts={n:v for section in cfg.values()for n,v in section.items()};builds=[]
    for mapper,base in [('mmc3',False),('mmc5',False),('mmc3',True),('mmc5',True)]:
        name=f'smb-crossover-{mapper}'+('-baseline'if base else'');obj=C/'build/objects'/name;obj.mkdir(parents=True)
        for filename in ('main.c','entrypoint.s'):shutil.copyfile(C/'src'/filename,obj/filename)
        values=dict(opts,MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper=='mmc5')),ENABLE_CROSSOVER=str(int(not base)))
        command=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C','smb1base.cfg','--ld-args',f'--dbgfile,build/{name}.dbg',
                 '--include-dir','.','--asm-include-dir','.','--asm-include-dir','src','--bin-include-dir','.','-m',f'build/{name}.map','-Ln',f'build/{name}.lbl','-o',f'build/{name}.nes']
        for key,value in values.items():command+=['--asm-define',f'{key}={value}','-D',f'{key}={value}']
        command +=[str(obj/'main.c'),str(obj/'entrypoint.s')]
        with(O/f'{name}.log').open('wb')as log:p=subprocess.run(command,cwd=C,stdout=log,stderr=subprocess.STDOUT)
        print(name,p.returncode,flush=True);assert p.returncode==0
        if base:assert sha(C/f'build/{name}.nes')==sha(R/f'build/{name}.nes')
        builds.append(dict(name=name,sha256=sha(C/f'build/{name}.nes')))
    assert all(sha(R/n)==value for n,value in before.items())
    report.update(status='PRIVATE_RYGAR_WORLD_PALETTE_FOUR_BUILDS_PASS_NOT_ADOPTED',builds=builds,source_hashes={p.relative_to(C).as_posix():sha(p)for p in C.rglob('*')if p.is_file()and'build'not in p.relative_to(C).parts})
    (O/'build.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
