# Prince of Persia clears World 1-1

Highlight Excitebike and press Select once for Prince. The controller-only
Mesen run starts at the title and clears all six pipes, all three gaps, the
final stairs and the native flagpole. It uses the original jump and climb,
with no shortcut, cheat or helper platform. On the flagpole approach, release
Right and press A from a settled stance to use the original standing jump.

The donor engine treated the flag shaft as a wall during the jump. The
corrected hand probe defers the shaft to the native flagpole handler during
original jump actions 3 and 4. The native upper side can now register a real
overlap with the shaft. The code uses the column from the actual tile query
and measures the pole center against Prince's 16-pixel body. The original
flagpole routine handles the grab, score and level exit.

Mesen recorded the native engine-4 write at X3167/Y176 in frame 14,747 and
the castle sequence in frame 14,749. Prince entered active underground 1-2
at X40/Y48 in frame 16,598 with both lives. The run ended with 2 HP before
the castle and the 1-2 entrance reset health to 5. The installed Downloads
ROM repeated the same receipt. Jay's installed regression also cleared 1-1
and fired five rounds with his earned machine gun in 1-2. The automatic
patch guard passed before and after replacement, with zero backups.

The exact CPU check passed 1,280 foreign collision cases, 864 Prince
overlap cases, and 389 unchanged pipe and stair updates. Empty upper side
probes retain their three-cycle branch. Nonempty upper contacts add 84–102
cycles. The Prince cold streams remain 6,400, 5,939 and 1,233 packed bytes.
The inverse recipe restores exact stair-only ROM `41bd1143`.

Prince's earned ability and wider gameplay audit remain open.

| Exact artifact | SHA-256 |
| --- | --- |
| MMC5 ROM | `2d7fb6e63ea55f2d0eb9ef3af4efc467233da013dc70e295952a4adcdd14ecdb` |
| IPS | `566a1ab2789c7a15c75485d1198c0f6742f23385b72000c4ebf65bde93910ce0` |
| Mesen 1-1 clear | `0dbfd29e1ee38afffea553c077c06545325930bfe9cbdbd0272eda708d0ab0c2` |
| Assembled Mesen controller | `fd0795e9d7c1e46a996bab6f87b75fbac2539af671c68ad7448f0b87b1d80458` |
| Flagpole observer | `80b131752f2d5a47b81d003f5bff28f9da979c7491bffd346b8251c8fbef4358` |
| Installed Jay regression | `a50ee4d02997c7c447273953c2eb82f7b2145512e38de0c6abcddf93d6bbe172` |

[CPU verifier](../../tools/audit/check_prince_native_flag_1111.py) ·
[Mesen replay](../../tools/audit/replay_prince_native_flag_1111.py) ·
[Delivery recipe](../../tools/audit/deliver_prince_native_flag_1111.py)
