"""Save the user's revised priority and precise new-roster implementation state."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from playthroughs.roster_run import workspace_bytes


def main():
    out=R/'build/verification/root-current49-progress-ly.json'
    assert not out.exists()
    checkpoint=R/'build/checkpoints/expanded-profiles-lr/manifest.json'
    cp=json.loads(checkpoint.read_text())
    evidence=(
        'build/verification/smb-crossover-mmc5-exram-exram.json',
        'build/verification/smb-crossover-mmc5-exram-native-proto.json',
        'build/verification/third-row-lp/menu-navigation.json',
        'build/verification/roster-audit-wide-lh/summary.json',
        'build/verification/vic-viper-lq/motion-proof.json',
        'build/verification/vic-viper-lq/gear-proof.json',
        'build/verification/vic-viper-lq/weapon-proof.json',
        'build/verification/route-five-kd/preserved-route-ledger-03.json')
    record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        status='NEW_ROSTER_PRIORITY_VIDEOS_DEFERRED_BY_USER',previous='build/verification/root-current49-progress-kz.json',
        latest_user_instruction='forget the videos for now - add the new characters',
        goal_status='active',goal_complete=False,videos_deferred=True,
        checkpoint=str(checkpoint.relative_to(R)),checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        ROMs=cp['ROMs'],
        current_main_playable='Standard14 identities; expandedaddsProtoMan (15). DD/ZeldaII/Kirby/Vic remain private candidates.',
        shared_foundation=dict(exram='CPU mode2; current512B+reserved bytes allocation below',
            native_proof='2048 actualCPU initialization writes;3072 actual CPU reads;1000frame ordinary Proto select/run/jump/shoot;NMI/IRQ/10bitCHR preserved.',
            standard_mappers='Both current standard cartridges rebuilt byte-identicalKB controls.',
            menu='6/6/7 explicit graph/packing tool;128 possible ready subsets7936 edges. Current12+originalKirby thumbnail pack116unique tiles. Not installed in live menu yet.'),
        allocations=dict(
            Proto=dict(PRG='64A/65C/66A',CHR='256..275',state='73DD..DE'),
            Darkwing=dict(PRG='67A/68C',CHR='276..307 reserve;28KB actual276..303',state='73DF,73EF..F7;recovery5E80..5E9F',draw_guard='4:BF8B..BFA8'),
            ZeldaII=dict(PRG='69A/70C/71A',CHR='308..339',state='73F8..FF;packedowner0InvAmmo16B;5E00..5E7F',draw_guard='4:BFA9..BFCB'),
            Kirby=dict(PRG='72A/73C/74A',CHR='340..379 reserve;16KB actual340..355',state='5C00..5CFF'),
            Vic=dict(PRG='75A/76C/77A',CHR='380..411',state='5D00..5DFF'),
            shared=dict(PRG='78A',persistent='5F00..5F6F seven16B records',menu_variants='5FE0..5FE6'),
            unallocated='5EA0..5EFF;5F70..5FDF;5FE7..5FFF'),
        agents=dict(
            player_guide='Darkwing authentic body/3gas/cape/hang/4HP/nativeArrow. Native50px jump, cost, visiblepowerblockcollection, hangA/Down,Arrow64pxpipe,4hitdeath pass. Fix paletteworld2 mutation and missinghang discovered by root. Recoverycache for actual1-1tallpipe now authorized/implementing. Audio remainsScrooge/SMB, disclose.',
            level_changes_audit='ZeldaII Link private compiles Select/name/preview,14,342native motion and324OAM,79,059RPGcomponent earlier. HP/MP/EXP/8spells/thrusts/6jardrops/UI wiring now authored;integratednativechecks pending. Audio remainsZelda1.',
            route_five_kd='Stopped/preserved all68 routepackets atuserpriority. Kirby authentic192poses+sourcepalette;core/14authoredSMBcopyfamilies/health/weapons privately authored,entryguards/realmenu/nativechecks inprogress.'),
        root_vic=dict(status='PRIVATE_COMPONENT_PORT_NOT_PLAYABLE',path='build/verification/vic-viper-lq',
            proof='OriginalROM retargeted128motion instructions match16,800CPUcases;18,144upgrade+3,584pickup cases;178weaponinstructions match4,320arenas with explicit terrain/SFXfixture callbacks.',
            next='Packrenderer/body+HUD art;replace fixtureworldqueries withSMB;realcameraownership/autoscroll and collision;pickups/drops;audio/selector; nativecontrols.',
            source='OriginalUSA Gradius SHA38c44e0e…; pinned annotatedsource reference/gradius-nes/manifest.json.'),
        deferred=dict(Bass='FinalKO/KQwatercornerfix remainsprivate. Genuinecold-verified ordinary branch now8614/X2610/Y128 beyond1-2final movingplatforms; build/roster-through-2-2/search/root-bass-12-lift-lo/winning-inputs.csv. No newvideo or fullrepairedcampaign.',
            audit='Observernowtracks actualwrite-time5130upperlatch;7212windowchecks/601highCHRchecks,passivephysicaltracesidentical. RunnerrealEasyHard+Proto/Lancevariants+losslessDBGgzipguardsdone.',
            level_helpers='NativehelpersJP and authoredlevelcandidate remainprivate oldHRcontext; not installed main. Reusegenuinenativeplatforms peruser. No DD artificialsidegrip or changedjump.'),
        accepted_darkwing_recovery='Original50pxjump preserved. Firstphysicalpowerblock grantsArrow; ifgroundedblockedbyactualinaccessibletallpipe andnoArrow/gas<3, visibleArrowadaptor24pxbehindplayer inempty native slot, pendingif6full;intentionalpickup only,onecache/cooldown,resetperarea/life. ExplicitSMBportacquisitionadaptation, notoriginalDDlocation.',
        evidence={name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in evidence},
        workspace_bytes=workspace_bytes(R),workspace_cap_bytes=30_000_000_000)
    assert record['workspace_bytes']<record['workspace_cap_bytes']
    out.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(progress=str(out),workspace_bytes=record['workspace_bytes'],goal_complete=False)))


if __name__=='__main__':main()
