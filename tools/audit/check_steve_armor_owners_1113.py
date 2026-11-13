"""Actual menu/Start cache transitions for the private Steve armor packet."""

import argparse
import json
from unittest.mock import patch

import audit_current_roster_powerups_1110 as Roster
import check_roster_powerup_continuation_1110 as Frames
import steve_armor_live_1113 as Live
import steve_armor_packet_1113 as Packet


ROWS = {
    'Steve': dict(name='STEVE HERMANN',slot=15,cycle=2,raw=16),
    'Jay': dict(name='JAY MCCRAY',slot=15,cycle=1,raw=16),
    'Mike': dict(name='MIKE JONES',slot=15,cycle=0,raw=16),
    'Quick': dict(name='QUICK MAN',slot=9,cycle=2,raw=9),
    'Excitebike': dict(name='EXCITEBIKE',slot=29,cycle=0,raw=37),
}


def check(raw, *, names=('Quick','Jay'),fast_order=False):
    if fast_order:
        with patch.object(Live,'order_blocks',lambda rows:rows):
            candidate, info = Live.proposal(raw)
    else:
        candidate, info = Live.proposal(raw)
    bundle = Roster.W.Symbols.bundle()
    bundle['raw'] = candidate
    N = Roster.N
    opened = {}

    def cold(name, cache=None):
        original_seed = Roster.Starts.UI.seed
        base_cpu = N.NesMPU
        written = set()
        raw1_writes = 0
        armor_entries = 0

        class ObservedCPU(base_cpu):
            def step(self):
                nonlocal raw1_writes,armor_entries
                model = self.memory
                if model.rawtags[1] == 1 and self.pc == 0xa000 and N.get(model,'SelectedCharacter') == 16 and model[0x730b]&0x60 == 0x40:
                    armor_entries += 1
                    assert bytes(model.ram[1][:len(info['runtime']['images']['STEVE_ARMOR_RUNTIME'])]) == info['runtime']['images']['STEVE_ARMOR_RUNTIME']
                    assert all(bytes(model.ram[bank][0x1fe0:0x1ff0]) == info['cookie']
                               for bank in (1,2,3))
                before = len(self.memory.ram_writes)
                result = super().step()
                updates = self.memory.ram_writes[before:]
                written.update((bank,offset) for bank,offset,_ in updates if bank in (1,2,3))
                if any(bank == 1 and offset < 2048 for bank,offset,_ in updates):
                    raw1_writes += 1
                    if all(bytes(model.ram[bank][0x1fe0:0x1ff0]) == info['cookie']
                           for bank in (1,2,3)):
                        assert bytes(model.ram[1][:len(info['runtime']['images']['STEVE_ARMOR_RUNTIME'])]) == info['runtime']['images']['STEVE_ARMOR_RUNTIME']
                return result

        def cached_seed(*args,**kwargs):
            memory = original_seed(*args,**kwargs)
            if cache is not None:
                # Explicit cache-survival fixture. Menu selection, Start,
                # native scene ownership and the constructor still execute.
                for bank in (1,2,3):
                    memory.ram[bank][:] = cache.ram[bank]
            return memory

        with patch.object(Roster.Starts.UI,'seed',cached_seed), patch.object(N,'NesMPU',ObservedCPU):
            opening, memory = Roster.cold(bundle,ROWS[name])
        assert opening['passed'] and opening['moved_right'], (name,opening)
        memory._armor_written = written
        memory._armor_entries = armor_entries
        memory._raw1_writes = raw1_writes
        return opening,memory

    for name in ('Steve',*names):
        opened[name] = cold(name)
        print(json.dumps(dict(event='cold_opening',name=name,
                              opening=opened[name][0]),sort_keys=True),flush=True)

    transitions = []
    for foreign in names:
        for source,target in ((foreign,'Steve'),('Steve',foreign)):
            opening, memory = cold(target,opened[source][1])
            fresh = opened[target][1]
            # Compare every byte written by the fresh owner's real menu,
            # constructor and opening. Padding outside those writes belongs
            # to neither the executable admission nor the new owner.
            different = [(bank,offset,memory.ram[bank][offset],fresh.ram[bank][offset])
                         for bank,offset in sorted(fresh._armor_written)
                         if memory.ram[bank][offset] != fresh.ram[bank][offset]]
            assert not different, (source,target,different[:12])
            if target == 'Steve':
                assert bytes(memory.ram[1][0x1fe0:0x1ff0]) == info['cookie']
            # Exercise the actual mounted conditional movement code beyond
            # the constructor, with the same controller sequence in both.
            for pad in (0,1,1,129,129,0,2,2,64,0):
                for model in (memory,fresh):
                    model.controller_pad = pad
                    Frames.frame(model,None)
                fields = ('SelectedCharacter','Player_X_Position','Player_PageLoc',
                          'Player_Y_Position','Player_Y_HighPos','Player_State',
                          'GameEngineSubroutine','NumberofLives')
                assert tuple(N.get(memory,name) for name in fields) == tuple(
                    N.get(fresh,name) for name in fields), (source,target,pad)
            transitions.append(dict(source=source,target=target,
                                    active_opening=opening,ordinary_followup_updates=10,
                                    compared_written_bytes=len(fresh._armor_written),
                                    raw1_writes=memory._raw1_writes,
                                    authenticated_armor_entries=memory._armor_entries,
                                    restored_owner_parity=True))
            # Follow-up controls consumed the fresh reference. Restore it
            # through the actual cold/menu path for the next transition.
            opened[target] = cold(target)
    return dict(parent=Packet.Entry.digest(raw),candidate=Packet.Entry.digest(candidate),
                transitions=transitions,output_files=0,release_qualified=False,
                packet_order_optimized=not fast_order,
                fixture_scope='Only old raw1/raw2/raw3 cache contents are transplanted into a fresh native menu fixture. Actual Select, Start, constructor and ordinary frames execute.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owners',nargs='+',choices=tuple(ROWS),default=['Quick','Jay'])
    parser.add_argument('--fast-order',action='store_true')
    parser.add_argument('--before-quick',action='store_true')
    args = parser.parse_args()
    print(json.dumps(check(Packet.qualification_parent(before_quick=args.before_quick),names=tuple(args.owners),fast_order=args.fast_order),
                     sort_keys=True),flush=True)
