"""Prepare a tiny actual earned-drop call/write diagnostic, not a full profile."""
from pathlib import Path
import argparse,hashlib,json,re,shutil
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OBSERVER=r'''
local T=FINAL_ROLL_DROP_TRACE
local D=FINAL_ROLL_ITEMS.ram
local tick,owner=0,'outside'
local calls,births,writes={},{},{}
local first=nil
local function read(n,i)return emu.read(D[n]+(i or 0),emu.memType.nesDebug)end
local function page(pc)return emu.convertAddress(pc).address//8192 end
local function j(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=j(x)end;return'['..table.concat(t,',')..']'end
  for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..j(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function exec(n,fn)local h=T.hooks[n];emu.addMemoryCallback(function()if page(h.address)==h.bank then fn()end end,emu.callbackType.exec,h.address)end
local function active()return read('SelectedCharacter')==9 and read('RlVariant')==1 and read('GameEngineSubroutine')==8 and read('OperMode_Task')==3 end
exec('GameLoop',function()if active()then tick=tick+1;owner='before-global'end end)
exec('Z2UpdateDropsGate',function()if active()then owner='object-global'end end)
exec('RlWeapons',function()if active()then owner='Roll-own'end end)
exec('InventoryUpdateDrops',function()
 if not active()then return end
 local s=emu.getState();local actors={};for i=0,3 do actors[#actors+1]={slot=i,kind=read('InvDropKind',i),age=read('InvDropAge',i)+256*read('InvDropAgeHi',i),y=read('InvDropY',i)}end
 calls[#calls+1]={tick=tick,owner=owner,pc=s['cpu.pc'],bank=page(s['cpu.pc']),sp=s['cpu.sp'],frame=read('FrameCounter'),actors=actors}
end)
emu.addMemoryCallback(function(a,v)
 local i=a-D.InvDropKind
 if active()and emu.read(a,emu.memType.nesDebug)==0 and(v==1 or v==2)then births[i]={tick=tick,owner=owner,kind=v,frame=read('FrameCounter')}end
end,emu.callbackType.write,D.InvDropKind,D.InvDropKind+3)
emu.addMemoryCallback(function(a,v)
 if not active()then return end
 local i=a-D.InvDropAge;local old=emu.read(a,emu.memType.nesDebug)
 if read('InvDropKind',i)==0 or v~=(old+1)%256 then return end -- Reject INC's dummy write.
 local s=emu.getState();local q={tick=tick,owner=owner,slot=i,old_age=old,new_age=v,high=read('InvDropAgeHi',i),callback_pc=s['cpu.pc'],bank=page(s['cpu.pc']),sp=s['cpu.sp'],frame=read('FrameCounter'),birth=births[i],instruction_pc=T.increment_pc,instruction_bytes=T.increment_bytes}
 writes[#writes+1]=q
 if not first and births[i]and births[i].tick==tick and owner=='Roll-own'then first=q end
end,emu.callbackType.write,D.InvDropAge,D.InvDropAge+3)
emu.addEventCallback(function()
 if not first then return end
 local after=read('InvDropAge',first.slot)+256*read('InvDropAgeHi',first.slot)
 local q={defect_observed=true,candidate_passed=false,native_lifecycle_passed=false,goal_complete=false,ROM_sha256=T.ROM_sha256,scope='Tiny cold selected Hard Roll; default-health Goomba and real free buster defeat/drop, no resource/RNG/drop/outcome writes. Call-owner instrumentation plus real INC write distinguishes duplicate native update from dummy RMW write.',first_premature_write=first,age_after_end_frame=after,calls=calls,real_increments=writes,expected='Global object drop owner already ran before this birth. New actor should remain age0 until the next global update; Roll-own extra update advances it on its birth tick.'}
 local f=assert(io.open(OUTPUT..'drop-owner-proof.json','w'));f:write(j(q));f:close()
 local f=assert(io.open(OUTPUT..'first-premature-write.argb','wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()
 emu.stop(0)
end,emu.eventType.endFrame)
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    frozen=a.packet/'frozen-current';z=json.loads((a.packet/'preparation.json').read_text(encoding='utf-8'))
    for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(frozen/('candidate'+ext),a.output/('candidate'+ext))
    profile=next(q for q in z['profiles']if q['mode_value']==1)
    c=json.loads((Path(profile['script']).parent/'config.json').read_text(encoding='utf-8'))
    c['plan']=[dict(action='expiry',name='bounded-natural-first-drop-owner-trace',kind=1,meter=128)]
    b=scoped_load(a.output/'candidate.nes');names=['GameLoop','Z2UpdateDropsGate','RlWeapons','InventoryUpdateDrops']
    needed=set(re.findall(r"\bread\('([A-Za-z_][A-Za-z_0-9]*)'",OBSERVER))|set(re.findall(r'\bD\.([A-Za-z_][A-Za-z_0-9]*)',OBSERVER))
    for n in needed:c['ram'][n]=address(b,n)
    assert needed<=set(c['ram'])
    hooks={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in names}
    at=location(b,'InventoryUpdateDrops');size=int(b['syms']['InventoryUpdateDrops']['size'],0);op=bytes([0xfe,address(b,'InvDropAge')&255,address(b,'InvDropAge')>>8]);offset=b['raw'][at:at+size].index(op)
    trace=dict(ROM_sha256=z['ROM_sha256'],hooks=hooks,increment_pc=address(b,'InventoryUpdateDrops')+offset,increment_bytes=list(op))
    module=ROOT/'tools/audit/final_roll_items_native.lua'
    script=a.output/'run.lua';script.write_text('FINAL_ROLL_ITEMS='+lua(c)+'\nFINAL_ROLL_DROP_TRACE='+lua(trace)+'\n'+module.read_text(encoding='utf-8')+'\n'+OBSERVER,encoding='utf-8')
    (a.output/'config.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    proof=dict(status='prepared_trace_not_run',ROM_sha256=z['ROM_sha256'],full_lifecycle=False,mode_value=1,script_sha256=sha(script),module_sha256=sha(module),preparer_sha256=sha(Path(__file__)),source_packet_sha256=sha(a.packet/'preparation.json'),hooks=hooks,increment_instruction=trace,scope=__doc__)
    (a.output/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(preparation_sha256=sha(a.output/'preparation.json'),script_sha256=sha(script))))


if __name__=='__main__':main()
