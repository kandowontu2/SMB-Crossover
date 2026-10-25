from pathlib import Path
import configparser,hashlib,json,shutil,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=D/'mmc3-flag-fix-v23';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tools=O/'tools';tools.mkdir();shutil.copytree(R/'tools/mmc3_oversized',tools/'mmc3_oversized')
for n in ('prepare_mmc3_oversized.py','mmc3_current_repairs.py'):shutil.copy2(R/'tools'/n,tools/n)
recipe=tools/'mmc3_oversized/repairs.json';m=json.loads(recipe.read_text());assert not any(r['path']=='src/vic_adapter.s'for r in m['text_repairs'])
old=' lda GameEngineSubroutine\n cmp #5\n beq ExitWalk\n cmp #8\n bne Legacy\n'
new=''' lda GameEngineSubroutine
 cmp #4
 beq Zero                    ; The scripted pole owns X; native edge clamps must not detach it.
 cmp #5
 beq ExitWalk
 cmp #8
 bne Legacy
'''
original=R/'src/vic_adapter.s';assert original.read_text().count(old)==1
m['text_repairs'].append(dict(path='src/vic_adapter.s',chunks=[dict(old=old,new=new)],scope='MMC3-only prepared-source repair. Flag-slide mode4 must retain scripted X so the ordinary side query keeps native climbing state; preserve all original gameplay and end-walk paths.'))
recipe.write_text(json.dumps(m,indent=2));source=O/'source'
with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(R),'--output',str(source),'--reference-rom',str(P/'candidate.nes')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'prepare.log').read_text()[-2000:]
config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini');options={k:v for section in config.values()for k,v in section.items()};options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
rom=O/'candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
with(O/'build.log').open('w')as log:p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'build.log').read_text()[-2500:]
oldrom=(D/'mmc3-tools-v16/canonical-build/smb-crossover-mmc3-oversized.nes').read_bytes();newrom=rom.read_bytes();assert len(oldrom)==len(newrom)==2097168
changes=[i for i,(a,b)in enumerate(zip(oldrom,newrom))if a!=b];assert oldrom[:16]==newrom[:16]
q=dict(compiled=True,adopted=False,goal_complete=False,ROM_sha256=sha(rom),parent_ROM_sha256=hashlib.sha256(oldrom).hexdigest(),source_recipe_sha256=sha(recipe),changed_PRG_banks=sorted(set((i-16)//8192 for i in changes)),changed_ROM_bytes=len(changes),scope='Private minimal MMC3 prepared-source flag ownership repair. Source movement/query geometry/audio and MMC5 working source are unchanged. Native failed-input regression and fresh route/cache witnesses required before any root recipe or release adoption.')
(O/'build-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
