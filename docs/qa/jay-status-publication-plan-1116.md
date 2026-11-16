# Detached Jay status publication on current 00bb

This is a measured proposal, not a source-code lease or an executed candidate. The current native witness shows a missing existing status publication: collecting the first real heart toggles `JnStars` from `00` to `80`, while `PlayerStatus` stays zero because the successful private update bypasses the old native movement publisher. The next real block therefore still selects a heart.

The owning parent is exact `00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21`. All 34 delivered Metal bytes are authenticated and disjoint. No proposed instruction was executed, no ROM was overlaid or serialized, and no new RAM/carrier is proposed. This report does not grant use of the Steve-owned span.

## Measured fit

- Plan: `tools/audit/plan_jay_status_publication_00bb_1116.py`, SHA-256 `0ae3ac71e6fa8f7e0f40fe0da13ce33af9ad79dec18367f01b0ae9698bbb0295`.
- Bounded invocation: `build/jay-status-plan-1116`, max-files 1, timeout 600 seconds; terminal exit 0, no output files and no active handle.
- Receipt: `7700b0a40d77f97a4264d6e8aceed97460d795e7bd1887d3a1b4ed9cfb7b8e0c`.
- Conditional scope: 106 owned bytes, 63 changed bytes; streamed conditional digest `df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe`. This digest describes the detached bytes and is not an executed or qualified ROM.
- The 50-byte private header/reject block is at file 1286160, R3 `B800..B831`. Its six private reject branches move their target from `B830` to `B82A`; the accepted `B832` anchor and following Ready/epoch/constructor code remain fixed.
- The eight-byte leaf would occupy file 1288935, R3 `BED7..BEDE`. Its current eight NOPs come from an explicit producer replacement of the 11-byte Steve token entry by `JMP C200` plus eight NOPs. They are source-declared Steve-owned capacity, not globally free padding.
- All three existing 16-byte live cookie views are included: file 534328 (PRG65 `A728`), file 774911 (PRG94 `B2EF`), and file 1429421 (CHR371+925, uncompressed `StevePacketCold::ExpectedCookie`). CHR371+64 contains a historical prior-cookie shadow and remains unchanged.

## Carry and status contract

The old native PRG96 `A2DF..A2E8` publisher is exactly `AD3E5F0AA9002A8D5B07`: read `JnStars=$5F3E`, shift bit 7 into `PlayerStatus=$075B`. The proposed load plus leaf reproduces that formula. It does not award a Jay weapon, ammunition or an invented ability.

The 13-byte reorder at `B825..B831` is `20E6A790021860AD3E5F20D7BE`. It consumes the original `StageRejected` carry before doing publication. A rejected stage reaches the same CLC/RTS behavior, with the same A, X, Y, N, Z and V. An accepted stage reaches the mirror with carry zero; the mirror returns carry zero and preserves X, Y and V. The unchanged following LDA Ready overwrites A/N/Z. The new JSR stack lifetime still requires actual IRQ/busy-NMI and caller/SMC qualification after a lease.

Inserting a mirror into the old six NOPs before the existing BCC is invalid: the original formula changes carry and could turn a rejected stage into an accepted update. That idea is explicitly excluded.

## Unclosed shared ingress

There is no Jay-only gate in the proposed 14 publication bytes. The actual current PRG94 hot admission accepts Jay variant 20 and Steve variant 40. The retained older `jay_silius_stock_draw_dispatch_1111.s` Jay-only comment/logic is not the current byte-level admission contract.

Actual current routing evidence is authenticated by the descriptor:

- R3 `B303` starts `JMP B3AA`.
- `B3AA` executes `PHP; BIT $730B; BVS StevePrivate`, then either `PLP; JMP B67B` or `PLP; JMP BED4`.
- The published movement suffix at `B30E` and the current pause-mux suffix at `B68D` jump to `B800`.
- `B67B` begins `JMP A7F6` (ProgressMux); Steve `BED4` starts `JMP C200`.

The Steve movement source includes the original common native movement prelude and its parity publisher, but that source alone does not prove every actual shared private-update ingress is dominated by it. Before any mount, the current Steve token Other/E0 path, non-E0 pause/draw/token paths and fallback rejects must establish either no accepted Steve entry at B800 or exact state equivalence. Mike and illegal variants must remain excluded by actual hot entry domains. Hidden helper independently owns this current ingress/consumer review; no proposed CPU suite has run.

