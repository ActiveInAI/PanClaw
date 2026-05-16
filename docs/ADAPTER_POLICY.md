# Adapter Policy

## Dependency Model

PanClaw core has no runtime third-party dependency. Optional tools are loaded lazily.

This keeps the distributed runtime small and avoids accidentally bundling libraries with incompatible licenses or heavy native runtimes.

## License Boundary

Allowed in core:

- MIT
- Apache-2.0
- BSD
- ISC
- Python Software Foundation License
- Other permissive licenses after review

Requires external process, sidecar or licensed adapter:

- GPL
- AGPL
- LGPL where linking/distribution obligations are unclear
- SSPL
- BUSL
- Commons Clause
- Cloud SDKs with account-specific terms
- Desktop apps such as Blender, FreeCAD and browser drivers

## Regulated Domains

Medical, legal, finance, architecture, military, safety, cloud infrastructure and commerce actions must return advisory/draft outputs unless a human approval and domain-specific authority are present.

