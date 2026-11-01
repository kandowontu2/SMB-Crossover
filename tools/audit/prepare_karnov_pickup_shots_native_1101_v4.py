"""Verify the first earned mushroom by firing the original double shot."""
from pathlib import Path
import prepare_karnov_pickup_native_1101_v4 as Q


def main():
    prepare=Q.P.prepare

    def shots(output,rom,t,refs,**kw):
        t=Q.once(t," elseif pickupPrepares>0 then pad={}",
            " elseif pickupContacts>0 then pad={b=updates%24<4}\n elseif pickupPrepares>0 then pad={}")
        t=Q.once(t,"if pickupPrepares>0 and pickupContacts>0 and sawRising and sawMature and sawOwner and sawErased and not lastMain then finish(kr(0x65)&3==1 and kr(0x68)&128==0,'Real head-hit block spawn, visible emergence, contact-only mushroom and earned source double shot');return end",
            "if pickupPrepares>0 and pickupContacts>0 and sawRising and sawMature and sawOwner and sawErased and maxShots==2 and not lastMain then finish(kr(0x65)&3==1 and kr(0x68)&128==0,'Real emerged mushroom collected by contact, then original double shot fired');return end")
        kw['scope']+=' After real collection, pulse the actual fire button and require two simultaneous original source projectiles.'
        return prepare(output,rom,t,[*refs,Path(__file__)],**kw)

    Q.P.prepare=shots
    Q.main()


if __name__=='__main__':main()
