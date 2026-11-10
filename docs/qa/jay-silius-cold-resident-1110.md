# Jay McCray resident cold loader

The fully placed cold and hot link is verified on exact
`a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1`.
The in-memory result is
`6824292a7d4a56ea493b0b4659fbfdf82c46b2be35e1e0f1982fbac606cbf7c3`.
All loader, scene and movement entry points use physical cartridge addresses.

## Released resident bytes

The old Proto Man table extent is physical PRG65 C-view `$C696..<$C738`.
The five live 27-byte tables move together to C94 `$D1F8..<$D27F` and the
unread 27-byte `ProtoPoseChrHi` table is retired. The original pose records
and their pointer values stay byte-identical. The five old indexed readers
are in PRG66 at `$A138`, `$A145`, `$A14B`, `$A151` and `$A157`.
`ProtoSetPose` retains its 53-byte extent at `$A12E..<$A163`. It switches to
C94 to read the tables and restores C65 before the renderer can read the
pose records. Both transitions use the existing fixed `$80C2` mapper setter.

The transfer fits after compacting the adjacent Sunny art. Sunny's 70 pose
records use 838 distinct bytes after exact aliases, down from 910 bytes.
Two code leaves reproduce the relocated high pointer tables by frame range.
The retained low pointers, CHR table and semantic indices are retargeted at
their seven original PRG81 readers. The C94 layout is as follows.

| C-window range | Bytes | Role |
|---|---:|---|
| `$CE00..<$D146` | 838 | Sunny's exact pose records with aliases |
| `$D146..<$D1D1` | 139 | Sunny low pointers, CHR and semantic tables |
| `$D1D1..<$D1F8` | 39 | Sunny high pointer leaves |
| `$D1F8..<$D27F` | 135 | Proto Man pointer and CHR tables |
| `$D27F..<$D2FB` | 124 | Jay hot gateway, executed at A-view `$B27F` |
| `$D2FB..<$D300` | 5 | Remaining bytes before Rogue Dawn art |

Before/after tests compare all 54 legal Proto Man pose calls and 1,024
Sunny calls across both forms, both facings and all input byte values. The
Sunny output pointers address the same record bytes at their new positions.
All 100 menu entries match. Actual 1-1 openings for Proto Man, Sunny, Rogue
Dawn, Little Mac, Doc Louis and Mike Tyson retain the same OAM, VRAM and CHR
state. Mike and Steve each match 60 actual Main updates.

## Cold path

Jay uses 147 of the 162 bytes released at A65 `$A696..<$A738`, including its
seven-byte descriptor and 16-byte cookie. The two shared redirects are
PRG65 `$AC2C` and `$AF00`. The original common copy call at `$AE85` and the
raw37–43 selector and retirement range remain in service.

The scene wrapper checks raw16 and `$730B & $60 == $20`, then stages
`02 00 01 4B 01 4C 01` on its live stack before entering the actual common
cold manager. The selector verifies the actual scene return address before
pointing the worker at the descriptor. The worker reads the stack through
its own A123 mapping. The cookie remains in A65 for the common header
checks and commit. Direct public cold entry without that scene frame
rejects Jay. On a warm scene the wrapper clears the private ready byte after
authentication, so the next active update reconstructs the actor at the
new spawn.

The unchanged typed copy path reads and verifies CHR331/332 through the
native PPU. The native bootstrap calls C2 `$D25E`, where a three-byte jump
enters the decoder at `$D000`. The decoder skips the jump's three bytes when
reading the packed stream. The existing finalizer returns the decoded
success carry to the common commit. The 2,045-byte stream contains a
257-byte decoder, 1,785 packed bytes, and the bootstrap jump. The decoded
2,240-byte movement image remains byte-exact. Both headers commit only after
the complete decode and readback succeed.

The cold path takes 4,100 PPU reads and a verified warm repeat takes zero.
Thirty-two header faults reload, three copy/decode faults leave both headers
invalid, and actual cold transitions pass in both directions with all seven
existing owners. Reached resident, worker and decoder instructions pass
327 real forced-blank NMIs and 94 real IRQs. Only PRG65, 66, 81, 94 and 96
and CHR331/332 change. CHR333/334 and the DK and Sonic payloads stay exact.

## Gameplay boundary

Actual title, scene and Main produce 86 private Jay updates with the
original held jump of 52.5 px and a floor landing. Jay ends at native
X78/Y176 with two lives. The hot path passes 186 actual NMIs and 186 actual
IRQs, with two mapper-shadow split cuts. Each of the 32 hot header-byte
faults follows the original fallback without entering private code.

The controller fixture releases B and calls the genuine donor weapon
input in a separate CPU model. A physical cartridge still needs the host
weapon and scripted-event bindings, camera progression and full-stage
qualification. The cold and hot residency proof creates no ROM file, Mesen
run, capture, or generated build file.

The cookie is `A710200370145A2FEC3087391B104C88`. The staged two-page SHA-256
is `d994dc1545efb8f930ff924992bc5492f618c836f1af5acab2e243d6b9d62655`.
The decoded SHA-256 is
`ff5aa4d75cfa4e8d13293fb6a55aa14c952f95db5268c33d460bf4111985307b`.

Run `python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-cold-resident-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_cold_resident_1110.py`.
If Downloads has advanced, the checker reconstructs exact a20d in memory
using the frozen DK Jr. second-pipe recipe.

The separate byte audit on exact Downloads
`b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65`
reproduces the DK Jr. four-pipe update from a20d and verifies zero overlap
between its 316 changed bytes and Jay's 3,307. Applying the Jay changes in
memory to b031 produces
`fedcc6eef6d7b6634842872634feee5e3da57517b0c43fd86c07439ac9466454`.
The execution and reader tests above bind a20d.

- Resident source SHA-256 `33c820005682ef279fba4992292c6942373a879bdc38bb5ca79a0614c8f3a8ab`.
- Bounded checker SHA-256 `92184ff045cbee83a7d7fc73946db042176e334977d26ff5b132d3cdeca2c341`.
