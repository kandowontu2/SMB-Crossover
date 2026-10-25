-- Appended in the immutable physical fixture's lexical chunk.
assert(type(C.hard)=='boolean'and(C.mode_value==0 or C.mode_value==1)and C.hard==(C.mode_value==1),'Explicit Lua boolean and numeric requested mode')
hook('GameLoop',function()
 if entered and not done then
  local actual=r('CrossoverBehaviorVersion')
  assert(actual==C.mode_value,'Actual numeric mode readback on every committed gameplay update')
  if not numericModeObserved then event('actual-numeric-mode-readback',{actual=actual,requested=C.mode_value});numericModeObserved=true end
 end
end)
