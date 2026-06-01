# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This is a **greenfield repository**. As of this writing it contains only `README.md` — there is no source code, build system, dependency manifest, or test suite yet. Any commands, frameworks, or directory structure described below should be *established* by the first implementation work, not assumed to already exist.

When you add the first real code, update this file with the actual build/lint/test commands and architecture so future sessions don't have to rediscover them.

## Project vision (from README)

**420BloomTools** — "The Automagic Gardener": a toolkit for hobbyists and DIY enthusiasts that bridges hardware (IoT devices) with code for real-world applications.

Two focus areas:

1. **Microgreen Monitor** — code and setup to monitor and automate care for indoor plants using low-cost Arduino or Raspberry Pi sensors.
2. **Wax-on, Wax-Off Automations** — gamified daily-chore automation: watering reminders, calendar-based tasks, and timers.

The IoT/sensor focus means implementation will likely span embedded device code (Arduino/Raspberry Pi) and host-side tooling. Keep hardware-facing code separate from host/application code as the structure grows.

## Conventions

- Default development branch for AI-assisted work: `claude/...` feature branches. Do not push to `main` without explicit permission.
- The repository name is `420BloomTools` (GitHub remote: `late-bloomer420/420bloomtools`). "420Bloom" refers to plant cultivation/bloom monitoring — keep that domain framing in mind for naming.
