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

Mesen confirmed a faster empty opening. The same 48 standing updates
took 72 video frame intervals for Sonic and 73 for Super Sonic. Each form
then completed 16 walking updates in 24 intervals and moved from X40 to
X47. On `59e1a591`, both forms took 96 standing intervals and 32 walking
intervals. The measured sections used normal inputs with all enemy slots
empty. [Downloads baseline](sonic-ceiling-native-root-1116.md)

| Form | Candidate video frames, inclusive | Skipped NMIs | Mesen receipt SHA-256 |
| --- | ---: | ---: | --- |
| Sonic | 97 | 64 | `363b8fd9bd48edab6a1dcc7a555948648ead0282936aadedf7f0295a8815f164` |
| Super Sonic | 98 | 65 | `2c387cde3489ba3827ac5033469d613f8860365c9098210c8aea69f1a84b422c` |

Both Downloads baselines took 129 inclusive frames and 96 skipped NMIs.
Both forms then passed the full 1-1 replay in the private candidate.
Each defeated four Goombas with the spin, cleared the flagpole and castle,
then completed 25 grounded updates in 1-2 at X40/Y176 with two lives.
These runs wrote zero captures.

| Form | Video frames | Full-route Mesen receipt SHA-256 |
| --- | ---: | --- |
| Sonic | 5,398 | `4af2023c9dfe61466a7a58214f23073a8dba51bc8d2edb86c219b36281640e20` |
| Super Sonic | 5,417 | `211952d2e32152b83084e04a827ac8b5f25dfaa5b5faefb5edbf5f0fe7a85831` |

The next performance target is the shared dispatch and mapper work around
repeated terrain checks.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_sonic_current_empty_cadence_1122.py --run --shared-slot --auth-candidate
```
