from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;rom=R/'build/checkpoints/native-items-px/candidate.nes'
source=D/'health-food-v1/chip-easy/run.lua';t=source.read_text();old='["kind"]=0,["health"]=3';assert t.count(old)==2
# Change only the second real block's expected reveal, preserving its native
# health outcome. No scene-power seed is added; parent should reveal0, not1.
start=t.index('["steps"]=');a=t[:start];b=t[start:];pos=b.index(old);b=b[:pos]+b[pos:].replace(old,'["kind"]=1,["health"]=3',1);t=a+b
out=D/'chip-natural-flower-parent-v1';out.mkdir(exist_ok=False);script=out/'run.lua';script.write_text(t)
cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(rom),'--timeout','60','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(out/'host.log').write_text(p.stdout+p.stderr)
print(p.returncode,(p.stdout+p.stderr)[-1000:])
