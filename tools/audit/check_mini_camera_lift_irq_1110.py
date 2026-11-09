"""Reuse genuine native-stack ISR qualification at camera-based lift entrances."""
from pathlib import Path
import check_mini_lift_admission_async_1108_v1 as Q

Q.F.ROM=Path('build/mini-box-terrain-visible-1110/candidate.nes').resolve()
Q.F.PIN='6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
Q.MANIFEST=Path('build/mini-camera-lifts-v2-1110/proof.json').resolve()
# The coarse gate has identical start/end addresses and branch displacement.
# Its original source signature establishes those addresses, not byte parity.
Q.KERNEL=Path('build/mini-kernel-transport-1109/v2/kernel.bin').resolve()
original_setup=Q.F.setup_main

def camera_setup(bus,right,seen,mode,area,world=0,level=0):
    original_setup(bus,right-151,seen,mode,area,world,level)
    Q.N.put(bus,ScreenLeft_X_Pos=(right-255)&255,ScreenLeft_PageLoc=(right-255)>>8,
            ScreenRight_X_Pos=right&255,ScreenRight_PageLoc=right>>8)

Q.F.setup_main=camera_setup
if __name__=='__main__':Q.main()
