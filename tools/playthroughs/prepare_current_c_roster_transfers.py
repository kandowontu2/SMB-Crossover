"""Prepare read-only identity guards for ordinary current-C fixed replays."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-current-c-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    D.mkdir(parents=True)
    policy='''-- Actual menu identity only. The harness supplies fixed ordinary inputs.
local frame=0
local seen=false
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
emu.addEventCallback(function()
 frame=frame+1
 if frame>480 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  local expected=ROSTER_CONFIG.character
  assert(r('SelectedCharacter')==expected,'Actual current-C selected character')
  assert(r('CrossoverBehaviorVersion')==0,'Actual Easy default from ordinary menu inputs')
  assert(r('PlayerOutlinesOff')==1,'Actual outlines-off preference')
  assert(r('MarioVariant')==(expected==8 and 1 or 0),'Actual Mario alternate identity')
  assert(r('BillVariant')==(ROSTER_CONFIG.variant or 0),'Actual Bill alternate identity')
  if not seen then
   local f=assert(io.open(ROSTER_CONFIG.out..'current-c-identity.json','w'))
   f:write(string.format('{"character":%d,"behavior":%d,"marioVariant":%d,"billVariant":%d,"outlinesOff":%d}\\n',expected,r('CrossoverBehaviorVersion'),r('MarioVariant'),r('BillVariant'),r('PlayerOutlinesOff')))
   f:close();seen=true
  end
 end
end,emu.eventType.endFrame)
return function()return{}end
'''
    (D/'identity.lua').write_text(policy)
    checkpoint=R/'build/checkpoints/roster-audit-v49-combined-ground-audio-samus-c/manifest.json'
    assert sha(checkpoint)=='7bde77980e47d11ed78b9348384016b1a805ff40a02ff180b33f0e8e727b5305'
    q=json.loads(checkpoint.read_text())
    cases=[(8,'mmc3','specialist-bq-luigi-easy-fixed-c-8-v0-mmc3'),
           (8,'mmc5','specialist-bq-luigi-easy-fixed-d-8-v0-mmc5'),
           (12,'mmc3','specialist-by-scrooge-fixed-o-12-v0-mmc3'),
           (12,'mmc5','specialist-by-scrooge-m5-fixed-aj-12-v0-mmc5')]
    bindings=[]
    for character,mapper,parent in cases:
        p=R/'build/roster-through-2-2'/parent
        m=json.loads((p/'manifest.json').read_text())
        assert m['verified_through_2_2'] and m['config']['character']==character
        assert sha(p/'inputs.csv')==m['inputs_sha256']
        bindings.append(dict(character=character,mapper=mapper,parent=parent,
            parent_ROM_sha256=m['rom_sha256'],inputs_sha256=sha(p/'inputs.csv'),parent_frames=m['result']['frames']))
    result=dict(status='PREPARED_FIXED_CURRENT_C_TRANSFERS_NOT_YET_VERIFIED',script_sha256=sha(__file__),
        checkpoint_sha256=sha(checkpoint),identity_sha256=sha(D/'identity.lua'),bindings=bindings,
        phase_cap_bytes=1000000000,final_reserve_bytes=100000000,global_cap_bytes=70000000000,
        qualification='Old clears identify only candidate ordinary input files. Current C must independently replay and satisfy full audit/identity/endpoint checks.',
        source_files=455,goal_complete=False)
    (D/'preparation.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Prepared four fixed input candidates and read-only actual identity guard.')


if __name__=='__main__':main()
