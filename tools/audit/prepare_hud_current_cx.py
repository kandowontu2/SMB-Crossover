"""Rebase the private deferred HUD onto CW and repair its real busy consumer."""
from pathlib import Path
import configparser,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';P=V/'specialist-rygar-hud-h-a/source-p';O=V/'hud-current-cx';C=O/'source'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def edit(name,old,new):
    path=C/name;text=path.read_text();assert text.count(old)==1,(name,old);path.write_text(text.replace(old,new))
def main():
    assert not O.exists();O.mkdir();C.mkdir()
    cp=json.loads((R/'build/checkpoints/water-visible-cw/manifest.json').read_text())
    assert all(sha(R/'build'/f'smb-crossover-{m}.nes')==value for m,value in cp['ROMs'].items())
    seed=json.loads((R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json').read_text())
    names=set(seed['source_hashes'])|{p.relative_to(R).as_posix()for p in(R/'src').rglob('*')if p.is_file()}
    for name in names:
        dst=C/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,dst)
    for name in seed['generated11']:
        dst=C/'build/generated'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'build/generated'/name,dst)
    # Copy only the HUD procedure's original107-byte replacement. Keep the
    # installed Sophia origin helper and every other current bank9 routine.
    path=C/'src/bill_native_rare.s';text=path.read_text();private=(P/'src/bill_native_rare.s').read_text()
    marker='.proc NativeRarePrintStatusBarNumbersCore\n';start=text.index(marker);end=text.index('.endproc',start)+len('.endproc')
    pstart=private.index(marker);pend=private.index('.endproc',pstart)+len('.endproc')
    path.write_text(text[:start]+private[pstart:pend]+text[end:])
    edit('src/characters.s','  farcall InventoryInit\n','  farcall HudStatusInitAndInventoryInit\n')
    # The current producer differs from P only in the HUD hunk itself.
    path=C/'src/screen_render.s';text=path.read_text();private=(P/'src/screen_render.s').read_text()
    start=text.index('UpdateNumber:\n');end=text.index('CoinTallyOffsets:',start)
    pstart=private.index('UpdateNumber:\n');pend=private.index('CoinTallyOffsets:',pstart)
    path.write_text(text[:start]+private[pstart:pend]+text[end:])
    path=C/'src/game.s';text=path.read_text();private=(P/'src/game.s').read_text()
    start=text.index('  farcall InventoryUiTick\n');end=text.index('  lda GamePauseStatus',start)
    pstart=private.index('  farcall HudBeginLogic\n');pend=private.index('  lda GamePauseStatus',pstart)
    block=private[pstart:pend]
    block=block.replace('  .res 15, $ea','''HudQueueBusy:
  lda VRAM_Buffer1
  ora HudStatusPending
  rts
  .res 8, $ea''')
    assert 'HudQueueBusy:'in block
    text=text[:start]+block+text[end:]
    old='PauseSkip:\n  lda #0\n  sta NmiDisable\n  rts'
    new='''PauseSkip:
.if ::ENABLE_CROSSOVER
  jmp HudPublishFrame
  .res 3, $ea
.else
  lda #0
  sta NmiDisable
  rts
.endif'''
    assert text.count(old)==1;text=text.replace(old,new)
    old='    lda VRAM_Buffer1          ;if vram buffer already being used here,'
    new=''' .if ::ENABLE_CROSSOVER
    jsr GameLoop::HudQueueBusy ; Pending numeric packets are busy too.
 .else
    lda VRAM_Buffer1          ;if vram buffer already being used here,
 .endif'''
    assert text.count(old)==1;text=text.replace(old,new);path.write_text(text)
    hud=(P/'src/hud_queue.s').read_text();assert hud.count('HudStatusPending=$7ffb')==1
    (C/'src/hud_queue.s').write_text(hud.replace('HudStatusPending=$7ffb','HudStatusPending=$7ffd'))
    path=C/'src/entrypoint.s';text=path.read_text();anchor='.include "water_shield_enemies.s"\n';assert text.count(anchor)==1
    path.write_text(text.replace(anchor,anchor+'.include "hud_queue.s"\n'))
    path=C/'smb1base.cfg';text=path.read_text();private=(P/'smb1base.cfg').read_text()
    additions='\n'.join(line for line in private.splitlines()if line.strip().startswith(('HUD_QUEUE_COLD:','HUD_STATUS_COLD:','HUD_RETRY_COLD:')))
    assert len(additions.splitlines())==3
    anchor='    CHAR_SELECT:     load = PRG_EXTRA, type = ro, optional=yes;';assert text.count(anchor)==1
    path.write_text(text.replace(anchor,anchor+'\n'+additions))
    before={n:sha(R/n)for n in names};after={n:sha(C/n)for n in names}
    report=dict(status='PRIVATE_CURRENT_HUD_BUSY_SUCCESSOR_BUILD_PENDING',parent_checkpoint_sha256=sha(R/'build/checkpoints/water-visible-cw/manifest.json'),
        ROMs=cp['ROMs'],changed={n:dict(before=before[n],after=after[n])for n in names if before[n]!=after[n]},
        new_source='src/hud_queue.s',new_source_sha256=sha(C/'src/hud_queue.s'),pending_address='7FFD',
        retained=['CW Water','terrain catch-up publication','cannon cooldown order','Cheats initialization','Sophia head origin','firebar fairness','score anchor'],
        known_open=['Foreign partial HUD overlap ordering and complete caller-output liveness remain unproven. This private build is not adopted.'],goal_complete=False)
    (O/'preparation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    config=configparser.ConfigParser();config.optionxform=str;config.read(C/'build_options.ini')
    options={n:v for section in config.values()for n,v in section.items()}
    builds=[]
    for mapper,baseline in(('mmc3',False),('mmc5',False),('mmc3',True),('mmc5',True)):
        name=f'smb-crossover-{mapper}'+('-baseline'if baseline else'');obj=C/'build/objects'/name;obj.mkdir(parents=True)
        for filename in('main.c','entrypoint.s'):shutil.copyfile(C/'src'/filename,obj/filename)
        opts=dict(options,MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper=='mmc5')),ENABLE_CROSSOVER=str(int(not baseline)))
        command=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C','smb1base.cfg',
            '--ld-args',f'--dbgfile,build/{name}.dbg','--include-dir','.','--asm-include-dir','.','--asm-include-dir','src','--bin-include-dir','.',
            '-m',f'build/{name}.map','-Ln',f'build/{name}.lbl','-o',f'build/{name}.nes']
        for key,value in opts.items():command+=['--asm-define',f'{key}={value}','-D',f'{key}={value}']
        command +=[str(obj/'main.c'),str(obj/'entrypoint.s')]
        with(O/f'{name}.log').open('wb')as log:result=subprocess.run(command,cwd=C,stdout=log,stderr=subprocess.STDOUT)
        print(name,result.returncode,flush=True);assert result.returncode==0
        builds.append(dict(name=name,ROM_sha256=sha(C/'build'/(name+'.nes'))))
    assert all(sha(R/n)==value for n,value in before.items()),'Main source is unchanged'
    report.update(status='PRIVATE_CURRENT_HUD_BUSY_SUCCESSOR_FOUR_BUILDS_PASS_NOT_ADOPTED',builds=builds)
    (O/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
