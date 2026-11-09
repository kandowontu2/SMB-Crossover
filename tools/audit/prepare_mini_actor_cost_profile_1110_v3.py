"""Record per-actor costs inside one naturally reached gameplay update."""
import prepare_mini_actor_profile_1110_v2 as actors
from pathlib import Path


def prepare(output, rom, source, refs, **kwargs):
    replacements = {
        'local foregroundCounts, interruptCounts, sampleISR = {}, {}, {}':
        'local foregroundCounts, interruptCounts, sampleISR = {}, {}, {}\nlocal sampledCalls = {}',
        'context.name, context.phase = name, phase':
        "context.name, context.phase = name, phase\n  context.actor_slot=read(0x0d)",
        'row.max = math.max(row.max, elapsed)':
        """row.max = math.max(row.max, elapsed)
  if instructionSample and call.name ~= 'GameLoop' then
   sampledCalls[#sampledCalls+1]={name=call.name,slot=call.actor_slot,
    foreground=cpu,gross=elapsed,caller=call.ret}
  end""",
        'hardware_interrupt_cycles=hardwareInterruptCycles,':
        'hardware_interrupt_cycles=hardwareInterruptCycles,sampled_calls=sampledCalls,',
    }
    for before, after in replacements.items():
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    actors.with_actors(output, rom, source, {*refs, Path(__file__)}, **kwargs)


if __name__ == '__main__':
    actors.profile.prepare = prepare
    actors.profile.main()