The private `Unsupported` relocation and the Steve pad also require external/interior executable/table/data-reader closure. The old original movement mirror remains unchanged and available for all old fallback paths.

## Required later source scope

Only after root reviews ingress and capacity may a new source lease authorize composition. That scope must cover actual current cold/Ready/epoch/header/lifecycle boundaries, all three cookie consumers including the Steve cold literal, foreign Mike/Steve behavior, meaningful public AXYP and live mapper/SMC/stack continuation, reached IRQ/busy NMI, and the same genuine heart prefix followed by actual complete second-block prepare and reward. The existing frozen S/L controllers and their current native positives remain separate.

The source-policy distinction matters: `JnStars` bit 7 is the native next-food parity. Its low three bits also serve the original native star remainder. Native Flower reward may change the Mike-family tier; a Jay-specific original Silius gun/ammunition upgrade must not be inferred without a separate current source policy witness.

## Full detached receipt

```json
{
  "detached": true,
  "lease_ready": false,
  "owning_parent_SHA256": "00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21",
  "historical_reference_SHA256": "7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98",
  "source_pins": {
    "tools/audit/check_jay_silius_machinegun_1111.py": "9c04b71b17261e24b3803a2e452ffb010c0f02b5c95e8775422688ea49d2f01a",
    "tools/audit/check_steve_shatterhand_token_ingress_1111.py": "30c7b1b034cb9d14542fc1392006ed1b406b8edf3230e48fc5895b6aac5b5824",
    "tools/audit/current_jay_natural_stock_7c0f_1116.py": "b8c128b51bd47cb2c3f7dce828277a06c54ed034b7d2e1071f667fee41016aeb",
    "tools/audit/audit_jay_upgrade_publication_7c0f_1116.py": "90fb3980b175c38d303b00f31bf14c196311c1bddfbc344af418d89b9ac50df6"
  },
  "main_PC": 47104,
  "main_bytes": 50,
  "main_old_SHA256": "a77e80b73bc66f8e5312464a207966843508b9ea2e2a62c8a3738c8b2659da5a",
  "main_new_SHA256": "a2d35e5811e5a06f494e5fb4d856e217dd98aee988bbea6986eae7b6dfb30e82",
  "proposed_main_hex": "ad7107c901d023ad7307c903d01ca50fc908d016ad77074ab010ad3901100badff5f4a900520e6a790021860ad3e5f20d7be",
  "redirected_private_reject_branches": [
    {
      "PC": 47109,
      "old_target": 47152,
      "new_target": 47146
    },
    {
      "PC": 47116,
      "old_target": 47152,
      "new_target": 47146
    },
    {
      "PC": 47122,
      "old_target": 47152,
      "new_target": 47146
    },
    {
      "PC": 47128,
      "old_target": 47152,
      "new_target": 47146
    },
    {
      "PC": 47133,
      "old_target": 47152,
      "new_target": 47146
    },
    {
      "PC": 47139,
      "old_target": 47152,
      "new_target": 47146
    }
  ],
  "Supported_anchor_unchanged": "B832",
  "private_Unsupported_moved": "B830->B82A; external ingress closure required",
  "original_native_mirror": {
    "bank": 96,
    "PC": 41695,
    "hex": "ad3e5f0aa9002a8d5b07"
  },
  "proposed_leaf": {
    "PC": 48855,
    "hex": "0aa9002a8d5b0760"
  },
  "source_declared_funding": [
    "Jay StageRejected call replacement explicitly emits6NOP",
    "Steve token ingress explicitly replaces11B with JMP C200+8NOP"
  ],
  "no_new_RAM_or_carriers": true,
  "all34_Metal_owned_bytes_preserved": true,
  "proposed_cookie": "aa10200deffb68f830e7c4bb7fe4b68a",
  "cookie_views": [
    {
      "file": 534328,
      "role": "PRG65 cold expected header"
    },
    {
      "file": 774911,
      "role": "PRG94 hot expected header"
    },
    {
      "file": 1429421,
      "role": "CHR371+925 uncompressed StevePacketCold::ExpectedCookie"
    }
  ],
  "cookie_parent_shadow_unchanged": "CHR371+64 historical prior-cookie shadow is NOT the live cookie",
  "owned_bytes": 106,
  "changed_bytes": 63,
  "streamed_conditional_digest": "df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe",
  "exact_spans": [
    {
      "file": 1286160,
      "bytes": 50,
      "old_hex": "ad7107c901d029ad7307c903d022a50fc908d01cad77074ab016ad39011011adff5f4a900b20e6a7eaeaeaeaeaea90021860",
      "new_hex": "ad7107c901d023ad7307c903d01ca50fc908d016ad77074ab010ad3901100badff5f4a900520e6a790021860ad3e5f20d7be",
      "old_SHA256": "a77e80b73bc66f8e5312464a207966843508b9ea2e2a62c8a3738c8b2659da5a",
      "new_SHA256": "a2d35e5811e5a06f494e5fb4d856e217dd98aee988bbea6986eae7b6dfb30e82",
      "role": "current PrivateUpdate scope/reject block50"
    },
    {
      "file": 1288935,
      "bytes": 8,
      "old_hex": "eaeaeaeaeaeaeaea",
      "new_hex": "0aa9002a8d5b0760",
      "old_SHA256": "90961fe2de2d340db3a96d20473c5d6c692df792bb7d7ed11c907c4afbceddf3",
      "new_SHA256": "3cfba51e87b0f87bbb25634494b3218b65896070b18acf4fbb742ef9ecf79c71",
      "role": "Steve token dispatch explicitly retired8-byte pad"
    },
    {
      "file": 534328,
      "bytes": 16,
      "old_hex": "aa10200c3c8114b6f52cd1db4b8564a0",
      "new_hex": "aa10200deffb68f830e7c4bb7fe4b68a",
      "old_SHA256": "e8f84d0882bc6d3c8b7c55a89e6989cf077004f863b23a7ad70878df46967be3",
      "new_SHA256": "f2206bb17b57112ea5973eade183712a21319af71da40a41392c057dd478a15e",
      "role": "full existing cookie view"
    },
    {
      "file": 774911,
      "bytes": 16,
      "old_hex": "aa10200c3c8114b6f52cd1db4b8564a0",
      "new_hex": "aa10200deffb68f830e7c4bb7fe4b68a",
      "old_SHA256": "e8f84d0882bc6d3c8b7c55a89e6989cf077004f863b23a7ad70878df46967be3",
      "new_SHA256": "f2206bb17b57112ea5973eade183712a21319af71da40a41392c057dd478a15e",
      "role": "full existing cookie view"
    },
    {
      "file": 1429421,
      "bytes": 16,
      "old_hex": "aa10200c3c8114b6f52cd1db4b8564a0",
      "new_hex": "aa10200deffb68f830e7c4bb7fe4b68a",
      "old_SHA256": "e8f84d0882bc6d3c8b7c55a89e6989cf077004f863b23a7ad70878df46967be3",
      "new_SHA256": "f2206bb17b57112ea5973eade183712a21319af71da40a41392c057dd478a15e",
      "role": "full existing cookie view"
    }
  ],
  "shared_ingress_blocker": "Current Hot94 admits BOTH Jay and Steve. No Jay-only gate fits these14 new publication bytes. Do not mount until all actual Steve/Mike ingress is proven nonexecuting or already mirror-equivalent, or a separately funded explicit gate is supplied.",
  "live_guard_preservation": "StageRejected carry consumed before mirror; early rejects retarget same CLC/RTS. Supported and Ready/epoch code unchanged.",
  "expected_data_domain": "Read JnStars5F3E; write only native PlayerStatus075B plus normal new JSR stack. Original Jay Q4/velocity/weapon/ammo/helpers unchanged.",
  "source_gate_requirements": [
    "actual current identity/variant/header/Ready/lifecycle and all three cookie consumers",
    "all external/interior readers of moved Unsupported and Steve8 pad",
    "actual Mike/Steve paired supported-update/collector/paused paths, not an assumed invariant",
    "actual public AXYP/meaningful flags/SMC/mapper/live stack and reached IRQ/busy NMI",
    "same ordinary genuine heart prefix then final prepared Flower kind and actual reward/usable ability policy"
  ],
  "CPU_executed": false,
  "ROM_overlay": false,
  "whole_candidate_created": false,
  "outputs": 0,
  "receipt_SHA256": "7700b0a40d77f97a4264d6e8aceed97460d795e7bd1887d3a1b4ed9cfb7b8e0c"
}
```

