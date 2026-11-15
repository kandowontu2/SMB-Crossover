# Authenticated Prince sword controls

The installed16a battle envelope RAM2:DAC6..DDBE is byte-identical to the
retained760-byte assembly, SHA256
`afdef17ad9635e03109557eb7c7bba60644eb81af70bc8383a1100bd192f702e`.
All303 original instruction preimages in its retained source match donor
SHA256 `5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4`.
The current input decoder A097..A134 also matches its retained assembly.

Bounded original-CPU component audit passes, receipt
`4b8fb721fd07587b742d25d8ad4b3e8ee27359abf77a1a00734536629d2adbac`.
It extends the initial map receipt
`ad1b3ad8d6ed148ccbe82201e473e33f53624481556240306332283a43526bdc`
with whole-combat input priority. These are explicitly seeded instruction
primitives; no ordinary gameplay, full-stage or physical-cadence claim.

| Input | Actual donor handler | Admission/result |
| --- | --- | --- |
| A128 |7:FE67| Held bit requests attack action58 unless current action67. |
| B64 |7:FE7A| Held bit requests parry action62 only when actual pose171. Pose170 is cleared to action0 by DBB9 but does not admit parry. |
| Forward |5:8972| Right1 when facing255, Left2 when facing0. Requests action56 through its distance gate; does not replace attack58. |
| Back |5:8943| Opposite direction requests retreat57. It exits while action56 or58; A128 also suppresses the normal retreat path. |

A and B use held-bit tests, not a button-edge/debounce condition. The full
F090 path evaluates attack, parry, advance and retreat in that order.
At opposed facing, pose171 and64-pixel separation, actual whole-handler
components produce B→62, B+Forward→56, B+Back→57, A+direction→58 and A+B→62.
Adding direction to B can therefore replace the parry request. This is the
original donor priority, not a new port input mapping.

Drawing is automatic. F090 first rejects equal facing and current action55
or74. Its later gates include sword inventory, vertical difference−30..29,
active opponent and original0401=0. With sword1/request0, the actual898B
path increments sword to2 and installs draw action55 without A or B. No
active opponent means no automatic draw; this does not establish a free
manual draw feature.

The actual8AE9 consumer requires pose171 and a nonzero sheath marker. For
the player it sets sword1 and action93. The new transition supplies marker1
only on real opponent loss. Equal-facing F090 exits before this consumer,
so that original exit remains explicitly open. No manual sheath button is
asserted from these handlers.

The original fullguard failure remains retained separately. Its policy
starts its B branch only after sword2 is observed. Whether prior Right was
already consumed during admission, and whether later pose/action gates skip
B, requires the reached-branch trace on frozen f582 controls. No new route
policy or game byte is qualified by this map alone.

## Reached late-control diagnosis

Source14335 replays the frozen failed f582 inputs on installed16a without
input or game-byte changes. Diagnostic receipt is
`65245f26d643c6971ff35be7e0bc9755067273810156cb740f24eb90f1b41e06`;
its retained full-route receipt remains8ebb574a. There are61 late F090
calls,25 reaching FE7A,9 actual B pose checks and one successful action62.

| Main | Actual source pad | Reached result |
| --- | ---: | --- |
|4679|Right1| UID128 birth at1882/176 installs draw55 then advance56. |
|4683..4695|B64| Poses164/165/158/170 fail parry;170 clears action0. |
|4699|B64| Actual pose171 admits62. |
|4739|A128| Attack58 is installed. |
|4755|A128| Original attack defeats UID128; sword becomes1 at action58/pose154. |
|4759|0| The controller's neutral release pause is consumed during UID129 birth. Draw55 is installed at1918/176, pose155. |
|4763..4779|B64| Imported B is correct, but busy action55 exits before FE7A; drawing moves the player to1936. |
|4783|B64| Pose170 clears action0; B reaches its pose test and declines. |
|4784|B64| First injury occurs before the next control update. Later action74 suppresses controls. |

HP then falls once at4784/4814/4844/4874. This is four separate injuries,
not a same-Main fatal drain or button-edge failure. The trace's HP `PC`
samples the CPU inside its memory-write accessor (A343, an operand position);
it is not presented as an instruction-entry writer witness. Its reliable
control-entry/action-store labels establish the admission diagnosis above.

The next ordinary-input hypothesis is to keep A through the actual
marker85/action58 kill-to-new-target interval, rather than insert the old
eight-update neutral release. FE67 can replace the same-pass automatic
draw55 with attack58; it is already the original attack button. A new
bounded successor must prove the actual continuation. The installed game,
the native-qualified narrow controllers and equal-facing exit are unchanged.
