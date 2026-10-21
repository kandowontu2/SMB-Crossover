"""Fresh H power-on fixed candidates using earlier ordinary Pit/Rygar input tapes."""
from pathlib import Path
import hashlib,importlib.util,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-pit-rygar-h-eg'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OBSERVER=r'''local H=EXPANDED_HOOKS
local frame,poll=0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function block(x,y)
 if y<32 or y>=240 then return 0 end
 return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)
end
local f=assert(io.open(ROSTER_CONFIG.out..'actual-expanded-launches.csv','w'))
f:write('frame,poll,cycle,event,x,y,yHigh,state,held,ab,previousRg,previousAB,footL,footR,spring,springForce,crouch,power,actors\n')
for name,h in pairs(H)do
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual H expanded hook8 '..name)end
  if r('GameEngineSubroutine')~=8 or r('SelectedCharacter')~=ROSTER_CONFIG.character then return end
  if name=='Entry'and not(r('SavedJoypadBits')&128~=0 and r('RgPreviousButtons')&128==0)then return end
  local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position');local actors={}
  for i=0,5 do
   actors[#actors+1]=table.concat({i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_BoundBoxCtrl',i),r('PlatformCollisionFlag',i)},':')
  end
  f:write(table.concat({frame+1,poll,emu.getState()['cpu.cycleCount'],name,x,y,r('Player_Y_HighPos'),r('Player_State'),r('SavedJoypadBits'),r('A_B_Buttons'),r('RgPreviousButtons'),r('PreviousA_B_Buttons'),block(x+2,y+32),block(x+13,y+32),r('JumpspringAnimCtrl'),r('JumpspringForce'),r('RgCrouch'),r('PlayerStatus'),table.concat(actors,';')},',')..'\n');f:flush()
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
emu.addEventCallback(function()poll=poll+1 end,emu.eventType.inputPolled)
return function()return{}end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';rom=cp.parent/'smb-crossover-mmc3.nes';assert sha(rom)=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('pit_rygar_H_EG',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(rom)
 hooks=dict(Entry=image.hook('ExpandedMovement'),AcceptedLaunch=image.hook('AfterJumpVelocity',scope='ExpandedMovement'))
 observer=J/'expanded-launch-observer.lua';observer.write_text('EXPANDED_HOOKS='+im.lua(hooks)+'\n'+OBSERVER)
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total+300000000<80000000000
 prep=dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),ROM_H_sha256=sha(rom),helper_sha256=sha(helper),observer_sha256=sha(observer),hooks=hooks,phase_cap=300000000,reserve=100000000,workspace_before=total,global_cap=80000000000,scope='Two new actual H complete fixed candidates. Earlier GQ ordinary tapes are proposals, not admitted current proofs. Passive observer tables/addresses rebound to actual compiled H; original files remain unchanged. Actual H accepted source launch/entry receipts added. No state/ROM/RAM/register writes, no automatic source-perfect or arsenal/media inference.')
 (J/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n');results=[]
 for ident,name,profile,table in[(6,'pit',3,'BlockBuffer_Mega_X_Adder'),(7,'rygar',6,'BlockBuffer_Samus_X_Adder')]:
  source=R/'build/roster-through-2-2'/f'specialist-gq-{name}-fixed-a-{ident}-v0-mmc3';m=json.loads((source/'manifest.json').read_text());assert m['verified_through_2_2']and m['controller_only']and not m['memory_or_register_writes']
  body=(source/'policy.lua').read_text();binding=dict(tables={n:image.hook(n)for n in[table,'BlockBuffer_SamusBall_X_Adder']},ROM_sha256=sha(rom),profiles=dict(standing=profile,crouch=8),source='Actual H compiled tables and addresses; observation logic ported from earlier GQ, not a source-physics equivalence claim.')
  body,n=re.subn(r'^'+name.upper()+r'_SUPPORT=\{[^\n]+\}',lambda m:name.upper()+'_SUPPORT='+im.lua(binding),body,flags=re.M);assert n==1
  edge={n:image.hook(n)for n in['LandPlyr','DoPlayerSideCheck','StopPlayerMove']};body,n=re.subn(r'^CORNER_HOOKS=\{[^\n]+\}',lambda m:'CORNER_HOOKS='+im.lua(edge),body,flags=re.M);assert n==1
  body='dofile('+im.lua(observer.as_posix())+')\n'+body
  assert not any(t in body for t in['emu.write(','emu.setState(','emu.loadSavestate'])
  policy=J/(name+'-policy.lua');policy.write_text(body)
  bind=J/(name+'-binding.json');bind.write_text(json.dumps(dict(source_manifest_sha256=sha(source/'manifest.json'),source_policy_sha256=sha(source/'policy.lua'),source_inputs_sha256=sha(source/'inputs.csv'),H_policy_sha256=sha(policy),H_tables=binding,H_edges=edge),indent=2)+'\n')
  assert workspace_bytes(R)+100000000<80000000000
  tag='root49-h-'+name+'-eg';out=R/'build/roster-through-2-2'/(tag+'-'+str(ident)+'-v0-mmc3')
  args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(ident),'--mapper','mmc3','--rom',str(rom),'--tag',tag,'--policy',str(policy),'--replay',str(source/'inputs.csv'),'--frames','40000','--timeout','900','--workspace-cap-gb','80']
  (J/(name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
  with(J/(name+'-native.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  a=json.loads((out/'manifest.json').read_text());z=dict(character=name,exit=q.returncode,manifest=str((out/'manifest.json').relative_to(R)),manifest_sha256=sha(out/'manifest.json'),result=a.get('result'),verified=a['verified_through_2_2'],analysis_pending=True,old_ROM=m['rom_sha256'],actual_ROM=a['rom_sha256'])
  results.append(z);(J/'partial.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(z),flush=True)
 (J/'result.json').write_text(json.dumps(dict(results=results,analysis_pending=True,goal_complete=False),indent=2)+'\n')
if __name__=='__main__':main()
