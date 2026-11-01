"""Observe all90 menu identities and all124 D-pad/Select transitions."""
from pathlib import Path
import prepare_roster_flicker_native_bounded_v3 as V


def main():
    original=V.V.prepare
    def prepare(output,rom,controller,refs,**kw):
        old='local counts={7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,4,1,2,1,6,2,4,2}'
        assert controller.count(old)==1
        controller=controller.replace(old,old.replace('4,1,2,4,1,2,1,6','4,1,2,8,1,2,1,6')).replace('All86','All90')
        refs=[p.with_name('graphics-assembly.json')if p.name=='source-stage.json'else p for p in refs]
        kw['scope']='All32 slots/90 identities,124 transitions; actual heading/display and visible PPUMASK deadlines. Four PNG cap. No gameplay claim.'
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.prepare=prepare;V.main()


if __name__=='__main__':main()
