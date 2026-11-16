# Current Jay private-label consumer closure

Exact owning ROM: `00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21`. This is a detached read-only prelease review for the frozen `7700b0a4` proposal. It executes no installed or proposed CPU, mounts no code, creates no ROM and leaves the bounded output root absent.

The new checker is `tools/audit/audit_jay_private_label_consumers_00bb_1116.py`, SHA-256 `0168fa038f575833dabde4fa70b3ef84d80ed9709c6a8857d6480b2e25002745`. Bounded run `build/jay-status-consumers-1116`, max-files 1 / 600 seconds, terminal exit 0 / zero files. Receipt `23be4ccb2719b76ca17b1ecd581f2e72b471eb548fe1e751057f4ccb52abfc59`.

## Admitted bytes and readers

The census decodes the exact current Jay primary and the current Steve packet rather than treating arbitrary ROM graphics as instructions. The packet's actual NextBlock code identifies table `BB2F`; all 22 descriptors decode 10,855 bytes, SHA-256 `966b8a3cb9bded031dd3e87e0efe9fd439a3e666fa381f3d06ae98a27ef0c318`. It includes the current bank 1/2/3 scatter code and data, the exact Jay service/motion/support/extra carriers, and the cold boot/cold reader bytes.

The intentionally conservative word census includes adjacent data/instruction bytes, A/C window aliases and RTS target-minus-one forms. Every candidate is retained and classified. The control-operand census finds no direct JSR/JMP/indirect-target operand into the moved/private ranges. Relative candidates are precisely the six current local reject branches.

The old source declares `Unsupported` locally in the camera-handoff source. Its six retained guard branches are the only current target consumers. The former seventh stage predicate is already the current StageRejected call plus the local carry decision. Neither the producer's published/farcall entries nor its pointer/data tables export Unsupported or an interior Steve-pad entry. Arbitrary manual interior PCs are not an admitted private ABI.

## Exact retarget and continuation set

Only raw3 branch operand bytes `B806, B80D, B813, B819, B81E, B824` may retarget `B830 -> B82A`. The old branch opcode addresses are `B805, B80C, B812, B818, B81D, B823`.

There is one intentional current dynamic interior return: unchanged `JSR A7E6` at `B825` returns to `B828`. The proposal puts its BCC exactly there so it consumes the unchanged StageRejected carry. This is an allowed return edge, not an unknown caller. The rejected CLC/RTS moves as a unit; the accepted B832 entry remains fixed.

At the Steve boundary, current WorldHit ends `DEY; BPL NextEnemy; RTS` at `BED0..BED3`. The producer-published Steve entry remains `BED4: JMP C200`; the next live attack entry stays `BEDF`. The eight NOPs `BED7..BEDE` cannot be reached by fallthrough from either boundary. Their original producer explicitly replaced an 11-byte entry with the JMP plus eight NOPs.

Current hot native entry still publishes raw3 B303; public private movement remains B800. The source/farcall/bridge entry operands remain unchanged. The independent shared-caller review is separate: `audit_jay_status_shared_ingress_00bb_1116.py`, receipt `30805c189c872df7d14eed7e767635f9413c1e8bb03b0b0eff3403e2dff5066f`.

## All three conservative word coincidences

1. Raw1 A536 is within ArmorPoseIds: the declared byte sequence `C4,C6,...,D2,DA,DC,...,EE`. Pairing neighboring pose IDs gives DEDC, but these are individual pose selectors, not code pointers. The immediately preceding byte is the actual routine RTS.
2. Raw2 D15D straddles `D15B: STA D7B7,X` and `D15E: DEC D7CD,X`. Neighboring operand/opcode bytes form DED7; no instruction addresses that target.
3. Raw3 AB4E contains the unchanged companion call to typed **raw2 D827**. It is not a raw3 B827 alias. The widened target-minus-one filter retained its D827 word near the earlier B828 interval; it neither targets moved B830/B831 nor the retired pad. Actual current C2 D827 starts `A90420CDD5AD6AC9...`; the bank type is preserved.

## Code as data

The current cold DirectRows at BAE7 reads full source rows 222/232/234 into raw3 staging C400/C800/CC00. The actual staged CopyAlternate at A7C0 (row222+3C0) copies 11 pages plus a 224-byte tail into B400..BFDF and compares each stored byte. Both proposed private spans are included in those existing read/copy/compare domains. These readers consume the corresponding new carrier bytes; they do not publish a pointer into Unsupported or the pad. The source row selectors, block descriptors, copy extents, cold decoder and native public call operands remain unchanged.

