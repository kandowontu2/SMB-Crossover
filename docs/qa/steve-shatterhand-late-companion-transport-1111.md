# Steve's late companion carrier

The proof starts from installed `c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2` and reconstructs the existing Steve companion image `484d159fee570e6646252a24b3d01d6a9ddd17c70af2172d536f510dc34d0eb9` in memory.

| Storage | Purpose |
| --- | --- |
| Raw2 `$CD00–CDFF` | Late cold loader in the existing CHR375 row |
| Raw2 `$D000–D77F` | 1,920 bytes of companion and lift code |
| Raw2 `$D780–D7FF` | 128 bytes of state, zeroed on cold load |
| Physical CHR336 and 338 | Immutable payload pages for those last 2 KiB |

The existing first row's temporary jump at raw3 `$A033` enters the late loader. The loader runs the original `$A7C0` transfer and decoder before reusing the spent raw2 `$D000–D7FF` stage. It reads back both new pages under the common forced-blank gate. The original outer owner commits both cookies after the loader returns with carry set. An upstream failure or a new readback failure leaves both headers invalid. The existing common PPU restoration still owns the visible mapper state.

The common descriptor retains seven code rows. An eighth row would stage at raw3 `$BC00`, where the compiled Jay and Steve gameplay paths read live code. The entire final raw3 resident, through `$BFDF`, compares byte for byte with the parent.

On the exact parent, Steve's controller route through three Alpha tokens, companion birth, and 51 projectile updates made 197,873 reads in raw3 `$BC00–BFDF`. Jay's flagpole, castle, and earned 1-2 machinegun route made 693,870 reads there. Both routes made zero raw2 `$D000–D7FF` reads or writes after authentication. The `--parent-footprint` mode reruns those traces separately from fixture testing.

Roll's pool 5 now requests blank CHR304 and 306 in slots 0 and 6, preserving slot 7 at CHR339 and the unrelated CHR337. The old and new graphics pages are all zero. The proof checks the compiled publisher with six pools and four incoming status values, 72 requested 1 KiB page pairs, and 60 controller-led Roll opening frames with matching OAM and mapped graphics bytes.

The CPU proof compares 80 opening updates each for Mike, Jay, and Steve. The fixture adds 4,100 PPU reads on a cold Jay or Steve load. Mike still makes zero cold reads. Two probes run from authenticated `$D000` and `$D400`. A warm call makes zero additional reads and preserves state. The 109-byte loader passed six readback faults, one upstream raw3 `$BC00` fault, and 50 lag-NMI instruction cuts. The fixture hashes to `f74fd31e168abab9d9cb81eb55523da90a8cc1897a60c7f43611ddb54be3aafc`.

The fixture also completed the same Steve and Jay controller routes. Steve retained all 51 projectile updates, and Jay earned the machinegun after the native flagpole and castle sequence and produced five matched DMA cells. Both raw3 read counts were identical to the parent, with zero new authenticated accesses to the retired decoder region during those existing routes.

Run the zero-output check with the exact installed parent and existing source bindings.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-late-companion-transport-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_late_companion_transport_1111.py --gameplay
```

The transport uses an executable fixture. The actual lift and Laserbot workers and their native gameplay qualification are separate source and emulator work.
