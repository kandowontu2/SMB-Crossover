# Jay McCray stock gun nightly

Select once on Mike Jones to choose Jay McCray. The nightly includes the
original Silius movement adapter and stock projectile. The projectile uses
the original graphics and advances four world pixels per update.

The candidate and the Downloads launch both passed the same controller-only
Mesen replay. Starting from the cold title and choosing Jay, the replay held
B once. It observed 50 distinct live projectile positions, from X56/Y191
through X252/Y191, followed by offscreen retirement. All 25 live physical
draws reached hardware OAM with the exact native DMA cell. The mapper
published Jay's CHR page 33 times. Jay retained both lives with no Mike
projectiles created.

The [CPU verification](jay-silius-stock-draw-dispatch-1111.md) covers
authenticated dispatch, cold readback, both interrupt paths and Mike and
Steve behavior. The [directed impact replay](jay-silius-stock-hit-draw-1111.md)
demonstrates native enemy defeat after parsing an authored Goomba. A
continuous Jay 1-1 clear, an organically reached enemy impact in Mesen,
and the alternate Silius weapons still need verification or integration.

The installed image repeated the previous Sonic ring route and Donkey
Kong Jr. four-pipe and second-gap route after normalizing the ROM hashes.
The Downloads patch guard passed before and after direct replacement. No
backup, save state, or capture was retained.

- Parent ROM SHA-256 `8c1ebb1bfbe21499461c5fd65ea75b784460ac2cb81a712a9db9941aa7cec711`
- Delivered ROM SHA-256 `6cb828b3c97bd287f5fb3421e01a478319bf3615e5f2eeed8a6b7888b15c9657`
- Reconstructed IPS SHA-256 `ae8d1671f8ddf94071acc64c1383814ffd834434a5c8e78db91e0f8eb72c0367`
- Jay candidate and Downloads receipt `6f7fda7b8db4ecb414bc9b6387d5330bcffdb6e00bf591dbd29eb49c1cd46701`
- Jay controller Lua SHA-256 `0a8ec015f54c6b58bd86c8c3935b53fb264934d2ed2e5a5a8bf3335f822ba821`
- Sonic Downloads regression `85b2c3d813515023fa07979e446c7e5fe37ecbc7d8b9a72609c1f17447a66cf3`
- Donkey Kong Jr. Downloads regression `2b7864d53db3649aa1523c1b15f3a28fa948706d9f8f7a006abe1787f21b5032`
