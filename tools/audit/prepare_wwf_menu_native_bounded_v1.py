"""Reuse the all-roster pixel/PPUMASK observer on an unqualified linked stage."""
from pathlib import Path
import prepare_roster_flicker_native_bounded_v3 as V


def main():
    original=V.V.prepare
    def prepare(output,rom,controller,refs,**kw):
        refs=[p.with_name('assembly-stage.json')if p.name=='source-stage.json'else p for p in refs]
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.prepare=prepare;V.main()


if __name__=='__main__':main()
