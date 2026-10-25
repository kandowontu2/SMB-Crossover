-- Preferences and identity are selected with controller inputs, never writes.
return function(r,hard,outlines)
 return function(frame)
  if frame<60 or frame%12~=0 then return{}end
  local menu=r('CrossoverMenuState')
  local outlineWrong=r('PlayerOutlinesOff')~=(outlines and 0 or 1)
  local behaviorWrong=r('CrossoverBehaviorVersion')~=(hard and 1 or 0)
  if menu==0 and(outlineWrong or behaviorWrong)then
   return r('CrossoverOptionsFocus')==0 and {down=true}or{a=true}
  elseif menu==4 then
   if outlineWrong then return r('CrossoverOptionsFocus')==0 and{a=true}or{up=true}
   elseif behaviorWrong then return r('CrossoverOptionsFocus')==1 and{a=true}or{down=true}
   else return{b=true}end
  elseif menu~=2 then return{start=true}
  elseif r('CrossoverMenuIndex')<6 then return{down=true}
  elseif r('CrossoverMenuIndex')~=9 then return{right=true}
  elseif r('RlVariant')~=1 then return{select=true}
  else return{a=true}end
 end
end
