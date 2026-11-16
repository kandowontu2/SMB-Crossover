# Jay native status publication: source qualification

Source-only candidate `df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe` is composed over verified installed `00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21`. Root's source lease is `docs/qa/allocations/jay-status-source-root-1116.json`, SHA-256 `812f8e8f040cf6cd79d65e7861c331003d7925340b2187f37641206d0305b460`. No candidate file, native run or delivery is authorized by this checkpoint.

## Frozen composer and owning facade

- `compose_jay_status_publication_00bb_1116.py`: SHA-256 `48fe2b7f1b9dd704f04f6118e333aca89f963cc0012bacd7c761ecf886bc2bca`; `proposal(raw00bb) -> (rawdf0e, report)`, `inverse(rawdf0e) -> raw00bb`, `spans()`.
- `current_jay_status_publication_00bb_1116.py`: SHA-256 `c7cf5ec1f238fb0d4b0001fb1c43d1507165052bf695776a37101f8da22f607c`; `bindings`, `primary`, `cold` require exact df0e. `load_current_image()` reads strict installed 00bb once and composes df0e in memory.
- Complete 106-byte ownership / 63 changed bytes, strict inverse/forward and four wrong-role/truncation rejects pass, receipt `0c7759b451c47b49bedec3233e56c88b08f75b3facd2fc6acc9c016cbdcd909b`. All 34 Metal bytes and every unowned parent byte remain exact.
- Small actual compiled cold job57021 passes: every CPU byte belongs to df0e; all RAM1/2/3 headers are `aa10200deffb68f830e7c4bb7fe4b68a`; Main50 and leaf8 match; activation is engine8, HP6/max3/tier1/lives2, stars/status zero.

## Actual component ABI and cost

`check_jay_status_publication_abi_1116.py` receipt `75e6df717ed9be4d076076851190c491ed81d369f4157a89d2a18ae4d81d0dc8` passes 18,976 actual old/new CPU component pairs. It covers all 256 star-byte values and all 64 meaningful flag combinations (including V and D), A/X/Y corners, Ready0/1/255, and all 256 values for nine admission fields.

Comparison continues through the real LDA Ready or the rejected actual return. A/X/Y/P/SP and the live return agree. Only the intended native status publication and ordinary JSR stack writes differ. Accepted publication adds **14 cycles**; rejected StageRejected paths save 12; earlier rejects have identical cycles. Minimum component SP220. This is not a cadence or whole-public-caller test.

## Before-Ready ordering and real earned parity

Lifecycle94574 passes receipt `72037d544227ac2a90bbec5d3237a9db707b2df6a2c233e4e57fc7de8b0f041b`. The actual compiled cold begins with empty persistent state, then native JnEnsure initializes it at A00E before the first new mirror. That closes the cold ordering premise instead of assuming the private actor's Ready means native persistence is initialized.

The independent ordinary V3 prefix is unchanged (policy cbee9977...). It physically collects the first heart at Main440/original motor441, HP6→8, max3→4. The candidate publishes stars80 as native status1 on the next update. Real +1000 score is observed at completed Main446/motor446. The actual model is captured at completed Main471/motor471: 25 completed original returns after score credit and 30 after collector, no pending worker. No item/actor/health/position/outcome is reconstructed or seeded. Seed receipt `2eccbcba39160d8237bdca500589a068488ce1d0c760ad459d90714ef0d087a5`; `heart_seed(raw)` returns that actual model plus receipt for forked components.

Eight declared Ready/stage/epoch/wrap components fork the actual cold parity0 and actual earned-heart parity80 models. They retain life/HP and settle status to the preserved parity at the accepted private continuation. These are declared lifecycle components, not natural area-completion/respawn routes.

All 96 resident-cookie-byte fault components keep the actual Jay admission domain strict: 64 RAM2/3 faults reject the new mirror. The other 32 are RAM1 faults, which belong to Steve armor and are outside JayHot's actual RAM3/2 loop. All three ROM cookie consumers are still updated and cold-bound; independent Steve ownership/regression must qualify the RAM1 role.

Retained lifecycle81572 is a fixture-expectation negative: it incorrectly demanded Steve's RAM1 header at JayHot admission. The role correction follows the actual native header loop; no game code, C/J API or behavior assertion was weakened.

The lifecycle receipt ran source file version `82b193d943e1c7b8c7481d0f1eb3d5ed8e22baf0f1dcc7a321ee5376fab35beb` before the separate IRQ implementation was appended. The lifecycle and heart-seed function bodies remain identical in this checkpoint. IRQ73680 is running with the extended checker and is **not yet qualified**.

