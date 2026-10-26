-- Read-only full real ReleaseBalloon owner. Native policy directly subtracts
-- eight/clamps, bypassing InventorySpend; this is a separate source debit.
local function pharaohDebit(before,shotAge,count,star,after)
 local paidPath=shotAge>=45 and count<2 and star==0
 local expected=paidPath and math.max(0,before-8)or before
 assert(after==expected,'Full native Pharaoh release direct eight-unit/clamp policy')
 local spent=before-after
 if spent>0 then fundedDebit(4,spent,before,after,true)end
 event('actual-pharaoh-direct-debit',{before=before,after=after,declared_cost=8,actual_spent=spent,shot_age=shotAge,active_shots=count,star=star,paid_path=paidPath,source='full actual SpecialWeapons::ReleaseBalloon return'})
 capture(current.q.name..'-direct-pharaoh-debit')
end
hook('SpecialWeapons::ReleaseBalloon',function()
 if not entered or not current or current.component~='funded' or current.q.item~=4 then return end
 local owner=current;local s=emu.getState();local slot=s['cpu.x']
 assert(r('InvSelected',9)==4 and r('SsSelected')==4 and slot==r('RgSlot'),'Real selected Pharaoh release owner/slot')
 local before,shotAge,count,star=stock(),r('RgShotAge',slot),pool(),r('StarInvincibleTimer')
 local entry={pc=s['cpu.pc'],sp=s['cpu.sp'],bank=bank(s['cpu.pc']),slot=slot,before=before,shot_age=shotAge,active_shots=count,star=star}
 onReturn('bass-pharaoh-direct-release',function()
  assert(current==owner and r('StarInvincibleTimer')==star,'Same finite release owner and stable seeded star state')
  local t=emu.getState()
  event('actual-pharaoh-release-full-return',{entry=entry,return_pc=t['cpu.pc'],return_sp=t['cpu.sp'],return_bank=bank(t['cpu.pc']),after=stock()})
  pharaohDebit(before,shotAge,count,star,stock())
 end)
end)
