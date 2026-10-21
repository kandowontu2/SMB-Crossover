"""Read actual firebar phases in the already verified GQ controller replay."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-samus-reference-pacing-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    policy=D/'phase-observer-f.lua'
    assert not policy.exists()
    rom=R/'build/verification/agent-lsr-link-ceiling-c/source/build/smb-crossover-mmc3.nes'
    assert sha(rom)=='a5583527ebfaf4cac1bb4384518ddf2a93a72abc79469e773e525b8ce227bb12'
    text='''-- Read-only ordinary replay observer; no collision or bitmap inference.
dofile(IDENTITY)
local frame=0
local f=assert(io.open(ROSTER_CONFIG.out..'firebar-phases.csv','w'))
f:write('frame,slot,id,x,y,high,low,speed,direction,count\\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addEventCallback(function()
 frame=frame+1
 if r('WorldNumber')==0 and r('LevelNumber')==3 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then
  for i=0,5 do
   local id=r('Enemy_ID',i)
   if r('Enemy_Flag',i)~=0 and id>=0x1b and id<=0x23 then
    local row={frame,i,id,r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('FirebarSpinState_High',i),r('FirebarSpinState_Low',i),r('FirebarSpinSpeed',i),r('FirebarSpinDirection',i),r('FirebarPartCount',i)}
    f:write(table.concat(row,',')..'\\n')
   end
  end
  f:flush()
 end
end,emu.eventType.endFrame)
return function()return{}end
'''.replace('IDENTITY',json.dumps((D/'identity.lua').as_posix()))
    policy.write_text(text)
    (D/'phase-binding-f.json').write_text(json.dumps(dict(status='PREPARED_READ_ONLY_GQ_PHASE_REFERENCE',
        script_sha256=sha(__file__),policy_sha256=sha(policy),rom_sha256=sha(rom),
        purpose='Observe actual old firebar phases for bounded ordinary controller waits, rather than change runtime collision from unproved visual inference.',
        emulated_writes=False,no_new_clear_claim=True),indent=2)+'\n')
    print('Prepared read-only GQ firebar phase observer.')


if __name__=='__main__':main()
