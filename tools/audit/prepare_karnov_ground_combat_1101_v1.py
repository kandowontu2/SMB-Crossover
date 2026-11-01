"""Avoid automatic jumps into the enemy group above the first post-pit blocks."""
from pathlib import Path
import prepare_karnov_pit_combat_1101_v1 as V
def main():
    original=V.V.V.V.V.V.V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        needle='or (wx>=1290 and wx<1362)'
        assert needle in controller
        controller=controller.replace(needle,'or (wx>=1140 and wx<1362)')
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.V.V.V.V.V.K.prepare=prepare
    V.main()
if __name__=='__main__':main()
