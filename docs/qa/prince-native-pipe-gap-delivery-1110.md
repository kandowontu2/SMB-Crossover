# Prince of Persia’s pipe and gap traversal

Select Prince of Persia by highlighting **Excitebike** in row 4, column 6 and
pressing **Select** once. The tested candidate is
`47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b`.
The candidate was copied directly to the Downloads nightly, where both replays
repeated with identical receipts. The before and after patch guards were clean.
The 2,099,510-byte IPS has SHA-256
`92527edf832ecb5349c3c3bfc568914a7fae3e746c5dc9982886b296ea9821cb`
and reconstructs the tested Downloads ROM.
The source is pushed at `fc65fcba`. GitHub’s Latest release is `Current` and
holds sole IPS asset `732894985`. The downloaded patch reconstructs the
tested Downloads ROM byte for byte.

Prince keeps his original running jump, ledge hang and climb. The updated
terrain bridge keeps his original careful step attached to the fourth pipe
when the animation moves his physical foot briefly below its logical support
point. In Mesen, the actual support writer at `D74B` published the native
surface Y144 five times during the approach. At X903 and X909, the physical
foot was 147. Prince finished the step at X928/Y112 with both feet on the pipe.

The replay starts at the title, selects Prince, and uses controller input
throughout. It confirms the complete Prince cookies in both mapped RAM banks
and observes the original movement and rendering calls. No health, actor,
position, terrain or timing state is written by the replay.

| Stage witness | Original updates | World X/Y | HP |
| --- | ---: | --- | ---: |
| First running-jump input | 118 | 206/176 | 5 |
| First pipe far side | 509 | 563/176 | 5 |
| Second pipe native top | 677 | 609/128 | 5 |
| Third pipe, both feet supported | 1077 | 752/112 | 5 |
| Fourth pipe, both feet supported | 1677 | 928/112 | 4 |
| First gap far side | 1885 | 1175/176 | 4 |
| Second gap far side | 2033 | 1461/176 | 4 |

Both lives remain. The only health debit is the original hard fall from the
third pipe at X846. The first gap has two empty columns from X1104 to X1135.
The second has three from X1376 to X1423. In both cases the replay observes
original running action 4 and finishes on native floor beyond the gap.
The four pipes and two gaps are authored 1-1 terrain. Prince uses zero helper
platforms. The later enemies, third gap, flag, and natural pickup sequence
remain to be qualified. The route recorded 2,015 frames without an original
update out of 4,048 gameplay frames.

The first Goomba forced a timing adjustment in the controller. Requests with
observed gaps of 78, 110 and 146 all entered original action 4 but arrived
too low. The passing replay requests A at gap134. At the second pipe, braking
earlier settled Prince at X572 and his Up input stalled against the pipe.
Braking once he reached X577 let him settle at X582 and enter his original
ledge hang. Those controller changes leave the ROM and authored stage intact.

| Physical Mesen replay | Controller SHA-256 | Receipt SHA-256 |
| --- | --- | --- |
| Prince through two gaps | `e9b45ae96c00ee55b456200f346ab2e4f22c78013a0820e98910ecddcc6dc65e` | `07216d828e974a8dead673eed93021fb10873bd53b5c562b7ed8bb46dcd78b95` |
| Sonic full 1-1 to active underground 1-2 | `2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee` | `410dd288da42744b8c300bf3be2a45bd752e7e1d2dee7e8cf5abab1f46478993` |

Sonic’s replay retains the same 1,423 original updates, 17 jumps, both lives
and final active 1-2 position as the preceding nightly. The Prince composition
changes 14,244 bytes within the existing 45 Prince CHR carrier pages and
the existing 16-byte owner cookie. All 100 names remain available. The
reconstruction keeps the shared Sonic transport and all previous owner code
outside those spans byte exact. [Transport qualification](prince-sonic-transport-1110.md)

The candidate occupies a single ROM slot. Mesen printed compact receipts to
stdout. No captures, backups or per-frame logs were generated. The other
roster members’ helper placements are recorded separately. [Helper inventory](helper-platform-inventory-1101.md)
