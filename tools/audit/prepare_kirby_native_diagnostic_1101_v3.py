"""Add bounded owner observations without changing the v2 gameplay assertions."""
from pathlib import Path
import prepare_kirby_owner_native_1101_v2 as V
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua


def main():
    original=V.prepare
    def observe(output,rom,t,refs,**kw):
        b=scoped_load(rom);raw=b['raw'];extra={}
        for k,n in [('WeaponsTrace','KbWeapons'),('InputsTrace','KbInputs'),('GuardYes','KbBodyContact::Protected'),('GuardNo','KbBodyContact::No')]:
            at=location(b,n);extra[k]=dict(pc=address(b,n),banks=[(at-16)//8192],bytes=list(raw[at:at+3]))
        t=V.once(t,'local C=assert(CURRENT_KIRBY_META_EARNED)','local C=assert(CURRENT_KIRBY_META_EARNED)\n'+''.join('C.hooks['+lua(k)+']='+lua(v)+'\n'for k,v in extra.items()))
        marker="owner('Capture',function(s)"
        t=V.once(t,marker,"for _,n in ipairs({'WeaponsTrace','InputsTrace','GuardYes','GuardNo'})do owner(n,function(s)event(n,r('SavedJoypadBits'))end)end\n"+marker)
        t=V.once(t,"owner('Injury',function()assert(","owner('Injury',function()event('before-injury-assert',r('SavedJoypadBits'));assert(")
        t=V.once(t,"owner('BodyContact',function(s)if", "owner('BodyContact',function(s)event('bodycontact-entry',s['cpu.x']);if")
        return original(output,rom,t,[*refs,Path(__file__)],**kw)
    V.prepare=observe;V.main()


if __name__=='__main__':main()
