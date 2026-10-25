from pathlib import Path
import configparser,hashlib,json,shutil,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-ship-lives-v25';O=D/'mmc3-sophia-stack-v26';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tools=O/'tools';shutil.copytree(V/'tools',tools);recipe=tools/'mmc3_oversized/repairs.json';m=json.loads(recipe.read_text());row=next((z for z in m['text_repairs']if z['path']=='src/inventory.s'),None)
if row is None:row=dict(path='src/inventory.s',chunks=[]);m['text_repairs'].append(row)
old='  ldx SelectedCharacter\n  cpx #13\n  bcc LegacySupported\n';new='  ldx SelectedCharacter\n  cpx #CHARACTER_SOPHIA\n  beq NativeSophiaSupported\n  cpx #13\n  bcc LegacySupported\n';row['chunks'].append(dict(old=old,new=new))
old='  farcall RlSupportedDispatch,jmp\n  .assert *-InventorySupported=46,error,"Original leaf span preserved"\n'
new='  farcall RlSupportedDispatch,jmp\nNativeSophiaSupported:\n  ; Exact native predicate result without exhausting stack through unrelated gates.\n  pla                          ; discard saved X\n  pla                          ; discard saved A\n  plp\n  lda #CHARACTER_SOPHIA\n  ldx #CHARACTER_SOPHIA\n  cpx #CHARACTER_SOPHIA         ; native final successful CPX/SEC flags\n  rts\n  .assert *-InventorySupported=60,error,"MMC3 Sophia support bypasses unrelated family gates"\n'
row['chunks'].append(dict(old=old,new=new));recipe.write_text(json.dumps(m,indent=2));source=O/'source'
with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(R),'--output',str(source),'--reference-rom',str(D/'native-probes-qa-v2/candidate.nes')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'prepare.log').read_text()[-2000:]
config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini');options={k:v for section in config.values()for k,v in section.items()};options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
rom=O/'candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
with(O/'build.log').open('w')as log:p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'build.log').read_text()[-2000:]
old=(V/'candidate.nes').read_bytes();new=rom.read_bytes();assert len(old)==len(new)==2097168 and old[:16]==new[:16];diff=[i for i,(a,b)in enumerate(zip(old,new))if a!=b];assert sha(source/'chr/characters/oversized-raw.chr')==sha(V/'source/chr/characters/oversized-raw.chr')
q=dict(compiled=True,adopted=False,goal_complete=False,ROM_sha256=sha(rom),parent_ROM_sha256=sha(V/'candidate.nes'),changed_ROM_bytes=len(diff),changed_PRG_banks=sorted(set((i-16)//8192 for i in diff)),new_RAM_bytes=0,new_CHR_bytes=0,scope='Private MMC3-only Sophia inventory predicate shortcut to avoid long unrelated bank-gate chain within brick/projectile contact. Exact A/X/Y/flags/SP and application/bank equivalence, native stack-write failure witness, unchanged-input Sophia clear and broader current-hash qualification remain mandatory. Root recipe and public builds are untouched.')
(O/'build-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
