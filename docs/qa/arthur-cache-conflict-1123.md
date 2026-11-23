# Arthur startup regression on `d1a40df1`

Mesen launched the Downloads nightly and selected Arthur through the menu.
The level opened with two lives. His data loader read a pose count of `$ED`
and rejected the cache. Over eight gameplay updates the game ran fallback
movement and never entered Arthur's movement or original action routines.
The cache remained uninitialized. Native receipt
`c6826519357b117c32dcd7375a88eda00cbdd990f90dfeb43c88c85b0ee29c24`.

The linked CPU check reproduced the same rejection on `27e01af3` and
`d1a40df1`. CHR pages 881–883 contain Donkey Kong Jr. code. Arthur's loader
still reads those pages for his metadata and drawing code. The archived
Arthur data matches the exact old bytes from all three pages. Restoring
those bytes in a diagnostic copy loaded Arthur's cache and reached his
original movement routine. The repair needs a location that preserves both
characters' data. The tracker reopened Arthur's 1-1 and Fire Flower tests.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 230 -- python -B tools/audit/probe_arthur_cache_conflict_1123.py --run
```

## Repair installed in `bcc26bb5`

Arthur now reads his original metadata and drawing code from unused parts
of his own CHR pages. The decoded cache and active sprite data matched the
compatible reference across 201 pose and mode combinations. The loader
fits the same 733-byte span. Donkey Kong Jr.'s pages 881–883 retain their
verified bytes. Linked checks also matched the old interrupt behavior
across 33 busy-NMI cuts and 14 hardware IRQ edges.

| Test | Mesen result | Receipt |
| --- | --- | --- |
| Cold start | Arthur's cache loaded and his original movement ran. Mesen reproduced the same result when launched directly from Downloads. | `4b6ecc62d6c99644ce82b1a10836afe15470db5d23f880497b01208677e5c47f` |
| Full 1-1 | Cleared all four pipes and three gaps. Reached 1-2 at X40/Y176 with two lives and 25 subsequent grounded updates. | `477b049749e5133e284bff642c2b208dab5b0d960717533d45720ee4a4b3852b` |
| Fire Flower | Collected the mature Flower in normal play, then fired the original torch. | `77a5332838422a79c3819d8f68ca7176d219afea2af2af140d9c7c80f4cf23a0` |
| Mushroom | A real Goomba hit removed Arthur's armor. The Mushroom from X336 restored it at X406/Y176 and awarded 1,000 points. Arthur kept his armor and both lives for 25 more movement updates. | `fe1fcd11107560273164dab6ba39e493303791f71ca90a2920e4c803c101871a` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 460 -- python -B tools/audit/run_arthur_restored_cache_native_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 350 -- python -B tools/audit/run_arthur_restored_cache_native_1123.py --install
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 285 -- python -B tools/audit/run_arthur_mushroom_1123.py --run
```
