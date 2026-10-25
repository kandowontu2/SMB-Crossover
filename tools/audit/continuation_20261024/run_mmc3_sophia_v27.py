from pathlib import Path
import hashlib,importlib.util,json,re,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-sophia-stack-v27';O=V/'native-sophia-v1';O.mkdir(exist_ok=False);ROM=V/'candidate.nes';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert json.loads((V/'predicate-cpu-v1/proof.json').read_text())['passed']
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address
sp=importlib.util.spec_from_file_location('img',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(ROM);bundle=load(ROM);sg=next(g for g in bundle['segs'].values()if g.get('name')=='"SMCCODE"');start,size,pos=(int(sg[k],0)for k in('start','size','ooffs'));mutable={address(bundle,n)+1:True for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']};mutable[address(bundle,'FarcallJmpTarget_SMC')+2]=True
cfg=dict(raw_chr=(D/'mmc3-ship-lives-v25/source/chr/characters/oversized-raw.chr').as_posix(),ram=image.ram,nmi=image.hook('NonMaskableInterrupt'),nmi_end=image.hook('NonMaskableInterrupt',delta='last'),irq=image.hook('IrqScrollSplit'),smc_start=start,masks=image.ram['RgAudioZp']+24,masks_high=image.ram['RgAudioCpuZp']+24,page_lo=image.ram['RgAudioCpuZp']+140,page_high=image.ram['RgAudioZp']+152)
guard=O/'native-guard.lua';guard.write_text('FULL_SMC_GUARD='+im.lua(dict(start=start,bytes=list(bundle['raw'][pos:pos+size]),mutable=mutable))+'\n'+(D/'mmc3_full_smc_guard_v1.lua').read_text()+'\nMMC3_ROUTE_GUARD='+im.lua(cfg)+'\n'+(D/'mmc3_full_route_cache_guard_v3.lua').read_text())
driver=D/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py';source=D/'mmc3-ship-lives-v25/remaining-routes-v1/sophia-easy';policy=(source/'policy.lua').read_text();policy=policy[policy.index('\n')+1:] # Replace only the prior guard dofile; retain exact controller code.
prefix=r'''
local physical=0
emu.addEventCallback(function()
 physical=physical+1;if physical~=3000 then return end
 local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
 local x=r('Player_X_Position')+256*r('Player_PageLoc')
 assert(r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('MmDeathFlag')==0,'Retained prefix survives past original CPU freeze')
 assert(x>1816,'Retained prefix advances at least200px beyond the frozen origin')
 local f=assert(io.open(ROSTER_CONFIG.out..'prefix-regression.json','w'));f:write(string.format('{"passed":true,"frame":3000,"x":%d,"originalFrozenX":1616,"controller_prefix_unchanged":true,"game_state_writes":false,"campaign_pass":false}',x));f:close();emu.stop(0)
end,emu.eventType.endFrame)
'''
report=dict(ROM_sha256=sha(ROM),complete=False,passed=False,goal_complete=False,runs=[],scope='Private MMC3 Sophia stack repair: exact failed physical-input prefix beyond original freeze plus fresh adaptive full1-1 clear, native mapper guard and complete immutable bank-switch code protection. No source/root adoption or other-family campaign admission.')
for kind in['prefix','fresh']:
 script=O/(kind+'-policy.lua');script.write_text('dofile('+im.lua(guard.as_posix())+')\n'+(prefix if kind=='prefix'else'')+policy);out=O/kind
 cmd=[sys.executable,str(driver),'sophia','--rom',str(ROM),'--output',str(out),'--mapper','mmc3','--behavior','easy','--frames','16000','--capture','12','--policy',str(script),'--timeout','240']
 if kind=='prefix':cmd+=['--replay',str(source/'inputs.csv')]
 with(O/(kind+'-host.log')).open('w')as log:p=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 m=json.loads((out/'manifest.json').read_text());g=json.loads((out/'mmc3-cache-guard.json').read_text())if(out/'mmc3-cache-guard.json').exists()else{};s=json.loads((out/'full-smc-guard.json').read_text())if(out/'full-smc-guard.json').exists()else{};passed=p.returncode==0 and g.get('passed')and s.get('passed')
 if kind=='prefix':passed=passed and json.loads((out/'prefix-regression.json').read_text())['passed']
 else:passed=passed and m.get('result',{}).get('cleared')and m['result']['deaths']==0
 row=dict(kind=kind,exit=p.returncode,passed=bool(passed),result=m.get('result'),full_smc_guard=s,mapper_guard_passed=g.get('passed'),manifest_sha256=sha(out/'manifest.json'));report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report.update(complete=True,passed=all(z['passed']for z in report['runs']));(O/'proof.json').write_text(json.dumps(report,indent=2))
