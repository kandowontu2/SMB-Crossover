"""Create an ordinary-input discovery policy following the old route's poses.

The terrain-publication repair changes physical-frame pacing. This reads live
positions to retime existing controls; it does not author gameplay state.
The resulting input CSV still requires a separate fixed power-on replay.
"""
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[2];O=R/'build/verification/bill-state-follow-r';assert not O.exists();O.mkdir()
P=R/'build/roster-through-2-2/claude-final-video-3-v0-mmc3'
with(P/'inputs.csv').open(newline='')as f:masks={int(t['frame']):int(t['mask'])for t in csv.DictReader(f)}
stages={}
with(P/'trace.csv').open(newline='')as f:
 for t in csv.DictReader(f):
  if t['mode']!='1'or t['task']!='3'or t['engine']!='8':continue
  key='-'.join(t[k]for k in ['world','level','area'])
  z=[int(t[k])for k in ['x','y','yHigh','state','power']]+[masks.get(int(t['frame']),0)]
  # Repeated physical frames carry the same pose. Retain the final control
  # offered before the next state, preserving ordinary hold/release edges.
  if stages.setdefault(key,[])and stages[key][-1][:5]==z[:5]:stages[key][-1]=z
  else:stages[key].append(z)
code='local stages={\n'+''.join('['+json.dumps(k)+']={'+','.join('{'+','.join(map(str,z))+'}'for z in v)+'},\n'for k,v in stages.items())+'}\n'
code+='local fallback=(function()\n'+(R/'tools/playthroughs/roster_policy.lua').read_text()+'\nend)()\n'
code+=r'''
local key,cursor,lastX,still='',1,nil,0
return function(c)
 local room=c.world..'-'..c.level..'-'..c.area
 if key~=room then key=room;cursor=1;lastX=nil;still=0 end
 local rows=stages[key];if not rows then return fallback(c)end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 local best,bscore=cursor,1e9
 for n=math.max(1,cursor-2),math.min(#rows,cursor+140)do
  local z=rows[n]
  local s=4*math.abs(c.x-z[1])+2*math.abs(c.y-z[2])+64*math.abs(c.yHigh-z[3])+(c.state~=z[4]and 6 or 0)+(c.status~=z[5]and 50 or 0)
  if s<bscore or(s==bscore and n<=cursor+3)then best,bscore=n,s end
 end
 cursor=math.max(cursor,best)
 if bscore>96 or still>60 then return fallback(c)end
 local mask=rows[best][6]
 return {a=(mask&128)~=0,b=(mask&64)~=0,select=(mask&32)~=0,start=(mask&16)~=0,up=(mask&8)~=0,down=(mask&4)~=0,left=(mask&2)~=0,right=(mask&1)~=0}
end
'''
(O/'policy.lua').write_text(code,encoding='utf-8');print('POLICY',sum(map(len,stages.values())),O/'policy.lua')
