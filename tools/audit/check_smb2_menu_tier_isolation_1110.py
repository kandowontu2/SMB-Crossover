"""Qualify the SMB2 preview fix on the exact installed MMC5 parent."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

import check_current_roster_stage_ingress_1110 as Ingress
import check_sonic_injury_prince_rebase_1110 as Previous
from check_remaining_roster_starts_1110 import inventory
from check_tmnt_render_oa import address, location

R, N, UI = Ingress.R, Ingress.N, Ingress.UI
sys.path.insert(0, str(R/'tools/reference'))
from sonic_sms_compact_cold_worker_1110 import assemble

SOURCE = R/'src/smb2_roster_core.s'
CANDIDATE = R/'build/smb2-menu-tier-isolation-native-1110/candidate.nes'
PARENT = Previous.PIN
NIGHTLY = Previous.Prince.NIGHTLY
OLD = bytes.fromhex(
    'ad0260c919d008a9008d2e5c4ccaac1860'
    'ad0260c919d0034ccaac1860'
    'a9008d9b5f8d995f8d9a5fa91f8d985f20e7ac202bafa9b28d9b5f3860')
BEGIN, END, BANK = 0xacad, 0xace7, 118
LEAK_ROUTE = (4, 4, 4, 1, 32, 32, 32)
CONTROL_ROUTE = (1, 4, 4, 4, 32, 32, 32)


def digest(data):
    return sha256(data).hexdigest()


def proposal(parent):
    assert digest(parent) == PARENT
    bundle = Ingress.F.Symbols.bundle()
    symbols = ('SelectedCharacter', 'S2Clock', 'S2Ready', 'S2MaxHealth',
               'S2Vegetables', 'S2Health', 'S2ResetTransient',
               'S2ExportPosition', 'OperMode')
    assert location(bundle, 'S2ColdInit') == 16+BANK*8192+(BEGIN&8191)
    assert location(bundle, 'S2ResetTransient') == 16+BANK*8192+(END&8191)
    at = location(bundle, 'S2ColdInit')
    assert parent[at:at+len(OLD)] == OLD and len(OLD) == END-BEGIN
    # The initializer is private and has only these two same-bank entrants.
    bank = parent[16+BANK*8192:16+(BANK+1)*8192]
    assert bank.count(bytes.fromhex('4ccaac')) == 2
    assert bytes.fromhex('20caac') not in bank
    source = SOURCE.read_text(encoding='utf-8')
    body = source[source.index('.proc S2ColdInit'):source.index('.proc S2ResetTransient')]
    assert len(re.findall(r'\bS2InitializeRecord\b', source)) == 2
    body = (body.replace('.proc ', '').replace('.endproc\n', '')
                .replace('bne No', 'bne ColdReject').replace('No:clc', 'ColdReject:clc')
                .replace('S2ColdInit::No', 'ColdReject'))
    body = re.sub(r'^(S2ColdInit|S2NewLife|S2InitializeRecord)$', r'\1:', body, flags=re.M)
    consts = {'CHARACTER_SMB2_ROSTER': 25} | {n: address(bundle,n) for n in symbols}
    asm = '\n'.join(f'{name} = ${value:x}' for name,value in consts.items())
    result = assemble(f'{asm}\n.segment "SMB2_INIT"\n{body}', {'SMB2_INIT': (BEGIN, END-BEGIN)})
    code = result['images']['SMB2_INIT']
    assert len(code) == len(OLD)
    assert result['symbols']['S2NewLife'] == address(bundle,'S2NewLife')
    assert result['symbols']['S2InitializeRecord'] == 0xacc5
    image = parent[:at]+code+parent[at+len(code):]
    return image, dict(ROM_SHA256=digest(image), parent_SHA256=PARENT, bank=BANK,
                       first=BEGIN, last_exclusive=END, old=OLD.hex(), new=code.hex(),
                       changed_bytes=sum(a!=b for a,b in zip(OLD,code,strict=True)),
                       source_SHA256=digest(SOURCE.read_bytes()))


def nav(bundle, keys):
    m = UI.seed(bundle, 0)
    result = [(UI.menu_name(m)[0], N.get(m, 'PlayerStatus'))]
    for key in keys:
        UI.key(m, key)
        result.append((UI.menu_name(m)[0], N.get(m, 'PlayerStatus')))
    return result, m


def menu(bundle, patched, current_inventory):
    old, _ = nav(bundle, LEAK_ROUTE)
    new, m = nav(patched, LEAK_ROUTE)
    control, _ = nav(patched, CONTROL_ROUTE)
    assert old[3] == ('SMB2 MARIO',1) and old[-1] == ('SONIC',1)
    assert [item[0] for item in new] == [item[0] for item in old]
    assert all(tier == 0 for _,tier in new+control)
    assert control[-1] == ('SONIC',0)
    UI.key(m, 16)
    assert N.get(m,'CrossoverMenuState') == 0 and N.get(m,'PlayerStatus') == 0
    assert current_inventory == inventory(patched['raw'])
    samples = []
    for cycle in range(8):
        a, b = (UI.seed(image, 24) for image in (bundle, patched))
        for model in (a,b):
            for _ in range(cycle):
                UI.key(model,32)
        name = UI.menu_name(a)[0]
        assert name == UI.menu_name(b)[0]
        assert N.get(a,'PlayerStatus') == 1 and N.get(b,'PlayerStatus') == 0
        assert N.get(a,'S2Health') == N.get(b,'S2Health') == 31
        assert N.get(a,'S2Size') == N.get(b,'S2Size') == 0
        assert bytes(a[512:768]) == bytes(b[512:768]), name
        assert UI.F.commands(a) == UI.F.commands(b), name
        for model in (a,b):
            UI.F.invoke(model,'X5PublishChr')
        assert a.chr_latches == b.chr_latches, name
        UI.key(a, 1)
        UI.key(b, 1)
        assert (UI.menu_name(b)[0],N.get(b,'PlayerStatus')) == ('MR GIMMICK',0)
        samples.append(name)
    return dict(old_navigation=old, corrected_navigation=new, control_navigation=control,
                exact_OAM_CHR_and_queue_for=samples,
                unchanged_resolvable_names=current_inventory['distinct_named_entries'])


def stage_rows(patched, current_inventory):
    class Track(Ingress.F.ControllerBus):
        def __setitem__(self, at, value):
            if (isinstance(at,int) and at == 0x75b and self[0x771] == 1
                    and self[0x773] == 3 and self[0x0f] == 8):
                self.active_tiers = getattr(self,'active_tiers',set()) | {value}
            return super().__setitem__(at,value)

    original = Ingress.F.ControllerBus
    # Capture the one memory instance built by the established source runner.
    seen = []

    class StageBus(Track):
        def __init__(self, bundle):
            super().__init__(bundle)
            seen.append(self)

    Ingress.F.ControllerBus = StageBus
    try:
        results = []
        rows = [r for r in current_inventory['rows'] if r['slot']==24][:8]
        assert len(rows) == 8 and len({r['name'] for r in rows}) == 8
        for row in rows:
            result = Ingress.stage(patched, row)
            m = seen.pop()
            assert len(seen) == 0
            assert getattr(m,'active_tiers',set()) == {1}
            assert (N.get(m,'S2Health'),N.get(m,'S2Size'),N.get(m,'PlayerStatus'),
                    N.get(m,'PlayerSize')) == (31,0,1,0), row['name']
            result.update(health=31, original_size=0, live_tier=1)
            results.append(result)
            print(json.dumps(dict(event='native_stage',**result),sort_keys=True),flush=True)
        return results
    finally:
        Ingress.F.ControllerBus = original


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,help='Stage only after CPU qualification')
    cli.add_argument('--menu-only',action='store_true')
    args=cli.parse_args()
    parent=NIGHTLY.read_bytes()
    image, record=proposal(parent)
    bundle=Ingress.F.Symbols.bundle()
    old=dict(bundle,raw=parent)
    new=dict(bundle,raw=image)
    existing=inventory(parent)
    evidence=menu(old,new,existing)
    print(json.dumps(dict(event='menu',**evidence),sort_keys=True),flush=True)
    stages=[] if args.menu_only else stage_rows(new,existing)
    if args.output:
        output=args.output.resolve()
        assert not args.menu_only and output==CANDIDATE.parent and not output.exists()
        output.mkdir()
        CANDIDATE.write_bytes(image)
        assert CANDIDATE.read_bytes()==image
    print(json.dumps(dict(passed=True, source_CPU=True, Mesen_run=False,
        outputs_written=int(bool(args.output)), stages=len(stages), record=record),sort_keys=True),flush=True)


if __name__=='__main__':
    main()
