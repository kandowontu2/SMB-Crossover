"""Read-only first-enemy source-shot ingress/return observer on current nightly."""
from pathlib import Path
import json
import check_arthur_side_clamp_1101_v8 as C
from prepare_selected_native_packet_v1 import prepare
P=C.P;O=P.O;R=P.R


def main():
 rom=R/'build/excitebike-pose-1101-v3/current3.nes';digest='37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c';assert P.sha(rom)==digest
 b=C.scoped_load(rom);at=C.location(b,'ArHostShotContacts');target=C.address(b,'ArNativeShotContact');raw=b['raw']
 hits=[i for i in range(144)if raw[at+i:at+i+3]==bytes([0x20,target&255,target>>8])];assert len(hits)==1
 returnpc=C.address(b,'ArHostShotContacts')+hits[0]+3;assert raw[at+hits[0]+3]==0x90
 ref=R/'build/arthur-full11-combat-1102-v13/native/controller.lua';t=ref.read_text()
 marker="local injuryLog=assert(io.open(OUTPUT..'injury.csv','w'))"
 assert t.count(marker)==1
 extra='''local ingress,contactClear,contactSet={},0,0
local pendingContact=nil
local detailRows=0
local contacts=assert(io.open(OUTPUT..'shot-contact.csv','w'))
contacts:write('event,frame,player_x,player_y,shot,shot_flags,shot_kind,shot_world_x,shot_screen_x,shot_screen_y,shot_source_y,shot_source_page,enemy,enemy_id,enemy_world_x,enemy_y,enemy_state,enemy_flag,carry,sp\\n')
local lifetime={}
for i=1,3 do lifetime[i]={samples=0,active_frames=0}end
'''
 t=t.replace(marker,extra+marker,1)
 marker='local function finish(passed,reason)\n';assert t.count(marker)==1
 t=t.replace(marker,marker+''' contacts:close()
 local out={};for k,v in pairs(ingress)do out[#out+1]=string.format('"%s":%d',k,v)end
 local lives={}
 for i=1,3 do local q=lifetime[i];lives[#lives+1]=string.format('{"slot":%d,"samples":%d,"active_frames":%d,"kind":%d,"first_x":%d,"first_y":%d,"last_x":%d,"last_y":%d,"minimum_x":%d,"maximum_x":%d,"minimum_y":%d,"maximum_y":%d}',i,q.samples,q.active_frames,q.kind or 0,q.firstX or 0,q.firstY or 0,q.lastX or 0,q.lastY or 0,q.minX or 0,q.maxX or 0,q.minY or 0,q.maxY or 0)end
 local f=assert(io.open(OUTPUT..'weapon-ingress.json','w'));f:write(string.format('{"source_lance64":true,"ingress":{%s},"contact_carry_clear":%d,"contact_carry_set":%d,"shot_lifetimes":[%s]}',table.concat(out,','),contactClear,contactSet,table.concat(lives,',')));f:close()
''',1)
 marker="emu.addMemoryCallback(function()\n local pc=assert(L.ArTakeHit)";assert t.count(marker)==1
 hook='''local function matches(pc,bank)
 if pc<0xa000 then return true end
 return (pc<0xc000 and r('CurrentBank')or r('CurrentBankC'))==(bank|128)
end
local function detail(event,slot,enemy,carry,sp)
 if detailRows>=160 or wx()<200 or wx()>380 then return end
 detailRows=detailRows+1
 contacts:write(string.format('%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\\n',event,frame,wx(),r('Player_Y_Position'),slot,r('ArR_04F0',slot),r('ArR_0631',slot),r('ArR_05AF',slot)+256*r('ArR_0583',slot),r('ArR_0554',slot),r('ArR_0509',slot),r('ArR_0599',slot),r('ArR_056D',slot),enemy,r('Enemy_ID',enemy),r('Enemy_X_Position',enemy)+256*r('Enemy_PageLoc',enemy),r('Enemy_Y_Position',enemy),r('Enemy_State',enemy),r('Enemy_Flag',enemy),carry,sp))
end
for _,name in ipairs({'NrWeapons','HuWeapons','ArHostShotContacts','ArNativeLance','ArNativeDagger','ArNativeMarkShotHit','HandleEnemyFBallCol','ShellOrBlockDefeat'})do
 local pc,bank=assert(L[name],name),assert(B[name],name)
 emu.addMemoryCallback(function()
  if phase~='play' or not matches(pc,bank)then return end
  ingress[name]=(ingress[name]or 0)+1
  if name=='ArHostShotContacts' then
   local s=emu.getState()
   for i=1,3 do if r('ArR_04F0',i)~=0 then detail('host',i,0,-1,assert(s['cpu.sp']))end end
  end
 end,emu.callbackType.exec,pc)
end
emu.addMemoryCallback(function()
 if phase~='play' or not matches(assert(L.ArNativeShotContact),assert(B.ArNativeShotContact))then return end
 local s=emu.getState();local sp=assert(s['cpu.sp']);local ret=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 if ret~=RETURN_PC or r('CurrentBank')~=154 then return end
 local slot=assert(s['cpu.y']);local enemy=r('ArDrawPart')
 ingress.ArNativeShotContact=(ingress.ArNativeShotContact or 0)+1
 pendingContact={sp=(sp+2)&255,slot=slot,enemy=enemy}
 detail('source',slot,enemy,-1,sp)
end,emu.callbackType.exec,assert(L.ArNativeShotContact))
emu.addMemoryCallback(function()
 if not pendingContact or phase~='play' or r('CurrentBank')~=154 then return end
 local s=emu.getState();if assert(s['cpu.sp'])~=pendingContact.sp then return end
 local c=assert(s['cpu.ps'])&1
 if c==0 then contactClear=contactClear+1 else contactSet=contactSet+1 end
 detail('return',pendingContact.slot,pendingContact.enemy,c,s['cpu.sp']);pendingContact=nil
end,emu.callbackType.exec,RETURN_PC)
'''.replace('RETURN_PC',str(returnpc))
 t=t.replace(marker,hook+marker,1)
 marker="  local x,y=wx(),r('Player_Y_Position')\n";assert t.count(marker)==1
 t=t.replace(marker,marker+'''  for i=1,3 do
   local q=lifetime[i];q.samples=q.samples+1
   if r('ArR_04F0',i)~=0 then
    local sx,sy=r('ArR_05AF',i)+256*r('ArR_0583',i),r('ArR_0509',i)
    q.active_frames=q.active_frames+1;q.kind=r('ArR_0631',i)
    if not q.firstX then q.firstX,q.firstY=sx,sy;q.minX,q.maxX,q.minY,q.maxY=sx,sx,sy,sy end
    q.lastX,q.lastY=sx,sy;q.minX,q.maxX=math.min(q.minX,sx),math.max(q.maxX,sx);q.minY,q.maxY=math.min(q.minY,sy),math.max(q.maxY,sy)
   end
  end
  if age>=700 then
   finish((ingress.HandleEnemyFBallCol or 0)>0 and r('NumberofLives')==startLives,'Targeted firstenemy source-lance/native hit observation');return
  end
''',1)
 prepare(O/'weapon-ingress',rom,t,[Path(__file__),ref,O/'weapon-contact-CPU.json'],expected=digest,timeout=150,allow_interactive=True,scope='Read-only real Main/NrWeapons/HuWeapons/Arthur sourcecontact/return observer on unchanged distance24 firstenemy stopx247 controller. Independently bounded700playframes; require genuine native enemy hit for pass, retain originalcampaignnegative. No shot/contact/outcome/RAMseeds, noROMchanges, atmost160detailCSVrows and4PNGs.')
 print(json.dumps(dict(ROM_sha256=digest,actual_source_contact_return_PC=hex(returnpc),no_Mesen_launched=True)))


if __name__=='__main__':main()
