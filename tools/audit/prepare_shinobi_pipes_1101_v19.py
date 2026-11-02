"""Bounded controller-only opening traversal using source jumps and shuriken."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_shinobi_chr_owner_1101_v18 as P
O=P.R/'build/shinobi-pipes-1101-v19'
def main():
 O.mkdir(exist_ok=True)
 ref=P.R/'build/metal-storm-pipes-1101-v36/native-normal/controller.lua'
 t=ref.read_text().replace('cycles<3','cycles<2').replace('cycles==3','cycles==2').replace('cycles==5','cycles==4').replace('==35','==36')
 t=t.replace('local route,ticks,initialLives=0,0,nil','local route,ticks,initialLives=2,0,nil')
 t=t.replace('age>=2300','age>=4000').replace('frame>3000','frame>4700').replace('age%20==0','age%40==0')
 t=t.replace('jt>85','jt>60')
 prepare(O/'native',P.O/'candidate.nes',t,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=150,scope='Cold controller-only Shinobi first four pipes, source jump/shuriken. Pass requires visible grounded crossing toX1000, enemy defeat and no life loss. Four PNG maximum, compact40-frame trace.')
if __name__=='__main__':main()
