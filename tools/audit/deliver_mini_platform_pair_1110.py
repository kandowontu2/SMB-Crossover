"""Deliver the native-tested two-lag-frame Mini build."""

from deliver_mini_contact_draw_1110 import main
from prepare_mini_platform_pair_native_1110 import Mix, PIN, R, ROLE, Stage


if __name__ == '__main__':
    main(default_root=R / 'build/mini-platform-pair-native-1110', previous=PIN,
         previous_root=Stage.PARENT_ROOT, parent_delivery=Stage.PUBLISHED,
         patch_spans={Stage.ROLE: [(bank, *bounds) for bank, bounds, _ in Stage.EXTENTS],
                      Mix.AUDIO_ROLE: [(29, 0xAB1C, 0xAB29), (29, 0xAC12, 0xAC28)],
                      ROLE: [(0, 0xB472, 0xB476)]},
         expected_saved=64_765, change_label='The shared terrain, mixer, and platform collision changes')
