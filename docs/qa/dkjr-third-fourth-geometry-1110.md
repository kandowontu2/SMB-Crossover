# DK Jr. tall pipes and first gap, November 10

These local CPU tests use DK Jr. raw40 and the exact authored 1-1 parser.
The room setup translates the original anchor to each approach and uses
normal NMI, GameLoop, source controls, collision, and stock actor code from
there. The taller-pipe fixtures instantiate existing native ID `$25` with
its genuine constructor, then set the same bounding-box policy as the
released second-pipe helper. These are local placement fixtures.

The current test input is installed SHA-256
`a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1`.
The first-gap control also ran against the prior exact
`9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97`.

## Authored terrain and original gap input

The parsed pipe caps start at world X448/Y176, X608/Y160, X736/Y144,
and X912/Y144. Each cap is 32 pixels wide. The first gap is
X1104 through X1135. At Y208 the columns X1088, X1104, X1120 and X1136
are `$54`, `$00`, `$00`, `$54`.

The supported setup is X1094/Y176. Right alone enters original fall state 4
and then defeat state 5 at X1105/Y202, update 34. Right+A for eight updates
then Right starts original state 3 at update 2 and reaches apex Y161. The
source floor returns at X1121/Y176 on update 46, native grounded state 0 at
X1124 on update 51, and far bank X1136/Y176 on update 70 with two lives.
Neither test calls the stock carry hook. This supplies an unassisted first
gap controller step for the later continuous route.

## Stock vertical placement trials

The positive third-pipe fixture places 32px-wide girders at world left
X688 and X752, with respective centers X704 and X768. Both start at top
Y192 and use native oscillator center Y169. DK Jr. takes off from
X717/Y111 with the first girder at Y143, stands on the cap at X740/Y112,
and reaches far ground at X799/Y176 on update 909 with two lives. The
native carry hook records 43 ascent and one descent contacts. The same
X placement with oscillator center161 reaches the cap, loses descent
support and enters defeat at X769/Y166. This establishes a difference
between actual native placement parameters while preserving actor motion.

The positive fourth-pipe fixture places the same stock girders at world
left X880 and X944, with centers X896 and X960. Both start at top Y192 and
use native oscillator center Y161. DK Jr. takes off at X909/Y112 with the
first girder at Y144, stands on the cap at X916/Y112, acquires the descent
girder at X942/Y106, and reaches far ground at X980/Y176 on update 1018
with two lives. The native carry hook records 33 ascent and 34 descent
contacts. The shifted lefts X864/X928 with center161 reach the roof but
lose descent support and enter defeat at X945/Y166.

| DK Jr. stage 1-1 fixture | Left X | Center X | Initial top Y | Oscillator center Y | Camera-left admission range |
|---|---:|---:|---:|---:|---|
| Third pipe ascent | 688 | 704 | 192 | 169 | 401–432 |
| Third pipe descent | 752 | 768 | 192 | 169 | 465–496 |
| Fourth pipe ascent | 880 | 896 | 192 | 161 | 593–624 |
| Fourth pipe descent | 944 | 960 | 192 | 161 | 657–688 |

The ranges retain the existing native 256–287-pixel spawn margin.
Together with the installed first and second pairs, these four X values
pack as 16px columns `26,30,35,39,43,47,55,59`. Oscillator centers by pipe
are `128,177,169,161`. Production admission and continuous route timing
remain separate checks.

## Owner-private cold space

The exact 119-byte DK cold worker at RAM2 `$D25E` through `$D2D4` is
stored in physical CHR960. Its preimage SHA-256 is
`cf8d2da03ec64fc89b860499805be3e706fe7c85f0ead368250c164c21affa7a`.
The eight native code-carrier pages all have high byte `$03`. The packed
worker keeps eight low bytes, sets the common high byte explicitly, and
sets the copy count once inside the shared row mapper. The last successful
compare supplies the existing carry result. It assembles to 105 bytes
and frees the half-open span `$D2C7..$D2D5`, immediately before the occupied
world helper. The live atlas and owner headers lie outside this grant.
The packed machine-code SHA-256 is
`365e177cbcb0bc76ea594931a523719c501829daa23b764322c687563e973132`.

Old and packed leaves execute 16,400 actual `$2007` reads and 80 identical
mapper/address writes on the MMC5 CPU bus. They return identical AXYP/SP,
mapper tags, and complete RAM3 output. Flipping one readback bit at reads
1,027, 2,050, and 16,400 separately preserves the original fail-closed
results. An integrated allocator still needs real owner cold, header,
retirement, lifecycle and route qualification.

The v2 leaf initializes Y to zero at entry, relies on both loops returning
Y to zero, and saves the copy destination high byte on the stack before
copying. It restores that byte before readback. This compiles to 102 bytes
and extends the free span to `$D2C4..$D2D5`, 17 contiguous bytes. Its
machine-code SHA-256 is
`c47ddf12e6df4f8abf189ab9c78c58ffdcd5f80c3ade8e610f51d977f45889d7`.
The same successful mapper/read stream and three faults pass. The saved
byte is popped before the verifier, so all injected errors return SP224.

Separately, 36 native ID `$25` constructor vectors on a20d cover six slots,
both native size modes, and incoming `ObjectOffset` values 0, 5, and 255.
The constructor preserves X, returns carry clear, and accesses no
`ObjectOffset` bytes. This permits omitting a redundant pre-call slot
store or post-call X reload in the four-pipe worker. Native box 6 in the
ordinary mode still needs the existing override to box 5.

`dkjr_four_pipe_sizing_1110.s` measures the independent per-camera-page
table proposal. Its PIPE section is 120 bytes ending at `$D203`, three
bytes past the existing runtime grant. Its candidate table layout uses
the prior 14-byte cold reclaim, plus the established BD3C, D2FC and D7FC
spans. It is a sizing source for the production integrator.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-third-fourth-space-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_gap_cap_probe_1110.py
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-third-fourth-space-1110 --resume --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_cold_space_1110.py
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-third-fourth-space-1110 --resume --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_cold_space_1110_v2.py
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-third-fourth-space-1110 --resume --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_tall_pipe_probe_1110.py
```

These recipes emit stdout and retain zero build files.
