"""Use original crouch-fire height to defeat the ground Goomba."""
from pathlib import Path
import prepare_karnov_combat_native_1101_v7 as V


def main():
    prepare=V.F.Q.P.prepare
    def crouch(output,rom,t,refs,**kw):
        t=V.F.Q.once(t,'pad=near and{b=updates%24<4}or{right=true}',
                    'pad=near and{down=true,b=updates%24<4}or{right=true}')
        kw['scope']=kw['scope'].replace('stand and shoot','crouch and shoot')
        return prepare(output,rom,t,[*refs,Path(__file__)],**kw)
    V.F.Q.P.prepare=crouch;V.main()


if __name__=='__main__':main()
