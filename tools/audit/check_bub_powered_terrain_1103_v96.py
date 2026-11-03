"""Finish only the64px column's far-side landing after the prior180-update bound."""
from pathlib import Path
import check_bub_powered_terrain_1103_v95 as P


def main():
    text=Path(P.__file__).read_text()
    text=text.replace('for top in[176,160,144]:','for top in[144]:').replace('range(180):','range(220):')
    text=text.replace("'powered-terrain-CPU-v95.json'","'powered-terrain-CPU-v96.json'")
    text=text.replace('Path(__file__),Path(P.__file__),P.ROM','Path(__file__),Path(Parent.__file__),Path(P.__file__),P.ROM')
    text=text.replace('cross32/48/64px columns at160..192','cross64px columns at160..192; unchanged32/48px cases alreadypassed95')
    env=dict(P.__dict__,Parent=P,__file__=__file__,__name__='powered96')
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
