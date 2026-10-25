from pathlib import Path
import configparser,hashlib,json,shutil,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-ship-state-v24';O=D/'mmc3-ship-lives-v25';assert O.exists()and not(O/'candidate.nes').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tools=O/'tools';shutil.copytree(V/'tools',tools);recipe=tools/'mmc3_oversized/repairs.json';m=json.loads(recipe.read_text())
row=next((r for r in m['text_repairs']if r['path']=='src/x5_menu_ui.s'),None)
if row is None:row=dict(path='src/x5_menu_ui.s',chunks=[]);m['text_repairs'].append(row)
row['chunks'].append(dict(old=' farcall DrawMetasprite,jmp\n',new=' farcall DrawMetasprite\n ; Lives portraits use the same tagged auxiliary tiles as gameplay OAM.\n farcall M3ResolveOam,jmp\n'))
recipe.write_text(json.dumps(m,indent=2));source=O/'source'
with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(R),'--output',str(source),'--reference-rom',str(D/'native-probes-qa-v2/candidate.nes')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'prepare.log').read_text()[-2000:]
config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini');options={k:v for section in config.values()for k,v in section.items()};options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
rom=O/'candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
with(O/'build.log').open('w')as log:p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'build.log').read_text()[-2500:]
assert sha(source/'chr/characters/oversized-raw.chr')==sha(V/'source/chr/characters/oversized-raw.chr')
old=(V/'candidate.nes').read_bytes();new=rom.read_bytes();assert len(old)==len(new)==2097168 and old[:16]==new[:16];diff=[i for i,(a,b)in enumerate(zip(old,new))if a!=b]
q=dict(compiled=True,adopted=False,goal_complete=False,ROM_sha256=sha(rom),parent_ROM_sha256=sha(V/'candidate.nes'),new_RAM_bytes=0,new_CHR_bytes=0,changed_ROM_bytes=len(diff),changed_PRG_banks=sorted(set((i-16)//8192 for i in diff)),scope='Private MMC3-only lives portrait repair: after ordinary portrait OAM construction, apply the existing tagged auxiliary sprite resolver just as normal DrawAll does. Parent broken portraits retained. All entry/motion/lives/native CHR/NMI checks and sampled physical visuals must be rerun on this exact candidate. No MMC5 source or public release adoption.')
(O/'build-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
