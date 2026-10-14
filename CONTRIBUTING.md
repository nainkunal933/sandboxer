# Contributing to Sandboxer

## Automated native builds

The **Test builds** workflow checks all four native builds on PR updates. The
**Build executables** workflow runs on pushes to `main` and publishes releases
after all builds succeed. Both workflows upload an archive containing the
executable, the README, and the license:

| Artifact | Target |
| --- | --- |
| `sandboxer-linux-x86_64` | Linux x86_64, glibc 2.35 or newer (Ubuntu 22.04 baseline) |
| `sandboxer-windows-x86_64` | Windows x86_64 |
| `sandboxer-macos-arm64` | macOS 15 or newer, Apple Silicon |
| `sandboxer-macos-x86_64` | macOS 15 or newer, Intel |

Download an artifact from a successful workflow run and extract both the
GitHub artifact wrapper and the archive inside it. Windows uses ZIP; Linux
and macOS use tar.gz to retain executable permissions. These are portable
executables, not OS installer packages. Workflow artifacts expire after 30 days.

## Releases

Before merging a PR, apply a release label:

| Label | Version bump |
| --- | --- |
| `release:patch` | Bug fixes |
| `release:minor` | New features |
| `release:major` | Breaking changes |

Unlabeled PRs default to patch. When multiple unreleased PRs are included, the
largest bump wins. After all builds succeed on `main`, CI creates the Git tag and
release automatically. Download binaries from **GitHub Releases**.
