"""Standalone read-only Lua recipe; the root owns all native Mesen runs."""
from hashlib import sha256
import re

import check_dkjr_powerups_current_1113 as B

CONTROLS=B.R/'tools/reference/dkjr_first_pickup_controls_1113.lua'


def one(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after)


def controller(raw,*,reserved_negative=False):
    text=B.SOURCE.read_text()
    controls=CONTROLS.read_text()
    if reserved_negative:
        controls=one(controls,"for i=0,5 do if r('Enemy_Flag',i)==1", "for i=0,4 do if r('Enemy_Flag',i)==1")
        controls=one(controls,"assert(i<6 and r('Enemy_ID',i)==37", "assert(i<5 and r('Enemy_ID',i)==37")
        start=controls.index("emu.addMemoryCallback(function()\n if not game or not active()or not mapped(L.NrPrepare")
        end=controls.index("emu.addMemoryCallback(function()\n if not game or not mapped(L.HandlePowerUpCollision",start)
        controls=controls[:start]+controls[end:]
    text=one(text,'local returns,pending={},nil',
        'local returns,pending={},nil\nlocal helperBirths,itemBirth,matureSeen,pickupReturn,followup,pickupPending,pickupReturns,released,grantEpoch,prepared={},nil,nil,nil,0,nil,{},0,nil,{}')
    text=one(text,'attempts=attempts}',
        'attempts=attempts,helper_births=helperBirths,item_birth=itemBirth,mature=matureSeen,pickup_return=pickupReturn,followup_updates=followup,prepared_slots=prepared}')
    start=text.index('local function control()');end=text.index('\nemu.addMemoryCallback',start)
    text=text[:start]+controls+text[end:]
    text=one(text,"if #pickups>0 then finish(true,'genuine-native-item-contact');return end",'''if pickupReturn and r('GameEngineSubroutine')==8 and r('PlayerStatus')==1 and r('GuestPowerupActive')==0 then
   if not grantEpoch then grantEpoch=epoch end;followup=epoch-grantEpoch
   if followup>=30 then
    assert(#helperBirths==1 and itemBirth and matureSeen and #effects>=1 and #pickups==1,'Real helper/head/item/maturity/collector chain')
    assert(pickupReturn.kind==0 and pickupReturn.erased and ram(0x8fe)==2,'Mushroom native return and live source owner')
    assert(prepared[tostring(pickupReturn.slot)]and prepared[tostring(pickupReturn.slot)].kind==0,'Actual selected item slot preparation')
    assert(itemBirth.actor.slot==pickupReturn.slot and matureSeen.actor.slot==pickupReturn.slot,'Same selected native item at birth, maturity and collection')
    finish(true,'natural-first-mushroom-with-stock-helper');return
   end
  end''')
    if reserved_negative:
        text=one(text,',grantEpoch,prepared={},nil,nil,nil,0,nil,{},0,nil,{}',',grantEpoch={},nil,nil,nil,0,nil,{},0,nil')
        text=one(text,',prepared_slots=prepared','')
        text=one(text,"\n    assert(prepared[tostring(pickupReturn.slot)]and prepared[tostring(pickupReturn.slot)].kind==0,'Actual selected item slot preparation')",'')
        text=one(text,"\n    assert(itemBirth.actor.slot==pickupReturn.slot and matureSeen.actor.slot==pickupReturn.slot,'Same selected native item at birth, maturity and collection')",'')
    text=one(text,'if epoch>1500 or frame>6000 then', 'if epoch>2000 or frame>9000 then')
    b=B.W.Symbols.bundle();b['raw']=raw
    names=set(re.findall(r"\br\('([^']+)'",text))|set(re.findall(r'\bL\.(\w+)',text))
    labels={n:B.W.address(b,n)for n in sorted(names)}
    prefix='local L={'+','.join(f'{n}={v}'for n,v in labels.items())+'}\n'
    prefix+=f'local ROM_SHA="{sha256(raw).hexdigest()}"\n'
    constants=(('HEAD_OFFSET','HuHead'),('EFFECT_OFFSET','NativeRarePlayerHeadCollisionCore'),('PICKUP_OFFSET','HandlePowerUpCollision'))
    if not reserved_negative:constants+=(('PREPARE_OFFSET','NrPrepare'),)
    for constant,name in constants:
        prefix+=f'local {constant}={B.W.location(b,name)-16}\n'
    return prefix+text


def full_stage_controller(raw):
    """Retained continuous full-stage controls; only bind new owned layout."""
    import check_dkjr_full_stage_physical_1111 as Full
    original=Full.Delivery.SCRIPT.read_bytes()
    assert sha256(original).hexdigest()==Full.Delivery.SCRIPT_PIN
    text=Full.compose(original.decode('utf-8').replace('\r\n','\n'),
        Full.DRIVER.read_text(encoding='utf-8'),raw[B.COOKIE_AT:B.COOKIE_AT+16].hex(),0xd1f0)
    text=one(text,'local centers={','local centers={[336]=128,')
    assert text.count('ram(2,0x8fd)~=8')==2
    text=text.replace('ram(2,0x8fd)~=8','ram(2,0x8fd)~=9')
    text=one(text,"local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''",f'local rom="{sha256(raw).hexdigest()}"')
    text=one(text,"os.getenv('SMB_TEST_VARIANT')=='0'",'true')
    assert text.count("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'")==2
    text=text.replace("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'",'true')
    text=one(text,"emu.addEventCallback(guarded('input',function()",
        "if CPU_CONTROLLER_OPENING then frame=541;playing=true end\nemu.addEventCallback(guarded('input',function()")
    return text
