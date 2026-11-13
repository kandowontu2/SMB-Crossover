# Metal Storm and Kirby nightly — November 12

ROM: `8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582`.
Parent: `f228e61399432c1a205b8f5ac6dad13d990515f9c2e2f5024bcd5ce443c76653`.

Metal Storm now uses genuine upward head contact to bump native blocks,
collects mature native powerups, and advances past its donor background-stream
acknowledgment using the host's existing terrain boundary. Kirby retains
inhale eligibility through the capture update, then clears it next update.
Rear contacts and hazards retain damage. Existing red-shell return behavior
is preserved.

Composition proves the two independent patches commute and reverses exactly
to the installed parent. See `metal-native-upgrades-1112.md` and
`kirby-inhale-native-1112.md` for the donor and CPU checks.

## Actual Mesen tests

| Controller-only test | Result | Receipt SHA256 |
| --- | --- | --- |
| Kirby Hard close-left natural Goomba inhale | HP6, lives2, mouth7, copy1 | `c6e7d5a7f6a52f8b6e1bcd7453108445f7a4166c345b83779478d284889ed8a6` |
| Kirby natural red-shell acquisition, enemy defeat, return catch | HP6, lives2, clean catch | `649388c86bbfabb7a073906e49ec66d79b6aeaccca257de43e4897f97823329e` |
| Metal natural mushroom and flower | Both mature items collected; upgraded shot fired; lives2 | `9312b808829fe15580626f65b1d1d5e811969af179d81a4e2aa3cd2abfc19893` |
| Metal full 1-1 to active 1-2 | 5,491 frames, both lives | `7975a676056c5968a1fd0eb9c69a144949f5933542b8ceb45f703dd79af54321` |

Script hashes, in the same order:

- `ab88ad92e07d73a1b6f9f251f573f760976bf0baea9f451b1e913ed7285cc26d`
- `2e8b0e1ad0edc039a95912e3a7b2786f9705ebcb2e6db30b09efb00f81f5bfa8`
- `ee6ae3dff7349a4e13618f169fdb007f2275063f5855da5b49b07b3d9b8be884`
- `153f0fbd5e5b18586c8331dfa5c062ac2a1ac6708475c716a35b411d132dbafe`

The Lakitu/Spiny overlap correction has directed native CPU proof, not a
controller-only Lakitu encounter. These tests do not establish all-roster
completion, all underwater behavior, or zero lag. No helper locations changed.
Only one candidate and one reusable Lua controller are retained; no captures
or videos were generated. Installation and publication status follows below.

## Installed build

Replaced `C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`
directly, without a backup. All four tests above repeated from that exact
Downloads launch path with identical receipts. Before/after patch guards
passed; installed bytes equal the candidate. Generated IPS reconstruction
equals those same bytes.

IPS SHA256: `7928a88a725be35592cc2278890d53650ea74e09464ee64c8911a67b029cba74`.
The publication command independently checks the downloaded Current asset
against the installed ROM before reporting success.
