"""Controller pickup proof for the authenticated low-stack preparation route."""
from pathlib import Path
import json,sys
import prepare_karnov_pickup_native_1101_v4 as Q
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def main():
    shots='--shots'in sys.argv
    if shots:sys.argv.remove('--shots')
    prepare=Q.P.prepare

    def final(output,rom,t,refs,**kw):
        b=scoped_load(rom)
        t='L["KrPickupPrepareBody"]='+str(address(b,'KrPickupPrepareBody'))+'\n'+t
        t=Q.once(t,"if raw(L.KrPickupPrepareThunk)==3 then pickupPrepares=pickupPrepares+1;firstHeadTick=updates end end,emu.callbackType.exec,L.KrPickupPrepareThunk)",
            "if raw(L.KrPickupPrepareBody)==157 then pickupPrepares=pickupPrepares+1;firstHeadTick=updates end end,emu.callbackType.exec,L.KrPickupPrepareBody)")
        if shots:
            t=Q.once(t," elseif pickupPrepares>0 then pad={}",
                " elseif pickupContacts>0 then pad={b=updates%24<4}\n elseif pickupPrepares>0 then pad={}")
            t=Q.once(t,"if pickupPrepares>0 and pickupContacts>0 and sawRising and sawMature and sawOwner and sawErased and not lastMain then finish(kr(0x65)&3==1 and kr(0x68)&128==0,'Real head-hit block spawn, visible emergence, contact-only mushroom and earned source double shot');return end",
                "if pickupPrepares>0 and pickupContacts>0 and sawRising and sawMature and sawOwner and sawErased and maxShots==2 and not lastMain then finish(kr(0x65)&3==1 and kr(0x68)&128==0,'Real emerged mushroom collected by contact, then original double shot fired');return end")
        kw['scope']+=' Observe authenticated ROM29 prepare body directly; row24 retains its A3 thunk. '+('Pulse the actual fire button after collection and require two simultaneous original projectiles.'if shots else'')
        return prepare(output,rom,t,[*refs,Path(__file__)],**kw)

    Q.P.prepare=final
    Q.main()


if __name__=='__main__':main()
