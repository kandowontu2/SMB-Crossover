"""Observe actual Metal service costs during the existing neutral/walk test."""
import re
from pathlib import Path
import prepare_metal_storm_shots_1101_v35 as P
from prepare_selected_native_packet_v1 import prepare,sha
O=P.P.R/'build/metal-storm-cost-1101-v39'

def main():
 O.mkdir(exist_ok=True)
 ref=P.P.R/'build/metal-storm-idle-1101-v38/native/controller.lua';t=ref.read_text()
 labels={m[2]:int(m[1],16) for m in re.finditer(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(P.O/'component.lbl').read_text(),re.M)}
 observer="""local services={}
local serviceStack={}
emu.addMemoryCallback(function()
 if phase~='play' or r('CurrentBank')~=206 then return end
 local at=emu.read(L.FarcallJmpTarget_SMC+1,emu.memType.nesDebug)+256*emu.read(L.FarcallJmpTarget_SMC+2,emu.memType.nesDebug)
 local row=(at-VENEERS)//3
 if row<0 or row>=37 then return end
 serviceStack[#serviceStack+1]={row=row,bucket=age<120 and 0 or 1,start=emu.getState()['cpu.cycleCount']}
end,emu.callbackType.exec,ENTER)
emu.addMemoryCallback(function()
 if r('CurrentBank')~=206 or #serviceStack==0 then return end
 local a=table.remove(serviceStack)
 local key=a.bucket*100+a.row
 local q=services[key] or {calls=0,total=0,max=0}
 local n=emu.getState()['cpu.cycleCount']-a.start
 q.calls=q.calls+1;q.total=q.total+n;q.max=math.max(q.max,n);services[key]=q
end,emu.callbackType.exec,RETURN)
"""
 for key,label in [('VENEERS','Ms12Veneers'),('ENTER','Ms12Enter'),('RETURN','Ms12Return')]:observer=observer.replace(key,str(labels[label]))
 t=t.replace('local function finish(reason)',observer+"""local function finish(reason)
 local rows={}
 for k,q in pairs(services) do rows[#rows+1]=string.format('{"phase":%d,"row":%d,"calls":%d,"mean_cycles":%.1f,"max_cycles":%d}',k//100,k%100,q.calls,q.total/q.calls,q.max) end
 local f=assert(io.open(OUTPUT..'services.json','w'));f:write('['..table.concat(rows,',')..']');f:close()
""")
 prepare(O/'native',P.O/'candidate.nes',t,[Path(__file__),ref,P.O/'component.lbl'],expected=sha(P.O/'candidate.nes'),timeout=90,scope='Read-only native service entry/return cycle observer, includes interrupts. Same cold idle/walk controller as v38; no game-state writes.')
if __name__=='__main__':main()
