"""Real cold-entry NMI guards plus a native question-block jump for each body."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--entries',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--after',type=Path)
    p.add_argument('--names',nargs='*');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    if a.after:
        while True:
            q=json.loads(a.after.read_text()) if a.after.exists() else {}
            if q.get('complete') or any(j['name']=='entries' and j['exit']==0 for j in q.get('jobs',[])):break
            time.sleep(2)
    digest=sha(a.rom);entries=json.loads((a.entries/'results.json').read_text());assert entries['rom_sha256']==digest
    assert len(entries['results'])==37,'Do not infer a complete matrix from partial entry results'
    report=dict(passed=False,complete=False,ROM_sha256=digest,runs=[],excluded=[],goal_complete=False,native_workers=1)
    def save():(a.output/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
    template=(ROOT/'tests/full-roster-entry.lua').read_text()
    head='''
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local headContacts,headMinX,headMaxX,headCapture=0,252,252,nil
'''
    template=template.replace('local frame,phase,entered=0,0,nil','local frame,phase,entered=0,0,nil\n'+head)
    old="local function shot(name)local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end"
    new="""local function shot(name)
 if name=='selection' then return end
 local s=emu.getState();assert(s['ppu.frameCount']==frame,'End-frame physical capture identity')
 local b=emu.getScreenBuffer();local f=assert(io.open(OUTPUT..name..'.rgba','wb'))
 for i=1,#b,8 do f:write(string.pack('<I4I4I4I4I4I4I4I4',table.unpack(b,i,i+7)))end
 f:close()
end"""
    assert template.count(old)==1;template=template.replace(old,new)
    old="""  b.right=t>=15 and t<125
  b.b=t>=15 and t<125
  b.a=(t>=30 and t<65)or(t>=95 and t<113)"""
    assert template.count(old)==1;template=template.replace(old,'  b.a=t>=20 and t<70')
    marker="  local t=frame-entered\n  local fc="
    seed="""  local t=frame-entered
  if t==10 then
   for i=0,5 do w('Enemy_Flag',0,i)end
   for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
   w('Player_X_Position',252);w('Player_PageLoc',0);w('MmOldX',252)
   w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0)
   w('Player_X_Speed',0);w('Player_X_Scroll',0);w('PlayerFacingDir',1)
   w('ScreenLeft_X_Pos',128);w('ScreenLeft_PageLoc',0)
   w('ScreenRight_X_Pos',127);w('ScreenRight_PageLoc',1);w('HorizontalScroll',128)
   w('Block_State',0);w('Block_State',0,1);w('BlockBounceTimer',0)
   w('CrossoverBehaviorVersion',HEAD_MODE)
  end
  if t>=12 then
   local x=r('Player_X_Position')+256*r('Player_PageLoc')
   headMinX=math.min(headMinX,x);headMaxX=math.max(headMaxX,x)
   assert(x>=251 and x<=253,'A stationary jump/head bump cannot displace the player: '..TARGET_NAME..' x='..x)
   for i=0,1 do
    if r('Block_State',i)%16==1 and r('Block_Orig_YPos',i)==112 then
     local bx=r('Block_X_Position',i)+256*r('Block_PageLoc',i)
     assert(bx==256,'Bumped question stays on its actual cell: '..TARGET_NAME..' x='..bx)
     headContacts=headContacts+1
     if not headCapture then headCapture=frame+3 end
    end
   end
   if frame==headCapture then shot('head-contact')end
  end
  local fc="""
    assert template.count(marker)==1;template=template.replace(marker,seed)
    start=template.index('  if t==140 then\n');end=template.index('\n  end\n end\n if frame>1800',start)
    template=template[:start]+'''  if t==140 then
   assert(headContacts>0,'Actual question-block head bump executed: '..TARGET_NAME)
   assert(nmis>200 and irqs>100,'Native interrupt path exercised')
   local f=assert(io.open(OUTPUT..'proof.json','w'))
   f:write(string.format('{"passed":true,"name":"%s","seeded_native":true,"mode":%d,"head_contacts":%d,"min_x":%d,"max_x":%d,"NMIs":%d,"IRQs":%d}\\n',TARGET_NAME,HEAD_MODE,headContacts,headMinX,headMaxX,nmis,irqs));f:close()
   emu.stop(0)'''+template[end:]
    save()
    for name,entry in entries['results'].items():
        if a.names and name not in a.names:continue
        if name in ['Vic Viper','Octopus','TwinBee','Pentarou']:
            report['excluded'].append(dict(name=name,reason='Flight family: no underside jump/head-bump move; projectile/flight terrain tests remain separate.'));continue
        assert entry['exit']==0
        folder=a.entries/name.lower().replace(' ','-');source=folder/'entry.lua';assert sha(source)==entry['script_sha256']
        prefix=source.read_text().split('-- Cold controller-only')[0]
        for mode in [0,1]:
            out=a.output/(name.lower().replace(' ','-')+'-'+str(mode));out.mkdir()
            script=out/'run.lua';script.write_text(prefix+'HEAD_MODE='+str(mode)+'\n'+template)
            while True:
                z=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Mesen.exe'\").Count"],capture_output=True,text=True)
                assert z.returncode==0,z.stderr
                if int(z.stdout.strip())<2:break
                time.sleep(2)
            args=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(a.rom.resolve()),'--timeout','60',
                '--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
            with (out/'host.log').open('w') as f:z=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
            report['runs'].append(dict(name=name,mode=mode,exit=z.returncode,script_sha256=sha(script),folder=str(out)))
            save();print(name,mode,z.returncode,flush=True)
            if z.returncode!=0:return 1
    report.update(complete=True,passed=all(r['exit']==0 for r in report['runs']));save()
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
