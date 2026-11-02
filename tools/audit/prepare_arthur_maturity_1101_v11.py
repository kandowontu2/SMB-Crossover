"""Trace real mature-item admission before any bounding-box consumer."""
from pathlib import Path
import itertools,json
import check_arthur_side_clamp_1101_v8 as C
from prepare_selected_native_packet_v1 import prepare
P=C.P;M=C.M;O=P.O


def main():
 rom=O/'candidate.nes';digest=P.sha(rom);b=C.scoped_load(rom);base=C.seed(b)
 M.put(base,SelectedCharacter=32,ArHostReady=167,OperMode_Task=3)
 sig=C.location(b,'ArCacheSignature');base.ram[2][0x1fe0:0x1ff0]=b['raw'][sig:sig+16]
 mature_slot=C.address(b,'ArOwnServices')+3*23;slot_at=C.location(b,'ArOwnServices')+3*23
 assert b['raw'][slot_at]==0x4c;target=int.from_bytes(b['raw'][slot_at+1:slot_at+3],'little')
 hits={};cls=M.NesMPU;step=cls.step
 def trace(c):
  if c.pc>=0x8000 and c.memory.rawtags[(c.pc-0x8000)//8192]==198 and c.pc in [mature_slot,target]:hits[c.pc]=hits.get(c.pc,0)+1
  return step(c)
 cls.step=trace;rows=[]
 try:
  for state,kind,flag in itertools.product([0,6,16,127,128,129,255],[0,1,2,3],[0x20,0x31,0x61,0xa9]):
   m=M.fork(base);m[C.address(b,'PowerUpType')+5]=kind;m[C.address(b,'Enemy_State')+5]=state
   z=M.invoke(m,'NrPickupCollision',a=85,x=5,y=73,p=flag)
   rows.append(dict(enemy_state=state,powerup_type=kind,input_flags=flag,output_C=z['P']&1))
 finally:cls.step=step
 assert len(rows)==112 and hits.get(mature_slot)==112 and hits.get(target)==112
 assert not any(v['output_C']for v in rows),'This receipt preserves the actual failing predicate, not a repaired expectation'
 q=dict(proven_negative=True,source_CPU_only=True,native=False,ROM_sha256=digest,actual_NrPickupCollision_cases=len(rows),actual_Arthur_mature_slot=f'70:{mature_slot:04X}',actual_slot_JMP=f'70:{target:04X}',reached_calls={hex(k):v for k,v in hits.items()},all_actual_cases_return_C0=True,scope='Actual full NrPickupCollision/Jn/union/Arthur table transport with valid cache signature and active gameplay. Mature state128 flower1 is rejected before player/enemy bbox work. No ROM or maturity predicate changed.',cases=rows,bindings={str(p.relative_to(P.R)):P.sha(p)for p in [Path(__file__),rom,P.SOURCE]})
 (O/'maturity-negative-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
 # Original powerup caller is genuine ROM0 B804: its next instruction is
 # BCC B809 and its pass branch invokes RemainingNormalPlayerCollision.
 at=16+0*8192+0x1804;assert b['raw'][at:at+5]==bytes([0x90,3,0x20,0x96,0xa4])
 ref=O/'flower-landwalk/controller.lua';t=ref.read_text()
 marker='local torchCalls=0';assert t.count(marker)==1
 t=t.replace(marker,marker+'''
local admission,admitClear,admitSet=0,0,0
local ingress={}
local admissionRows=0
local admissions=assert(io.open(OUTPUT..'admission.csv','w'))
admissions:write('frame,carry,x,y,y_high,item_x,item_y,item_y_high,item_flag,item_id,item_state,item_type,player_ul_x,player_ul_y,player_lr_x,player_lr_y,item_ul_x,item_ul_y,item_lr_x,item_lr_y,offscreen,source_flags\\n')''',1)
 marker='local function finish(passed,reason)\n';assert t.count(marker)==1
 t=t.replace(marker,marker+''' admissions:close()
 local f=assert(io.open(OUTPUT..'admission.json','w'));local a={}
 for n,v in pairs(ingress)do a[#a+1]=string.format('"%s":%d',n,v)end
 f:write(string.format('{"calls":%d,"carry_clear":%d,"carry_set":%d,"ingress":{%s}}',admission,admitClear,admitSet,table.concat(a,',')));f:close()
''',1)
 marker="emu.addMemoryCallback(function()\n if phase=='play' then mainCalls=mainCalls+1 end"
 hook='''local observed={'NrPickupCollision','JnCollisionDispatch','HuMature','RemainingNormalPlayerCollision','PlayerEnemyCollision','PlayerCollisionCore','HandlePowerUpCollision','NrPickup','HuPickup','ArHostCollect','ArHostNativePickup','HuFullBox','ArHostBox'}
for _,name in ipairs(observed)do
 local pc=assert(L[name],name);local bank=assert(B[name],name)
 emu.addMemoryCallback(function()
  local actual=pc<0xa000 and nil or(pc<0xc000 and r('CurrentBank')or r('CurrentBankC'))
  if phase=='play' and(actual==nil or actual==(bank|128))then ingress[name]=(ingress[name]or 0)+1 end
 end,emu.callbackType.exec,pc)
end
emu.addMemoryCallback(function()
 if phase~='play' or r('CurrentBank')~=128 then return end
 local s=emu.getState();local c=assert(s['cpu.ps'],'Actual CPU status')&1
 admission=admission+1;if c==0 then admitClear=admitClear+1 else admitSet=admitSet+1 end
 if mature and wx()>=320 and r('Player_Y_Position')==112 and r('ArMode')==0 and admissionRows<24 then
  admissionRows=admissionRows+1;local at=24
  admissions:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\\n',frame,c,wx(),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Enemy_X_Position',5)+256*r('Enemy_PageLoc',5),r('Enemy_Y_Position',5),r('Enemy_Y_HighPos',5),r('Enemy_Flag',5),r('Enemy_ID',5),r('Enemy_State',5),r('PowerUpType',5),r('BoundingBox_UL_Corner'),r('BoundingBox_UL_Corner',1),r('BoundingBox_LR_Corner'),r('BoundingBox_LR_Corner',1),r('BoundingBox_UL_Corner',at),r('BoundingBox_UL_Corner',at+1),r('BoundingBox_LR_Corner',at),r('BoundingBox_LR_Corner',at+1),r('EnemyOffscrBitsMasked',5),r('ArR_04F0')))
 end
end,emu.callbackType.exec,0xb804)
'''
 assert t.count(marker)==1;t=t.replace(marker,hook+marker,1)
 prepare(O/'flower-eligibility',rom,t,[Path(__file__),ref,O/'maturity-negative-CPU.json'],expected=digest,timeout=150,allow_interactive=True,scope='Unchanged genuine parkedfirstflowercontroller withreadonlyactualNrPickupCollisionreturnC atROM0B804 and24matureparkedbbox/itemrows plusingresscounts. Allflower/torchpassassertionsretained; actualnegativeexpected. NoRAMseeds/BBox/physics/predicatechanges.')
 print('Actual maturity112cases allC0; native read-only admission diagnosis prepared')


if __name__=='__main__':main()
