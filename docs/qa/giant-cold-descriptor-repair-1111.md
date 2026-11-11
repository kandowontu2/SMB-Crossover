# Mega Giant Mario cold-start regression

The predecessor `e6b152e26b43449115a7ff21903ae756346052e55dbdd94d8751e8c3a0951f23`
reaches Mega Giant Mario’s first draw with zero at raw3 `$A200`. The
normal CPU loop detects BRK at that address. Both cold headers were already
published because the worker successfully copied and verified the wrong
physical CHR rows.

The earliest isolated failure is the compact common worker on the previously
passing `c10b7d87` roster. Its PRG123 `$B9DB` operand changes `$05` to `$04`
to omit the redundant metadata-high byte. The six-owner migration updates
the common registry descriptors. Giant reaches that worker directly from
PRG84 and still passes `02 01 01 D0 D6 00 D4 00`. The compact worker reads
physical CHR720 for raw3 code and CHR0 for raw2 metadata. CHR214 and CHR212
are the intended rows. The direct caller and both carrier pages are
byte-identical between the known-good roster and the current image.

| Image | Exact Mega Giant opening |
| --- | --- |
| Delivered Giant `94650fbc` | Passes 60 active updates |
| All-roster `c10b7d87` | Passes 60 active updates |
| Compact-worker-only `e8163cd0` | BRK at raw3 `$A200` |
| Sonic seventh cold `d07012de` | Same BRK |
| Prior public WWF `d76e070e` | Passes 60 active updates |
| Public Sonic movement `d2542ff3` | Same BRK |
| Jay movement `4df81758` through installed `e6b152e2` | Same BRK |

The repair changes five bytes at PRG84 `$BEFB..$BEFF`, from
`D0 D6 00 D4 00` to `D6 00 D4 00 FF`. This preserves the eight-byte
stack frame. The compact copier consumes the first seven bytes and ignores
the padding. Giant’s existing compare and publish routines share the first
four descriptor bytes with the 16-byte header. The repair gives both banks
the new complete cookie `a7000902331ad79e8d280b2d020101d6`.

The in-memory candidate
`5482f0d69d0179e0d4361b14c599199fc88ed9bfb899edb7735fe9fe682ef455`
copies and verifies physical rows 214 and 212 in 4,100 buffered PPU reads,
publishes both headers, and reaches real Giant draw. The first `$A200`
instructions again match the known-good Giant. After 60 active Main
updates Giant reaches X96/Y111 with both lives.
Mario, Mini Mario, Mike, Jay, and Steve each match their parent’s opening
result across 60 active updates. Reversing the descriptor reproduces the
exact installed image.

The controller-only Mesen candidate run verifies the same repair
through active underground 1-2. Giant passes the flagpole at
X3158/Y121 and reaches X40/Y48 in 1-2 with both lives after 3,512
physical frames. The body observer records 46 sprite parts, a
112-pixel vertical extent and the expected CHR pages 180 and 182.
Its receipt is
`6cd22a0ee702e0839ae93a752cab5b810a8964b38472a55cb9ec484c02a94d4e`.
The stdout-only replay creates no capture files.
[Physical launcher](../../tools/audit/replay_giant_current_1111.py)

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/giant-cold-bisect-1111 --max-files 1 --timeout 240 -- python -B tools/audit/bisect_giant_cold_start_1111.py --chronology
python -B tools/audit/run_bounded_build_v1.py --output build/giant-cold-repair-1111 --max-files 1 --timeout 240 -- python -B tools/audit/bisect_giant_cold_start_1111.py --repair
```

The CPU checker writes zero files. The physical replay remains separate.
