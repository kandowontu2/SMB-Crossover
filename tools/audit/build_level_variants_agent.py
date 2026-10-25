"""Prepare a small, isolated current-source level-parity candidate; never adopt it."""
from pathlib import Path
import configparser,csv,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2]
O=R/'build/verification/level-variants-candidate-agent'
C=O/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def tables():
    inv=R/'build/verification/level-layout-audit-agent/spawn-revision2/complete-interactive-differences.csv'
    cells=[];coin=[]
    ptrs={'1-2b':0x40,'4-2b':0x41,'5-2a':0x31,'6-2a':0x23}
    for z in csv.DictReader(inv.open()):
        if z['version']!='2.02' or not z['source_map'].startswith('groundUnbreakable'):continue
        x,y=json.loads(z['original_tile']);old=int(z['original_metatile']);assert old in(0x51,0x52)
        d=dict(area=ptrs[z['area']],world=int(z['area'][0])-1,page=x//16,column=x%16,row=y-2,easy=0x6e if old==0x51 else 0x6f,hard=0x58 if old==0x51 else 0x5d,mask=0,source_area=z['area'],native_tile=[x,y],source_tile=json.loads(z['source_tile']),reason='UnbreakableBrick constructor: hosted solid;2.02 single-coin brick')
        cells.append(d);coin.append(d)
    assert len(coin)==16
    def add(a,w,x,y,e,h,mask,reason):cells.append(dict(area=a,world=w,page=x//16,column=x%16,row=y-2,easy=e,hard=h,mask=mask,native_tile=[x,y],reason=reason))
    for x,y in [(72,5),(73,4),(74,4),(75,5)]:
        add(0x27,1,x,y,0,0,0,'2-3 coin old row removed;7-3 unchanged')
        add(0x27,1,x,y+1,0xc2,0xc2,0,'2-3 coin moved one tile down')
    add(0x41,3,128,2,0,0,0,'4-2 ceiling brick absent in both sources')
    add(0x61,3,96,10,0xff,0,0,'4-4 native maze cell maps to source161,10; repeated source225,10 same maze section remains separately documented')
    for x,t in [(34,0x19),(35,0x1b)]:add(0x20,2,x,14,0xff,t,1,'2.02-only3-3 horizontal helper landing')
    for x,t in [(30,0x19),(31,0x1a),(32,0x1b)]:add(0x2c,3,x,7,t,t,2,'Both versions4-3 vertical helper landing')
    for y in range(8,15):add(0x2c,3,31,y,0x4f if y==8 else 0x50,0x4f if y==8 else 0x50,2,'4-3 helper decorative stem; noncollidable')
    out=[f'CrossoverCellCount={len(cells)}',f'CrossoverCoinCellCount={len(coin)}']
    for label,key in [('Area','area'),('World','world'),('Page','page'),('Column','column'),('Row','row'),('Easy','easy'),('Hard','hard'),('Mask','mask')]:
        out += ['Cell'+label+':','  .byte '+','.join(f'${z[key]:02x}'for z in cells)]
    for z in coin:
        x=z['native_tile'][0];address=0x300+208*((x//16)%2)+x%16;z['bufferLo']=address&255;z['bufferHi']=address>>8;z['contactRow']=z['row']*16
    for label,key in [('Area','area'),('World','world'),('Page','page'),('Column','column'),('Row','contactRow'),('BufferLo','bufferLo'),('BufferHi','bufferHi')]:
        out += ['CoinCell'+label+':','  .byte '+','.join(f'${z[key]:02x}'for z in coin)]
    (O/'implemented-cell-contract.json').write_text(json.dumps(dict(cells=cells,coin_cells=coin),indent=2)+'\n')
    return '\n'.join(out)

def edit(name,old,new,count=1):
    p=C/name;s=p.read_text();assert s.count(old)==count,(name,old,s.count(old));p.write_text(s.replace(old,new))

def main():
    O.mkdir(exist_ok=True);C.mkdir(exist_ok=True)
    if not (O/'preparation.json').exists():
        names=[p.relative_to(R).as_posix() for folder in ('src','inc','chr','audio','build/generated') for p in (R/folder).rglob('*') if p.is_file()]
        names+=['smb1base.cfg','build_options.ini']
        before={n:sha(R/n)for n in names}
        for n in names:
            dst=C/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,dst)
        (O/'preparation.json').write_text(json.dumps(dict(parent_checkpoint='build/checkpoints/ryu-overlap-hr/manifest.json',parent_manifest_sha256=sha(R/'build/checkpoints/ryu-overlap-hr/manifest.json'),parent_ROMs={m:sha(R/f'build/smb-crossover-{m}.nes')for m in('mmc3','mmc5')},source_before=before),indent=2)+'\n')
    else:
        before=json.loads((O/'preparation.json').read_text())['source_before']
        # Reapply only our local hunks to the immutable current-source snapshot.
        for n in ('src/entrypoint.s','src/level_tiles.s','src/object.s','src/screen_render.s','src/collision.s','src/sprite_render.s','src/bill_native_rare.s','smb1base.cfg'):
            assert sha(R/n)==before[n],f'Main source changed; rebase explicitly: {n}'
            shutil.copyfile(R/n,C/n)
    module=(R/'tools/audit/level_variants_source.s').read_text().replace(';@@CELL_TABLES@@',tables())
    liftstart=module.index('.segment "LEVEL_LIFT_BRIDGE"\n')
    lift=module[liftstart+len('.segment "LEVEL_LIFT_BRIDGE"\n'):].removesuffix('.popseg\n')
    module=module[:liftstart]+'.popseg\n'
    original=(R/'src/sprite_render.s').read_text();ds=original.index('DrawSmallPlatform:\n');de=original.index(';-------------------------------------------------------------------------------------',ds)
    draw=original[ds:de];dbody=draw.removeprefix('DrawSmallPlatform:\n')
    dbody=dbody.replace('jsr DumpSixSpr','farcall DumpSixSpr').replace('jsr DumpThreeSpr','farcall DumpThreeSpr')
    dbody=dbody.replace('       clc\n       adc #$80                    ;add 128 pixels','       farcall CrossoverLiftSecondY')
    module+='\n.pushseg\n.segment "LEVEL_VARIANTS"\n.proc CrossoverDrawSmallPlatform\n'+dbody+'.endproc\n.assert *<=$a800,error,"Authored level code must preserve helper cold space atA800"\n.popseg\n'
    (C/'src/level_lift_bridges.inc').write_text(lift)
    (C/'src/level_variants.s').write_text(module)
    edit('src/entrypoint.s','.include "ryu_side_overlap.s"\n','.include "ryu_side_overlap.s"\n.include "level_variants.s"\n')
    edit('smb1base.cfg','    ZELDA_WRAP_MEM:start=$c000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;',
         '    LEVEL_VARIANTS_MEM:start=$a000, size=$1a00, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;\n    HELPER_SELECTOR_MEM:start=$ba00, size=$0200, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;\n    ZELDA_WRAP_MEM:start=$dc00, size=$0400, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;')
    edit('smb1base.cfg','    LEVEL:      load = PRGA_02, type = ro;',
         '    LEVEL:      load = PRGA_02, type = ro;\n    LEVEL_VARIANTS: load=LEVEL_VARIANTS_MEM, type=ro, optional=yes;\n    LEVEL_VARIANTS_BRIDGE: load=PRGA_02, type=ro, optional=yes, start=$bfef;')
    edit('src/level_tiles.s','RendBBuf:\n    jsr ProcessAreaData        ;do the area data loading routine now',
         'RendBBuf:\n.if ::ENABLE_CROSSOVER\n    jsr CrossoverLevelColumnBridge ; Native parser, then authored source overrides.\n.else\n    jsr ProcessAreaData        ;do the area data loading routine now\n.endif')
    edit('src/level_tiles.s','  farcall CheckpointEnemyID, jmp    ;jump ahead to run jump engine and subroutines',
         '.if ::ENABLE_CROSSOVER\n  farcall CrossoverLevelEnemyInit, jmp\n.else\n  farcall CheckpointEnemyID, jmp    ;jump ahead to run jump engine and subroutines\n.endif')
    edit('src/level_tiles.s','        farcall CheckpointEnemyID     ;process each enemy object separately',
         '.if ::ENABLE_CROSSOVER\n        farcall CrossoverLevelGroupInit\n.else\n        farcall CheckpointEnemyID     ;process each enemy object separately\n.endif')
    edit('src/object.s','FirebarSpinSpdData:\n  .byte $28, $38, $28, $38, $28',
         'FirebarSpinSpdData:\n.if ::ENABLE_CROSSOVER\n  .byte $28, $28, $28, $28, $28 ; Both pinned sources use uniform106 degrees/s.\n.else\n  .byte $28, $38, $28, $38, $28\n.endif')
    edit('src/object.s','MoveSmallPlatform:\n      jsr MoveLiftPlatforms      ;execute common to all large and small lift platforms',
         'MoveSmallPlatform:\n.if ::ENABLE_CROSSOVER\n      jsr CrossoverLiftMoveBridge\n.else\n      jsr MoveLiftPlatforms      ;execute common to all large and small lift platforms\n.endif')
    edit('src/object.s','      adc PlayerPosSPlatData-1,y ;coordinate',
         '.if ::ENABLE_CROSSOVER\n      jsr CrossoverLiftPlayerY\n.else\n      adc PlayerPosSPlatData-1,y ;coordinate\n.endif')
    edit('src/collision.s','       clc                        ;128 pixels downwards\n       adc #$80',
         '.if ::ENABLE_CROSSOVER\n       jsr CrossoverLiftSecondY\n.else\n       clc                        ;128 pixels downwards\n       adc #$80\n.endif')
    edit('src/collision.s','       clc\n       adc #$80\n       sta BoundingBox_DR_YPos,y',
         '.if ::ENABLE_CROSSOVER\n       jsr CrossoverLiftSecondY\n.else\n       clc\n       adc #$80\n.endif\n       sta BoundingBox_DR_YPos,y')
    edit('src/collision.s','  .byte $00, $00, $18, $06',
         '.if ::ENABLE_CROSSOVER\n  .byte $00, $00, $18, $08 ;24x8 source constant-lift rectangle.\n.else\n  .byte $00, $00, $18, $06\n.endif')
    # Retain the original body span and all old diagnostic label addresses.
    # MMC5 has no OBJECT tail; these tiny bridges fit the freed draw-body span.
    labels={}
    for line in (R/'build/smb-crossover-mmc3.lbl').read_text().splitlines():
        p=line.split()
        if len(p)==3:labels[p[2].lstrip('.')]=int(p[1],16)
    span=labels['FlagpoleGfxHandler']-labels['DrawSmallPlatform']
    alias='\n'.join(f'{n}=DrawSmallPlatform+{labels[n]-labels["DrawSmallPlatform"]}'for n in('TopSP','BotSP','SOfs','SOfs2','ExSPl'))
    wrapper='DrawSmallPlatform:\n.if ::ENABLE_CROSSOVER\n  farcall CrossoverDrawSmallPlatform\n  rts\n'+alias+'\n.include "level_lift_bridges.inc"\n'+f'  .assert *-DrawSmallPlatform<={span},error,"Retain old draw-body span"\n  .res {span}-(*-DrawSmallPlatform),$ea\n.else\n'+draw.removeprefix('DrawSmallPlatform:\n')+'.endif\n\n'
    edit('src/sprite_render.s',draw,wrapper)
    edit('src/bill_native_rare.s','      lda SelectedCharacter\n      beq NativeCoinTimer\n      farcall MegaManCoinBrick\n      jmp PutMTileB',
         '      lda SelectedCharacter\n      nop                         ; Keep all original public PCs.\n      nop\n      farcall CrossoverLevelCoinBrick\n      jmp PutMTileB')
    edit('src/screen_render.s','MTILE_CURRENT_INDEX .set $80',
         '.if ::ENABLE_CROSSOVER\nMTILE_CURRENT_INDEX .set $6e\n  MTileDefine $47, $48, $47, $48, MTILE_PALETTE_1 | MTILE_SOLID | MTILE_BUMP ; hosted solid brick, lined\n  MTileDefine $48, $48, $48, $48, MTILE_PALETTE_1 | MTILE_SOLID | MTILE_BUMP ; hosted solid brick, plain\n.endif\n\nMTILE_CURRENT_INDEX .set $80')
    config=configparser.ConfigParser();config.optionxform=str;config.read(C/'build_options.ini')
    opts0={n:v for section in config.values()for n,v in section.items()}
    builds=[]
    for mapper,baseline in(('mmc3',False),('mmc5',False),('mmc3',True),('mmc5',True)):
        name=f'smb-crossover-{mapper}'+('-baseline'if baseline else'');obj=C/'build/objects'/name;obj.mkdir(parents=True,exist_ok=True)
        for n in('main.c','entrypoint.s'):shutil.copyfile(C/'src'/n,obj/n)
        opts=dict(opts0,MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper=='mmc5')),ENABLE_CROSSOVER=str(int(not baseline)))
        cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C','smb1base.cfg','--ld-args',f'--dbgfile,build/{name}.dbg','--include-dir','.','--asm-include-dir','.','--asm-include-dir','src','--bin-include-dir','.', '-m',f'build/{name}.map','-Ln',f'build/{name}.lbl','-o',f'build/{name}.nes']
        for n,v in opts.items():cmd+=['--asm-define',f'{n}={v}','-D',f'{n}={v}']
        cmd +=[str(obj/'main.c'),str(obj/'entrypoint.s')]
        with(O/(name+'.log')).open('wb')as f:z=subprocess.run(cmd,cwd=C,stdout=f,stderr=subprocess.STDOUT)
        print(name,z.returncode,flush=True)
        if z.returncode:print((O/(name+'.log')).read_text()[-5000:]);return 1
        builds.append(dict(name=name,sha256=sha(C/f'build/{name}.nes')))
    changed={n:sha(C/n)for n,h in before.items()if sha(C/n)!=h}
    changed['src/level_variants.s']=sha(C/'src/level_variants.s')
    changed['src/level_lift_bridges.inc']=sha(C/'src/level_lift_bridges.inc')
    assert all(sha(R/n)==h for n,h in before.items()),'Main source changed during private build'
    (O/'build.json').write_text(json.dumps(dict(status='PRIVATE_CANDIDATE_NOT_ADOPTED',builds=builds,modified_files=changed,new_RAM_bytes=0,reserved_helper_selector='$1A:BA00..BBFF'),indent=2)+'\n')
    return 0

if __name__=='__main__':raise SystemExit(main())
