"""Install the earned-powerup repair and verify the actual Downloads launch."""
import json,sys
import deliver_mini_nightly_root_1103_v30 as D
D.O=D.R/'build/mini-power-delivery-root-1103-v61'
D.PREVIOUS='ca90e8be125c55e7ae12413964ecf766c9b890525751ea1e0ad6ce225613f4db'

if __name__=='__main__':
    full=D.R/'build/mini-power-regression-root-1103-v60/full49/capture/result.json'
    f=json.loads(full.read_text())
    assert f['passed'] and f['full_stage'] and f['ROM_sha256']=='9d291cb7562aad3a21e575386d0d6461dc39eab5cbd34c85856ae8a1f1d2b622'
    irq=json.loads((D.R/'build/mini-mario-power-contract-1103-v51/native-power-v57-ISR.json').read_text())
    assert irq['passed'] and irq['ROM_memory_SHA256']==f['ROM_sha256']
    D.main()
    path=D.O/('delivery.json' if sys.argv[1]=='install' else 'verified-delivery.json')
    q=json.loads(path.read_text())
    q['verification_scope']='Actual first question-block release, mushroom emergence/maturity and collection, one erase/constructor/score1000,60 native power updates, resumed powered6x15/source sprite/CHR/OAM checks. Separate exact-ROM full non-shortcut1-1 reaches active1-2 without life loss or helpers.'
    q['full_stage_receipt']=str(full.relative_to(D.R))
    q['original_power_timing_qualified']=False
    q['remaining']='Generic60update/+1 progression remains a host adaptation. Original30/35 transition clips, type-specific mushroom/flower targets and fireballs are unfinished.'
    path.write_text(json.dumps(q,indent=2)+'\n')
    if sys.argv[1]=='finalize':
        (D.O/'release-notes.txt').write_text(
            'Current MMC5 work-in-progress nightly.\n\n'
            'Apply this sole IPS to clean, headered Super Mario Bros. (World).\n'
            'Base SHA-256: 0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea\n'
            'Patched ROM SHA-256: '+q['ROM_SHA256']+'\n\n'
            'Mini Mario is unlocked under Mario: press Select until MINI MARIO. A jumps; B runs. '
            'His mushroom pickup is repaired: real block release, collection, growth animation and powered sprite/hitbox pass from Downloads. '
            'Full non-shortcut1-1 still reaches active1-2 without life loss or helper platforms. '
            'Original Mini transition timing, exact type-specific progression and fireballs remain unfinished. '
            '93 selectable identities; Prince remains locked and Donkey Kong Jr. is not on the public menu.\n')
