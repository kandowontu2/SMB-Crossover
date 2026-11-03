"""Successor preserving actual C-window ingress negative; CPU fixture only."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_deferred_death_1102_v76 as V


def main():
 source=Path(V.__file__);text=source.read_text().replace('v76','v77')
 marker=" blob,_=A.A.assemble('deferred-selector-v77'"
 assert marker in text
 patch=" text='CurrentBankC=$7da1\\n'+text.replace('PrPrince:\\n','PrPrince:\\n ldx #2\\n stx CurrentBankC\\n stx $5116\\n')\n"
 text=text.replace(marker,patch+marker)
 env=dict(__file__=str(Path(__file__)),__name__='prince_deferred_core_v77');exec(compile(text,str(source),'exec'),env);env['main']()


if __name__=='__main__':main()
