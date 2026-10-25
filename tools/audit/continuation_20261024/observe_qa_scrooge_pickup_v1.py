from pathlib import Path
import json,hashlib,importlib.util,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';source=P/'remaining-roster-v1/scrooge-easy';O=P/'scrooge-pickup-observer-v1'
# This script is prepared now and must only be launched with a free Mesen slot.
def main():
 O.mkdir(exist_ok=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 h=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('img',h);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(P/'candidate.nes');hook=image.hook('GameLoop',delta='last');assert hook['bytes'][0]==0x60
 lua=r'''
local frame,rows=0,0
local f=assert(io.open(OUTPUT..'committed-items.csv','w'))
f:write('frame,x,y,status,engine,camera,slot,flag,id,kind,state,itemX,itemY,itemYHigh\n')
local cells=assert(io.open(OUTPUT..'cells.csv','w'));cells:write('frame,x,y,worldX,worldY,tile\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function block(x,y)return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
emu.addMemoryCallback(function()
 if frame<600 or emu.convertAddress(OBS_HOOK.address).address//8192~=OBS_HOOK.physical_bank then return end
 for j,v in ipairs(OBS_HOOK.bytes)do assert(emu.read(OBS_HOOK.address+j-1,emu.memType.nesDebug)==v,'Exact actual completed-loop observer hook')end
 local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position');local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 for i=0,5 do
  if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then
   f:write(table.concat({frame,x,y,r('PlayerStatus'),r('GameEngineSubroutine'),camera,i,r('Enemy_Flag',i),r('Enemy_ID',i),r('PowerUpType',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_Y_HighPos',i)},',')..'\n');rows=rows+1
  end
 end
 if frame%60==0 then for wx=320,432,16 do for _,wy in ipairs({80,144})do cells:write(table.concat({frame,x,y,wx,wy,block(wx,wy)},',')..'\n')end end end
end,emu.callbackType.exec,OBS_HOOK.address)
local originalStop=emu.stop
emu.stop=function(code) f:flush();cells:flush();f:close();cells:close();originalStop(code)end
'''
 (O/'observer.lua').write_text('OBS_HOOK='+im.lua(hook)+'\n'+lua)
 t=(source/'run.lua').read_text();a='out='+json.dumps(source.as_posix()+'/');assert t.count(a)==1;t=t.replace(a,'out='+json.dumps(O.as_posix()+'/'))
 assert t.count('replay=nil')==1;t=t.replace('replay=nil','replay='+json.dumps((source/'inputs.csv').as_posix())).replace('capture=12,','capture=0,')
 k=t.index('dofile(');t=t[:k]+'dofile('+json.dumps((O/'observer.lua').as_posix())+')\n'+t[k:];script=O/'run.lua';script.write_text(t)
 with(O/'host.log').open('w')as f:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(O),str(script),str(P/'candidate.nes'),'--timeout','180','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==1
 assert json.loads((O/'result.json').read_text())==json.loads((source/'result.json').read_text())
 for n in ('inputs.csv','trace.csv'):assert(O/n).read_bytes()==(source/n).read_bytes(),n
 q=dict(expected_failure_reproduced=True,read_only=True,ROM_sha256=sha(P/'candidate.nes'),exact_parent_inputs_and_CPU_trace=True,source_failure_manifest_sha256=sha(source/'manifest.json'),hook=hook,scope='Read-only committed-loop powerup/map observation of the failed Scrooge route. This receipt reproduces the failure, it does not certify a clear or identify the cause by assumption.')
 (O/'observation.json').write_text(json.dumps(q,indent=2));print(json.dumps(q))
if __name__=='__main__':main()
