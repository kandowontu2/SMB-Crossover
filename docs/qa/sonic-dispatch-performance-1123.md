# Sonic and Super Sonic dispatch performance

An enemy-free standing update on the Downloads `59e1a591` nightly runs
14 complete code header checks. The private `2ac7c084` revision keeps the
first full check and reuses it for the other 13 calls in that update.
The caller still checks both live bank headers, and checks the dispatch
range before entering the shortcut. A dedicated Sonic check limits reuse
to ordinary gameplay after the active character, scene and frame match.

The linked CPU test used both characters' real menu selections and cold
starts, then compared 55 gameplay updates for each form. Standing cost
fell from 49,227 to 44,781 cycles per update, and walking cost fell from
49,313 to 44,867. The test compared the gameplay state and bank mappings
for both forms. Both standard 1-1 clears and their pickup results still
count on the installed build.

The source tests exercised 1,666 owner and service-entry cases, 94 invalid
address ranges, 768 upper-collision input cases and 776 reached interrupt
test points. A separate check covered 112 reached interrupt points during
rejected or fallback calls. All used the original interrupt handlers and
verified the respective return. Source receipts
`a203f5fcd4d75042c0daecea5fd657b75d20f797162862b84d8612dae8c2015c`
and `83f3b339369aa85071139ead4b29939f143b0d4c12aa696709b96af5f0772908`.

The source comparison does not determine the physical frame rate. Mesen
cadence and full-stage verification are still pending for this candidate.
The next performance target is the remaining shared dispatch and mapper
work around repeated terrain checks.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_sonic_current_empty_cadence_1122.py --run --shared-slot --auth-candidate
```
