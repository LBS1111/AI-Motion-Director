# AI Motion Director

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An open-source AI motion director for Codex that turns natural-language briefs into motion design plans and videos. It selects suitable tools and skills, then learns reusable patterns from new skills and video references with user approval.

## Apple Soft UI motion showcase

Five short conceptual films show the director's visual language. Each GIF opens the full MP4; [source and production notes](demos/apple-soft-ui/README.md) are included.

[Watch the 20-second showreel](demos/apple-soft-ui/videos/00_Showreel.mp4).

[![AI Motion Director](demos/apple-soft-ui/previews/01_AI-Motion-Director_Intro.gif)](demos/apple-soft-ui/videos/01_AI-Motion-Director_Intro.mp4)

| Brief → Scene | Route |
| --- | --- |
| [![Brief to scene](demos/apple-soft-ui/previews/02_Brief-to-Scene.gif)](demos/apple-soft-ui/videos/02_Brief-to-Scene.mp4) | [![Skill routing](demos/apple-soft-ui/previews/03_Skill-Routing.gif)](demos/apple-soft-ui/videos/03_Skill-Routing.mp4) |

| Direct | Review → Learn |
| --- | --- |
| [![2.5D camera](demos/apple-soft-ui/previews/04_2.5D-Camera.gif)](demos/apple-soft-ui/videos/04_2.5D-Camera.mp4) | [![Reviewed learning](demos/apple-soft-ui/previews/05_Review-and-Learn.gif)](demos/apple-soft-ui/videos/05_Review-and-Learn.mp4) |

## Install for Codex

Run this one command in a terminal to install the skill globally for Codex:

```sh
npx --yes skills add LBS1111/AI-Motion-Director --skill codex-motion-director -g -a codex -y
```

This uses the [Skills CLI](https://github.com/vercel-labs/skills) and requires Node.js/npm. Start a new Codex task after installation; if the skill does not appear, restart Codex. Mention `$codex-motion-director` to invoke it explicitly, or describe a motion project in natural language for automatic selection. Python 3.11+ is needed for the local director tools, and FFmpeg is needed for video extraction and MP4 checks.

## Optional preset skill packs

The director can discover and analyze third-party skills after they are installed. The four reviewed source repositories provide 23 individual skills:

| Source | Skills | Good starting points |
| --- | ---: | --- |
| [Vibe Motion](https://github.com/vibe-motion/skills) | 15 | Product films, logo motion, 3D cameras, Remotion effects |
| [Kinetic Typography](https://github.com/iart-ai/kinetic-typography-skills) | 1 | Animated headlines, staggered text, lyric and title cards |
| [Framer Motion](https://github.com/C-Jeril/framer-motion-skills) | 6 | React UI animation, scroll, gestures, variants and layout |
| [Video Shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 1 | Product films from shot cards, real page captures and sound |

From a checkout of this repository, install all four packs globally for Codex with one command:

```sh
python scripts/install_presets.py
```

Use `--dry-run` to see the commands, or `--only framer-motion` (repeat `--only` for several packs). This installer runs the upstream Skills CLI for each repository; it does not copy their code into this MIT-licensed project. Their source revisions and licenses are recorded in [the preset registry](presets/sources.json). Video and web animation engines still need to be checked for a specific project.

Installing makes each skill available to Codex on the next task. The director's next scan discovers candidates, but its router and permanent memory only gain a new capability after you review and approve the specific analysis. A preset name or repository README alone is not implementation validation.

## Get started

Tell Codex what you want to make or learn:

> Create a 20-second AI product introduction in a minimal, premium style. Show me two concepts first.

> Learn this new motion skill. Explain its tools and capabilities, then let me review what you propose to save.

> Study the card expansion and camera push in this video. Extract reusable motion principles, but do not save them yet.

> Show me what the director has learned and which capabilities have been tested in practice.

The project combines a **Codex skill and local tools**. Codex interprets the brief and makes design decisions. Local scripts handle skill discovery, storage, versioned approval, search, and media checks. There is no background model process or automatic paid service call.

## Project structure

- `SKILL.md`: The entry point for automatic skill selection and the directing workflow.
- `router/`: Capability terms, routing rules, and the first three tool adapters.
- `presets/`: Upstream source, license, revision and skill inventory for optional packs.
- `knowledge/`: Motion physics, easing, camera language, and composition.
- `learning/`: Guides for learning from new skills and video references.
- `references/`: Production, approval, operation, and quality guidance.
- `scripts/`: Local commands, video frame extraction, MP4 verification, and a render example.
- `assets/implementations/`: Original time-based motion functions.
- `tests/`: Checks for approvals, routing, project recovery, concurrent writes, and real media files.

Personal memory and media are stored outside the repository. A local configuration file points to the data directory and is excluded from version control.

## Learning and approval

Discover → analyze → present a specific proposal → get user approval → save → summarize.

Approval and testing are tracked separately. A capability can be **read**, **runnable**, **reproduced**, or **reusable**. Approval means the director may remember it; it does not mean the original tool has run successfully. If the source changes, the director will not silently use an older verified implementation.

External skills can be used through their original tools or adapted from their motion principles to another suitable tool. Frequently used implementations become owned modules only after practical validation, with source and licensing information retained.

## Run and verify

Python 3.11+ is required. PyYAML provides full metadata parsing, and FFmpeg handles media operations. Pillow is used only for the render example and GIF tests. Video engines are checked for each task rather than installed automatically.

```text
python scripts/director.py status
python scripts/director.py scan
python scripts/director.py pending
python scripts/director.py report
python -m unittest discover -s tests -v
```

See the [command guide](references/commands.md) for details. Codex runs the workflow for you, so you do not need to enter these commands yourself.

## V1 scope

- Skill discovery runs when the director starts or resumes; there is no always-on monitor.
- The router provides explainable capability matches, while Codex judges the creative and semantic fit.
- Initial learning proposals do not become confirmed capabilities automatically. Third-party engines have not been installed or tested in bulk.
- The example MP4 verifies the export workflow; it does not guarantee that every external skill can render on the current machine.
- Technical checks cannot replace watching the video and listening to its audio. A project is not marked complete without those reviews.

## License

This project is free and open source under the [MIT License](LICENSE). You may use, modify, distribute, and use it commercially. Keep the copyright notice and license when distributing the project or substantial parts of it.

The license covers the original code and documentation in this repository. External skills, dependencies, assets, and services retain their own licenses and pricing terms.
