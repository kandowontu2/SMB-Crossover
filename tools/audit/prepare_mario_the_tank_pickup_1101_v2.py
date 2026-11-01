"""Later jump aligns the head with the mushroom block rather than its neighbor."""
from pathlib import Path
import prepare_mario_the_tank_pickup_1101_v1 as N
def main():
    original=N.prepare
    def prepare(output,rom,controller,refs,**kw):
        controller=controller.replace('x>=290 and x<350','x>=322 and x<365')
        return original(output.with_name('probe2'),rom,controller,[*refs,Path(__file__)],**kw)
    N.prepare=prepare;N.main()
if __name__=='__main__':main()
