"""Use the donor's initial jump-direction latch for powered bubble riding."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-earned-flower-1103-v94'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-earned-flower-1103-v92/bub-flower/controller.lua';text=source.read_text()
    before='gap>=0 and gap<=16';assert text.count(before)==1
    text=text.replace(before,'gap>=-12 and gap<=-4')
    before="full_part='jump';full_step=0;full_pad={right=true,a=true};full_event('grown-free-bubble-gap16-freshA')";assert text.count(before)==1
    text=text.replace(before,"full_part='jump';full_step=0;full_pad={a=true};full_event('powered-vertical-takeoff-bubble-behind4to12')")
    before='  full_pad={right=true,a=true};full_min_y=math.min(full_min_y,y)';assert text.count(before)==1
    text=text.replace(before,before+"\n  if full_part=='jump'and q.source_total_jump_starts<=full_ride_base.source_total_jump_starts then full_pad={a=true}end")
    before="gap>=0 and gap<=24 then flower_change('ride');full_pad={right=true,a=true}";assert text.count(before)==1
    text=text.replace(before,"gap>=-12 and gap<=-4 then flower_change('ride');full_pad={a=true}")
    before='  full_pad={right=x<tx-2,left=x>tx+3,a=true}';assert text.count(before)==1
    text=text.replace(before,before+'\n  if q.source_total_jump_starts<=flower_launch_base.source_total_jump_starts then full_pad={a=true}end')
    rom=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
    donor=R/'build/bub-upgrades-root-1102-v47/component.s';assert 'sta $c005,x ; source$D36F'in donor.read_text()
    prepare(O/'bub-flower',rom,text,[Path(__file__),source,donor,R/'build/bub-earned-flower-1103-v93/bub-flower/capture/full11.json'],expected=PIN,timeout=240,allow_interactive=True,scope='Private samecf7, no mechanics/state/helper changes. Actual donor D36B..D36F latches initial horizontal direction intoactor+5.93 airborne left alignment produced a genuine bubble restart latchedleft, then Right could not reverse it.94 makes original initial jump vertical, with grown bubble4..12behind; only after observed originaljump entry holdRight so the later original bubble restart latchesRight. All earned/support/source/hardware/no-death assertions remain.')
if __name__=='__main__':main()
