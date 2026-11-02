"""Prepare the controller-only full 1-1 Arthur discovery for root's queue."""
from pathlib import Path
import prepare_arthur_camera_1101_v3 as P
from prepare_selected_native_packet_v1 import prepare,sha


def main():
 ref=P.P.R/'tools/reference/arthur_full11_native_1101_v3.lua'
 prepare(P.O/'full11',P.O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=240,scope='Actual cold menu/controller-only1-1: readonly terrain/enemy reaction, existing Arthur6A/12release/9A doublejump, allfourpipes/threegaps/stairs/flag and actual1-2gameplay. No outcome/state/helper writes. Passrequiresno life loss,allcrossings. Capture4PNGs and one compact12-frameCSV. Discovery mayfail; no qualification untilrootrun.')


if __name__=='__main__':main()
