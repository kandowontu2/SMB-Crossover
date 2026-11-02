"""Capture the first exact vector imbalance before preserving its assertion."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/thomas-full11-1102-v1'
def main():
    source=O/'native-vectors/controller.lua';text=source.read_text()
    marker="   assert(q.kind==kind and q.sp==s['cpu.sp'],'Real vector stack balance')"
    assert text.count(marker)==1
    diagnostic="""
   if q.kind~=kind or q.sp~=s['cpu.sp'] then
    local f=assert(io.open(OUTPUT..'vector-mismatch.json','w'));f:write(json({frame=frame,kind=kind,entry=entry,leave=leave,pc=s['cpu.pc'],entry_sp=q.sp,exit_sp=s['cpu.sp'],saved_kind=q.kind,saved_a=q.a,saved_x=q.x,saved_y=q.y,current_a=s['cpu.a'],current_x=s['cpu.x'],current_y=s['cpu.y'],remaining_depth=#isrs,phase=phase,Main=updates}));f:close()
   end
"""
    text=text.replace(marker,diagnostic+marker)
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    prepare(O/'native-vector-trace',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Read-only first vector mismatch diagnostic. Preserve complete RTI/stack/SMC assertions and unchanged controls; no ROM edits, one small JSON on first mismatch.')
if __name__=='__main__':main()
