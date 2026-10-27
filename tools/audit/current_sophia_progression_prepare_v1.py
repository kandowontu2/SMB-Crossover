"""Prepare ONE SophiaEasy progression route with a surviving unmodified policy.

Source/CPU preparation only. No emulator, archived-tree recovery or source edit.
"""
from pathlib import Path
from types import SimpleNamespace
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/audit'))
from current_roster_compact_11_v1 import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena

EXPECTED = '6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
POLICY = '17d3a38d53fe09b930048f081938bf707028f765577207bce41777ea4f5edb7b'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', newline='\n')


def mushroom_source_control(bundle):
    q = Arena(bundle, 11)
    q.invoke('InventoryInit')
    q.put(CrossoverBehaviorVersion=0, PlayerStatus=0)
    q.set('PowerUpType', 1, 5)
    q.invoke('InventoryPreparePickup', x=5)
    prepared = dict(item=q.get('InvPickup', 5), owner=q.get('InvPickupOwner', 5),
                    native_type=q.get('PowerUpType', 5))
    assert prepared == dict(item=0, owner=11, native_type=0)
    q.invoke('InventoryCollect', x=5)
    started = dict(active=q.get('GuestPowerupActive'), target=q.get('GuestPowerupTarget'),
                   owned_lo=q.get('InvOwnedLo', 11), owned_hi=q.get('InvOwnedHi', 11))
    assert started == dict(active=1, target=1, owned_lo=129, owned_hi=0)
    for tick in range(60):
        q.invoke('GuestPowerupUpdate')
        assert q.get('GuestPowerupActive') == int(tick < 59)
    finished = dict(power=q.get('PlayerStatus'), active=q.get('GuestPowerupActive'),
                    age=q.get('GuestPowerupAge'), engine=q.get('GameEngineSubroutine'))
    assert finished == dict(power=1, active=0, age=60, engine=8)
    return dict(prepared=prepared, collected=started, after_60_updates=finished,
                actual_assembled_calls='InventoryInit / InventoryPreparePickup / InventoryCollect / 60 GuestPowerupUpdate',
                scope='Isolated legal CPU component with disclosed setup. No physical reveal, actor motion, contact, IRQ, NMI or PPU claim.')


