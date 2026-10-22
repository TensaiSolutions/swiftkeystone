# Acknowledgements and provenance

iOS Forge is inspired by [Nightforge](https://github.com/jfreal/nightforge), especially the separation
of shared workflows, adapters, project configuration, and operational memory. Nightforge is published
under the [Unlicense](https://github.com/jfreal/nightforge/blob/main/LICENSE).
This release contains original workflow instructions and helper code; no Nightforge implementation is vendored.

[Paul Hudson's Swift Agent Skills directory](https://github.com/twostraws/Swift-Agent-Skills)
provided the starting point for identifying specialist skills. The directory's license does not license
every linked project. Candidate projects and reported licenses are recorded in `upstream/registry.json`;
none is distributed or installed by this package. Reported license labels are not a completed dependency audit.

Relevant Codex guidance:

- [Skills for repeatable maintenance](https://developers.openai.com/blog/skills-agents-sdk)
- [Focused skills and project instructions](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)

Before vendoring future dependencies, preserve their license notices and document the exact upstream
revision, inspected files, compatibility findings, and any local changes.
