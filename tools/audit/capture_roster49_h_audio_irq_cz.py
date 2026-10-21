"""Ordinary stationary Samus firing smoke and passive private-H audio/ISR capture."""
from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-audio-scan-h';J=H/'native-irq-cz'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''dofile(IDENTITY)
local H=AUDIO_HOOKS
local frame,active,serial,writes,offset,isrSerial=0,nil,0,0,0,0
local isrs,returns={},{}
local ev=assert(io.open(ROSTER_CONFIG.out..'audio-native.jsonl','w'))
local raw=assert(io.open(ROSTER_CONFIG.out..'audio-native.ram','wb'))
local wr=assert(io.open(ROSTER_CONFIG.out..'audio-writes.bin','wb'))
local hw=assert(io.open(ROSTER_CONFIG.out..'audio-hardware.jsonl','w'))
local function phys(pc)local p=emu.convertAddress(pc);return p and p.memType==emu.memType.nesPrgRom and p.address//8192 or -1 end
local function guard(h)
 if phys(h.address)~=h.physical_bank then return false end
 for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Private H actual entry8')end
 return true
end
local function snapshot(event,name,id)
 local s=emu.getState();local data={}
 for a=0,2047 do data[#data+1]=string.char(emu.read(a,emu.memType.nesDebug))end
 for a=0x6000,0x7fff do data[#data+1]=string.char(emu.read(a,emu.memType.nesDebug))end
 raw:write(table.concat(data));raw:flush()
 ev:write(string.format('{"event":"%s","name":"%s","id":%d,"call":%d,"frame":%d,"cycle":%d,"PC":%d,"A":%d,"X":%d,"Y":%d,"P":%d,"SP":%d,"bank8":%d,"bankA":%d,"bankC":%d,"bankE":%d,"ramOffset":%d,"ramBytes":10240,"writeCount":%d}\n',event,name,id,active.id,frame,s['cpu.cycleCount'],s['cpu.pc'],s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps'],s['cpu.sp'],phys(0x8000),phys(0xa000),phys(0xc000),phys(0xe000),offset,writes))
 ev:flush();offset=offset+10240
end
emu.addMemoryCallback(function(a,v)
 if not active then return end
 wr:write(string.pack('<I2I1',a,v));writes=writes+1
end,emu.callbackType.write,0,0xffff)
emu.addMemoryCallback(function(a,v)
 if not active then return end
 hw:write(string.format('{"call":%d,"cycle":%d,"address":%d,"value":%d}\n',active.id,emu.getState()['cpu.cycleCount'],a,v))
end,emu.callbackType.read,0x2000,0x5fff)
emu.addMemoryCallback(function()
 if frame<540 or not guard(H.Audio)then return end
 assert(not active,'No recursive private H AudioUpdate')
 local s=emu.getState();local sp=s['cpu.sp'];local pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 local bytes={};for i=0,7 do bytes[i+1]=emu.read(pc+i,emu.memType.nesDebug)end
 assert(phys(pc)>=0,'AudioUpdate actual fixed ROM caller')
 serial=serial+1;active={id=serial,pc=pc,SP=(sp+2)&255,bank=phys(pc),bytes=bytes};assert(#isrs==0,'No prior unmatched ISR')
 snapshot('audio-entry','AudioUpdate',serial)
 if returns[pc]then return end;returns[pc]=true
 emu.addMemoryCallback(function()
  if not active or active.pc~=pc or active.SP~=emu.getState()['cpu.sp']or active.bank~=phys(pc)then return end
  for i,b in ipairs(active.bytes)do assert(emu.read(pc+i-1,emu.memType.nesDebug)==b,'Private H actual return8/SP/bank')end
  assert(#isrs==0,'All child ISR returns before AudioUpdate return')
  snapshot('audio-return','AudioUpdate',active.id);active=nil;wr:flush();hw:flush()
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,H.Audio.address)
local function enter(name)
 local h=H[name]
 emu.addMemoryCallback(function()
  if not active or not guard(h)then return end
  isrSerial=isrSerial+1;isrs[#isrs+1]={name=name,id=isrSerial};snapshot('isr-entry',name,isrSerial)
 end,emu.callbackType.exec,h.address)
 local last=H[name..'End']
 emu.addMemoryCallback(function()
  if not active or not guard(last)then return end
  local z=isrs[#isrs];assert(z and z.name==name,'Actual nested ISR name/depth')
  snapshot('isr-pre-RTI',name,z.id);isrs[#isrs]=nil
 end,emu.callbackType.exec,last.address)
end
enter('NMI');enter('IRQ')
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
return function(c)return{b=c.poll%8<4}end
'''
def main():
 assert not J.exists();J.mkdir()
 build=H/'build-review.json';assert sha(build)=='b3c597eecd63eaaab3b15fad6e31766d8c051d2413a6e92536b49420b1a0e18b'
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';s=importlib.util.spec_from_file_location('capture_H',helper);im=importlib.util.module_from_spec(s);s.loader.exec_module(im);image=im.Image(H/'source/build/smb-crossover-mmc3.nes')
 hooks=dict(Audio=image.hook('AudioUpdate'),NMI=image.hook('NonMaskableInterrupt'),IRQ=image.hook('IrqScrollSplit'),NMIEnd=image.hook('NonMaskableInterrupt',delta='last'),IRQEnd=image.hook('IrqScrollSplit',delta='last'));assert hooks['NMIEnd']['bytes'][0]==hooks['IRQEnd']['bytes'][0]==0x40
 source=R/'build/roster-through-2-2/root49-g-samus-clock-c-2-v0-mmc3';inputs=list(csv.DictReader((source/'inputs.csv').open(newline='')));prefix=J/'prefix-540.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(inputs[:540])
 identity=V/'root49-current-c-transfers-a/identity.lua';policy=J/'policy.lua';policy.write_text('AUDIO_HOOKS='+im.lua(hooks)+'\n'+BODY.replace('dofile(IDENTITY)','dofile('+im.lua(identity.as_posix())+')'))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);owned=sum(p.stat().st_size for p in H.rglob('*')if p.is_file());assert total+120000000<80000000000 and owned+120000000+50000000<300000000
 pre=dict(script_sha256=sha(__file__),build_review_sha256=sha(build),ROM_sha256=sha(image.path),policy_sha256=sha(policy),prefix_sha256=sha(prefix),hooks=hooks,dependencies={str(p.relative_to(R)):sha(p)for p in [helper,identity,source/'manifest.json',source/'inputs.csv']},phase_before=owned,phase_cap=300000000,reserve=50000000,workspace_before=total,global_cap=80000000000,scope='Ordinary power-on Samus selection followed by stationary B pulses, no emulated state/ROM/RAM/register/mapper writes. Passive complete AudioUpdate entry/return and real child NMI/IRQ entry/preRTI snapshots, complete ordered writes and hardware reads. Frame1100 stop is intentional partial smoke, not a full route/acquisition/media claim.')
 (J/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
 tag='root49-h-samus-audio-cz';args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(image.path),'--tag',tag,'--policy',str(policy),'--prefix',str(prefix),'--frames','1100','--timeout','240','--workspace-cap-gb','80'];(J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2'/(tag+'-2-v0-mmc3');m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,result=m.get('result'),manifest_sha256=sha(out/'manifest.json'),native_log_sha256=sha(J/'native.log'),preparation_sha256=sha(J/'preparation.json'),native_directory=str(out.relative_to(R)),analysis_pending=True,expected_partial=True,main_changed=False,goal_complete=False)
 (J/'native-result.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
