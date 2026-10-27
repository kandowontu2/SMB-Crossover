-- Read-only additive observer. Original native_v3 mechanics/guards unchanged.
-- AvDrawIndex is only a secondary invariant: real helper -> ArtPointer C=1 ->
-- immediate farcall render, with actual stack/PC/bank ownership, admits HUD.
local hudScope,hudPending=nil,nil
local hudCases={0,0,0,0,0,0,0}
local hudHelpers,hudReturns,hudStores,hudForeign=0,0,0,0
local function hudCall()
 local s=emu.getState();local sp=s['cpu.sp']
 local function byte(i)return emu.read(256+(sp+i)%256,emu.memType.nesDebug)end
 return{sp=sp,ret=(byte(1)+256*byte(2)+1)%65536,savedA=byte(3),outer=(byte(4)+256*byte(5)+1)%65536,
  pc=s['cpu.pc'],bank=bank(s['cpu.pc'])}
end
hook('RemainingDraw',function()
 assert(not hudScope,'Prior immediate HUD renderer completed before next RemainingDraw')
 hudPending=nil
end)
hook('BillHudAnchor',function()
 hudPending=nil
 if not entered or not current then return end
 local call=hudCall();local chain=C.hud_call_chain
 assert(call.ret==chain.helper_after and bank(call.ret)==chain.source_bank,'Actual HUD helper source caller')
 local s=emu.getState();local x=s['cpu.x'];local p=s['cpu.ps']or s['cpu.p']
 local selected=r('InvSelected',3)
 local expected=assert(C.hud_records[tostring(selected)],'Actual legal selected Bill capsule art')
 assert(r('SelectedCharacter')==3 and r('AvDrawIndex')==20 and r('AvDrawArt')==expected.art,'Actual Bill/Lance HUD helper owner')
 local q={state='helper',sp=call.sp,expected=expected,selected=selected,case=index}
 onReturn('combined-Bill-HUD-anchor-v2',function()
  local z=emu.getState();local flags=z['cpu.ps']or z['cpu.p']
  assert(z['cpu.a']==112 and z['cpu.y']==16 and z['cpu.x']==x,'Actual helper anchor and live X')
  assert(p and flags and flags&0xcf==p&0xcf,'Actual helper architectural flags preserved')
  q.state='anchor';q.pointerReturnSP=(call.sp+2)%256;hudPending=q;hudHelpers=hudHelpers+1
 end)
end)
hook('RemainingDraw::ArtPointer',function()
 local q=hudPending;hudPending=nil -- consume before every qualification/rejection
 if not q then return end
 local call=hudCall();local chain=C.hud_call_chain
 onReturn('combined-Bill-HUD-pointer-v2',function()
  if q.state~='pointer' then return end
  local z=emu.getState();local flags=z['cpu.ps']or z['cpu.p']
  if flags&1==0 then return end -- real source CHR-family rejection is not a draw
  local ptr=r('R0')+256*r('R1')
  assert(ptr==q.expected.address and bank(0xc000)==q.expected.bank,'Actual successful source capsule pointer and C bank')
  q.state='render';hudPending=q
 end)
 if not entered or not current or call.ret~=chain.pointer_after or bank(call.ret)~=chain.source_bank or call.sp~=q.sp then return end
 assert(r('SelectedCharacter')==3 and r('AvDrawIndex')==20 and r('InvSelected',3)==q.selected and r('AvDrawArt')==q.expected.art,'Only immediate source HUD pointer consumes helper')
 q.state='pointer'
end)
hook('MetaspriteRenderLoop',function()
 local q=hudPending;hudPending=nil -- foreign/early-rejected renders cannot leak ownership
 if not q then hudForeign=hudForeign+1;return end
 local call=hudCall();local chain=C.hud_call_chain
 -- Install cleanup before any admission gate or coordinate/source assertion.
 onReturn('combined-Bill-HUD-render-v2',function()
  if not q.admitted then return end
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
  local wanted={};local bytes=q.expected.bytes
  for off=2,10,4 do wanted[#wanted+1]=table.concat({1,bytes[off],bytes[off+1],112+(bytes[off+3]>=128 and bytes[off+3]-256 or bytes[off+3])},':')end
  table.sort(actual);table.sort(wanted);assert(#actual==3 and table.concat(actual,'|')==table.concat(wanted,'|'),'Actual native capsule tile/attributes/coordinates match complete compiled art')
  if q.case>=1 and q.case<=7 and q.selected==C.cases[q.case].expected_selected then hudCases[q.case]=hudCases[q.case]+1 end
  hudReturns=hudReturns+1;hudStores=hudStores+#q.writes
 end)
 if not entered or not current or q.state~='render' or call.sp~=(q.pointerReturnSP+chain.render_sp_delta)%256 or call.ret~=chain.render_return or call.savedA~=chain.source_bank|0x80 or call.outer~=chain.render_after then hudForeign=hudForeign+1;return end
 assert(call.pc==C.hooks.MetaspriteRenderLoop.address and call.bank==C.hooks.MetaspriteRenderLoop.physical_bank,'Actual immediate HUD renderer PC and physical bank')
 assert(r('SelectedCharacter')==3 and r('AvDrawIndex')==20 and r('InvSelected',3)==q.selected and r('R4')==112 and r('R5')==0 and r('R6')==16 and r('R7')==1,'Only Bill/Lance capsule moved to the new screen anchor')
 local ptr=r('R0')+256*r('R1')
 assert(ptr==q.expected.address and bank(0xc000)==q.expected.bank,'Actual source capsule pointer and physical C bank')
 assert(not hudScope,'Prior HUD renderer returned before another starts')
 q.writes={};q.admitted=true;hudScope=q
end)
emu.addMemoryCallback(function(at,value)
 if hudScope then hudScope.writes[#hudScope.writes+1]={address=at-L.Sprite_Data,value=value}end
end,emu.callbackType.write,L.Sprite_Data,L.Sprite_Data+255)
-- Before original terminal callback; original stop cannot hide this aggregate.
emu.addEventCallback(function()
 if not done then return end
 assert(not hudScope and not hudPending and hudHelpers>0 and hudReturns>0 and hudStores==hudReturns*12,'HUD helper and real renderer/cleanup fully observed')
 assert(hudCases[1]==0,'Normal selected0 has no invented capsule')
 for i=2,7 do assert(hudCases[i]>0,'Every upgraded case renders its actual selected capsule')end
 local f=assert(io.open(OUTPUT..'combined-bill-hud.json','w'))
 f:write(json({passed=true,ROM_sha256=C.ROM_sha256,actual_variant_readback=r('BillVariant'),actual_mode_readback=r('CrossoverBehaviorVersion'),helper_calls=hudHelpers,genuine_render_returns=hudReturns,actual_OAM_stores=hudStores,case_counts=hudCases,source_anchor={112,16},OAM_bounds={100,1,123,16},foreign_renders_refused=hudForeign,scope='Actual source helper -> successful ArtPointer -> immediate farcall render PC/bank/SP/stack chain and twelve compiled OAM fields. No AvDrawIndex-only ownership. Full PPU images require review; original gallery guards remain independent.'}));f:close()
end,emu.eventType.endFrame)
