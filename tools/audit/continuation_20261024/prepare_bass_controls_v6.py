from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;out=D/'bass-controls-v6';out.mkdir(exist_ok=False);rows=[]
for mode in ['easy','hard']:
 source=D/('remaining-controls-v4/bass-'+mode+'.lua');t='local normal=(function()\n'+source.read_text()+'\nend)()\n'+r'''
local hold=0
local log=assert(io.open(ROSTER_CONFIG.out..'bass-navigation.csv','w'))
log:write('frame,x,y,grounded,selected,face,visibleDx,visibleId,blockedAhead,bulletTypes,buttons\n')
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 or c.x<500 or(c.x>=2160 and c.x<2258)or(c.x>=2390 and c.x<2516)then return b end
 if c.r('InvSelected',9)~=0 then return b end
 local e;local blockedAhead=false
 local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 for i=0,5 do
  local flag=c.r('Enemy_Flag',i);local id=c.r('Enemy_ID',i);local state=c.r('Enemy_State',i)
  if flag>0 and flag<128 and id<21 and id~=13 and state<32 and not(id==6 and state>=2)and c.r('Enemy_Y_HighPos',i)==1 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local dx=x-c.x;local y=c.r('Enemy_Y_Position',i)
   if math.abs(dx)<150 and math.abs(y-c.y)<42 then
    local blocked=false
    for wx=math.min(c.x+8,x+8),math.max(c.x+8,x+8),8 do if solid(c.block(wx,c.y+16))then blocked=true;break end end
    if blocked then if dx>0 then blockedAhead=true end
    elseif not e or math.abs(dx)<math.abs(e.dx)then e={dx=dx,y=y,x=x,id=id}end
   end
  end
 end
 if c.grounded then
  if e then
   hold=0;local face=e.dx<0 and 2 or 1
   if c.r('PlayerFacingDir')~=face then b={left=face==2,right=face==1}
   else b={b=c.poll%24<12}end
  elseif blockedAhead and(solid(c.block(c.x+24,c.y+8))or solid(c.block(c.x+24,c.y+24)))then
   if not c.lastA and hold==0 then hold=10 end
   b={right=true,a=hold>0}
  else b.right=true;b.left=false end
 end
 if hold>0 then b.a=true;hold=hold-1 end
 local mask=(b.a and 128 or 0)|(b.b and 64 or 0)|(b.left and 2 or 0)|(b.right and 1 or 0)
 log:write(table.concat({c.frame,c.x,c.y,tostring(c.grounded),c.r('InvSelected',9),c.r('PlayerFacingDir'),e and e.dx or999,e and e.id or-1,tostring(blockedAhead),c.r('MmBulletType')..':'..c.r('MmBulletType',1)..':'..c.r('MmBulletType',2)..':'..c.r('MmBulletType',3),mask},',')..'\n')
 return b
end
'''
 # Whitespace separates Lua's `or` keyword from its numeric fallback.
 t=t.replace('or999','or 999').replace('or-1','or -1')
 assert 'emu.write('not in t and 'dofile('not in t;p=out/(mode+'.lua');p.write_text(t);rows.append(dict(identity='bass',mode=mode,policy=str(p),policy_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(out/'proof.json').write_text(json.dumps(dict(prepared=True,game_changes=False,memory_writes=False,cases=rows,scope='Read-only Bass navigation: clear visible ground enemies in either direction before approaching a pipe; ignore enemies behind solid terrain until the pipe is crossed. Keep real double jumps and stair-top landings. Declared telemetry records native shots and actor choice. Native clear/replay required.'),indent=2)+'\n')
t=(D/'run_remaining_routes_v4.py').read_text().replace("out=D/'remaining-routes-v4'","out=D/'bass-routes-v6'").replace("D/'remaining-controls-v4/proof.json'","D/'bass-controls-v6/proof.json'");(D/'run_bass_routes_v6.py').write_text(t)
