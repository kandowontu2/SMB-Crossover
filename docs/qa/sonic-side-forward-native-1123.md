# Sonic side collision dispatch timing

The private MMC5 candidate `cba16344` uses the existing forwarder to call
the Sonic terrain service. It leaves the service and its header checks in
place. The change occupies 35 bytes in PRG 33 on top of Downloads
`ffd70810`.

The linked CPU test found four calls per normal update, with 446 cycles
saved on each call. Sonic and Super Sonic matched gameplay and hardware
state in their cold, standing, walking, jumping, crouching, charging and
release checks. The test covered actual terrain queries, rejected headers
and the existing fallback, and ran 100 IRQ and 100 busy NMI continuations.
Donkey Kong Jr. used four additional cycles per game update. Mini Mario's
linked timings matched the parent.

Source receipt `dec51c968e486d9dfe59e6b199629f76c26a21f3c7871733bc0747e33d8b4997`.

| Character and build | Video frames for 64 game updates | Frames with no game update | Skipped NMIs | Mesen receipt SHA-256 |
| --- | ---: | ---: | ---: | --- |
| Sonic on Downloads | 98 | 34 | 65 | `7ced5967df4c93edb8448cebe6f0290edebcd013a839bdd77f34faa35fb6e9ff` |
| Sonic on private candidate | 97 | 33 | 64 | `b15e7e95124576dec850d339a761230e08cd0ac3d7a4ffddacce6d9ffe116d2b` |
| Super Sonic on Downloads | 98 | 34 | 65 | `7cc4d653de2e1c9e21565ff8b2557fbe30c4d82e0d0864875e7d22d620f53521` |
| Super Sonic on private candidate | 97 | 33 | 64 | `559cf550cb9a1aa885385867cb449cabea48548d0446d06549b73823574fef76` |

Each run used ordinary controls from character select and measured 48
standing and 16 walking updates without enemies. Both characters reached
X47 at the end of the measured walking phase with two lives. The candidate
saved one video frame per sample and substantial standing and walking lag
remains. The Mesen runs saved zero captures. Downloads remains `ffd70810`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/sonic-cost-1123 --timeout 600 --max-files 1 -- python -B tools/audit/check_sonic_side_forward_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 420 -- python -B tools/audit/run_sonic_side_forward_native_1123.py
```
