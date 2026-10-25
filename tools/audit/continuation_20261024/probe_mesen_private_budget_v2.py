from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-flag-fix-v23/script-budget-probe-v2';O.mkdir(exist_ok=False);E=O/'emulator';E.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();original=Path('C:/mesen2');settings=original/'settings.json';before=sha(settings);cfg=json.loads(settings.read_text(encoding='utf-8-sig'));files={}
for n in ('Mesen.exe','MesenCore.dll','libSkiaSharp.dll','libHarfBuzzSharp.dll','MesenNesDB.txt'):
 shutil.copy2(original/n,E/n);assert sha(original/n)==sha(E/n);files[n]=sha(E/n)
rom=D/'mmc3-flag-fix-v23/candidate.nes';rows=[]
for seconds in (1,5):
 changed=json.loads(json.dumps(cfg));changed['Debug']['ScriptWindow']['ScriptTimeout']=seconds;(E/'settings.json').write_text(json.dumps(changed,indent=2),encoding='utf-8-sig')
 out=O/str(seconds);out.mkdir();script=out/'probe.lua';script.write_text("local once=false\nemu.addEventCallback(function()if once then return end;once=true;local start=os.clock();while os.clock()-start<1.3 do end;print('HOST_BUDGET_PROBE_FINISHED');emu.stop(0)end,emu.eventType.endFrame)\n")
 with(out/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--emulator',str(E/'Mesen.exe'),'--output',str(out),str(script),str(rom),'--timeout','15','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 text=(out/'host.log').read_text();assert (p.returncode!=0 and'Maximum execution time (1 seconds)'in text)if seconds==1 else(p.returncode==0 and'HOST_BUDGET_PROBE_FINISHED'in text)
 rows.append(dict(callback_host_budget_seconds=seconds,exit=p.returncode,finished='HOST_BUDGET_PROBE_FINISHED'in text))
actual=json.loads((E/'settings.json').read_text(encoding='utf-8-sig'));actual['Debug']['ScriptWindow']['ScriptTimeout']=cfg['Debug']['ScriptWindow']['ScriptTimeout'];assert actual==cfg;assert sha(settings)==before
q=dict(passed=True,user_settings_unchanged=True,identical_emulator_binary_hashes=files,private_emulator=str(E/'Mesen.exe'),only_setting_changed='Debug.ScriptWindow.ScriptTimeout',callback_host_budget_seconds=5,cases=rows,scope='Bounded host-only callback probe proves the portable identical-binary emulator honors the private5second Lua budget. CLI override was ineffective in retained probev1. No emulated clock/frame/ROM/game-state changes or global user-setting changes.');(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
