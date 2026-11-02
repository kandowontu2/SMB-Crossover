"""Observe exact Start identity plus the existing BT gameplay palette lease."""
from pathlib import Path
import copy,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
import prepare_bub_menu_qualification_1102_v2 as N
O=N.O;PIN='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'

def main():
    rom=O/'combined-visible.nes';assert sha(rom)==PIN
    proof=O/'BT-Start-palette-CPU-v2.json';q=json.loads(proof.read_text())
    assert q['passed'] and q['ROM_SHA256']==PIN and q['active_groups']==96 and q['private_variant']==32
    b=scoped_load(R/'build/wwf-death-1102-v2/candidate.nes')
    old=O/'native-visible-bt-start/controller.lua';text=old.read_text()
    anchor="local log=assert(io.open(OUTPUT..'observations.csv','w'))"
    trace="""local bt_group_writes={}
emu.addMemoryCallback(function(_,v)
 if phase=='game'and #bt_group_writes<16 then
  local s=emu.getState();local a=emu.convertAddress(s['cpu.pc'])
  bt_group_writes[#bt_group_writes+1]={value=v,PC=s['cpu.pc'],physical=a and a.address or -1}
 end
end,emu.callbackType.write,L.FmGroups)
"""
    assert text.count(anchor)==1;text=text.replace(anchor,trace+anchor)
    oldassert="assert(startGroups==Q.launch.groups and r('FmGroups')==Q.launch.groups,'Simultaneous Select/confirm preserved identity')"
    newassert="""assert(startGroups==32,'Exact post-Select identity at real Start boundary')
  assert(r('FmGroups')==96,'Existing BT body color lease64 retains identity32')
  assert(emu.read(3*8192+0x1f60,emu.memType.nesWorkRam)==1 and emu.read(3*8192+0x1f61,emu.memType.nesWorkRam)==32,'Actual private BT ready and selected source variant')
  local lease=false;for _,w in ipairs(bt_group_writes)do if w.value==96 then lease=true end end
  assert(lease,'Actual existing gameplay palette marker writer observed')
  print('BT Start32 -> existing palette lease96; private source variant32 ready1; writes '..#bt_group_writes)"""
    assert text.count(oldassert)==1;text=text.replace(oldassert,newassert)
    # The retained v1 negative already has visual evidence. This identity-only
    # successor needs no PNG and keeps the one-root file budget small.
    assert text.count("shot('active-owner');finish()")==1
    text=text.replace("shot('active-owner');finish()","finish()")
    refs={Path(__file__),old,proof,R/'tools/audit/check_bub_bt_start_1102_v2.py',
          R/'tools/audit/bub_menu_qualification_1102_v2.lua',O/'combined-visible.json',
          R/'docs/qa/allocations/bubble-visible-1102-v6.json'}
    prepare(O/'native-visible-bt-start2',rom,text,refs,expected=PIN,timeout=120,
        scope='Unchanged4395 original simultaneous Select+A. ExactStart32, existing body-color lease96, actual private BtVariant32/ready1; source-proven observer correction only. No PNG/fullstage/install.',allow_interactive=True)
    own=[p for p in O.rglob('*')if p.is_file()]
    assert len(own)<=128 and sum(p.stat().st_size for p in own)<32000000
    print(json.dumps(dict(files=len(own),bytes=sum(p.stat().st_size for p in own),ROM_SHA256=PIN,ROM_changed=False)))

if __name__=='__main__':main()
