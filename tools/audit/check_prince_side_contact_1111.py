"""Trace native live-enemy side contact and compare the original ROM's defender."""

from collections import Counter
from unittest.mock import patch

import check_prince_flagpole_route_1110 as Route
import prince_original_cpu_1101_v1 as Original


PIN = '4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc'
C, N, F, Combined = Route.C, Route.N, Route.F, Route.Combined
Late, I = Route.Late, Route.Combined.I
DEFENDER = (2, 0xdadd)
ORIGINAL_DEFENDER = 0xacec
HP = 0x6cf
ACTION = 0x616
SWORD = 0x6ee


def donor_defense(state, regs, sword):
    cpu = Original.machine()
    model = cpu.memory
    model.switch(4)
    list.__setitem__(model, slice(0, 0x800), state)
    model[SWORD] = sword
    a, x, y, p = regs
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 0xfd
    cpu.stPushWord(0x5ffe)
    cpu.pc = ORIGINAL_DEFENDER
    debits = []

    def observe(c):
        if model.bank == 5 and c.pc == 0x8725 and c.x == 0:
            assert bytes(model[c.pc:c.pc+3]) == bytes.fromhex('9dcf06')
            debits.append([c.pc, model[HP], c.a])

    Original.until(cpu, 0x5fff, sp=0xfd, limit=20000, trace=observe)
    return bytes(model[:0x800]), debits


def side_contact(context, first, enemy_id, expected_dy):
    env, seed, labels = context
    model = Combined.Q.Sonic.slim_fork(seed)
    watch = {(3, 0xbd22): 'PrinceNativeContact', DEFENDER: 'OriginalDefender'}
    for name in ('GuestBodyContactBridge', 'ChkForPlayerInjury', 'ChkETmrs',
                 'InjurePlayer', 'EnemyStomped'):
        tag = ((I.location(model.bundle, name) - 16) // 8192) | 128
        watch[tag, I.address(model.bundle, name)] = name

    tick = first
    entries = []
    debits = []
    snapshots = []
    timers = ('StompTimer', 'InjuryTimer', 'StarInvincibleTimer',
              'GuestHurtKind', 'GuestHurtTicks', 'GuestInvulTicks')
    native = N.NesMPU

    class Trace(native):
        def step(self):
            if self.memory is not model:
                return super().step()
            bank = model.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else -1
            point = bank, self.pc
            state = model.ram[2]
            old_hp = state[HP]
            if point in watch:
                entries.append(dict(tick=tick, name=watch[point], bank=bank, pc=self.pc))
            if point == DEFENDER:
                sp = self.sp
                resume = ((model[0x101 + sp] | model[0x102 + sp] << 8) + 1) & 65535
                row = F.sample(model, tick)
                slot = N.get(model, 'ObjectOffset')
                actor = next(actor for actor in row['actors'] if actor['slot'] == slot)
                camera = row['camera_left']

                def box(at):
                    return [v + (camera if i in (0, 2) else 0)
                            for i, v in enumerate(model[at:at+4])]

                snapshots.append(dict(resume=(resume, sp+2), before=bytes(state[:0x800]),
                    regs=(self.a,self.x,self.y,self.p), actor=actor, player_box=box(0x658),
                    enemy_box=box(0x65c + slot*4), dy=N.get(model, 'Player_Y_Speed'),
                    prior_sole=state[0x14b1] + 256 * state[0x14a6],
                    current_sole=int.from_bytes(state[0x84:0x86], 'little'),
                    timers={name:N.get(model, name) for name in timers},
                    player={k:row[k] for k in ('x','y','action','frame','mode','hp','lives')}))
            if snapshots and (self.pc, self.sp) == snapshots[-1]['resume']:
                snapshots[-1]['after'] = bytes(state[:0x800])
            result = super().step()
            if state[HP] != old_hp:
                debits.append([bank, point[1], old_hp, state[HP]])
            return result

    with patch.object(N, 'NesMPU', Trace):
        for tick in range(first, first+220):
            C.Route.controls(env, model, labels, 1)
            N.consume(model)
            if not model.ram[2][HP]:
                break
    hit, = snapshots
    before, after = hit.pop('before'), hit.pop('after')
    regs = hit.pop('regs')
    hit.pop('resume')
    actor, player = hit['actor'], hit['player']
    assert actor['id'] == enemy_id and actor['state'] == 0, hit
    assert player['y'] == 176 and actor['y'] == 184 and hit['dy'] == expected_dy, hit
    assert all(value == 0 for value in hit['timers'].values()), hit
    assert before[SWORD] == 0 and (before[HP],after[HP],after[ACTION]) == (4,0,85)
    player_left, player_top, player_right, player_bottom = hit['player_box']
    enemy_left, enemy_top, enemy_right, enemy_bottom = hit['enemy_box']
    assert player_left < enemy_left <= player_right < enemy_right
    assert player_top <= enemy_bottom and enemy_top <= player_bottom
    assert hit['prior_sole'] >= enemy_top, hit
    calls = [event for event in entries if event['tick'] == tick]
    seen = Counter(event['name'] for event in calls)
    assert seen['InjurePlayer'] == seen['PrinceNativeContact'] == seen['OriginalDefender'] == 1
    assert not seen['EnemyStomped']
    assert debits == [[3,0xa342,hp,hp-1] for hp in range(4,0,-1)], debits

    source = []
    for sword, hp, action in ((0,0,85),(1,0,85),(2,3,74)):
        original, original_debits = donor_defense(before, regs, sword)
        assert (original[HP], original[ACTION]) == (hp,action), (original[HP], original[ACTION])
        assert [row[1:] for row in original_debits] == [[i,i-1] for i in range(4,hp,-1)]
        if sword == 0:
            assert original[0x60e:0x61c] == after[0x60e:0x61c]
            assert original[HP] == after[HP]
        source.append(dict(sword=sword, hp_before=before[HP], hp_after=hp,
                           action=action, debit_instructions=original_debits))
    return dict(epoch=tick, **hit, native_calls=calls, translated_HP_writes=debits,
                original_defender=[4,ORIGINAL_DEFENDER], original_variants=source)


def main():
    raw = Combined.Stage.NIGHTLY.read_bytes()
    assert Combined.Q.digest(raw) == PIN
    image = C.Start.W.bundle(raw)
    result = None, image, None, {'in_memory_SHA256':PIN}, None, None, None
    route, _, context = Combined.first_gap(result)
    late = Late.second_gap(context, route['first_gap']['epoch'], True, request_min=1328)
    assert (late['outcome'],late['terminal']['epoch'],late['terminal']['x']) == ('second-far-ground',1244,1440)
    goomba = side_contact(context, 1244, 6, expected_dy=0)
    pair, model = Late.retreat_pair(context,1244,settle=True,standing_reverse=True,back_up=True)
    assert (pair['outcome'],pair['terminal']['epoch'],pair['terminal']['x']) == ('pair-native-falls-and-return',1760,1441)
    context = context[0], model, context[2]
    row = Late.run_past_pair(context,1760)
    assert (row['epoch'],row['x'],row['hp'],row['lives']) == (1856,1547,4,2)
    koopa = side_contact(context, row['epoch'], 0, expected_dy=254)
    Combined.emit('PRINCE_SIDE_CONTACT_1111', dict(installed_SHA256=PIN,
        original_SHA256=Original.SHA, encounters=[goomba,koopa],
        translated_third_pipe_scene=True, natural_native_actors=True, ROM_written=False))


if __name__ == '__main__':
    main()
