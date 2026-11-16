# Battletoads mature-item candidate source qualification, November 16

This is source-only qualification of exact candidate
`91dc4ac58ae749bc81f1ef91953c7c3e5aba73dd07e4b6ea2cd3059d1cdb41cc`
over actual Downloads parent
`6a3ff7c9a60b5ff5906d38f7815f021062006e0817d43e7ed139f47589c4eee2`.
No candidate ROM file, Mesen run, capture, backup, patch, release or delivery was
performed by this helper. Root owns any subsequent physical qualification.

## Repair and ownership

The source lease is
[allocations/battletoads-mature8-source-1116.json](allocations/battletoads-mature8-source-1116.json),
SHA256 `432d8f7e4797a646a394756ab04af58ed56ce1f9fbe7f83ba5030e25347e08dd`.
Exactly 27 bytes are owned and 22 change:

| Physical half-open range | Private address | Preimage | New bytes |
| --- | --- | --- | --- |
| 1989717..1989720 | A045 | `4c46b5` | `4c03b6` |
| 1995283..1995291 | B603 | `ffffffffffffffff` | `b51f0a90fa4c3eae` |
| 765863..765879 | Native header cookie | `a72101758605ac5665158653b677e7e1` | `a72101759affcd89019388384ff42e24` |

A045 now enters the eight-byte maturity guard at B603. LDA Enemy_State,X / ASL
copies bit 7 into carry. Immature objects branch to the existing B602 RTS with
carry clear; mature objects enter existing BtActive at AE3E. BtActive retains its
ready, owner, game, engine, pause and timer checks. Existing BtPickup retains the
independent food maturity check and +8 HP capped at 47. Food does not publish Mario
growth or force a Flower; native power remains zero in these natural routes.

B603 is authenticated declared fill after the current camera appendage ending at
B603. B548 remains live palette code. The earlier Active-only 19-byte proposal
fails immature-fallback semantics and is never mountable. The prior detached
funding, caller and rejection evidence remains in
[battletoads-natural-food-6a3-source-1116.md](battletoads-natural-food-6a3-source-1116.md).

The new cache SHA256 is
`9affcd89019388384ff42e2463134678102aa2a160e2bde28f92b2848b4897d8`;
the 487-byte native header SHA256 is
`6055a1ea4a97e20430dc8b592a7ea04ec1aee70153ea03a24696dcd44f1d6c2c`.
All bytes outside those three ranges equal 6a3, preserving Bowser, Hot118, carry,
camera, Prince, art, helpers and level data. No capacity or RAM was added.
The strict portable inverse restores the three authenticated preimages and
requires exact 6a3 without reading mutable Downloads.

## Frozen source APIs

Paths below are under `tools/audit/`. All controller strings are LF text;
their SHA256 values are not hashes of a later Windows CRLF serialization.

- `compose_battletoads_mature8_1116.py`,
  SHA256 `6db3aa513aac81d022efdc881b01bdcb93a639ccd4f99e8671fed3f8986bb27c`:
  `proposal(raw6a3) -> (raw91dc, receipt)`, `inverse(raw91dc) -> raw6a3`.
- `current_battletoads_mature8_1116.py`,
  SHA256 `9b0e39ddd6d258f5e4d3fd5b36d80292aeb09d424d01e36c4e3dd0866410c35a`:
  actual candidate CPU bundle and compiled cold Select/Start/parser.
- `replay_battletoads_mature8_food_credit_1116.py`,
  SHA256 `d74fe441747a1863a175950351bbec84a16627bc9ef07e5b350056c994ad4109`:
  `controller(raw91dc, identity, 'mushroom')`.
- `replay_battletoads_mature8_full11_1116.py`,
  SHA256 `0706e449fb1a88ebdf12f55865e2e1277795fb75c2c16827c43f9313f7212c1e`:
  `controller(raw91dc, identity)`.
- `replay_battletoads_mature8_stock_1116.py`,
  SHA256 `440391671f4e129086951fb38ac3d031a4e8d0d8bc83a22e952f1a36c2176c8e`:
  `controller(raw91dc, identity, 'oneup' | 'star')`.
  Controls `tools/playthroughs/battletoads_mature8_stock_1116.lua` SHA256
  `adb354cb1921fbe76f61f242ee7de0ff48b9a00d111ef5e6ab4b445d6bf8f7d9`.

