# Third-party materials and asset provenance

KinGuard's [MIT license](../LICENSE) applies to the project's own contributions.
It does not replace upstream licenses or service terms. This inventory records
what is identifiable in the checkout, not a blanket permissions certification.

| Material | Location or source | Attribution and scope |
| --- | --- | --- |
| Python application dependencies | [pyproject.toml](../pyproject.toml), [uv.lock](../uv.lock) | Cryptography, FastAPI, fpdf2, Google ADK and Google Cloud clients, Pydantic, python-dotenv, Segno and Uvicorn; resolved transitive packages are in the lockfile. Preserve their upstream licenses when distributing them. |
| Browser booker dependencies | [booker/requirements.txt](../booker/requirements.txt) | FastAPI, Uvicorn, Playwright, google-genai and Google Cloud Storage have separate upstream terms. |
| Firebase JavaScript SDK | `https://www.gstatic.com/firebasejs/13.4.0` in the dashboard and handoff page | Firebase AI Logic, App Check and app initialization use the upstream SDK. SDK code is not claimed as team-authored. |
| Atkinson Hyperlegible Next | Google Fonts stylesheet in [dashboard](../kinguard/webui/index.html) | Atkinson Hyperlegible Next Project Authors; SIL Open Font License 1.1. [Upstream license](https://github.com/google/fonts/blob/main/ofl/atkinsonhyperlegiblenext/OFL.txt). |
| Google Stitch design references | [Design source record](design/README.md), `docs/design/stitch-*.png` | Existing repository notes attribute the visual design to Google Stitch. These are design references, not proof of current app execution. Original generation dates/account permissions were not independently verified. |
| Dashboard previews | `docs/design/mobile/` | Existing notes describe captures of the built UI at simulated phone width. They are not evidence of physical phone inference or a current deployment. |
| Architecture diagrams | [SVG generator](../scripts/build_architecture_svg.py), [PDF generator](../scripts/make_architecture_pdf.py), `docs/diagram/` | Repository-generated diagrams of the implementation. These are not execution traces. |
| Synthetic medical fixtures | [Synthetic-document generator](../scripts/make_synthetic_docs.py), [bill-image generator](../scripts/make_bill_images.py), `assets/synthetic/` | Demo material must remain labelled synthetic. Printed patient/report dates do not establish project creation dates. Layout references are listed in [CITATIONS.md](CITATIONS.md). |
| KinGuard logo | `kinguard/webui/static/logo.png` | Included in the dashboard commit and covered by the team's project ownership declaration. Its original creation method is not recorded in the inspected repository. |
| Hospital snapshots and policy/clinical references | `kinguard/kb/data/`, [CITATIONS.md](CITATIONS.md) | Seeded capabilities and insurer relationships are demo data. Preserve source/status labels; cited reference material is not authored by the team. |
| External APIs | Firebase/Google Cloud, Google Maps/Places, WhatsApp providers and payment providers | Integration code does not establish account permission or production approval. Each configured service must be used under its own terms. |

AI assistance is part of the current code/documentation remediation, and the
repository also contains Google Stitch design attribution. Neither tool use nor
generated output substitutes for the team's review or third-party permissions.

If additional copied or adapted code/assets are identified, add their sources
and permissions here. The unavailable legacy references remain explicitly
disclosed in [PROVENANCE_EVIDENCE.md](PROVENANCE_EVIDENCE.md); they are not used as
proof of ownership or independent implementation.
