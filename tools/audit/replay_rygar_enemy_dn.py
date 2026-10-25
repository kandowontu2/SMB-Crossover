"""Independently replay the current first-two-level route and inspect1-3 injury."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'rygar-enemy-replay-dn'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not O.exists();O.mkdir()
    p=V/'agent49g-samus-crouch-fix-proposal-b/image.py';s=importlib.util.spec_from_file_location('rygar_dn_image',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
    rom=R/'build/checkpoints/water-visible-cw/build/smb-crossover-mmc3.nes';im=a.Image(rom)
    policy=O/'policy.lua';hook=im.hook('InjurePlayer')
    text='local H='+a.lua(hook)+'\n'+r'''
local frame=0
local f=assert(io.open(ROSTER_CONFIG.out..'enemy-observer.csv','w'))
f:write('frame,event,playerX,playerY,playerYHigh,playerState,playerVY,slot,kind,flag,state,x,y,yHigh,injury\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function snap(event)
 if frame<8660 then return end
 for i=0,5 do
  f:write(table.concat({frame,event,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('Player_Y_Speed'),i,r('Enemy_ID',i),r('Enemy_Flag',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_Y_HighPos',i),r('InjuryTimer')},',')..'\n')
 end
 f:flush()
end
emu.addMemoryCallback(function()
 local p=emu.convertAddress(H.address)
 if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=H.physical_bank then return end
 for i,v in ipairs(H.bytes)do assert(emu.read(H.address+i-1,emu.memType.nesDebug)==v,'Actual current injury entry')end
 snap('injury-slot'..r('ObjectOffset'))
end,emu.callbackType.exec,H.address)
emu.addEventCallback(function()snap('input')end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
'''
    text+='return assert(dofile('+json.dumps((R/'tools/playthroughs/rygar_pipe_gap_dm.lua').as_posix())+'))\n';policy.write_text(text,encoding='utf-8')
    source=R/'build/roster-through-2-2/root-rygar-retime-dm-7-v0-mmc3'
    command=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','7','--tag','root-rygar-enemy-proof-dn','--mapper','mmc3','--rom',str(rom),
        '--policy',str(policy),'--replay',str(source/'inputs.csv'),'--frames','8785','--timeout','150','--workspace-cap-gb','100']
    (O/'binding.json').write_text(json.dumps(dict(ROM_sha256=sha(rom),input_sha256=sha(source/'inputs.csv'),policy_sha256=sha(policy),command=command,
        scope='Ordinary fixed controller replay; passive current-byte/physical-bank injury and actor observer. Expected1-3 death, not a through2-2 clear.'),indent=2)+'\n',encoding='utf-8')
    with(O/'host.log').open('wb')as log:result=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
    out=R/'build/roster-through-2-2/root-rygar-enemy-proof-dn-7-v0-mmc3';manifest=json.loads((out/'manifest.json').read_text())
    assert manifest['result']['frames']==8785 and manifest['result']['failure']=='death'
    assert(source/'trace.csv').read_bytes()==(out/'trace.csv').read_bytes(),'Every physical trace row including cycles'
    assert(source/'inputs.csv').read_bytes()==(out/'inputs.csv').read_bytes()
    report=dict(status='PASS_LITERAL_FIXED_CURRENT_RYGAR_ROUTE_THROUGH1_2_EXPECTED1_3_DEATH',native_exit=result.returncode,
        ROM_sha256=sha(rom),frames=8785,trace_sha256=sha(out/'trace.csv'),inputs_sha256=sha(out/'inputs.csv'),stage_entries=manifest['result']['stage_entries'],
        observer_sha256=sha(out/'enemy-observer.csv'),full_frame_audit=True,verified_through_2_2=False,goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
