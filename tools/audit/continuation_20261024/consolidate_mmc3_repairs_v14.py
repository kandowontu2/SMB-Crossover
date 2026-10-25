"""Prepare a self-contained, guarded mapper-repair recipe outside the workspace."""
from pathlib import Path
import configparser,difflib,hashlib,json,subprocess,sys,zipfile
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-consolidated-v14'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 O.mkdir(exist_ok=False);base=O/'baseline';original=R/'tools/prepare_mmc3_oversized.py';text=original.read_text()
 anchor='    released=args.reference_rom.resolve()';assert text.count(anchor)==1
 addition='''    # Native linked assets added after the initial oversized packing list.
    roll=(prepared/'roll.chr').read_bytes();assert len(roll)==24576
    raw[364*1024:380*1024]=roll[:16384]
    raw[304*1024:308*1024]=roll[16384:20480]
    raw[336*1024:340*1024]=roll[20480:24576]
    ui=(prepared/'zelda2-pause-font.chr').read_bytes();assert len(ui)==1024
    raw[395*1024:396*1024]=ui
    parodius=(prepared/'parodius.chr').read_bytes();assert len(parodius)==192*1024
    raw[832*1024:1024*1024]=parodius
'''
 text=text.replace(anchor,addition+anchor)
 ns=dict(__name__='_current_base',__file__=str(original));exec(compile(text,str(original),'exec'),ns);ns['ROOT']=R;ns['OUT']=base;sys.argv=[str(original),'--reference-rom',str(R/'build/checkpoints/native-head-pz/candidate.nes')];ns['main']()
 target=D/'ryu-head-oversized-mmc3-v12/roundtrip-v1/prepared-source.zip';assets=O/'assets';assets.mkdir();patches=[];binary=[]
 with zipfile.ZipFile(target)as z:
  for name in z.namelist():
   if name.endswith('/'):continue
   wanted=z.read(name);p=base/name;old=p.read_bytes()if p.exists()else b''
   if old==wanted:continue
   try:a=old.decode('utf-8');b=wanted.decode('utf-8')
   except UnicodeDecodeError:
    binary.append((name,old,wanted));continue
   aa=a.splitlines(keepends=True);bb=b.splitlines(keepends=True);chunks=[]
   for group in difflib.SequenceMatcher(None,aa,bb,autojunk=False).get_grouped_opcodes(3):
    before=''.join(aa[group[0][1]:group[-1][2]]);after=''.join(bb[group[0][3]:group[-1][4]])
    assert before and a.count(before)==1,(name,before[:100],a.count(before))
    chunks.append(dict(old=before,new=after))
   patched=a
   for q in chunks:
    assert patched.count(q['old'])==1,(name,'overlapping replacement context')
    patched=patched.replace(q['old'],q['new'],1)
   assert patched==b,name
   patches.append(dict(path=name,baseline_sha256=sha(old),repaired_sha256=sha(wanted),chunks=chunks))
 expected={'chr/characters/oversized-raw.chr','chr/characters/mmc3-menu-previews.chr'}
 assert {n for n,_,_ in binary}==expected,[n for n,_,_ in binary]
 atlas=next(b for n,a,b in binary if n.endswith('mmc3-menu-previews.chr'));assert len(atlas)==74*1024
 (assets/'mmc3-menu-previews.chr').write_bytes(atlas)
 raw=next((a,b)for n,a,b in binary if n.endswith('oversized-raw.chr'));assert raw[1][:756*1024]==raw[0][:756*1024]and raw[1][830*1024:]==raw[0][830*1024:]and raw[1][756*1024:830*1024]==atlas
 manifest=dict(format=1,text_repairs=patches,atlas=dict(path='mmc3-menu-previews.chr',sha256=sha(atlas),length=len(atlas),raw_offset=756*1024,raw_replaced_sha256=sha(raw[0][756*1024:830*1024]),old_preview_sha256=sha(next(a for n,a,b in binary if n.endswith('mmc3-menu-previews.chr')))),reference_ROM_sha256='675c57f4abd94d51d0f48a54f0a1d661ed75ef18b153de32a29d94145ba1d47d',expected_ROM_sha256='43134c243d752fcaeab93d348ef56849df810f069788de9af1d76ed498359867',scope='Generated reviewable context patches for the tested mapper repairs and native menu atlas. All source contexts are required exactly once; no blind file replacement. Prepared-source and fresh source preparation are verified separately.')
 (assets/'repairs.json').write_text(json.dumps(manifest,indent=2))
 repair=r'''
from pathlib import Path
import hashlib,json
def apply(source,assets):
 source=Path(source);assets=Path(assets)
 sha=lambda b:hashlib.sha256(b).hexdigest()
 m=json.loads((assets/'repairs.json').read_text())
 for row in m['text_repairs']:
  p=source/row['path'];t=p.read_text()
  for q in row['chunks']:
   assert t.count(q['old'])==1,('Current MMC3 repair context changed',row['path'],q['old'][:120])
   t=t.replace(q['old'],q['new'],1)
  p.write_text(t)
 a=m['atlas'];atlas=(assets/a['path']).read_bytes();assert sha(atlas)==a['sha256']and len(atlas)==a['length']
 p=source/'chr/characters/oversized-raw.chr';raw=bytearray(p.read_bytes());offset=a['raw_offset'];assert sha(raw[offset:offset+len(atlas)])==a['raw_replaced_sha256'],'Current atlas packing overlaps changed source art'
 raw[offset:offset+len(atlas)]=atlas;p.write_bytes(raw)
 p=source/'chr/characters/mmc3-menu-previews.chr';assert sha(p.read_bytes())==a['old_preview_sha256'];p.write_bytes(atlas)
 return m
'''
 (O/'mmc3_current_repairs.py').write_text(repair)
 # New frontend carries the small native raw packing correction and invokes
 # the checked recipe after the original preparation has produced its tree.
 call="    from mmc3_current_repairs import apply\n    apply(OUT, Path(__file__).resolve().parent/'assets')\n"
 marker="if __name__";index=text.rfind(marker);assert index>=0
 text=text[:index]+call+'\n'+text[index:]
 frontend=O/'prepare_mmc3_current.py';frontend.write_text(text)
 module={};exec(compile(repair,str(O/'mmc3_current_repairs.py'),'exec'),module);module['apply'](base,assets)
 with zipfile.ZipFile(target)as z:
  for name in z.namelist():
   if not name.endswith('/'):assert (base/name).read_bytes()==z.read(name),name
 # This self-contained frontend is then called fresh, not merely compiled
 # from the already repaired baseline.
 source=O/'source';ns=dict(__name__='_current_frontend',__file__=str(frontend));sys.path.insert(0,str(O));exec(compile(text,str(frontend),'exec'),ns);ns['ROOT']=R;ns['OUT']=source;sys.argv=[str(frontend),'--reference-rom',str(R/'build/checkpoints/native-head-pz/candidate.nes')];ns['main']()
 with zipfile.ZipFile(target)as z:
  for name in z.namelist():
   if not name.endswith('/'):assert (source/name).read_bytes()==z.read(name),name
 config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini');options={k:v for section in config.values()for k,v in section.items()};options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
 rom=O/'candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
 for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
 cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
 with(O/'build.log').open('w')as log:p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,(O/'build.log').read_text()[-3000:]
 digest=sha(rom.read_bytes());assert digest==manifest['expected_ROM_sha256'],digest
 q=dict(passed=True,ROM_sha256=digest,prepared_source_exact_to_qualified_bundle=True,fresh_preparation_exact=True,text_files_repaired=len(patches),text_contexts=sum(len(r['chunks'])for r in patches),atlas_bytes=len(atlas),external_version_chain_required=False,root_tools_adopted=False,goal_complete=False,scope='Consolidated standalone preparation module plus guarded repair recipe reproduces all629 prepared files and exact tested MMC3 ROM. Root tools and release adoption remain separate. No new mapper gameplay qualification is implied.')
 (O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
if __name__=='__main__':main()
