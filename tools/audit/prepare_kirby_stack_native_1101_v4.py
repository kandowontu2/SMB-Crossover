"""Observe actual native stack addresses in the unchanged earned cases."""
from pathlib import Path
import prepare_kirby_owner_native_1101_v2 as V


def main():
    original=V.prepare
    def observe(output,rom,t,refs,**kw):
        t=V.once(t,'local C=assert(CURRENT_KIRBY_META_EARNED)',
            'local C=assert(CURRENT_KIRBY_META_EARNED)\nlocal stackDeep={address=512};local stackWrites=0;local nativeMainSP={}\n')
        t=V.once(t,"hook('GameLoopOwned',function()", "hook('GameLoopOwned',function()\n if entered then nativeMainSP[tostring(emu.getState()['cpu.sp'])]=true end")
        marker='-- All callback registration is startup-static. No callback adds/removes callbacks.'
        t=V.once(t,marker,'''emu.addMemoryCallback(function(a)
 if entered then
  stackWrites=stackWrites+1
  if a<stackDeep.address then
   local s=emu.getState();stackDeep={address=a,SP=s['cpu.sp'],PC=s['cpu.pc'],bank=bank(s['cpu.pc']),phase=phase,update=updates,NmiDisable=r('NmiDisable'),NMI=nmi~=nil,IRQ=irq}
  end
 end
end,emu.callbackType.write,0x100,0x1ff)
'''+marker)
        t=V.once(t,'minSP=minSP,screenshots=images,','minSP=minSP,actual_stack_deepest=stackDeep,actual_stack_writes=stackWrites,actual_Main_entry_SP=nativeMainSP,screenshots=images,')
        return original(output,rom,t,[*refs,Path(__file__)],**kw)
    V.prepare=observe;V.main()


if __name__=='__main__':main()
