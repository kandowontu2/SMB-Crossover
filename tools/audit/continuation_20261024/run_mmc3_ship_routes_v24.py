from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,re,csv
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=D/'mmc3-ship-state-v24/native-routes-v1';O.mkdir(exist_ok=False)
ROM=D/'mmc3-ship-state-v24/candidate.nes';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(ROM)=='66f5b3184f0e8f6238ac6ae3f3f227ef71aca55d5b1ac778c2d98adf95343283'
helper=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('img',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(ROM)
source=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py';text=source.read_text();a="if a.name=='roll':";assert text.count(a)==1;text=text.replace(a,"if a.name=='roll' and rom.read_bytes()[6]>>4!=4:")
assert text.count("if frame<60 or frame%12~=0 then return{}end")==1
text=text.replace("if frame<60 or frame%12~=0 then return{}end","if frame<180 or frame%12~=0 then return{}end")
anchor="'--output',str(out),str(script),str(rom),'--timeout'";assert text.count(anchor)==1;text=text.replace(anchor,"'--emulator','C:\\\\Users\\\\kando\\\\Videos\\\\SMB Crossover Archive\\\\2026-10-24-native-rest-py\\\\mmc3-flag-fix-v23\\\\script-budget-probe-v2\\\\emulator\\\\Mesen.exe','--output',str(out),str(script),str(rom),'--timeout'")
driver=O/'bound-mmc3-runner.py';driver.write_text(text)
cfg=dict(raw_chr=(D/'mmc3-tools-v16/canonical-build/source/chr/characters/oversized-raw.chr').as_posix(),ram=image.ram,nmi=image.hook('NonMaskableInterrupt'),nmi_end=image.hook('NonMaskableInterrupt',delta='last'),irq=image.hook('IrqScrollSplit'),smc_start=int(re.search(r'al ([0-9A-Fa-f]+) \.__SMCCODE_RUN__',ROM.with_suffix('.lbl').read_text())[1],16),masks=image.ram['RgAudioZp']+24,masks_high=image.ram['RgAudioCpuZp']+24,page_lo=image.ram['RgAudioCpuZp']+140,page_high=image.ram['RgAudioZp']+152)
guard=O/'native-guard.lua';guard.write_text('MMC3_ROUTE_GUARD='+im.lua(cfg)+'\n'+(D/'mmc3_full_route_cache_guard_v3.lua').read_text())
source=json.loads((P/'full-roster-aggregate-v1/proof.json').read_text());report=dict(ROM_sha256=sha(ROM),complete=False,passed=False,goal_complete=False,runs=[],scope='Fresh native MMC3 full-level controller discoveries with mapper-specific cache/CHR/bank guards. MMC5-only Roll/CHR observers are deliberately inapplicable, not silently treated as passed. Independent physical replays and full pose/source-fidelity admission remain required.')
for name,mode in [('vic','easy'),('octopus','easy'),('twinbee','easy'),('pentarou','easy')]:
 row=next(r for r in source['runs']if r['identity']==name and r['mode']==mode);base=Path(row['discovery']).parent
 policy=O/(name+'-'+mode+'-policy.lua');policy.write_text('dofile('+im.lua(guard.as_posix())+')\n'+(base/'policy.lua').read_text());out=O/(name+'-'+mode)
 with(O/(name+'-'+mode+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(driver),name,'--rom',str(ROM),'--output',str(out),'--mapper','mmc3','--behavior',mode,'--frames','16000','--capture','12','--policy',str(policy),'--timeout','240'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};result=m.get('result')or{};guard_path=out/'mmc3-cache-guard.json';g=json.loads(guard_path.read_text())if guard_path.exists()else{}
 row=dict(identity=name,mode=mode,folder=str(out),exit=p.returncode,controller_clear=p.returncode==0 and result.get('cleared')is True and result.get('deaths')==0,mapper_guard_passed=g.get('passed')is True,frames=result.get('frames'),failure=result.get('failure'),manifest_sha256=sha(path)if path.exists()else None,mapper_guard_sha256=sha(guard_path)if guard_path.exists()else None)
 trace=list(csv.DictReader((out/'trace.csv').open()))if(out/'trace.csv').exists()else[]
 active=[z for z in trace if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['world']==z['level']=='0'];pairs=[(a,b)for a,b in zip(active,active[1:])if int(b['frame'])==int(a['frame'])+1]
 if pairs:
  row['max_world_step']=max(abs(int(b['x'])-int(a['x']))for a,b in pairs);row['min_camera_step']=min(int(b['camera'])-int(a['camera'])for a,b in pairs);row['max_camera_step']=max(int(b['camera'])-int(a['camera'])for a,b in pairs);row['motion_passed']=row['max_world_step']<=8 and row['min_camera_step']>=0 and row['max_camera_step']<=4
 else:row['motion_passed']=False
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report['complete']=True;report['passed']=all(r['controller_clear']and r['mapper_guard_passed']and r['motion_passed']for r in report['runs']);(O/'proof.json').write_text(json.dumps(report,indent=2));(O/'progress.json').write_text(json.dumps(report,indent=2))
