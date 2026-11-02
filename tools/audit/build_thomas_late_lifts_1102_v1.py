"""Source-link two late Thomas pipe lifts within the existing six-page kernel."""
from pathlib import Path
from rebuild_selected_thomas_bounded_v1 import R, build

P = R / 'build/thomas-platform-ground'
O = R / 'build/thomas-late-lifts-1102-v1'


def main():
    lift = (P / 'lift.s').read_text()
    def once(old, new):
        nonlocal lift
        assert lift.count(old) == 1, old
        lift = lift.replace(old, new)
    once(' sta SafecallA_SMC+1\n', ' ; InitEnemyObject overwrites incoming A immediately; outer movement restores SMC.\n')
    once(' cpy #4\n', ' cpy #6\n')
    once('XLo:.byte $90,$30,$b0,$60', 'XLo:.byte $90,$30,$b0,$60,$00,$00')
    once('XHi:.byte 1,2,2,3', 'XHi:.byte 1,2,2,3,10,11')
    once('Bits:.byte 1,2,4,8', 'Bits:.byte 1,2,4,8,16,32')
    build(P, O, (P / 'cache.s').read_text(), lift,
          extra_refs=[Path(__file__), R / 'docs/qa/allocations/thomas-late-lifts-1102-v1.json'],
          adaptation='Private source proposal: six native actor25 lift records; original four unchanged, new leftX2560/2816 initialY192. Removes3-byte dead incomingA publication before native constructor to fund6tablebytes within6144. Full source/CPU/native qualification and composition onto current ROM remain required; not installed.')


if __name__ == '__main__':
    main()
