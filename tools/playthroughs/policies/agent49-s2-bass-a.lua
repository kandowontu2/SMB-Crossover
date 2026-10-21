-- Fresh power-on ordinary controls; historical helpers provide geometry only.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v34_finish_policy.lua'))
local f=assert(io.open(ROSTER_CONFIG.out..'bass-native-state.csv','w'))
f:write('poll,x,y,state,power,ownedLo,ownedHi,selected,ammo,dash,jumpUsed,bulletTypes,enemies\n')
return function(c)
 if c.poll%4==0 then
  local es,bs={},{}
  for i=0,3 do bs[#bs+1]=c.r('MmBulletType',i)end
  for i=0,5 do
   local flag,id=c.r('Enemy_Flag',i),c.r('Enemy_ID',i)
   if flag>0 and flag<128 then es[#es+1]=table.concat({i,id,c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i),c.r('Enemy_State',i),c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},':')end
  end
  local item=c.r('InvSelected',c.char)
  f:write(table.concat({c.poll,c.x,c.y,c.state,c.status,c.r('InvOwnedLo',c.char),c.r('InvOwnedHi',c.char),item,c.r('InvAmmo',c.char*16+item),c.r('XgDash'),c.r('XgJumpUsed'),table.concat(bs,':'),table.concat(es,';')},',')..'\n');f:flush()
 end
 return prior(c)
end