Identity is `'rash'` or `'zitz'`, actual slot 33 with compiled Select variants
0 and 32. Old default APIs and all earlier factories remain unchanged.
Cold qualification executes the actual candidate and compares all 8192 loaded
bytes, including all 16 cookie bytes, before first BtConstruct AE11/SP217.
Loaded-image SHA256 is
`55e04fe9846ef9b6c37392a4d4989a36e6ac202a9c30adc84d020c6f0fd88253`.
The native-ready Lua compares the immutable 8160-byte prefix and all 16 cookie
bytes before that constructor, then authenticates the original worker bytes.

## Ordinary-control source results

| Scope | LF controller SHA256 | Source receipt SHA256 |
| --- | --- | --- |
| Rash M | `201360bcb558f76e1d82a1c3fb1694228e71a8ced514529b3c3dc030212480ce` | `b5f1dd4edaf91a45de20eebc5727ae86bc74da6479a76098c5b4188f4c361284` |
| Zitz M | `e97126c6fcec96d9e27d5fa436c50ee770214421c397e421f542ffe6be4b8a12` | `b73b70ae6d351c2e37d29f6c7d5b71c59d0fcf2f2f3d0382fa8b6ab9005ad868` |
| Rash full 1-1 | `9908e6083065c8b88a6b0496b57dbf9fa7417dd480196f8c7e07c76e11b858c5` | `ed1d638f7ef119468fe348da31a94909a9c11d467fa01dcf92a5d96c24a25450` |
| Zitz full 1-1 | `4c7c21129a66d41c080c7f8f42a462745e4fd1ba4c553c4f346234d7c1c63e4d` | `50a251f1b9148d0fbf146c7932cf37ee81c5b202d078a330ab64ceeb13fe3e1b` |
| Rash hidden 1-UP | `1e709d29deaa06e6295535276974f09a4746434c372fffdf44fefd729cd61a1b` | `506f5d278a4c1ca8a83f2b807102bee3a386feb4bd61b506a8bdadf05bc8e72b` |
| Zitz hidden 1-UP | `8931be37f595af69fd9d789831823e987fde63fb7ae97382dd42a42b9b73cee0` | `2ade80e20d90a65a73469ee0f81304505dddc1a41f524eecf83e945fb707eb44` |
| Rash Star | `441b8e4d8e06abe1801bd188c860a2c4510d1b751e8c8dedf92e4c5459707ceb` | `78a77777d1342c56dee8abbb4d0a8fc106751ef5f4078825b448178ddbfe6b74` |
| Zitz Star | `24ea6292ebda06618ff0e0c791facc3dba5ccd0eee118ba0b6cb99a92eb49f30` | `f5cf63559e0cc5616fe68be196d8d4d30474fe115908a45b72f04df3291fe490` |

Both M routes finish with 429 balanced Main and original-worker returns. Genuine
birth is worker 211 at 336/136; maturity is 278 at 336/119. Physical BtPickup
B44B/SP231 occurs at worker 399 (Main 398), player 395/176 versus item 407/184,
with positive 1x13 overlap. HP 43 becomes 47, actor erases, popup 6 and cue 32 are
observed. Actual DEC 897C/SP245 at worker 404 has timer 43/Y6; authenticated
83D6/SP247 return proves score 0 to 1000. Exactly 25 subsequent completed original
workers finish at actual Main return 82BE/SP252, HP47/lives2/power0.

Both hidden 1-UP routes retain that genuine M and its 25-return endpoint.
The authored hidden tile is raw60; request worker960 at1017/176 produces the
actual actor at969/1024/120, mature1034/1024/103. BtPickup at1068/Main1067 has
positive10x1 overlap, actor erase/popup11/cue32. Actual INC8987/SP245 at1073
changes lives2 to3 with cue64. Exactly25 subsequent returned workers finish1098
at Main82BE/SP252,1073/176/HP47/power0/lives3 and saved BtLife3.

Both Star routes also retain genuine M first. Request1308 at1609/176/raw87
produces actor1313/1616/136 and maturity1378/1616/119. Actual injury between
birth and maturity reduces HP47 to43; this is not an injury-free claim.
BtPickup1408/Main1407 has positive12x3 overlap, erase/popup6/cue32, native Star35
and music64. Actual DEC897C at1413 and return83D6 prove score1520 to2520.
Exactly25 subsequent completed original workers finish1438 at actual Main
82BE/SP252,1666/176/HP43/lives2/power0/Star33.

