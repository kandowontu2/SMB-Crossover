"""Passive current Imajin flag-cell/contact observer; no input changes."""
from hashlib import sha256
import json

import replay_smb2_stage_current_1113 as Root

BASE='6371ab8df461a9a347ad6baf5f7f3d84de78fa1472af4a49d73b98574958231e'


def controller(raw):
    text=Root.controller(raw,4,jump_hold=24,enemy_gap=48,source_edges=True,injury_trace=True,last_pit_settle=True,runup=True)
    assert sha256(text.encode()).hexdigest()==BASE
    text='local flagDiagnostic={samples={}}\n'+text
    point='idle=smb2Idle';assert text.count(point)==1
    text=text.replace(point,point+',flag_diagnostic=flagDiagnostic')
    text+=r'''
emu.addEventCallback(guard(function()
 if not game or done or not active()or x()<3120 then return end
 local s=state();local q={s=s,base_nibble=s.x&15,size=read(0x5c74),duck=read(0x5c44),sourceX=read(0x5c00)+256*read(0x5c10),sourceY=read(0x5c0a),sourceYPage=read(0x5c1a),air=read(0x5c3f),vx=read(0x5c20),vy=read(0x5c2a),pad=pad,cells={}}
 for xx=s.x//16*16-16,s.x//16*16+32,16 do
  local row={x=xx,tiles={}};for yy=32,208,16 do local t=tile(xx,yy);row.tiles[tostring(yy)]={tile=t,attr=emu.read(attrs+t,emu.memType.nesPrgRom)}end;q.cells[#q.cells+1]=row
 end
 flagDiagnostic.first=flagDiagnostic.first or q;flagDiagnostic.last=q
 if s.x==flagDiagnostic.previousX then flagDiagnostic.still=(flagDiagnostic.still or 0)+1 else flagDiagnostic.previousX=s.x;flagDiagnostic.still=1 end
 if flagDiagnostic.still%10==0 then flagDiagnostic.samples[#flagDiagnostic.samples+1]=q;if #flagDiagnostic.samples>6 then table.remove(flagDiagnostic.samples,1)end end
 if flagDiagnostic.still>=60 then finish(false,'passive-native-flag-cell-stall60')end
end),emu.eventType.endFrame)
'''
    # Root's formatter originally has string-keyed records only; these new
    # bounded numeric-keyed arrays need quoted JSON object keys as well.
    point="string.format('%q',k)";assert text.count(point)==1
    text=text.replace(point,"string.format('%q',tostring(k))")
    Root.Base.LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    from check_smb2_flag_handoff_1113 import load_input
    raw=load_input();text=controller(raw)
    print(json.dumps(dict(ROM_SHA256=Root.PIN,base_SHA256=BASE,script_SHA256=sha256(text.encode()).hexdigest(),
        bytes=len(text),Lua_compile=True,input_changes=0,ROM_or_runtime_writes=0,outputs=0,Mesen_run=False)),flush=True)
