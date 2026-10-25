from pathlib import Path
import configparser,difflib,hashlib,json,re,shutil,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';V=D/'mmc3-flag-fix-v23';O=D/'mmc3-ship-state-v24';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tools=O/'tools';shutil.copytree(V/'tools',tools);recipe=tools/'mmc3_oversized/repairs.json';m=json.loads(recipe.read_text());changed=[]
for p in sorted((V/'source/src').iterdir()):
 if not p.is_file()or not p.name.startswith(('vic_','parodius'))or p.suffix not in('.s','.inc'):continue
 old=p.read_text();new,n=re.subn(r'\bM3State_5d([0-9a-f]{2})\b',lambda z:'RgAudioRam+$1'+z[1].lower(),old,flags=re.I)
 if not n:continue
 chunks=[];aa=old.splitlines(keepends=True);bb=new.splitlines(keepends=True)
 for group in difflib.SequenceMatcher(None,aa,bb,autojunk=False).get_grouped_opcodes(3):
  a=''.join(aa[group[0][1]:group[-1][2]]);b=''.join(bb[group[0][3]:group[-1][4]]);assert old.count(a)==1,(p.name,a[:80]);chunks.append(dict(old=a,new=b))
 path='src/'+p.name;row=next((r for r in m['text_repairs']if r['path']==path),None)
 if row is None:row=dict(path=path,chunks=[]);m['text_repairs'].append(row)
 row['chunks']+=chunks;changed.append(dict(path=path,source_page_5d_references=n,contexts=len(chunks)))
assert any(r['path']=='src/vic_native_motion.s'for r in changed)and any(r['path']=='src/parodius_native.s'for r in changed)
row=next(r for r in m['text_repairs']if r['path']=='src/mmc3_oversized.s')
anchor='M3CacheProfile=RgAudioCpuZp+158'
row['chunks'].append(dict(old=anchor,new='.assert RgAudioRam+$200<=RgAudioZp,error,"Native ship5c/5d state fits the two existing inactive Contra/Zelda audio pages"\n'+anchor))
recipe.write_text(json.dumps(m,indent=2));source=O/'source'
with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(R),'--output',str(source),'--reference-rom',str(P/'candidate.nes')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'prepare.log').read_text()[-2000:]
config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini');options={k:v for section in config.values()for k,v in section.items()};options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
rom=O/'candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
with(O/'build.log').open('w')as log:p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'build.log').read_text()[-2500:]
labels={z[2]:int(z[1],16)for line in rom.with_suffix('.lbl').read_text().splitlines()if(z:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
base=labels['RgAudioRam'];assert labels['RgAudioZp']>=base+512 and labels['VgAudioRam']==labels['XgLzHistory']
assert labels['VvObjY']==base+256 and labels['VvObjX']==base+320 and labels['PnType']==base and labels['PnX']==base+56
assert labels['VvHeld']==base+483 and not(labels['PnX']<=labels['VvObjX']<labels['PnX']+28)
assert sha(source/'chr/characters/oversized-raw.chr')==sha(V/'source/chr/characters/oversized-raw.chr')
old=(V/'candidate.nes').read_bytes();new=rom.read_bytes();assert len(old)==len(new)==2097168 and old[:16]==new[:16];diff=[i for i,(a,b)in enumerate(zip(old,new))if a!=b]
q=dict(compiled=True,adopted=False,goal_complete=False,ROM_sha256=sha(rom),parent_ROM_sha256=sha(V/'candidate.nes'),new_RAM_bytes=0,new_CHR_bytes=0,changed_files=changed,changed_ROM_bytes=len(diff),changed_PRG_banks=sorted(set((i-16)//8192 for i in diff)),layout={n:labels[n]for n in ('RgAudioRam','RgAudioZp','PnType','PnX','VvObjX','VvObjY','VvHeld','VgAudioRam','XgLzHistory')},scope='Private MMC3-only correction: native ship5d variables occupy the second of the two already allocated inactive Contra/Zelda audio state pages, preserving5c actor arrays in the first. Gradius native audio owns separate XgLzHistory and is untouched. No universal family remap, new RAM, CHR, movement constants or root-source adoption. Native entry/motion/ability/campaign qualification remains required.')
(O/'build-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
