"""Cold controller-only Shinobi menu/entry/movement smoke, three screenshots."""
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_shinobi_menu_1101_v13 as P


def main():
 source=P.R/'build/metal-storm-background-1101-v19/native-smoke/controller.lua'
 text=source.read_text().replace('cycles<3','cycles<2').replace('cycles==3','cycles==2').replace('cycles==5','cycles==4').replace('==35','==36')
 prepare(P.O/'native-smoke',P.O/'candidate.nes',text,[source],expected=sha(P.O/'candidate.nes'),timeout=90,
         scope='Cold title, right twice/down/Select, Shinobi Start and36 right+B frames. No state writes or complete1-1 claim.')


if __name__=='__main__':main()
