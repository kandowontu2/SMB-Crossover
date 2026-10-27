-- Read-only additive observer. Original native_v3 mechanics/guards unchanged.
local hudScope=nil
local hudCases={0,0,0,0,0,0,0}
local hudHelpers,hudReturns,hudStores=0,0,0
hook('BillHudAnchor',function()
 if not entered or not current then return end
 local s=emu.getState();local x=s['cpu.x'];local p=s['cpu.ps']or s['cpu.p']
 assert(r('SelectedCharacter')==3,'Actual Bill/Lance HUD owner')
 onReturn('combined-Bill-HUD-anchor',function()
  local z=emu.getState();local flags=z['cpu.ps']or z['cpu.p']
  assert(z['cpu.a']==112 and z['cpu.y']==16 and z['cpu.x']==x,'Actual helper anchor and live X')
  assert(p and flags and flags&0xcf==p&0xcf,'Actual helper architectural flags preserved')
  hudHelpers=hudHelpers+1
 end)
end)
hook('MetaspriteRenderLoop',function()
 if not entered or not current or r('AvDrawIndex')~=20 then return end
 local selected=r('InvSelected',3)
 if selected==0 then return end
 local expected=assert(C.hud_records[tostring(selected)],'Actual legal selected Bill capsule art')
 assert(r('SelectedCharacter')==3 and r('R4')==112 and r('R5')==0 and r('R6')==16 and r('R7')==1,'Only Bill/Lance capsule moved to the new screen anchor')
 local ptr=r('R0')+256*r('R1')
 assert(ptr==expected.address and bank(0xc000)==expected.bank,'Actual source capsule pointer and physical C bank')
 assert(not hudScope,'Prior HUD renderer returned before another starts')
 local q={writes={},expected=expected,case=index,selected=selected};hudScope=q
 onReturn('combined-Bill-HUD-render',function()
  assert(hudScope==q,'Only genuine immediate HUD return owns its writes')
  hudScope=nil;assert(#q.writes==12,'Actual three-sprite Bill capsule emits twelve OAM stores')
  local sprites={}
  for _,w in ipairs(q.writes)do
   local slot=w.address//4;local part=w.address%4
   sprites[slot]=sprites[slot]or{};assert(sprites[slot][part]==nil,'Each actual capsule OAM field written once');sprites[slot][part]=w.value
  end
  local actual={}
  for _,v in pairs(sprites)do
   assert(v[0]==1 and v[3]>=100 and v[3]<=116,'Native capsule OAM coordinates avoid WORLD/TIME')
   actual[#actual+1]=table.concat({v[0],v[1],v[2],v[3]},':')
  end
  local wanted={};local bytes=expected.bytes
  for off=2,10,4 do
   wanted[#wanted+1]=table.concat({1,bytes[off],bytes[off+1],112+(bytes[off+3]>=128 and bytes[off+3]-256 or bytes[off+3])},':')
  end
  table.sort(actual);table.sort(wanted);assert(#actual==3 and table.concat(actual,'|')==table.concat(wanted,'|'),'Actual native capsule tile/attributes/coordinates match complete compiled art')
  if q.case>=1 and q.case<=7 and q.selected==C.cases[q.case].expected_selected then hudCases[q.case]=hudCases[q.case]+1 end
  hudReturns=hudReturns+1;hudStores=hudStores+#q.writes
 end)
end)
emu.addMemoryCallback(function(at,value)
 if hudScope then hudScope.writes[#hudScope.writes+1]={address=at-L.Sprite_Data,value=value}end
end,emu.callbackType.write,L.Sprite_Data,L.Sprite_Data+255)
-- Registered before the original terminal callback: emu.stop must not hide
-- this final aggregate. No state, outcome, palette or hardware writes here.
emu.addEventCallback(function()
 if not done then return end
 assert(not hudScope and hudHelpers>0 and hudReturns>0 and hudStores==hudReturns*12,'HUD helper and real renderer/cleanup fully observed')
 assert(hudCases[1]==0,'Normal selected0 has no invented capsule')
 for i=2,7 do assert(hudCases[i]>0,'Every upgraded case renders its actual selected capsule')end
 local f=assert(io.open(OUTPUT..'combined-bill-hud.json','w'))
 f:write(json({passed=true,ROM_sha256=C.ROM_sha256,actual_variant_readback=r('BillVariant'),actual_mode_readback=r('CrossoverBehaviorVersion'),helper_calls=hudHelpers,genuine_render_returns=hudReturns,actual_OAM_stores=hudStores,case_counts=hudCases,source_anchor={112,16},OAM_bounds={100,1,123,16},scope='Actual read-only helper/qualified full source capsule pointer and twelve OAM stores, all upgraded cases. Full PPU images still require review; original gallery mechanics/guards remain independent.'}));f:close()
end,emu.eventType.endFrame)