def main():
    old = ROOT / 'build/verification/compact-next-sophia-6be-easy-v2'
    first = ROOT / 'build/verification/compact-next-sophia-6be-easy-v1'
    out = ROOT / 'build/verification/compact-next-sophia-6be-easy-v3'
    receipt = ROOT / 'docs/qa/sophia-easy-v2-native-failure-2026-10-27.json'
    policy = ROOT / 'tools/playthroughs/full_roster_policy_og.lua'
    rom = ROOT / 'build/samus_fixed_hud_current4a.nes'
    assert not out.exists() and not receipt.exists()
    assert sha(rom) == EXPECTED and sha(policy) == POLICY
    raw_policy = policy.read_bytes()
    text = raw_policy.decode()
    prior = json.loads((old / 'ready.json').read_text())
    failed = json.loads((old / 'result.json').read_text())
    assert failed['ROM_sha256'] == prior['ROM_sha256'] == EXPECTED
    assert failed['actual_mode'] == 0 and not failed['passed']
    assert failed['frames'] == 2708 and failed['reason'] == 'Zero-death 1-1 route'
    assert sha(old / 'review.json') == '7a36561a64053b82d464aabc89dcb6d4a487b017684beefaebc7d46f1e1c664e'
    assert sha(old / 'selected-whole-frames.png') == '897ee8de1cdc104c189c75bdb9bc14b294739307c6faa19243628ad71154730b'
    trace = list(csv.DictReader((old / 'trace.csv').open(newline='')))
    final = trace[-1]
    assert all(int(final[n]) == v for n, v in dict(frame=2708, x=1241, y=149, state=1, vx=0, vy=252, power=0, engine=11).items())
    assert int(trace[2694]['x']) == 1230 and int(trace[2694]['y']) == 172
    assert all(int(row['power']) == 0 for row in trace)
    # Genuine unchanged controller branches; this is not an archived body-equality claim.
    for needle in ["if phase=='approach'and c.x>=332 then phase='bump'", 'b.a=t>=16 and t<45',
                   "if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then",
                   "if not item or item.state<128 then return b end", 'b.right=c.x<item.x-4;b.left=c.x>item.x+12',
                   "if seenItem and not item then phase='route'", "elseif c.frame-pickupStart>600 then phase='route'",
                   'local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)']:
        assert needle in text, needle
    source = mushroom_source_control(scoped_load(rom))
    evidence = [old/n for n in ['ready.json', 'result.json', 'review.json', 'trace.csv', 'inputs.csv', 'selected-whole-frames.png']]
    ledger = dict(identity='sophia', mode=0, ROM_sha256=EXPECTED, component='controller-only1-1',
                  outcome='FALSE', frame=2708, x=1241, y=149,
                  failure='Zero-death guard during rising approach beneath visible Goomba near question-block row',
                  remaining='Fresh progression-controller clear, actual first-mushroom readback and independent replay; no exact collision-owner or source-physics defect established.')
    negative = dict(status='NATIVE_FALSE', ROM_sha256=EXPECTED, actual_numeric_mode=0,
                    identity='sophia', frame=2708, route_clear=False, zero_death=False,
                    completed_GameLoops=failed['completed_loops'], actual256_DMAs=failed['completed_DMAS'],
                    whole_PPU_frames_valid=failed['full_frames'], selected_frames_ROOT_viewed=5,
                    actual_final_state=final,
                    trajectory='Grounded X1229/Y176 at2693; A first requested poll2694, visible rising X1230/Y172 at2695; X1241/Y149 before engine11 at2708. Power stays0 throughout. The prior tall pipe is now passed.',
                    contact_scope='ROOT-viewed final whole frame shows a Goomba at/above Sophia beside the low question-block row, plus another high-row enemy. Exact collision actor slot/ID/contact PC is not serialized, so this does not identify the precise native damage branch.',
                    next_controller='Use surviving generic real-mushroom reveal/chase policy unchanged, rather than another cold-form coordinate exception or an unproven upward-cannon response.',
                    original_v1_and_v2_unchanged=True, ledger_entry=ledger,
                    external_evidence=[dict(path=str(p), sha256=sha(p), bytes=p.stat().st_size) for p in evidence])
    put(receipt, negative)
    prepare(SimpleNamespace(rom=rom, expected_sha256=EXPECTED, output=out, identity='sophia', mode='easy',
                            frames=8000, policy=policy, replay=None))
    review = dict(PREPARED_DO_NOT_RUN=True, native_run=False, ROM_sha256=EXPECTED,
                  policy_path=str(policy), policy_sha256=POLICY, policy_bytes_unchanged=True,
                  changes='Controller selection only: scoped v2 dry policy replaced by surviving generic progression policy. Game, shared harness, source and all 8000-frame/zero-death/mode/motion/CHR/IRQ/NMI/DMA guards unchanged.',
                  current_policy_behavior='At X332 pause and physically head-bump first block with A at elapsed16..44, then scan six real actor slots for live ID2e and chase mature state>=128 mushroom; a seen actor disappearing or 600-frame timeout resumes ordinary terrain route. No resources, invulnerability, ownership, motion or result writes.',
                  source_mushroom_component=source,
                  historical_scope=dict(ROM='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99',
                                        old_source_sha256='f4e84baefbafa94986a3a56ff1209fd135549d24eb2ef58ba8749ccdfd4f61cc',
                                        old_Sophia_readback='PlayerStatus0->1 at1027; preceding engine9 at967; route endpoint5288',
                                        warning='Historical receipts only. Archived source body is not restored or available for byte comparison; current surviving policy hash differs. No historical route, native pickup or graphics result transfers to6be.'),
                  remaining_limits='No native attempt performed. First real pickup is an intended controller action, not an automatic PASS in the unchanged route harness: ROOT must inspect actual actor/growth/power readback. Existing 35-physical-poll air hold and route adaptation remain unproved on6be; no cap increase or new Up-cannon claim.',
                  public_failure_receipt=str(receipt))
    put(out/'controller-review.json', review)
    put(out/'negative-ledger-entry.json', ledger)
    ready = out/'ready.json'
    z = json.loads(ready.read_text())
    z['PREPARED_DO_NOT_RUN'] = True
    z['controller_revision'] = dict(policy_selection_only=True, review=str(out/'controller-review.json'),
                                    previous_native_FALSEs_preserved=True, no_native_run=True)
    sources = ['src/inventory.s', 'src/guest_powerups.s', 'src/expanded.s', 'src/expanded_weapons.s']
    historical = ['docs/qa/current3cee-remaining27-readiness-2026-10-26.txt', 'docs/qa/current3cee-remaining27-native-2026-10-26.txt']
    for p in [Path(__file__).resolve(), receipt, out/'controller-review.json', out/'negative-ledger-entry.json',
              ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py', ROOT/'tools/audit/robots_weapon_cpu_v1.py',
              first/'ready.json', first/'result.json'] + evidence + [ROOT/p for p in sources+historical]:
        z['bindings'][str(p)] = sha(p)
    put(out/'command.json', dict(PREPARED_DO_NOT_RUN=True, requires_ROOT_native_lease=True, argv=z['command']))
    z['bindings'][str(out/'command.json')] = sha(out/'command.json')
    for p, h in z['bindings'].items():
        assert sha(p) == h, p
    put(ready, z)
    assert policy.read_bytes() == raw_policy
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN', ready=str(ready), sha256=sha(ready),
                          bindings=len(z['bindings']), policy_sha256=sha(policy),
                          public_failure_receipt=str(receipt), receipt_sha256=sha(receipt))))


if __name__ == '__main__':
    main()
