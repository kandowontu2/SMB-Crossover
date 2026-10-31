"""Preserve the donor's independent float collision thresholds at7E98.

Stock Tile_AttrTable begins7E94 and the controller indexes four quadrants.
The expanded donor assigns the following four bytes to its float consumer.
V1/V2 incorrectly copied all eight host attribute bytes over both owners.
Keep that negative and preserve the native snapshot's actual float table.
"""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_whole_controller_edges_1031_v1.py';text=prior.read_text()
    text=text.replace('smb3plus-whole-controller-edges-1031-v1','smb3plus-whole-controller-edges-1031-v3')
    text=text.replace('smb3plus-peach-complete-controller-1031-v3','smb3plus-peach-gravity-consumer-1031-v1')
    old='text=prior.read_text()'
    new="text=prior.read_text().replace('for i in range(8):bus.ram','for i in range(4):bus.ram')"
    assert text.count(old)==1;text=text.replace(old,new)
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_correct_attribute_owners'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()


if __name__=='__main__':main()
