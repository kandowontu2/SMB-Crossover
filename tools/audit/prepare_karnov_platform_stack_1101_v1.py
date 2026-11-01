"""Observe actual CPU stack depth during the cold two-pipe crossing."""
from pathlib import Path
import prepare_karnov_platform_crossing_1101_v1 as V

def main():
    original=V.V.V.V.V.V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        marker='local function r(n)'
        controller=controller.replace(marker,"local stackMin=255;local stackSamples=0;local lowestStackWrite=512\n"+marker)
        marker='emu.addEventCallback(function()'
        controller=controller.replace(marker,"""emu.addMemoryCallback(function(a)
 if phase=='game' then
  stackSamples=stackSamples+1
  if a>=0x180 and a<lowestStackWrite then
   lowestStackWrite=a
   local s=emu.getState();stackMin=math.min(stackMin,s['cpu.sp'])
  end
 end
end,emu.callbackType.write,0x100,0x1ff)
"""+marker,1)
        controller=controller.replace("trace:close();shot('stage-endpoint')","""trace:close()
   local metrics=assert(io.open(OUTPUT..'stack.json','w'))
   metrics:write(string.format('{"minimum_sampled_SP":%d,"stack_page_write_samples":%d,"lowest_write_in_180_1ff":%d,"scope":"SP sampled at descending write addresses in stack upper half; not exhaustive IRQ-cut proof"}\\n',stackMin,stackSamples,lowestStackWrite));metrics:close()
   shot('stage-endpoint')""")
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.V.V.V.V.K.prepare=prepare
    V.main()

if __name__=='__main__':main()
