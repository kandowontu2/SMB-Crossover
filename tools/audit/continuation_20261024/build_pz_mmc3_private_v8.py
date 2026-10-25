"""Run the existing oversized port preparation only in an external fresh tree."""
from pathlib import Path
import configparser,subprocess,sys,json,hashlib
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
O=D/'ryu-head-oversized-mmc3-v8';O.mkdir(exist_ok=False);source=O/'source'
original=R/'tools/prepare_mmc3_oversized.py';text=original.read_text()
anchor='    released=args.reference_rom.resolve()'
assert text.count(anchor)==1
addition='''    # Current linked assets omitted by the old hardcoded packing list.
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
script=O/'prepare-current.py';script.write_text(text)
ns=dict(__name__='_private_prepare',__file__=str(original));exec(compile(text,str(script),'exec'),ns)
ns['ROOT']=R;ns['OUT']=source;sys.argv=[str(script),'--reference-rom',str(D/'ryu-head-candidate-v5/candidate.nes')];ns['main']()
f=source/'src/roll_fast_render.s';t=f.read_text();a='Legacy:jmp NativeGoombaRender';assert t.count(a)==1
t=t.replace(a,".if ::MAPPER_MMC3\nLegacy:jmp MetaspriteRenderLoop\n.else\n"+a+"\n.endif");f.write_text(t)
f=source/'src/tmnt_hud_world.s';t=f.read_text();a='.proc TnHudWorldRender';assert t.count(a)==1
t=t.replace(a,a+"\n.if ::MAPPER_MMC3\n farcall MetaspriteRenderLoop,jmp\n.else");a=' jmp TnFastWorldRender::Legacy\n.endproc';assert t.count(a)==1
t=t.replace(a,' jmp TnFastWorldRender::Legacy\n.endif\n.endproc');f.write_text(t)

import importlib.util
module=D/'extend_pz_mmc3_v8.py'
spec=importlib.util.spec_from_file_location('port_storage',module);extension=importlib.util.module_from_spec(spec);spec.loader.exec_module(extension);extension.apply(source)
config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini')
options={k:v for section in config.values()for k,v in section.items()};options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
rom=O/'candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
with(O/'build.log').open('w')as log:p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
report=dict(compiled=p.returncode==0,exit=p.returncode,scope='Compatibility compilation of existing oversized-MMC3 preparation with adopted PZ sources, entirely external. Native behavior/menu/CHR/lag and release admission remain separate; no public install.')
if p.returncode==0:report['ROM_sha256']=hashlib.sha256(rom.read_bytes()).hexdigest()
(O/'proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));print((O/'build.log').read_text()[-1800:]if p.returncode else'')
raise SystemExit(p.returncode)


