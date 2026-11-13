"""Pinned, reversible composition of Prince reach/sword and roster facing."""
from hashlib import sha256
import compose_menu_facing_1112 as Menu
import prince_pickup_reach_1112 as Reach
import prince_sword_box_1112 as Sword
import prince_cold_packet_1111 as Packet

PARENT = 'cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7'
PIN = 'c5ce8c1557f6eb27c97f1fb1b0404c7854f59feb18717f27171d7dcb890efbbd'


def restore_menu_code(raw):
    result = bytearray(raw)
    start = Menu.prg(3, 0xb345)
    result[start:start+len(Menu.PREFIX)] = Menu.PREFIX
    start = Menu.prg(9, 0xbc94)
    result[start:start+3] = bytes.fromhex('8d4601')
    return bytes(result)


def transform(raw, reverse=False):
    assert sha256(raw).hexdigest() == (PIN if reverse else PARENT)
    if reverse:
        # Icon reflection is its own inverse. Restore the menu code first so
        # the normal proposal authenticates its code preimages, reflect the
        # four exclusively owned icons again, then restore code once more.
        image, _ = Menu.proposal(restore_menu_code(raw))
        image = restore_menu_code(image)
        image = Reach.reverse(Sword.reverse(image))
    else:
        image = Reach.transform(raw)[0]
        image = Sword.transform(image)[0]
        image, _ = Menu.proposal(image)
    assert sha256(image).hexdigest() == (PARENT if reverse else PIN)
    return image, {'cookie': image[Packet.COOKIE:Packet.COOKIE+16].hex()}
