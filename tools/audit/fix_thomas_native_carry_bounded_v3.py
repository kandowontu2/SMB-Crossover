"""Import proven native lift displacement before the next donor actor update."""
from pathlib import Path
from rebuild_selected_thomas_bounded_v1 import R,build,sha
P=R/'build/thomas-pipe-lifts';O=R/'build/thomas-native-carry'


def main():
    assert sha(P/'candidate.nes')=='173ab59b94b295b326d89dfe7a63be60e89b82954f6ad6e52a43bc5a75d1bb21'
    cache=(P/'cache.s').read_text()
    old=' bcc ThNaturalMoveDone\n ; Raw10'
    assert cache.count(old)==1
    cache=cache.replace(old,' bcc ThNaturalMoveDone\n jsr ThomasHostAfterTerrain ; import prior completed native support/carry before donor motion\n ; Raw10',1)
    build(P,O,cache,(P/'lift.s').read_text(),
          extra_refs=[Path(__file__),P/'boarding-runup/probe.json'],
          adaptation='Import completed native platform support/carry before donor motion; retain genuine platform25 initialization, AI and collisions. No speculative constructor-stack transport change. The running-start control negative actually boards (flag5) but loses carry as the platform rises.')


if __name__=='__main__':main()
