# Steve throw bridge storage

Source and byte inspection on installed `80e6aa3e32574f38b23fa6da6ab3c94bbe7b5ae11b29339b32b11a624fe6f1ed` and the carrier contract for fixture `cc2d58533b243b91f80b63e48c854ffd34522eae22965b2286c7136d76ab9918`. The scatter now has cold, warm-gameplay and foreign-owner CPU qualification below.

## Source and destination

Physical CHR307 offsets `$300–$3FF` are the explicit 256-byte pad after the eight CHR307 recovery cells. The pad SHA-256 is `5341e6b2646979a70e57653007a1f310169421ec9bdd9f1a5648f75ade005af1`. Recovery poses `$AE/$B2` use slot-zero tile IDs `$20–$2E`, so their 8×16 cells finish at offset `$2FF`. The exact current Roll mapping already aliases the blank CHR307 request to CHR304. The pose loader reads and verifies all 1,024 bytes into raw2 `$CE00–D1FF`. It keeps `$CE00–CFFF` for the pose worker, then the Laserbot copy replaces `$D000–D3FF`. The interval between the two transfers can supply the new code.

| Interval | Current compiled ownership |
| --- | --- |
| Raw2 `$C4A0–C4FF` | 96-byte candidate. CHR371's fifth copier at `$B134–B142` writes and verifies `$C400–C47E` (127 bytes), then `$B146–B154` writes and verifies `$C480–C496` (23 bytes). The existing reservation ends at `$C49F`. The next resident copy starts at `$C500`. |
| Raw2 `$C980–C9FF` | 128-byte candidate. CHR379's bootstrap writes `$C500–C8FF`, explicitly skips the `$C900` page at `$B7E4`, then writes `$CA00–CDFF`. Its `$B7E8–B7F4` state loop clears and rereads exactly `$C900–C97F`. The throw state and pose scratch are in that lower half. |
| Shared decoder | PRG65 `$A70E` holds descriptor `0B 07 01 DA 00 DE 00 E8 00 EA 00 73 01 7B 01 77 01 4B 01 4C 01 DC 00 A7 00`. The common worker zeros one raw2 page at `$C000`, loads seven rows into raw3 `$A000–BBFF`, and puts its final four rows into raw2 `$D000–DFFF`. The `$A7C0` transfer uses raw3 `$A400` and `$B400`, then jumps to the `$D000` decoder. The decoder's explicit C2 scratch is `$C038–C03C`; decoded code goes to raw3 `$A000–A8BF`. The warm scene shim clears `$C033`. |

The two proposed ranges have no initializer in this family today. The current loader assigns destinations only to the neighboring intervals above. The Steve/Jay source state layouts end below `$C980`; the dynamic pose records are bounded to their two 32-byte buffers at `$C8C0/$C8E0`.

An every-byte operand scan of the installed family resident streams, including the independent data decode of the CHR331/332 packet to raw3 `$A000–A8BF`, found no actual absolute access into either range. The real indexed operands near `$C980` are the companion coordinate copies at `$CCA7–CCB0` and `$D2E3–D2E9` with X at 1 or 0, the pose draw copy at `$CFD3` with X at 3 through 0, and lift animation at `$D47B` and `$D5CF–D615` with indices no larger than 5. They reach at most `$C959`. The other candidates are data bytes or instruction-operand overlaps. The earlier Jay private-motion source audit also rejects all indirect indexed opcodes in its linked motion block. Bank-aware live coverage is still needed for indirect native readers and foreign owner transitions.

After the existing CHR307 and CHR306 readbacks, use a 36-byte helper at raw2 `$DA4D` to copy `$D100–D17F` to `$C980–C9FF` and `$D180–D1DF` to `$C4A0–C4FF`. Each destination byte gets a readback against its source. The existing Laserbot load may then overwrite `$D100–D1FF`. The helper runs under the forced-blank cold frame before either header commits. Bind both new payload pieces into the full cookie. The `JSR` and failure branch increase the 127-byte boot to 132 bytes. Moving angles to `$CD88` leaves 120 bytes through `$CDFF`, enough for 64 angle bytes and the 46 bytes of recovery records.

## Existing backed padding

| Resident interval | Bytes | Source and boundary |
| --- | ---: | --- |
| `$DE92–DEBF` | 46 | CHR167. The movement linker pads the host bridge to its fixed motion origin `$DEC0`. |
| `$DFDE–DFDF` | 2 | CHR167. Stop before `$DFE0`, where the common owner publishes the header. |
| `$C8A5–C8BF` | 27 | CHR379. The companion payload is padded to `$C8C0`, the start of the copied bootstrap and the later pose buffer. |
| `$D777–D77F` | 9 | CHR338. Late lift payload padding immediately before Laserbot state at `$D780`. |
| `$CFF3–CFFF` | 13 | CHR307. Tail of the current 499-byte pose payload. |
| `$DA71–DA7F` | 15 | CHR306 after the proposed 36-byte helper, with the 589-byte live throw core ending before `$DA4D`. Stop before the exact punch suffix at `$DA80`. |
| `$CDF6–CDFF` | 10 | CHR375 after the proposed relocated angles and recovery records. |

The exact installed ROM contains `$EA` in the first five spans. Their ownership comes from the linker boundaries and verified transfers. With the 224-byte scatter, the listed ranges provide 346 bytes across multiple entry points after reserving the copier and recovery records. Verify linked symbols and no fallthrough into each tail before binding it. The 256-byte CHR307 tail has 32 more source bytes whose resident destination has not been assigned.

PRG96 still contains Mike's actual movement and fallback, and the adjacent banked spans include WWF runtime. PRG97 `$C409` begins Rogue Dawn's audio driver. Its installed apparent zero runs in `$C4AE–C4EF`, `$C4F5–C50F` and later lie in that resident bank. The same CPU addresses in raw2 are different storage. No common PRG96/97 retirement is established by this inspection.

## Qualification

The root carrier probe `12d6fdebde6901e175ce1c987899e5a9cee39704e2b7e809b87be6226276cbeb` copied all 224 bytes with the 132-byte boot. It passed 76 NMI cuts, nine readback faults, 24 Roll publisher cases, 80 paired opening updates for each of Mike, Jay and Steve, and the loaded throw launch check. It produced no files.

The implemented `steve_shatterhand_throw_bridge_cold_1111.s` copies and reads
back both regions before either full cookie commits. `--bridge-space` retains
the same fixture hash above. It now also passes an actual same-bus Steve →
Prince (raw38) → Steve transition. Prince's real cold loader overwrites all224
destination bytes, commits its own headers, and matches a fresh canonical
Prince load. Returning through Steve's actual loader restores the exact224
bytes and full headers. Both transitions invalidate the two header markers
before committing replacements. No manual cookie edits or retirement stubs
were used. Prince consumed31,276 PPU reads; returning Steve consumed30,750.

`--live-pose --bridge-space --warm-routes` additionally passed6,289 authenticated
game updates with zero bank-tagged reads or writes into either destination,
and unchanged payload canaries. Steve earned Alpha, displayed all required
lift poses and restored ordinary CHR220 after release. Jay completed the native
flagpole/castle sequence, entered1-2, earned the machine gun and fired five
DMA-verified shots with both lives. These are CPU-model route checks, not new
Mesen runs or a proof for every possible character/state. The separate80-update
Mike/Jay/Steve opening comparisons and24 Roll publisher comparisons also pass.

All these checks generated zero files and left the installed nightly unchanged.
The allocated payload is still patterned canary data; the actual throw control,
contact and retirement bridge remains to be linked and qualified there.