Both full routes use the unchanged qualified ordinary navigation, then actually
reach flag/castle/entrance and 1-2. They finish with 4003 balanced Main returns and
2864 balanced original-worker returns, including25 distinct living grounded
completed original workers in 1-2 at40/176, high1, engine8, HP43/lives2/power0/Star0.
Older movement-entry counters remain separate from completed original returns.
Lag without a new return preserves the endpoint count. There are no gameplay
seeds, added/moved helpers, direct area skips or input-time changes to game code.

## Caller, interrupt and lifecycle closure

Strict forward/inverse rejection receipt:
`a7e3064560fb39557c70905b643095490b5cfbd2a585f9a844d538ea408054b5`.
Twenty wrong-image, dirty-image, direction and unrelated-span cases reject.

Actual candidate public-admission matrix receipt:
`5f97d31e98722b83750e3b6a1733bcd714105c1b3be871e69196fc87d3f746be`.
552 actual public cases cover all256 object states, native guard values and
all256 input status bytes; minimum SP201. Every cookie byte corrupted separately
and retired ownership reject. All256 BtCheck owners are tested;255 foreign
owners do not enter new private code. Private RAM and above-entry stack remain
exact. X/Y/I/D/V are preserved. Carry intentionally reports admission.
A/N/Z are dead at actual PowerUpObjHandler B804's C-only return boundary; the
existing two continuations overwrite them before use. Arbitrary private direct
callers that consume A/N/Z are outside this specific proved contract.
Natural Lua execution witnesses the actual B804 client, immature C0 and mature C1,
and balanced dynamic caller returns; it does not substitute Python-only callbacks
for native hook registration.

Reached paired-interrupt receipt:
`b7e455305c33f36e6b8da044e432547e8178f9ffa28196a5d396641fcecd6ea1`.
The genuine M route reaches165 cuts at A045, B603/B605/B606/B608, B602 and the
native header comparison ADDC, including all16 header X indices. Each cut runs
actual IRQ and busy NMI:165 of each,330 complete private/header continuations,
minimum ISR SP160. The paired baseline uses actual parent ROM/header, old cache
preimages and old cookie at the same foreground cut. No ISR reads or executes
changed code/cookie. Effects on native/host/audio, all four private banks,33 SMC
operands, critical game fields, R0..R7, mapper state, registers and above-entry
stack match; busy NMI increments NmiSkipped once. There is no native RAM/audio
allowlist and no claim about forced regular-NMI nested schedules.
Trace SHA256:
`40a29e94de6042a25ad350ccccd4ecdc2b94568c083eecc97ee6480d346b3665`.

Actual candidate lifecycle receipt:
`62098e16e5617f54faad1d0007638aca9e616993033c9ab429eaf0221b675859`.
Both identities use genuine compiled cold first. Separate diagnostic components
exercise original HP-underflow death (HP0/death timerC0/engine11, admission C0),
four player/life/area constructors per identity, and retirement. Retirement
changes only cookie byte0; BtCheck/public admission reject afterwards.
Existing BtLoad in its declared safe cold window reloads the exact8192-byte cache
and full16 cookie in16400 PPU reads, then BtCheck succeeds. Those initialized
component states qualify lifecycle boundaries, not seeded gameplay clears.
The first lifecycle invocation's terminal output was lost at context transition;
process inventory confirmed it ended, followed by one compact receipt repeat.

## Retained negatives and limits

The parent native baseline29986 remains honest no-collection negative
`fc7e990532e32ff5d0da536327ab2d39a26f550347c2feabc2f1f64a9c0dcd62`.
The candidate's first credit observer negative
`f392f299bcd05eadb3e34536527059d4a394e0e3a577d6ee296994ef52e5676f`
collected M but watched an inherited entry that the actual popup continuation
does not revisit. Its factory remains frozen. The separate successor observes
the already-authenticated DEC897C and actual score return83D6 without changing
controls, pickup, timing or the +25-return requirement.

The source frontend uses actual compiled menu, Select, Start, parser, constructor
and owning bytes. Its bus does not provide real title-vblank/video/APU timing;
native frontend/cadence and all physical results remain root's responsibility.
Every source producer used the bounded wrapper, absent output roots, max1 file,
600-second ceiling and zero output files. One lifecycle output recovery was
explicitly repeated. No further broad qualification was added after these gates.
The public nightly remains6a3 at this source checkpoint.

