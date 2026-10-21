"""Prepare a controller-only reference pacing experiment on immutable audio-E."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/root49-samus-reference-pacing-a'
B = R / 'build/roster-through-2-2/specialist-gq-samus-fixed-bc-2-v0-mmc3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    assert not D.exists()
    D.mkdir(parents=True)
    trace = read(B / 'trace.csv')
    inputs = {int(z['frame']): int(z['mask']) for z in read(B / 'inputs.csv')}
    native = read(B / 'samus-telemetry.csv')
    print('Native fields:', list(native[0]))
    ref = D / 'reference.lua'
    fields = 'frame world level area areaType x y yHigh state vx vy power engine mode task camera buttons'.split()
    with ref.open('w') as f:
        f.write('return {\n')
        for row in trace:
            values = [int(row[k]) for k in fields] + [inputs.get(int(row['frame']), 0)]
            f.write('{' + ','.join(map(str, values)) + '},\n')
        f.write('}\n')
    identity = D / 'identity.lua'
    shutil.copyfile(R / 'tools/playthroughs/samus_fixed_identity.lua', identity)
    policy = '''-- Controller-only experiment: pace the old input decisions by actual pose.
-- The reference proposes buttons; it never supplies emulated state.
dofile(IDENTITY)
local ref=dofile(REFERENCE)
local cursor=1
local log=assert(io.open(ROSTER_CONFIG.out..'reference-pacing.csv','w'))
log:write('poll,frame,x,y,yHigh,state,referenceFrame,cost,mask\\n')
local lastStage=''
local stuck,previousBest=0,0
local function signed(v)return v>=128 and v-256 or v end
local function distance(c,q)
 if q[2]~=c.world or q[3]~=c.level or q[5]~=c.areaType then return 100000 end
 local cost=10*math.abs(q[6]-c.x)+3*math.abs((q[7]+256*q[8])-(c.y+256*c.yHigh))
 cost=cost+(q[9]~=c.state and 25 or 0)+math.abs(signed(q[10])-signed(c.vx))
 cost=cost+2*math.abs(signed(q[11])-signed(c.vy))+(q[12]~=c.status and 35 or 0)
 cost=cost+(q[13]~=c.engine and 100 or 0)+(q[4]~=c.area and 200 or 0)
 return cost
end
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
return function(c)
 local key=c.world..'-'..c.level..'-'..c.area
 if key~=lastStage then
  lastStage=key
  local best,score=cursor,math.huge
  for i=math.max(1,cursor-30),math.min(#ref,cursor+2500)do
   local d=distance(c,ref[i]);if d<score then best,score=i,d end
  end
  cursor=best
 end
 local best,score=cursor,math.huge
 for i=math.max(1,cursor-3),math.min(#ref,cursor+8)do
  local d=distance(c,ref[i])+0.05*math.abs(i-cursor)
  if d<score then best,score=i,d end
 end
 if best==previousBest then stuck=stuck+1 else stuck=0 end
 assert(stuck<180,'Reference pacing stalled; retain actual endpoint for diagnosis')
 previousBest=best;cursor=math.min(#ref,best+1)
 local q=ref[best];local mask=q[18]
 log:write(table.concat({c.poll,c.frame,c.x,c.y,c.yHigh,c.state,q[1],score,mask},',')..'\\n');log:flush()
 local b={};for n,v in pairs(bits)do b[n]=(mask&v)>0 end;return b
end
'''
    policy = policy.replace('dofile(IDENTITY)', 'dofile(' + json.dumps(identity.as_posix()) + ')')
    policy = policy.replace('dofile(REFERENCE)', 'dofile(' + json.dumps(ref.as_posix()) + ')')
    (D / 'policy.lua').write_text(policy)
    prefix = D / 'prefix-1971.csv'
    with prefix.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['poll', 'frame', 'mask'])
        for row in read(B / 'inputs.csv'):
            if int(row['poll']) > 1971:
                break
            w.writerow([row['poll'], row['frame'], row['mask']])
    report = dict(status='PREPARED_CONTROLLER_PACING_EXPERIMENT_NOT_A_CLEAR', script_sha256=sha(__file__),
        old_GQ_reference_ROM='a5583527ebfaf4cac1bb4384518ddf2a93a72abc79469e773e525b8ce227bb12',
        reference_trace_sha256=sha(B / 'trace.csv'), reference_inputs_sha256=sha(B / 'inputs.csv'),
        generated={p.name: sha(p) for p in (ref, identity, D / 'policy.lua', prefix)},
        fields=fields+['next_input_mask'],
        rationale='First fixed transfer difference is a missed update; retain proposals until actual pose advances so short button edges can cross an update. This is a bounded controller hypothesis, not a physics model or emulated grant.',
        controller_only=True, emulated_writes=False, phase_cap_bytes=250000000, final_reserve_bytes=40000000,
        global_cap_bytes=70000000000, accepted_release=False, goal_complete=False)
    (D / 'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Prepared reference pacing for a fresh native run.')


if __name__ == '__main__':
    main()
