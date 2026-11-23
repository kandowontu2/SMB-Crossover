# Mega Giant Mario's block rewards in 1-1

On `3ce7788d`, ordinary Right input brought Mega Giant Mario to the first
Mushroom block. The crush routine read the real `$C1` at X336/Y144 and
changed it to a plain brick before calling the native block handler.
The block shattered and the Mushroom never appeared. The first coin
question block at X256 showed the same problem. Linked Mushroom
diagnostic `3b1ac96cf5796852e17b542c6aa57f356a6cbfb5d0bfacae99c18fc43c537d07`.

The fix passes the tile Giant actually struck to the native block
handler. It changes nine bytes in Giant's existing PRG90 crush routine.
In a linked replay, the native handler awarded the question block
rewards and still shattered four plain bricks. The PRG90 changes and
the DK Jr. lift changes occupy separate bytes. The paired check also
matched 7,436 bytes used by the Giant replay outside the repair.

## Mega Giant Mushroom and level clear

Mesen selected Mega Giant Mario through the normal roster and held
Right. On `6201e3b6`, the first Mushroom emerged at X336/Y136 and Giant
collected it at X327/Y176. The normal 60-update growth sequence ran,
awarded 1,000 points, and left him moving with the upgrade and both
lives for 25 further grounded updates. Receipt
`5871ce324e566953b1f0e6b28471d7cd2623e8784281c4a76a8403a9a119b412`.

A separate controller-only run on the same image passed the flagpole
at X3159 and reached active 1-2 at X40/Y48 with both lives. It took
3,734 video frames and the Giant body drew 46 parts from CHR pages 180
and 182. Receipt
`f4f8605ceeb125e58d8fb048cce110666ba826136003873a39ed26b92967f3d7`.
Both runs used controller input and wrote zero captures.

Mesen repeated the Mushroom run from the Downloads nightly and returned
the same receipt. The installation verified the ROM bytes and checked
for a same-name patch before and after replacing the Downloads file.

## Fire Flower

The second Mesen route collected the first Mushroom, kept the first
upgrade through 25 grounded returns, and reached the authored second
question block. The Fire Flower emerged at X1248/Y136. Giant collected
it at X1264/Y176 on the normal route and obtained his second tier after
60 original growth updates. The Flower granted 1,000 points. He still
had both lives and tier two after 25 grounded returns at X1307/Y176.
Receipt `a72472685c9e7d767f03247f2be25ea0ead6cdc2a7bea9a24d12390eae288dce`.

## Hidden 1-UP and Star

On the Downloads nightly, Giant jumped from X1016 to reveal the 1-UP
from X1024/Y128. He caught it at X1020/Y166, gained a third life, and
retained that life and the Mushroom upgrade through 25 grounded returns
at X1049/Y176. Mesen receipt
`8593d60a65c450849a185db80fc3ba3c44636709ce84e2b243525d65c415aef5`.

On the same Downloads nightly, the Star brick at X1616 released the
item, which Giant collected at X1627/Y176. The native collector started
the timer at 35 and queued the Star music. The game awarded 1,000
points, and he reached X1671/Y176 with tier two, both lives and 25
grounded returns. Mesen receipt
`0a4757368d1ab585adf549ef2a76cdf4b2a56c896f2a5f94889612eafb3c15ab`.

The first observer checked the music queue after the interrupt had
already read it. The passing replay observed the mapped collector's
actual timer and music writes before the interrupt. Earlier diagnostic
`bf55d07e8fadd07747c30a309402a9fbeee3153c9fe3b35d8f70a884f2afa65d`.
