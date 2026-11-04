"""Bound the no-proposal Mini empty guest-chain audit; produces no candidate."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import build_storage_guard_v1 as G
O=R/'build/mini-noop-chains-1103-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    G.preflight(private_root=O,reserved_bytes=14000,reserved_files=1,fresh=True);O.mkdir(exist_ok=True)
    profile=R/'build/mini-direct-idle-cpu/idle-cpu.json'
    parent=R/'build/mini-direct-head-candidate/mini-optimized.nes'
    raw=parent.read_bytes()
    assert sha(parent)=='22db9288a5ba5b92e2e1a724d39f2bec83faa97c4e8304481eb0080058d8f217'
    files=[R/'src'/n for n in ['object.s','inventory_drops.s','zelda2_link_drops.s',
        'roll_shot_bank.inc','z2_platform_late_render.s','z2_platform_late_legacy.inc',
        'player.s','zelda2_link_motion.s','megaman_weapons.s']]
    text={p.name:p.read_text() for p in files}
    assert 'stx InvDropSlot' in text['inventory_drops.s']
    assert 'sta MmFireBank' in text['roll_shot_bank.inc'] and 'inc ReloadCHRBank' in text['roll_shot_bank.inc']
    assert 'stx FirebarSlot' in text['z2_platform_late_legacy.inc']
    assert 'cmp #$2b' in text['z2_platform_late_render.s'] and 'cmp #$2c' in text['z2_platform_late_render.s']
    motion=text['zelda2_link_motion.s']
    assert 'jsr Z2MovementTerrainBegin\n .res 17,$ea' in motion
    # Byte observations confirm the source candidates, not executable grants.
    def area(bank,pc,n):return raw[16+8192*bank+(pc&8191):16+8192*bank+(pc&8191)+n]
    assert area(71,0xa48d,17)==bytes([0xea])*17
    assert area(4,0xbf7a,12)==bytes([0xea])*12
    q=dict(status='AUDIT_COMPLETE_NO_QUALIFIED_PROPOSAL',ROM_written=False,Mesen_run=False,
        ready_500_cycle_gate=False,patches=[],source_mutations=[],
        profiled_reference_SHA256=sha(parent),
        observed_empty_CPU_range=[min(json.loads(profile.read_text())['totals']),max(json.loads(profile.read_text())['totals'])],
        chain_findings=[
            dict(chain='ProcFireball_Bubble -> Z2UpdateDropsGate -> InventoryUpdateDrops',
                 required='Preserve four drop-kind domains and active drop physics/collection. Empty loop still writes InvDropSlot0 and returns XFF.',
                 disposition='No source-funded upstream Mini guard qualified.'),
            dict(chain='MegaManFullShotBank -> RlFullShotBankDispatch -> RlOriginalFullShotBank',
                 required='Four legacy bullet types can select a CHR bank; empty path writes MmFireBank0 and native CurrentCHR4/Reload when needed.',
                 disposition='Literal return would change shared native fields; constant specialization not qualified.'),
            dict(chain='WorldFirebarAdmission -> Z2LateLegacyFirebarAdmission + Z2DrawLateSmallLifts',
                 required='All six IDs can select firebar1B..22 or late small lift2B/2C. Empty path writes FirebarSlotFF and has specific AXYP return.',
                 disposition='No actor/world-effect path skipped. A selected41 + complete domain guard and exact return does not fit sole12B source candidate.'),
            dict(chain='Native end palette',
                 required='ResetPalStar mutates Player_SprAttrib low palette bits; star palette cycle mutates R0 and attributes. Not a no-op for arbitrary legal state.',
                 disposition='No palette source path bypassed.')],
        funding_findings=[
            dict(bank=71,CPU_half_open=[0xa48d,0xa49e],bytes=17,
                 status='NOT_FREE_EXECUTED_PADDING',reason='Straight-line Link movement executes these EA after Z2MovementTerrainBegin; arbitrary helper body would alter Link.'),
            dict(bank=4,CPU_half_open=[0xbf7a,0xbf86],bytes=12,
                 status='UNGRANTED_SOURCE_CANDIDATE_ONLY',reason='Tail after native player-owner JMP; full consumer closure and sufficient gate budget unproved.'),
            dict(bank=79,CPU_half_open=[0xb53f,0xb54c],bytes=13,status='FIRE_AGENT_CLAIMED_DO_NOT_USE'),
            dict(bank=20,status='GRAPHICS_BACKGROUND_FULL_DO_NOT_USE'),
            dict(bank=84,status='DIRECT_DISPATCH_DO_NOT_USE'),dict(bank=89,status='FIRE_AGENT_DO_NOT_USE')],
        delivery='Do not block root-qualified Mini build for this audit. No profitable/safe candidate asserted.',
        bindings={p.relative_to(R).as_posix():sha(p) for p in [Path(__file__),profile,parent,*files]})
    (O/'audit.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ['bindings','chain_findings','funding_findings']}))


if __name__=='__main__':main()
