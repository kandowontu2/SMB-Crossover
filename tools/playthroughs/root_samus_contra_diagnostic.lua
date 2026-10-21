local policy=dofile(ROSTER_CONFIG.out:match('^(.*)/build/')..'/tools/playthroughs/root_samus_contra.lua')
return function(c)
 if c.poll>=1000 and c.poll%80==0 and c.poll<1500 then
  local a={};for i=0,5 do a[#a+1]=table.concat({c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i),c.r('Enemy_State',i),c.r('InvPickup',i)},'/')end
  print('ROOTDIAG x='..c.x..' y='..c.y..' status='..c.status..' blocks='..table.concat({c.block(320,144),c.block(336,144),c.block(352,144),c.block(368,144),c.block(384,144)},'/')..' actor='..table.concat(a,','))
 end
 return policy(c)
end
