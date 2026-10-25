"""Relocate the private HUD flush away from the installed Sophia tail."""
from pathlib import Path
import configparser,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'hud-current-cy';C=O/'source';OLD=V/'hud-current-cx/source'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not O.exists();O.mkdir()
    shutil.copytree(OLD,C,ignore=shutil.ignore_patterns('build'))
    shutil.copytree(OLD/'build/generated',C/'build/generated')
    path=C/'smb1base.cfg';text=path.read_text();line='    HUD_QUEUE_COLD: load=PRGA_05, type=ro, optional=yes;\n';assert text.count(line)==1
    text=text.replace(line,'')
    anchor='    SCORE_POPUP_COLD: load=XG_SOPHIA_A_TAIL_MEM, type=ro, optional=yes, start=$bfc0;';assert text.count(anchor)==1
    text=text.replace(anchor,'    HUD_QUEUE_COLD: load=XG_SOPHIA_A_TAIL_MEM, type=ro, optional=yes, start=$ba00;\n'+anchor)
    path.write_text(text)
    report=dict(status='PRIVATE_HUD_RELOCATED_CURRENT_SUCCESSOR_BUILD_PENDING',predecessor_negative='hud-current-cx: bank5 overflows103B because current Sophia terrain helper occupies the old HUD reservation.',
        parent_ROMs={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')},
        private_partition=dict(bank24_Water='B600-B6FF',bank24_Ryu_primary='B700-B9FF; frozen helper endsB9D4',bank24_HUD='BA00-BBFF; flush379B',bank24_Ryu_additional='BC00-BFBF',bank24_Score='BFC0-BFFF'),
        source_catalog={p.relative_to(C).as_posix():sha(p)for p in C.rglob('*')if p.is_file()},
        scope='Root private allocation replaces the old HUD bank5 tail. No main config/source/ROM changes, no Ryu source installation. Foreign overlap and caller proof still required.',goal_complete=False)
    (O/'preparation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    config=configparser.ConfigParser();config.optionxform=str;config.read(C/'build_options.ini');options={n:v for section in config.values()for n,v in section.items()};builds=[]
    for mapper,baseline in(('mmc3',False),('mmc5',False),('mmc3',True),('mmc5',True)):
        name=f'smb-crossover-{mapper}'+('-baseline'if baseline else'');obj=C/'build/objects'/name;obj.mkdir(parents=True)
        for filename in('main.c','entrypoint.s'):shutil.copyfile(C/'src'/filename,obj/filename)
        opts=dict(options,MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper=='mmc5')),ENABLE_CROSSOVER=str(int(not baseline)))
        command=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C','smb1base.cfg','--ld-args',f'--dbgfile,build/{name}.dbg',
            '--include-dir','.','--asm-include-dir','.','--asm-include-dir','src','--bin-include-dir','.','-m',f'build/{name}.map','-Ln',f'build/{name}.lbl','-o',f'build/{name}.nes']
        for key,value in opts.items():command+=['--asm-define',f'{key}={value}','-D',f'{key}={value}']
        command +=[str(obj/'main.c'),str(obj/'entrypoint.s')]
        with(O/f'{name}.log').open('wb')as log:result=subprocess.run(command,cwd=C,stdout=log,stderr=subprocess.STDOUT)
        print(name,result.returncode,flush=True);assert result.returncode==0
        builds.append(dict(name=name,ROM_sha256=sha(C/'build'/(name+'.nes'))))
    assert all(sha(R/'build'/f'smb-crossover-{m}.nes')==value for m,value in report['parent_ROMs'].items())
    report.update(status='PRIVATE_CURRENT_HUD_BUSY_SUCCESSOR_FOUR_BUILDS_PASS_NOT_ADOPTED',builds=builds)
    (O/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
