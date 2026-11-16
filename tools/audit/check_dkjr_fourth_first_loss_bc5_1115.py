"""Read-only eight-witness first support loss from the genuine currentbc5 prefix."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json

import check_dkjr_public_fourth_carried_bc5_1115 as Route

F, Cold = Route.F, Route.Cold
B, N = Cold.B, Cold.N


def main():
    raw = F.Prior.Early.Old.NIGHTLY.read_bytes()
    reference, binding = F.Prior.normalize(raw, kind=F.Prior.KIND)
    _, payload = F.Prior.Early.Old.identity(reference)
    text = Route.source_controller(raw)
    opening, memory = Cold.first_active_cold(raw)
    source_writers = {0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d6bc0')}
    origin_writers = {0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d76c0')}
    assert len(origin_writers) == 3
    witnesses = {}
    counts = dict(motor_entries=0, motor_returns=0, post_carry_returns=0, support_queries=0,
                  wall_queries=0, helper_plane_candidates=0, actual_944_positions=0)
    pending = {}
    tick = 0
    captured_motor = None
    carried_slot = None

    def slot944():
        return next((slot for slot in range(6) if N.get(memory, 'Enemy_Flag', slot)
                     and N.get(memory, 'Enemy_ID', slot) == 37
                     and N.get(memory, 'Enemy_X_Position', slot)+256*N.get(memory, 'Enemy_PageLoc', slot) == 944), None)

    def rects(offset):
        result = []
        for at in range(offset, offset+16, 4):
            if memory.ram[2][at] == 255:break
            result.append(list(memory.ram[2][at:at+4]))
        return result

    def view(cpu, kind):
        s = memory.ram[2]
        slot = carried_slot if carried_slot is not None else slot944()
        helper = None
        if slot is not None:
            at = 0x65c+4*slot
            helper = dict(slot=slot, flag=N.get(memory, 'Enemy_Flag', slot), id=N.get(memory, 'Enemy_ID', slot),
                          x=N.get(memory, 'Enemy_X_Position', slot)+256*N.get(memory, 'Enemy_PageLoc', slot),
                          raw_y=N.get(memory, 'Enemy_Y_Position', slot), vy=N.get(memory, 'Enemy_Y_Speed', slot),
                          passenger=N.get(memory, 'PlatformCollisionFlag', slot), bbox=list(memory[at:at+4]))
        return dict(kind=kind, tick=tick, motor_entries=counts['motor_entries'], PC=cpu.pc,
                    bank=memory.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc >= 0x8000 else -1,
                    A=cpu.a, X=cpu.x, Y=cpu.y, P=cpu.p, SP=cpu.sp, **B.state(memory),
                    prior=s[0x6c], origin=s[0x76], limit=s[0x7b], original_fraction_x=s[0x56],
                    source_direction=s[0x54], source_facing=s[0x6d], native_direction=memory[0x45],
                    native_x_speed=memory[0x46], saved=memory[0xdc], controller=memory.controller_pad,
                    bbox=list(memory[0x658:0x65c]), helper=helper,
                    kind_query=s[0x8db], original_query=list(s[0x3e:0x42]),
                    contact_rect=list(s[0x42:0x46]), support_rects=rects(0x800), wall_rects=rects(0x880),
                    world_window=list(s[0x8e8:0x8ec]), candidate_rect=list(s[0x8e4:0x8e8]),
                    WCount=s[0x8dd], WObject=s[0x8f0], source_screen=list(s[0x8ed:0x8ef]),
                    source_delta=list(s[0x8f1:0x8f3]))

    def token(cpu):
        return ((memory[0x100+((cpu.sp+1)&255)]+256*memory[0x100+((cpu.sp+2)&255)]+1)&65535,
                (cpu.sp+2)&255)

    Base = type(memory)
    class Writes(Base):
        def __setitem__(self, at, value):
            if ('first_carry' in witnesses and isinstance(at, int) and at == 0x75
                    and 'first_native_x_decrease' not in witnesses and value < self[at]
                    and self[at]-value < 8):
                cpu = getattr(self, 'loss_cpu', None)
                if cpu is not None:
                    row = view(cpu, 'first-native-X-decrease-before-store')
                    row.update(old_low=self[at], new_low=value)
                    witnesses['first_native_x_decrease'] = row
            return super().__setitem__(at, value)
    memory.__class__ = Writes

    def observe(m, cpu):
        nonlocal carried_slot, captured_motor
        pc = cpu.pc
        tag = m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
        if 'first_carry' in witnesses:
            m.loss_cpu = cpu
        for key in tuple(pending):
            q = pending[key]
            if q['token'] == (pc, cpu.sp):
                del pending[key]
                if key == 'motor':
                    counts['motor_returns'] += 1
                    if 'first_carry' in witnesses:counts['post_carry_returns'] += 1
                elif key in ('support', 'wall'):
                    row = witnesses[key+'_probe']
                    row['return'] = dict(PC=pc, SP=cpu.sp, A=cpu.a, P=cpu.p,
                                         original_query=list(m.ram[2][0x3e:0x42]),
                                         contact_rect=list(m.ram[2][0x42:0x46]),
                                         source=m.ram[2][0x6b], sourceY=m.ram[2][0x210],
                                         support_rects=rects(0x800), wall_rects=rects(0x880))
                elif key == 'plane':
                    row = witnesses['first_helper_plane']
                    row['return'] = dict(PC=pc, SP=cpu.sp, WCount=m.ram[2][0x8dd],
                                         appended=m.ram[2][0x8dd]>row['entry']['WCount'])
        if (tag, pc) == (2, 0xd65e):
            counts['motor_entries'] += 1
            pending['motor'] = dict(token=token(cpu))
            if 'first_carry' in witnesses and 'first_motor_entry' not in witnesses:
                captured_motor = counts['motor_entries']
                witnesses['first_motor_entry'] = view(cpu, 'first-D65E-entry-after-carry')
        if (tag, pc) == (199, 0xac29):
            slot = cpu.x
            if slot < 6 and N.get(m, 'Enemy_ID', slot) == 37 and slot944() == slot:
                counts['actual_944_positions'] += 1
                if 'first_carry' not in witnesses:
                    carried_slot = slot
                    witnesses['first_carry'] = view(cpu, 'first-actual-944-position')
        if 'first_carry' not in witnesses or tag != 3:return
        if pc in (0xb065, 0xb061):
            kind = 'support' if pc == 0xb065 else 'wall'
            counts[kind+'_queries'] += 1
            if kind+'_probe' not in witnesses:
                witnesses[kind+'_probe'] = dict(entry=view(cpu, 'first-'+kind+'-probe'))
                pending[kind] = dict(token=token(cpu))
        if pc == 0xb5c8 and m.ram[2][0x8f0] == carried_slot and m.ram[2][0x8db] >= 3:
            counts['helper_plane_candidates'] += 1
            if 'first_helper_plane' not in witnesses:
                row = view(cpu, 'first-944-AppendPlatformY')
                left, right, top, bottom = m.ram[2][0x8e8:0x8ec]
                actor_left, actor_right = m.ram[2][0x8e4], m.ram[2][0x8e6]
                row['actual_plane_Y'] = cpu.a
                row['horizontal_overlap'] = actor_right >= left and right >= actor_left
                row['vertical_overlap'] = cpu.a >= top and cpu.a <= bottom
                witnesses['first_helper_plane'] = dict(entry=row)
                pending['plane'] = dict(token=token(cpu))
        if pc in source_writers and cpu.a == 4 and m.ram[2][0x6b] != 4 and 'first_source4_writer' not in witnesses:
            witnesses['first_source4_writer'] = view(cpu, 'first-source4-before-store')
        if pc in origin_writers and 'first_source4_writer' in witnesses and 'first_origin_writer' not in witnesses:
            witnesses['first_origin_writer'] = view(cpu, 'first-origin-before-store')
        assert len(witnesses) <= 8

    class Complete(Exception):pass
    def after(m):
        nonlocal tick
        tick += 1
        if tick % 1000 == 0:
            print('DKJR_FIRST_LOSS_PROGRESS '+json.dumps(dict(tick=tick, **B.state(m))), file=output, flush=True)
        if (captured_motor is not None and counts['post_carry_returns'] >= 4
                and 'first_source4_writer' in witnesses and 'first_origin_writer' in witnesses):
            raise Complete()
    output = __import__('sys').stdout
    result = None
    with redirect_stdout(io.StringIO()):
        try:
            result = B.route(memory, raw, 4500, controller_text=text, observe_extra=observe, after_frame=after)
        except Complete:
            pass
    report = dict(source_diagnostic_complete='first_origin_writer' in witnesses, binding=binding,
                  frozen_control_Lua='ed3e7206e7e2cd29f403048d4816de5c01f58768b53113eba5021f24ade6d4b1',
                  opening=opening, counts=counts, witnesses=witnesses, final=B.state(memory),
                  source_updates=tick, source_route_pass_claim=False, native_claim=False,
                  output_files=0, game_or_control_changes=False,
                  route_stopped_before_probe=result['stopped'] if result else False)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_FOURTH_FIRST_LOSS '+encoded, flush=True)
    print('DKJR_FOURTH_FIRST_LOSS_SHA256 '+sha256(encoded.encode()).hexdigest(), flush=True)
    assert report['source_diagnostic_complete']


if __name__ == '__main__':main()