## Retained fixture corrections and limits

The first asserted version rejected an incorrect guessed BPL displacement A1; actual WorldHit displacement is 81. A subsequent assertion counted a 22-byte copy prefix as 21. Both were checker-binding failures before any CPU or overlay; the exact observed preimages corrected them without changing the frozen plan or any game bytes.

This closes only the detached label/pad consumer obligation. It does not claim proposed-code AXYP/IRQ/SMC safety, cold/Fresh/Ready/lifecycle parity coherence or a real Flower reward. Those require a later explicit source lease. In particular, the planned publication precedes Ready while the old native publisher follows JnEnsure; that ordering remains an actual lifecycle obligation.

## Compact receipt

The receipt hash also covers all per-domain hashes and the retained source-label lines, reproducible through the checker CLI. This compact copy omits those two verbose fields only.

```json
{
  "passed": true,
  "scope": "detached prelease private-label/code-data consumer closure only",
  "parent_SHA256": "00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21",
  "frozen_plan_SHA256": "0ae3ac71e6fa8f7e0f40fe0da13ce33af9ad79dec18367f01b0ae9698bbb0295",
  "plan_receipt": "7700b0a40d77f97a4264d6e8aceed97460d795e7bd1887d3a1b4ed9cfb7b8e0c",
  "codec": {
    "rows": [
      {
        "bank": 2,
        "PC": 49408,
        "bytes": 239
      },
      {
        "bank": 2,
        "PC": 49648,
        "bytes": 16
      },
      {
        "bank": 2,
        "PC": 49664,
        "bytes": 447
      },
      {
        "bank": 2,
        "PC": 50171,
        "bytes": 5
      },
      {
        "bank": 2,
        "PC": 50176,
        "bytes": 128
      },
      {
        "bank": 2,
        "PC": 50304,
        "bytes": 32
      },
      {
        "bank": 2,
        "PC": 50336,
        "bytes": 96
      },
      {
        "bank": 1,
        "PC": 49152,
        "bytes": 1912
      },
      {
        "bank": 2,
        "PC": 50432,
        "bytes": 1024
      },
      {
        "bank": 2,
        "PC": 51456,
        "bytes": 128
      },
      {
        "bank": 2,
        "PC": 51584,
        "bytes": 128
      },
      {
        "bank": 2,
        "PC": 51712,
        "bytes": 1024
      },
      {
        "bank": 2,
        "PC": 52736,
        "bytes": 512
      },
      {
        "bank": 2,
        "PC": 53248,
        "bytes": 1024
      },
      {
        "bank": 2,
        "PC": 54272,
        "bytes": 1024
      },
      {
        "bank": 2,
        "PC": 55296,
        "bytes": 1024
      },
      {
        "bank": 2,
        "PC": 56320,
        "bytes": 992
      },
      {
        "bank": 3,
        "PC": 51968,
        "bytes": 1024
      },
      {
        "bank": 2,
        "PC": 50111,
        "bytes": 60
      },
      {
        "bank": 3,
        "PC": 54662,
        "bytes": 6
      },
      {
        "bank": 3,
        "PC": 54738,
        "bytes": 4
      },
      {
        "bank": 3,
        "PC": 57114,
        "bytes": 6
      }
    ],
    "decoded_bytes": 10855,
    "decoded_SHA256": "966b8a3cb9bded031dd3e87e0efe9fd439a3e666fa381f3d06ae98a27ef0c318",
    "cold941_SHA256": "33035891cbc5100db632ae4dc864c4f1676f7dfea65ace38769466b29e94c947",
    "table_PC": 47919,
    "table_SHA256": "dfdda1abfdea6169e890ff720197e98d5ece121995f98a7d41c68c76a0ca28f2",
    "consumed": 9780
  },
  "target_words_including_RTS_minus1": [
    {
      "domain": "scatter7",
      "bank": 1,
      "PC": 42294,
      "target": 57052,
      "around": "d0d2dadcdee0e2e4"
    },
    {
      "domain": "scatter13",
      "bank": 2,
      "PC": 45405,
      "target": 57047,
      "around": "d79db7d7decdd7d0"
    },
    {
      "domain": "scatter17",
      "bank": 3,
      "PC": 43855,
      "target": 55335,
      "around": "73c92027d8adf6c1"
    }
  ],
  "control_operand_candidates": [],
  "relative_branch_candidates": [
    {
      "domain": "motion",
      "bank": 3,
      "PC": 47109,
      "target": 47152,
      "opcode": 208,
      "around": "c901d029ad73"
    },
    {
      "domain": "motion",
      "bank": 3,
      "PC": 47116,
      "target": 47152,
      "opcode": 208,
      "around": "c903d022a50f"
    },
    {
      "domain": "motion",
      "bank": 3,
      "PC": 47122,
      "target": 47152,
      "opcode": 208,
      "around": "c908d01cad77"
    },
    {
      "domain": "motion",
      "bank": 3,
      "PC": 47128,
      "target": 47152,
      "opcode": 176,
      "around": "074ab016ad39"
    },
    {
      "domain": "motion",
      "bank": 3,
      "PC": 47133,
      "target": 47152,
      "opcode": 16,
      "around": "39011011adff"
    },
    {
      "domain": "motion",
      "bank": 3,
      "PC": 47139,
      "target": 47152,
      "opcode": 144,
      "around": "5f4a900b20e6"
    }
  ],
  "classified_words": [
    {
      "domain": "scatter7",
      "kind": "ArmorPoseIds BYTE ladder, not a pointer",
      "PC": 42294,
      "bytes": "c4c6c8caccced0d2dadcdee0e2e4e6e8eaecee",
      "source": "steve_armor_art_1112.py::POSES"
    },
    {
      "domain": "scatter13",
      "kind": "cross-instruction bytes, not an operand",
      "PC": 53597,
      "instructions": "D15B STA D7B7,X; D15E DEC D7CD,X",
      "hex": "9db7d7decdd7"
    },
    {
      "domain": "scatter17",
      "kind": "unchanged typed C2 companion call; no raw3 reject/pad target",
      "call_PC": 43854,
      "target_bank": 2,
      "target_PC": 55335,
      "target_first32": "a90420cdd5ad6ac9304c2cf6c13016ad0cc9cd70c9ad0dc9ed71c99004c91090",
      "note": "D827 itself is also outside moved B830/B831; widened RTS-minus-one word filter retained it."
    }
  ],
  "allowed_retargets": [
    {
      "bank": 3,
      "operand": 47110,
      "old": 47152,
      "new": 47146
    },
    {
      "bank": 3,
      "operand": 47117,
      "old": 47152,
      "new": 47146
    },
    {
      "bank": 3,
      "operand": 47123,
      "old": 47152,
      "new": 47146
    },
    {
      "bank": 3,
      "operand": 47129,
      "old": 47152,
      "new": 47146
    },
    {
      "bank": 3,
      "operand": 47134,
      "old": 47152,
      "new": 47146
    },
    {
      "bank": 3,
      "operand": 47140,
      "old": 47152,
      "new": 47146
    }
  ],
  "allowed_dynamic_return": {
    "bank": 3,
    "call_PC": 47141,
    "callee": 42982,
    "return_PC": 47144,
    "new_return_instruction": "BCC consumes original StageRejected carry"
  },
  "preserved_public_entries": {
    "Hot94_private_target": "raw3:B303",
    "PrivateUpdate": "raw3:B800",
    "Supported": "raw3:B832",
    "SteveCombat": "raw3:BED4 JMP raw2:C200",
    "SteveAttackMain": "raw3:BEDF"
  },
  "code_as_data_readers": {
    "DirectRows_PC": 47847,
    "DirectRows_hex": "00c4030a0000000400c8030b0000000400cc030c0000000400d4020e0000000400d0030f4000bf03",
    "SourceRows": "222/232/234 -> raw3 C400/C800/CC00",
    "transfer": "staged A7C0 (row222+3C0) -> B400..BFDF, 11 pages plus224 tail; exact compare after each store",
    "transfer64_SHA256": "71db90e86f33ef16986a93beeda89963654e2df422147dfe632ad5e2b43433af",
    "original_data_semantics": "copy/compare, not a pointer into Unsupported or padding"
  },
  "pointer_tables": "Current scatter/direct descriptors, original probe words, armor BYTE pose IDs and code-label publishers do not export Unsupported/pad. No generic private-entry contract admits arbitrary interior PCs.",
  "no_CPU_or_proposed_overlay": true,
  "outputs": 0,
  "remaining": "No proposed-code ABI, IRQ, lifecycle, cold or natural reward claim. Public foreign-Y closure is independent30805c18.",
  "receipt_SHA256": "23be4ccb2719b76ca17b1ecd581f2e72b471eb548fe1e751057f4ccb52abfc59"
}
```

