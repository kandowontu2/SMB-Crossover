# Steve Hermann companion runtime storage

The in-memory probe starts from the exact token candidate
`f61501cc1c173f5437ef3ae5c7b179116deb1c6bbebe118f41e68fced9497cea`,
rebuilt from installed `2d7fb6e6`. It reserves 960 executable bytes in
raw2 `$C500–$C8BF` and 64 zeroed mutable bytes at `$C900–$C93F`. The probe
image is `cb37fbc23a2c0352fed6e3c808bf0c6d9c517a25d2c391ad57fc8f369126fd0c`.

Physical CHR379 starts with the same 1 KiB as CHR367, 371 and 375. The
finite CHR ledger assigns it to Roll’s body and effects. Roll publishes
all six body pools with upper page 1. PRG79 `$B052`, `$B072` and `$B092`
now load the constant upper page, and the existing six-byte PRG121 table
at `$CC73` supplies Roll’s slot 7 low page. Only pool 3 changes its physical
page from 379 to the identical 367. Slot 0, slot 6, and every other slot 7
selection retain their original pages. The mounted ROM can use 379 for
the companion packet.

The sixth code row stages at raw3 `$B400–$B7FF`. A 58-byte bootstrap at
`$B7C0` copies and reads back the 1 KiB stage into raw2 `$C500–$C8FF`, then
clears and verifies the private state. The last 64 copied bytes are the
cold bootstrap itself and its padding. The incumbent loader then restores
the entire raw3 staging window. The descriptor grows to 23 bytes and its
PRG65 wrapper remains 161 of 162 bytes. The wrapper uses two accumulator
shifts to return the original owner bit in carry. Both headers use a
cookie bound to the payload, Roll alias, and caller edits.

Mike, Jay and Steve enter actual 1-1 through the menu and match 80 ordinary
Main updates with application RAM, OAM, VRAM and CHR latches held exact
outside the new resident bytes and headers. Mike retains zero cold PPU
reads. Jay and Steve move from 18,450 to 20,500 cold reads. A loaded probe
executes and writes the new raw2 state. The probe demonstrates storage and
authentication. The live companion behavior uses a separate source worker.

The sixth-row proof covers 65,536 owner and variant carry comparisons, 28
actual forced-blank lag NMI cuts and seven injected readback faults. None
of the faults authenticates either header. Warm calls perform zero cold
reads and keep the companion state. Roll’s 24 compiled publishers select
72 byte-identical 1 KiB images, and its actual menu and 60 opening Main
updates match OAM and all CHR latches after the one physical alias. Jay’s
full 1-1 route still earns and fires the machine gun in 1-2. Steve’s
controller still collects all three authored tokens, commits `$15`, and
settles at X1740/Y48 with six health and two lives.

## Companion extension

The optional seventh row adds 1,024 executable bytes at raw2
`$CA00–$CDFF` and 64 more state bytes at `$C940–$C97F`. Roll’s pool 2 slot
7 selection changes from CHR375 to its byte-identical canonical page 367.
The existing pool 3 alias stays in place. The seventh code row stages at
raw3 `$B800–$BBFF`. The same bootstrap copies eight consecutive staged
pages, skips the `$C900` state page in the destination, then clears and
reads back all 128 state bytes. Its 63 bytes fit the existing `$B7C0`
reservation. The 25-byte descriptor still fits the 161-byte wrapper by
reusing X=0 after pulling the descriptor to clear the existing readiness
byte. The exact native bank setter preserves X.

`mount(token_image, token_info, core, extension=payload)` links both
regions and binds the extra bytes to the authentication cookie.
The extension probe image is
`6a7ff1fc0a9f7d72f5ee9613af83e5df1d3e3922bcc7f965e34b52eeb6782fcb`.
The two loaded probes execute from their own ranges and reach their own
state. Jay and Steve take 22,550 cold PPU reads and Mike still takes zero.
All three 80-update opening comparisons pass. Roll’s 24 compiled publisher
comparisons and 60 Main/NMI OAM and CHR comparisons pass with both aliases.
All 65,536 owner and variant decisions agree, all 31 forced-blank lag NMI
cuts return safely, and each of 13 corrupt stage, resident or state reads
prevents authentication. Warm calls keep the state and read no CHR.
Jay still fires five verified machine-gun shots after completing 1-1, and
Steve still commits all three tokens to `$15` with six health and two lives.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-companion-transport-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_companion_transport_1111.py --full-routes
python -B tools/audit/run_bounded_build_v1.py --output build/steve-companion-seventh-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_companion_transport_1111.py --seventh-row --full-routes
```
