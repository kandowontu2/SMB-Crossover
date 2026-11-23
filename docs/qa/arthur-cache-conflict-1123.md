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
