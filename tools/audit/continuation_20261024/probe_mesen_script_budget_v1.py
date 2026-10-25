from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-flag-fix-v23/script-budget-probe-v1';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();settings=Path('C:/mesen2/settings.json');before=sha(settings)
rom=D/'mmc3-flag-fix-v23/candidate.nes';rows=[]
for seconds in (1,5):
 out=O/str(seconds);out.mkdir();script=out/'probe.lua';script.write_text("local once=false\nemu.addEventCallback(function()if once then return end;once=true;local start=os.clock();while os.clock()-start<1.3 do end;print('HOST_BUDGET_PROBE_FINISHED');emu.stop(0)end,emu.eventType.endFrame)\n")
 with(out/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(rom),'--timeout','15','--option=--debug.scriptWindow.scriptTimeout='+str(seconds),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 text=(out/'host.log').read_text();assert (p.returncode!=0 and 'Maximum execution time (1 seconds)'in text)if seconds==1 else(p.returncode==0 and'HOST_BUDGET_PROBE_FINISHED'in text)
 rows.append(dict(callback_host_budget_seconds=seconds,exit=p.returncode,finished='HOST_BUDGET_PROBE_FINISHED'in text))
assert sha(settings)==before
q=dict(passed=True,user_settings_unchanged=True,cases=rows,scope='Bounded host-only Lua callback budget probe at the first frame. Confirms per-process override support without changing emulator instructions/frame bounds, ROM or game state. Not gameplay qualification.');(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
