# Jay status candidate hold: omitted native size publication

**df0e is not a deliverable candidate.** Actual current Downloads00bb is unchanged. The new consumer witness proves that the detached 10-byte status-only mirror omitted part of the old movement contract: PlayerSize must also become zero. Existing composition/ABI/lifecycle/IRQ receipts retain their narrow scopes; they did not qualify this native head-size consumer.

Source causal job43465 is terminal exit0, receipt `5d02c293721c27839e8637f5e81bb804d59105a0ecc5e5ca5ab892418bf54d87`, with zero files under absent `build/jay-status-source-1116`. No actor, health, position, power or size fields are seeded. No revised instruction or ROM is mounted or executed.

The unchanged actual first-heart seed is `2eccbcba39160d8237bdca500589a068488ce1d0c760ad459d90714ef0d087a5` at completed Main471: PlayerSize1, PlayerStatus1, JnStars80, MmBlockAttack0, raw16, HP8/max4/lives2. The real current CrossoverBlockSize at PRG126:9034 receives tile51 and Y equal to actual PlayerSize1. It returns Y1 and leaves those fields unchanged. This is the native small-head decision, consistent with the repeated real tile51 bumps seen by the independent natural route.

Actual native code/source explains the transition: CrossoverBlockSize's raw16 path falls into MegaManHead; nonzero PlayerStatus returns the incoming PlayerSize. The earlier status0 path instead reaches CrossoverSmallHeadCold, whose raw16 branch forces Y0. Thus adding status1 alone exposes stale PlayerSize1 and loses the prior large-head policy.

The unchanged original JnMovement prefix begins PRG96:A2CB (file787163). Its A2DF15-byte publication is exactly `AD3E5F0AA9002A8D5B07A9008D5907`: the status formula followed by `LDA #0; STA PlayerSize($0759)`. Any new proposal must preserve both original publications. Reusing the leaf's existing LDA#0 can fund the zero value; the extra STA still requires three explicitly owned instruction bytes and a new reviewed layout.

Root has been notified to hold physical/native/delivery. All frozen df0e C/J/plan files remain unchanged. A separate detached funding revision follows; no control/physics/helper change is inferred from this negative.

## Reproducer (in-memory source only)

Run through the bounded wrapper; the code uses the frozen7cb0 lifecycle helper's unchanged genuine heart capture and reads the actual native size oracle without poisoning fields.

```python
import sys,json;sys.path.insert(0,'tools/audit');import check_jay_status_publication_lifecycle_irq_1116 as K;J=K.J;raw=J.load_current_image();m,proof=K.heart_seed(raw);names=('PlayerSize','PlayerStatus','JnStars','MmBlockAttack','SelectedCharacter','JnHealth','JnMaxHearts','NumberofLives');before={n:J.N.get(m,n)for n in names};result=J.N.invoke(m,'CrossoverBlockSize',a=51,x=0,y=before['PlayerSize'],p=0x31);after={n:J.N.get(m,n)for n in names};pc=J.W.address(m.bundle,'CrossoverBlockSize');at=J.W.location(m.bundle,'CrossoverBlockSize');cold=J.W.location(m.bundle,'CrossoverSmallHeadCold');native=16+96*8192+(0xa2cb&8191);out={'candidate':J.H(raw),'genuine_seed_receipt':proof['receipt_SHA256'],'actual_state_before':before,'actual_state_after':after,'head_oracle':{'incoming_tile':51,'incoming_Y_actual_PlayerSize':before['PlayerSize'],'returned':result,'PC':pc,'physical_PRG':(at-16)//8192,'first48_hex':raw[at:at+48].hex(),'cold_first24_hex':raw[cold:cold+24].hex()},'unchanged_original_JnMovement_prefix':{'PC':0xa2cb,'physical_PRG':96,'file':native,'first80_hex':raw[native:native+80].hex(),'mirror_and_size15_hex':raw[native+20:native+35].hex()},'no_actor_health_position_power_or_size_seed':True,'no_proposed_revision_or_ROM_written':True,'outputs':0};out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
```

## Causal receipt

```json
{
  "candidate": "df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe",
  "genuine_seed_receipt": "2eccbcba39160d8237bdca500589a068488ce1d0c760ad459d90714ef0d087a5",
  "actual_state_before": {
    "PlayerSize": 1,
    "PlayerStatus": 1,
    "JnStars": 128,
    "MmBlockAttack": 0,
    "SelectedCharacter": 16,
    "JnHealth": 8,
    "JnMaxHearts": 4,
    "NumberofLives": 2
  },
  "actual_state_after": {
    "PlayerSize": 1,
    "PlayerStatus": 1,
    "JnStars": 128,
    "MmBlockAttack": 0,
    "SelectedCharacter": 16,
    "JnHealth": 8,
    "JnMaxHearts": 4,
    "NumberofLives": 2
  },
  "head_oracle": {
    "incoming_tile": 51,
    "incoming_Y_actual_PlayerSize": 1,
    "returned": {
      "A": 1,
      "X": 0,
      "Y": 1,
      "P": 49,
      "CPU": 96,
      "minimum_SP": 218,
      "counts": {}
    },
    "PC": 36916,
    "physical_PRG": 126,
    "first48_hex": "08ada468d020ad0260c908d009ad5b07f011a000f010c902f00ec900f008ad5b07d0034ce2bf2860adee5fc901f0f4ad",
    "cold_first24_hex": "a001ad0260c910d002a0002860ffffffffffffffffffffff"
  },
  "unchanged_original_JnMovement_prefix": {
    "PC": 41675,
    "physical_PRG": 96,
    "file": 787163,
    "first80_hex": "200ea020f5a020c8a0ee035cad045cf003ce045cad3e5f0aa9002a8d5b07a9008d59078db0688d006b8d0f6c8d17078d14608dc1688dc068a5758d095c8db568a51ec903f0034c26a38d6a01a90c8d6c",
    "mirror_and_size15_hex": "ad3e5f0aa9002a8d5b07a9008d5907"
  },
  "no_actor_health_position_power_or_size_seed": true,
  "no_proposed_revision_or_ROM_written": true,
  "outputs": 0,
  "receipt_SHA256": "5d02c293721c27839e8637f5e81bb804d59105a0ecc5e5ca5ab892418bf54d87"
}
```