## Remaining source scope

Reached actual IRQ/busy-NMI and complete caller continuation are pending. Hidden helper independently owns the same V3 natural M→F route and paired actual Mike/Steve regressions. Its early same-control witness already changes the real second block to private82 Flower; physical Flower collection is still open at this checkpoint. Original Silius weapon/ammo policy remains unchanged; the native parity publication does not grant an invented gun.

All producers use absent `build/jay-status-source-1116`, max-files1 / timeout600, generated files zero. Root owns physical staging, Mesen and Downloads.

## Compact receipts

```json
{
  "composition": {
    "parent_SHA256": "00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21",
    "candidate_SHA256": "df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe",
    "owned_bytes": 106,
    "changed_bytes": 63,
    "main_bytes": 50,
    "retired_producer_pad_bytes": 8,
    "cookie_views": 3,
    "cookie": "aa10200deffb68f830e7c4bb7fe4b68a",
    "all_unowned_00bb_bytes_exact": true,
    "all34_Metal_bytes_preserved": true,
    "new_RAM_carriers_helpers": 0,
    "grant_SHA256": "812f8e8f040cf6cd79d65e7861c331003d7925340b2187f37641206d0305b460",
    "plan_SHA256": "0ae3ac71e6fa8f7e0f40fe0da13ce33af9ad79dec18367f01b0ae9698bbb0295",
    "plan_receipt": "7700b0a40d77f97a4264d6e8aceed97460d795e7bd1887d3a1b4ed9cfb7b8e0c",
    "proposed_CPU_executed": false,
    "ROM_written": false,
    "outputs": 0,
    "strict_roundtrip": true,
    "wrong_role_or_truncated_rejections": 4,
    "composer_SHA256": "48fe2b7f1b9dd704f04f6118e333aca89f963cc0012bacd7c761ecf886bc2bca",
    "receipt_SHA256": "0c7759b451c47b49bedec3233e56c88b08f75b3facd2fc6acc9c016cbdcd909b"
  },
  "ABI": {
    "passed": true,
    "scope": "Declared old/new private header/leaf components only, through accepted LDA Ready or rejected actual return",
    "parent_SHA256": "00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21",
    "candidate_SHA256": "df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe",
    "C_SHA256": "48fe2b7f1b9dd704f04f6118e333aca89f963cc0012bacd7c761ecf886bc2bca",
    "J_SHA256": "c7cf5ec1f238fb0d4b0001fb1c43d1507165052bf695776a37101f8da22f607c",
    "cases": 18976,
    "counts": {
      "accepted": 17063,
      "rejected": 1913
    },
    "cycle_delta_histogram": {
      "0": 1149,
      "14": 17063,
      "-12": 764
    },
    "minimum_SP": 220,
    "fullAXYP_SP_live_stack_equal_at_actual_continuation": true,
    "only_intended_PlayerStatus_bit7_publication_and_JSR_stack_writes": true,
    "no_blanket_status_flag_masks": "P normalized only with standard B/U bits30; all C/V/N/Z/D/I meaningful flags compare",
    "role": "Component fixtures are not ordinary gameplay, cold lifecycle or public foreign ingress proof",
    "accepted_extra_cycles": 14,
    "rejected_stage_saved_cycles": 12,
    "early_reject_cycles_unchanged": true,
    "source_SHA256": "cc5937aea53b3dff50b9f6da4d4c6b43b9a07240ec91d0b811d69eaf1098bfd5",
    "outputs": 0,
    "receipt_SHA256": "75e6df717ed9be4d076076851190c491ed81d369f4157a89d2a18ae4d81d0dc8"
  },
  "lifecycle": {
    "passed": true,
    "scope": "Genuine compiled cold witness plus declared resident Ready/stage/epoch/header-fault components",
    "candidate_SHA256": "df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe",
    "all_three_cold_headers_new": true,
    "first_JnEnsure_precedes_first_new_mirror": true,
    "counts": {
      "JnAreaReset": 1,
      "JnEnsure": 65,
      "JnClearGear": 1,
      "mirror": 52,
      "post_mirror": 52
    },
    "initial_events": [
      {
        "name": "JnAreaReset",
        "PC": 41104,
        "SP": 217,
        "fields": {
          "stars": 0,
          "status": 0,
          "max": 0,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 0,
          "epoch": 0,
          "frame": 1,
          "life": 2,
          "hp": 0
        }
      },
      {
        "name": "JnEnsure",
        "PC": 40974,
        "SP": 224,
        "fields": {
          "stars": 0,
          "status": 0,
          "max": 0,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 0,
          "epoch": 0,
          "frame": 6,
          "life": 2,
          "hp": 0
        }
      },
      {
        "name": "JnClearGear",
        "PC": 41077,
        "SP": 222,
        "fields": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 0,
          "epoch": 0,
          "frame": 6,
          "life": 2,
          "hp": 6
        }
      }
    ],
    "actual_earned_heart_seed": {
      "collector": {
        "label": "mushroom",
        "item": {
          "slot": 4,
          "flag": 1,
          "id": 46,
          "kind": 1,
          "state": 128,
          "x": 336,
          "y": 120,
          "yhigh": 1,
          "private": 129,
          "owner": 16,
          "contact": 0
        },
        "before": {
          "x": 348,
          "y": 112,
          "native_state": 0,
          "native_vy": 0,
          "native_yhigh": 1,
          "source_flags": 2,
          "source_control": 0,
          "grounded": true,
          "hp": 6,
          "maximum": 3,
          "tier": 1,
          "lives": 2,
          "status": 0,
          "star": 0,
          "engine": 8,
          "camera": 295,
          "score": 100,
          "weapon": 0,
          "ammo": 63,
          "Main": 440,
          "motor": 441
        },
        "after": {
          "x": 348,
          "y": 112,
          "native_state": 0,
          "native_vy": 0,
          "native_yhigh": 1,
          "source_flags": 2,
          "source_control": 0,
          "grounded": true,
          "hp": 8,
          "maximum": 4,
          "tier": 1,
          "lives": 2,
          "status": 0,
          "star": 0,
          "engine": 8,
          "camera": 295,
          "score": 100,
          "weapon": 0,
          "ammo": 63,
          "Main": 440,
          "motor": 441
        },
        "Main": 440,
        "motor": 441
      },
      "credit": {
        "Main": 446,
        "motor": 446,
        "state": {
          "x": 348,
          "y": 112,
          "native_state": 0,
          "native_vy": 0,
          "native_yhigh": 1,
          "source_flags": 2,
          "source_control": 0,
          "grounded": true,
          "hp": 8,
          "maximum": 4,
          "tier": 1,
          "lives": 2,
          "status": 1,
          "star": 0,
          "engine": 8,
          "camera": 295,
          "score": 1100,
          "weapon": 0,
          "ammo": 63,
          "Main": 446,
          "motor": 446
        }
      },
      "completed": {
        "x": 371,
        "y": 112,
        "native_state": 0,
        "native_vy": 0,
        "native_yhigh": 1,
        "source_flags": 0,
        "source_control": 0,
        "grounded": true,
        "hp": 8,
        "maximum": 4,
        "tier": 1,
        "lives": 2,
        "status": 1,
        "star": 0,
        "engine": 8,
        "camera": 295,
        "score": 1100,
        "weapon": 0,
        "ammo": 63,
        "Main": 471,
        "motor": 471
      },
      "actual_postcredit_returns": 25,
      "actual_postcollector_returns": 30,
      "pending_workers": 0,
      "parent_route_receipt": "c139124d5848f6dca3fdd5df5716d121ff3acc7dd7d4f48365115424f67f0d28",
      "policy_SHA256": "cbee9977f74f301b92026cac516f9e088a002636fe21ccdbf44c2daccaa7a443",
      "derived_observer_SHA256": "ade4c27a9bf4960410a7b236e10c74c8ad48264dd94dd8cb2594f4db1edf12f5",
      "natural_prefix_only": true,
      "no_gameplay_seeds": true,
      "original_entry_and_return_counts_equal": true,
      "receipt_SHA256": "2eccbcba39160d8237bdca500589a068488ce1d0c760ad459d90714ef0d087a5"
    },
    "lifecycle": [
      {
        "name": "genuine compiled cold plus4 neutral updates",
        "fields": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 1,
          "epoch": 170,
          "frame": 170,
          "life": 2,
          "hp": 6
        },
        "counts": {
          "JnAreaReset": 1,
          "JnEnsure": 1,
          "JnClearGear": 1,
          "mirror": 4,
          "post_mirror": 4
        }
      },
      {
        "name": "declared Ready/stage/epoch lifecycle component",
        "seed": "cold parity0",
        "before": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 0,
          "epoch": 170,
          "frame": 254,
          "life": 2,
          "hp": 6
        },
        "after": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 1,
          "epoch": 0,
          "frame": 0,
          "life": 2,
          "hp": 6
        }
      },
      {
        "name": "declared Ready/stage/epoch lifecycle component",
        "seed": "cold parity0",
        "before": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 1,
          "ready": 0,
          "epoch": 170,
          "frame": 255,
          "life": 2,
          "hp": 6
        },
        "after": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 1,
          "ready": 1,
          "epoch": 1,
          "frame": 1,
          "life": 2,
          "hp": 6
        }
      },
      {
        "name": "declared Ready/stage/epoch lifecycle component",
        "seed": "cold parity0",
        "before": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 1,
          "epoch": 170,
          "frame": 255,
          "life": 2,
          "hp": 6
        },
        "after": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 1,
          "epoch": 1,
          "frame": 1,
          "life": 2,
          "hp": 6
        }
      },
      {
        "name": "declared Ready/stage/epoch lifecycle component",
        "seed": "cold parity0",
        "before": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 1,
          "ready": 1,
          "epoch": 170,
          "frame": 0,
          "life": 2,
          "hp": 6
        },
        "after": {
          "stars": 0,
          "status": 0,
          "max": 3,
          "stage": 0,
          "world": 0,
          "level": 1,
          "ready": 1,
          "epoch": 2,
          "frame": 2,
          "life": 2,
          "hp": 6
        }
      },
      {
        "name": "declared Ready/stage/epoch lifecycle component",
        "seed": "real earned-heart parity80",
        "before": {
          "stars": 128,
          "status": 1,
          "max": 4,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 0,
          "epoch": 125,
          "frame": 254,
          "life": 2,
          "hp": 8
        },
        "after": {
          "stars": 128,
          "status": 1,
          "max": 4,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 1,
          "epoch": 0,
          "frame": 0,
          "life": 2,
          "hp": 8
        }
      },
      {
        "name": "declared Ready/stage/epoch lifecycle component",
        "seed": "real earned-heart parity80",
        "before": {
          "stars": 128,
          "status": 1,
          "max": 4,
          "stage": 0,
          "world": 0,
          "level": 1,
          "ready": 0,
          "epoch": 125,
          "frame": 255,
          "life": 2,
          "hp": 8
        },
        "after": {
          "stars": 128,
          "status": 1,
          "max": 4,
          "stage": 0,
          "world": 0,
          "level": 1,
          "ready": 1,
          "epoch": 1,
          "frame": 1,
          "life": 2,
          "hp": 8
        }
      },
      {
        "name": "declared Ready/stage/epoch lifecycle component",
        "seed": "real earned-heart parity80",
        "before": {
          "stars": 128,
          "status": 1,
          "max": 4,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 1,
          "epoch": 125,
          "frame": 255,
          "life": 2,
          "hp": 8
        },
        "after": {
          "stars": 128,
          "status": 1,
          "max": 4,
          "stage": 0,
          "world": 0,
          "level": 0,
          "ready": 1,
          "epoch": 1,
          "frame": 1,
          "life": 2,
          "hp": 8
        }
      },
      {
        "name": "declared Ready/stage/epoch lifecycle component",
        "seed": "real earned-heart parity80",
        "before": {
          "stars": 128,
          "status": 1,
          "max": 4,
          "stage": 0,
          "world": 0,
          "level": 1,
          "ready": 1,
          "epoch": 125,
          "frame": 0,
          "life": 2,
          "hp": 8
        },
        "after": {
          "stars": 128,
          "status": 1,
          "max": 4,
          "stage": 0,
          "world": 0,
          "level": 1,
          "ready": 1,
          "epoch": 2,
          "frame": 2,
          "life": 2,
          "hp": 8
        }
      }
    ],
    "header_cases": 96,
    "header_fault_outcomes": {
      "Steve-only R1 header outside JayHot admission": 32,
      "rejected-no-mirror": 64
    },
    "retained_fixture_negative81572": "Incorrectly required Steve-only RAM1 header for JayHot, whose actual loop owns only RAM3/2. No code or gameplay change.",
    "Starspolicy": "Initialization clears the16B persistent block; stage gear clear and original drop writers preserve bit7; only actual typed collector togglesbit7.",
    "no_new_food_or_weapons_seeded": true,
    "outputs": 0,
    "C_SHA256": "48fe2b7f1b9dd704f04f6118e333aca89f963cc0012bacd7c761ecf886bc2bca",
    "J_SHA256": "c7cf5ec1f238fb0d4b0001fb1c43d1507165052bf695776a37101f8da22f607c",
    "source_SHA256": "82b193d943e1c7b8c7481d0f1eb3d5ed8e22baf0f1dcc7a321ee5376fab35beb",
    "receipt_SHA256": "72037d544227ac2a90bbec5d3237a9db707b2df6a2c233e4e57fc7de8b0f041b"
  }
}
```

