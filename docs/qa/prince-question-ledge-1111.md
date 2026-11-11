# Prince’s first floating question-block climb

In World 1-1, the original climb state reaches X1752/Y173 beside the
question block at X1744–1759 with top Y144. The old host alignment
looks below the block and falls back to a 32-pixel cell. This starts
the climb too far right and leaves Prince at X1771/Y113 without a
native foothold.

The repaired path recognizes an isolated, exposed native question
block and starts the same climb at X1728. Native wall collision
resolves the moving feet and the original script reaches X1731/Y112
grounded, with the right foot on X1744. The same typed tile may support
the original neutral pose when both soles and the native grounded
state agree. True falls, mirrored climbs and covered or adjacent
terrain keep their previous decisions.

On candidate `99eeae72`, a cold Mesen run stays grounded for 20
original updates with 4 HP and both lives. A second run jumps from
the corrected stance, passes above the live trailing Goomba at X1751
and reaches grounded X1853/Y176 with 4 HP and both lives. Both use
stock 1-1 terrain and controller input. The remaining stage is open.

- Neutral receipt `00b49ef5a58b9ab642456b45cff808d86c6cf0698533d6728b11105f1ee5dc7a`
- Goomba-pair receipt `e5c8b4fc29893ace26aca1200166d35a8a38b053a6e51ef6bdea39270030aa3e`
- Candidate `99eeae726f5cb7b5af35c4e59421ea110cd3365336e76e65114b49c75c11018e`

The earlier installed ROM can pass this pair by immediately jumping
from the overshot unsupported donor pose. That controller-only result
is `f2526466044b95664fa3367b7b4ab8084d1fe5d8b7fa5f8a9128a8fc0054316e`.

The CPU qualification verifies 42 preserved geometry cases, 1,279
preserved material pairs, and 355 IRQ plus 355 lag-NMI cuts. The
runtime stream fits the existing 6,400-byte staging limit.

[Source](../../tools/reference/prince_question_ledge_1111.s) ·
[CPU check](../../tools/audit/check_prince_question_ledge_1111.py) ·
[Physical replay](../../tools/audit/replay_prince_question_route_1111.py)
