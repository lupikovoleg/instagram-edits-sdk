# Documentation design

The site takes visual cues from Instagram while presenting an independent SDK:
white surfaces, near-black typography, rounded code panels, and restrained
purple/pink/orange gradient accents. The SDK's code-bracket symbol is original.

- Direction reference: [Instagram's brand system](https://www.meta.com/design-at-meta/blog/the-new-instagram-brand-identity/).
- Body and display type: Onest, including Cyrillic, under the bundled SIL OFL.
  This is an open font choice, not Instagram Sans.
- Code type: IBM Plex Mono, under the bundled SIL OFL.
- All font files are served locally. `assets/fonts/provenance.json` records
  upstream sources and SHA-256 hashes; each font's license is beside it.
- Authorship is shown on both homepages and in every page footer, including
  Swagger. The project's MIT license credits Oleg Lupikov and contributors.

Run `python tools/build_site.py` in the docs environment, then
`python tools/check_site.py` and `python tools/check_release.py`.
The build only writes a local preview and does not publish it.
