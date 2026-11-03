"""Qualify the ninth cycle with unchanged legacy public inputs and Mini cases."""
from pathlib import Path
import check_mini_mario_menu_1103_v15 as P


def main():
    text=Path(P.__file__).read_text()
    text=text.replace("O/'proposal.json'","O/'proposal-v16.json'").replace("O/'menu-CPU-v15.json'","O/'menu-CPU-v17.json'").replace("O/'menu-CPU-v15-negative.json'","O/'menu-CPU-v17-negative.json'")
    text=text.replace("Path(__file__),Path(B.__file__),","Path(__file__),Path(Parent.__file__),Path(B.__file__),")
    env=dict(P.__dict__,Parent=P,__file__=__file__,__name__='mini17');exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
