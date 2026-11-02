"""Correct the physical capture event schema; preserve the exact proven inputs."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
O=R/'build/bub-menu-candidate-1102-v2'
PIN='5a8a04c3deabafc2222e594bdcefd4a445afecb5c1ab4c1753e66acc4a883d29'

def main():
    rom=O/'combined-cold-fixed.nes';assert sha(rom)==PIN
    source=O/'native-cold-fixed-bub-pop/controller.lua';text=source.read_text()
    changes={
        " if q.pops>combat_base.pops then\n  assert":" if q.pops>combat_base.pops then\n  local observed=BUB_OBSERVER.finish();combat_write(false,'pre-assert-earned-pop-observation',observed)\n  assert",
        "if e.kind=='original-source-trap'then slot=e.detail.slot;born=e.Main end":"if e.kind=='original-source-trap'or e.kind=='original-source-trap-commit'then slot=e.detail.slot;born=e.detail.completed_Main_pending or e.Main end",
        "slot~=nil and born~=nil and q.completed_Main-born<40":"slot~=nil and born~=nil and q.completed_Main-born>=0 and q.completed_Main-born<40",
        "combat_event('earned-pop',geometry(slot));local final":"local detail=geometry(slot);detail.elapsed_source_updates=q.completed_Main-born;combat_event('earned-pop',detail);local final"
    }
    for old,new in changes.items():assert text.count(old)==1,old;text=text.replace(old,new)
    oldkeys=source.read_text().split('local function combat_keys()',1)[1].split('local function combat_event',1)[0]
    assert text.split('local function combat_keys()',1)[1].split('local function combat_event',1)[0]==oldkeys
    observer=R/'build/bubble-bobble-source-1101-v1/native-observer-bub-1102-v5.lua'
    assert "event('original-source-trap-commit'"in observer.read_text()
    refs={Path(__file__),source,observer,O/'combined-cold-fixed.json',R/'docs/qa/allocations/bubble-cold-fixed-1102-v8.json'}
    prepare(O/'native-cold-fixed-bub-pop2',rom,text,refs,expected=PIN,timeout=230,
        scope='Exact same source-proven24pxshot/Rightinputs as negativepop1. Observer-only correction accepts actual physical original-source-trap-commit schema and its pendingMain epoch, writes complete live events before assertions, retains nonnegativeage<40/committedcapture/physicalnativeDefeat/State32.',allow_interactive=True)

if __name__=='__main__':main()
