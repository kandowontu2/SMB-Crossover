"""Deliver the measured shared GameLoop tail successor."""

from deliver_mini_contact_draw_1110 import main
from prepare_mini_shared_game_loop_tail_native_1110 import BASE, PARENT, PARENT_DELIVERY, R, ROLE


if __name__ == '__main__':
    main(default_root=R / 'build/mini-shared-game-loop-tail-native-1110',
         previous=PARENT, previous_root=BASE.parent, parent_delivery=PARENT_DELIVERY,
         patch_spans={ROLE: [(126, 0x8352, 0x8355), (126, 0x8365, 0x8369)]},
         expected_saved=94_500, change_label='The shared GameLoop call changes')
