# AI Motion Director

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An open-source AI motion director for Codex that turns natural-language briefs into motion design plans and videos. It selects suitable tools and skills, then learns reusable patterns from new skills and video references with user approval.

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
