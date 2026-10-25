from pathlib import Path
import hashlib,importlib.util,json,re
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-flag-fix-v23';T=O/'cold-entries-v2';T.mkdir(exist_ok=False);ROM=O/'candidate.nes'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=D/'ryu-head-oversized-mmc3-v12/entry-all-v2';old=json.loads((source/'results.json').read_text());assert len(old['results'])==37
raw=O/'source/chr/characters/oversized-raw.chr';assert sha(raw)==sha(D/'ryu-head-oversized-mmc3-v12/source/chr/characters/oversized-raw.chr')
sp=importlib.util.spec_from_file_location('runner',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(sp);sp.loader.exec_module(runner)
report=dict(complete=False,passed=False,goal_complete=False,ROM_sha256=sha(ROM),results={},scope='All37 actual cold controller selections, variants,140 native gameplay frames, full boot CHR-RAM, VBlank/protected native cache bytes and NMI/bank/SMC checks on the private flag fix. Native assertions unchanged; deterministic power-on and actual post-boot menu readiness are pinned, with a5second host-only callback budget. Parent failures retained. Separate from full campaigns and independent full-level replay.')
for name in old['results']:
 key=name.lower().replace(' ','-');base=source/key/'entry.lua'
 if not base.exists():
  # The original runner uses canonical case keys recorded by its directories.
  candidates=[p for p in source.glob('*/entry.lua')if p.read_text().startswith('TARGET_NAME='+json.dumps(name))]
  assert len(candidates)==1,(name,candidates);base=candidates[0]
 out=T/base.parent.name;out.mkdir();text=base.read_text();text,n=re.subn(r'^RAW_CHR=.*$', 'RAW_CHR='+json.dumps(raw.as_posix()),text,count=1,flags=re.M);assert n==1
 text=text.replace('b.start=frame>=150','b.start=frame>=180').replace("if frame>=60 and r('CrossoverMenuState')==2","if frame>=180 and r('CrossoverMenuState')==2")
 script=out/'entry.lua';script.write_text(text);runner.ROOT=out
 code=runner.run(script,ROM,timeout=90,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false','--debug.scriptWindow.scriptTimeout=5','--doNotSaveSettings']);report['results'][name]=dict(exit=code,script_sha256=sha(script));(T/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(name=name,exit=code)),flush=True)
 assert code==0,name
report.update(complete=True,passed=True);(T/'proof.json').write_text(json.dumps(report,indent=2));(T/'progress.json').write_text(json.dumps(report,indent=2))
