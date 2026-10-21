"""Give Up a fresh native edge after the real bomb boost has landed."""
from pathlib import Path
import csv,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age='release',0
local f=assert(io.open(ROSTER_CONFIG.out..'unmorph-edge-g.csv','w'))
f:write('frame,poll,x,y,state,ball,phase,age,previousDirections,clearance,mask,headTiles\n')
local hooks=HOOKS
local hf=assert(io.open(ROSTER_CONFIG.out..'stand-call-g.csv','w'));hf:write('event,frame,a,x,y,p,sp\n')
local currentFrame=0
for name,h in pairs(hooks)do
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual F stand call '..name)end
  local s=emu.getState()
  hf:write(table.concat({name,currentFrame,s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps'],s['cpu.sp']},',')..'\n');hf:flush()
 end,emu.callbackType.exec,h.address)
end
return function(c)
 currentFrame=c.frame
 if phase=='done'then return base(c)end
 age=age+1;assert(age<120,'Fresh grounded Up edge must resolve or yield a stand-clearance witness')
 local b={}
 if phase=='release'then
  if age>=4 and c.grounded and c.r('SmPreviousDirections')&8==0 then phase='press'end
 elseif phase=='press'then
  b.up=true;phase='observe'
 elseif phase=='observe'then
  if c.r('SmBall')==0 and c.grounded then phase='done'
  elseif c.grounded and c.r('SmPreviousDirections')&8==0 then b.up=true end
 end
 local a={}
 for _,dy in ipairs({0,8,16})do for _,dx in ipairs({-5,0,5,10})do a[#a+1]=c.block(c.x+dx,c.y+dy)end end
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('SmBall'),phase,age,c.r('SmPreviousDirections'),c.r('SmClearance'),b.up and 8 or 0,table.concat(a,':')},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-g.json';assert not out.exists()
    p=R/'build/roster-through-2-2/root49-f-samus-route-f-2-v0-mmc3'
    t=list(csv.DictReader((p/'trace.csv').open()));pose=next(z for z in t if z['frame']=='10000')
    assert pose['x']=='829'and pose['y']=='176'and pose['state']=='0'
    lines=(p/'inputs.csv').read_text().splitlines();prefix=H/'prefix-10000-g.csv';prefix.write_text('\n'.join(lines[:10001])+'\n')
    spec=importlib.util.spec_from_file_location('actual_F_g',V/'agent49g-samus-crouch-fix-proposal-b/image.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    im=m.Image(R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/smb-crossover-mmc3.nes')
    hooks={n:im.hook('SamusCanStand',None,d)for n,d in [('entry',0),('return','last')]}
    policy=H/'policy-g.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-f.lua').as_posix())).replace('HOOKS',m.lua(hooks)))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-g-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-f.py').read_text().replace('native-f.log','native-g.log').replace('native-result-f.json','native-result-g.json').replace('allocation-f.json','allocation-g.json').replace('preparation-f-run.json','preparation-g-run.json').replace('policy-f.lua','policy-g.lua').replace('prefix-9540-f.csv','prefix-10000-g.csv').replace('root49-f-samus-route-f','root49-f-samus-route-g')
    (H/'run-g.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_NATIVE_FRESH_UP_EDGE_AFTER_ACTUAL_BOOST',script_sha256=sha(__file__),parent_manifest_sha256=sha(p/'manifest.json'),
      parent_bombs_sha256=sha(p/'actor-bombs-f.csv'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-g.py'),hooks=hooks,
      actual_prefix_pose=pose,hypothesis='F pressed and held Up in the bomb-boost apex. If clearance rejected that first edge, holding Up cannot request another stand on landing. Supply a genuine release and supported Up edge.',
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
