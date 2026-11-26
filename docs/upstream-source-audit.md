# Upstream Repository and License Audit

Audit date: 2026-11-26. This is a source-reuse gate for LYRA AI Studio; no upstream repository was modified.

## Pinned references

| Repository | Audited revision | Root license file | LYRA reuse decision |
|---|---|---|---|
| [Forget-C/Jellyfish](https://github.com/Forget-C/Jellyfish) | `ddafcf997d7d50f48051972003aedcaa5ff29d83` | Apache-2.0 | Architecture and workflow patterns may be studied. If source code is copied, preserve license text, notices, and mark modified files. Do not import its full infrastructure stack into LYRA. |
| [Chamanrajragu/purffle-shorts](https://github.com/Chamanrajragu/purffle-shorts) | `514fd2547227b98d951dfc1489fc8c7ce72f1b68` | MIT | Suitable reference for script/hook evaluation and FFmpeg workflow patterns. Any copied code must retain the MIT copyright and permission notice. Prefer independent implementation of required contracts. |
| [charliewwdev/OpenMontage](https://github.com/charliewwdev/OpenMontage) | `481aeca47491b095274bb93ad96b9e82d1b8a19e` | AGPL-3.0 | Do not copy, port, or link its implementation into LYRA in this phase. Use high-level workflow concepts only. Any future reuse requires a separate AGPL compatibility and network-source obligation review. |
| [seme-org/open-director](https://github.com/seme-org/open-director) | `16922ab34c905b6c2983fbb844fc62c9cc3ed2c9` | LGPL-3.0 | Use orchestration concepts only for now. Do not copy library code until the exact linking/distribution model and LGPL obligations are reviewed. |

The revisions above are the latest commits returned by the repository commit search at audit time. They are recorded as reproducible reference points, not as a guarantee that every nested dependency or asset is licensed under the root license.

## Mandatory secondary checks before importing any asset or model

- Inspect each repository's `NOTICE`, dependency manifests, submodules, model cards, and asset directories.
- Verify each model checkpoint, LoRA, dataset, font, sound effect, sample video, and image has its own explicit license and permitted-use terms.
- Do not assume an open-source code license grants rights to model weights, training data, or demo media.
- Pin exact revisions and record checksums for downloaded weights/assets.
- Keep upstream code isolated behind LYRA adapters; do not copy full application stacks or their infrastructure assumptions.

## Selected architecture direction

- Reuse the useful functional ideas from Jellyfish and Purffle through LYRA-native interfaces.
- Build story intelligence, continuity contracts, orchestration, and provider adapters inside LYRA rather than importing full stacks.
- Keep OpenMontage and OpenDirector as non-code architectural references unless a future license review explicitly approves a different use.
- Keep all image/video engines optional. A provider must declare its compute requirements, network use, model/license terms, and real cost before it can be enabled.

## Current decision

Phase 0 source pinning and root-license screening is complete for these four repositories. Secondary asset/model/dependency checks remain a mandatory gate before any specific upstream code, model, or media is imported.
