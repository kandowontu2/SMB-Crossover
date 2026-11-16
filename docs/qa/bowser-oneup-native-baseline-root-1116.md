# Bowser1UP: current native reset reproduced

Root36997 runs both genuine hidden1UP episodes on actual Downloadsbc5.
The observer intentionally finishes false at the first constructor return;
diagnostic exit0 means the requested cause is observed, not that the powerup
works correctly. No source repair is executed in these runs.

| Identity | Native receipt | INC Main/frame | Constructor-return frame | Observed reset |
| --- | --- | --- | ---: | --- |
| SMB3 Bowser | `57e5e460cc69b2bea541ae1e055c8080a357ca4d08bd43e45197d3f78c8ea6fe` |974/1992|1993|tier/status1to0; HP34 stays34 |
| SMB1 Bowser | `0478bd34e81271cac4c74ecf850d814add676c5de2394b435ebe7015589a2d09` |1289/2377|2378|tier/status1to0; HP4 incorrectly refills5 |

Both use real title/roster/Select/defaultEasy, earned Mushroom and hidden
1024/128 item birth/maturity/physical collector with13x2 overlap, native
erase/popup11 and delayed INC2to3/cue64. Loaded2615 code bytes and the full16
cookie are exact. Source and native agree on the first wrong transition:

1. BwEnsure A133 sees the increased life count.
2. It invokes BwConstruct A071, then BwSelectPlayer A0CF/BwPlayerNew A0F0.
3. Saved tier BF81 clears1to0, saved lives BF82 updates2to3, live tier BE28
   clears1to0. Mesen write callbacks report the post-STA PCs A101/A107/A118;
   the source pre-STA addresses are A0FE/A104/A115, the same instructions.
4. Actual constructor return A41A/SP227 has tier/status0 and lives3.

The signed40-byte repair remains source-only under
`allocations/bowser-life-gain-signed-source-1116.json`. In-memory6a3 candidate
has passed both genuine sourceL episodes and header/foreign checks; actual
caller/lifecycle/reached-interrupt gates remain required before physical
promotion. No successful current nativeL claim is made here.

Both ROMs remain exact. Eleven then fifteen other Mesen processes stay
untouched. Zero captures/images/videos/backups/patches/releases; existing
two-file native slot only.
