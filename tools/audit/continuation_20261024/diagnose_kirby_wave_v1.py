from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;rom=R/'build/checkpoints/native-items-px/candidate.nes'
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
q=qualified(rom);out=D/'kirby-wave-diagnosis-v1';out.mkdir(exist_ok=False)
aliases=''.join('L['+json.dumps(k[0])+']='+str(v)+'\n'for k,v in q.items()if len(k)==1 and k[0].startswith('Kb'))
lua=r'''
local frame=0
local trace=assert(io.open(OUTPUT..'wave.csv','w'))
trace:write('frame,tick,x,y,hp,enemyX,enemyY,enemyFlag,enemyState,boxL,boxT,boxR,boxB,type0,shotX0,shotY0,age0,type1,shotX1,shotY1,age1,type2,shotX2,shotY2,age2\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addEventCallback(function()
 frame=frame+1
 if COPY_CASE~=8 or COPY_PHASE~='attack'then return end
 local row={frame,COPY_TICK,r('Player_X_Position'),r('Player_Y_Position'),r('KbHealth'),r('Enemy_X_Position'),r('Enemy_Y_Position'),r('Enemy_Flag'),r('Enemy_State')}
 for i=0,3 do row[#row+1]=emu.read(L.BoundingBox_UL_XPos+4+i,emu.memType.nesDebug)end
 for i=0,2 do row[#row+1]=r('KbShotType',i);row[#row+1]=r('KbShotX',i);row[#row+1]=r('KbShotY',i);row[#row+1]=r('KbShotAge',i)end
 trace:write(table.concat(row,',')..'\n');trace:flush()
 local buf=emu.getScreenBuffer();local f=assert(io.open(OUTPUT..'frame-'..frame..'.rgba','wb'));for i=1,#buf,8 do f:write(string.pack('<I4I4I4I4I4I4I4I4',table.unpack(buf,i,i+7)))end;f:close()
end,emu.eventType.endFrame)
'''
script=out/'run.lua';script.write_text(aliases+lua+'\ndofile('+json.dumps((D/'kirby-copies-v2/easy/run.lua').as_posix())+')\n')
cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(rom),'--timeout','150','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(out/'host.log').write_text(p.stdout+p.stderr);print(p.returncode,(p.stdout+p.stderr)[-800:])
