from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;out=D/'remaining-controls-v2';out.mkdir(exist_ok=False);records=[]
ledge=r'''
local ledges=LEDGES
local hold=0
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 for _,s in ipairs(ledges)do
  if c.x>=s.finish then s.phase='done'end
  if c.x>=s.start and c.x<s.finish and s.phase~='done'then
   if s.phase=='approach'then
    b.right=c.x<s.target;b.left=c.x>s.target+2
    if c.x>=s.target-1 and c.x<=s.target+2 and c.y<=s.top then s.phase='land'end
   end
   if s.phase=='land'then
    b={right=c.x<s.target,left=c.x>s.target+2}
    if c.grounded then
     if c.y<=s.top then
      s.wait=s.wait+1
      local ready=c.char~=4 or c.r('RgAttack')==0
      if s.wait>=6 and ready and not c.lastA then s.phase='cross';hold=34;b={right=true,b=c.char==0,a=true}end
     else s.phase='approach';s.wait=0 end
    end
   elseif s.phase=='cross'then b={right=true,b=c.char==0,a=hold>0}end
  end
 end
 if hold>0 then b.a=true;hold=hold-1 end
 return b
end
'''
for name,mode in [('mario','hard'),('link','easy'),('link','hard'),('pit','hard'),('rygar','hard'),('bass','hard'),('chip','easy'),('chip','hard'),('dale','hard')]:
 source=D/('mario-gap-controls-v2/policy.lua'if name=='mario'else'remaining-routes-v1/'+name+'-'+mode+'-policy.lua');t='local normal=(function()\n'+source.read_text()+'\nend)()\n'
 if name in ['mario','link','chip','dale']:
  entries="{start=2160,target=2197,top=112,finish=2258,phase='approach',wait=0},{start=2390,target=2440,top=112,finish=2516,phase='approach',wait=0}"
  if name=='link':entries="{start=1016,target=1072,top=176,finish=1170,phase='approach',wait=0},{start=1290,target=1328,top=176,finish=1496,phase='approach',wait=0},"+entries
  t+=ledge.replace('LEDGES','{'+entries+'}')
 else:
  t+=r'''
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==9 and c.r('RlVariant')==0 and c.r('InvSelected',9)~=0 then
  return{select=(c.r('SavedJoypadBits')&32)==0}
 end
 local e=c.enemy()
 if c.grounded and e and math.abs(e.dx)<150 and math.abs(e.y-c.y)<42 then
  local face=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=face then return{left=face==2,right=face==1}end
  return{down=c.char==6 or c.char==7,b=c.poll%24<12}
 end
 -- The old controller stopped above low enemies after the jump apex,
 -- making Hard-mode landings collide with the enemy it was waiting for.
 if not c.grounded then b.right=true;b.left=false;b.b=c.poll%24<12 end
 return b
end
'''
 assert 'emu.write('not in t and 'dofile('not in t;p=out/(name+'-'+mode+'.lua');p.write_text(t);records.append(dict(identity=name,mode=mode,policy=str(p),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),policy_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(out/'proof.json').write_text(json.dumps(dict(prepared=True,game_changes=False,memory_writes=False,cases=records,scope='Controller-only corrections from retained actual failures: land before floor/stair gaps and release attacks/A; shoot Hard ground contacts from a distance; continue air travel over low enemies; cycle Bass to his owned normal buster. No game-state, physics, terrain or equipment grants. Clear/replay and visual guards remain required.'),indent=2)+'\n')
