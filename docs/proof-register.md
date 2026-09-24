# Proof Register — RA Operations Control Tower v0.1

Repository: https://github.com/rash1ed/ra-operations-control-tower

## Verified local gates

- Approved unittest suite: 10/10 PASS.
- CSV end-to-end smoke: PASS.
- Microsoft Excel-created XLSX input smoke: PASS.
- Microsoft Excel application open/readback of generated reports: PASS.
- RA Verifier Agent v0.1 Phase 2d gate: PASS.
- Secret scan: PASS.
- GitHub Actions workflow configured for Python 3.11 and 3.12; remote result pending first push.

## SHA-256 evidence

- `src/control_tower/analytics.py`: `5114CDFBD3CF811BA67B3F873A8EA8B43F07714B446CB091B8AD5612A26BEBB9`
- `src/control_tower/validation.py`: `DDA2F0DCC4AD85B9D1A8AF27254EBDFFF19B7699A1A735737EF64E9158B9228A`
- `src/control_tower/excel_writer.py`: `C1C1D669CD5433E8B4065B66246A6A4B240A6F83112954F6B40EF54B029445AC`
- `src/control_tower/loader.py`: `531D596936A10B0A54E3FD2702316F01E306FE6A32C032ADC4274BFFE23A5EB0`
- `src/control_tower/cli.py`: `49AE6A63910167B7339AF6193006F1C385C26FD45577D4A2D90DF1459310A9CE`
- `tests/test_initial_red_gate.py`: `F9A565782CBFDEA61C8402A1CD064090DF8EB9DCD7BB699597A665519661E7A4`
- `tests/test_phase2a.py`: `AFBCCD3412509BACFE70A012BF351DFD76D5162CBEBA6A74E17C01BB72C1A00A`
- `tests/test_phase2b.py`: `ED0635CCAB151F8C860D0A7E4B43D43907FEA8142A61022AC09E1F4C0816C34D`
- `tests/test_phase2c.py`: `06628BDBE0513783F24BA122DA19FB7EEF90ECCB4CF1AC457E7AB332DE6B354F`
- `tests/test_phase2d.py`: `413B79F4A2FFF4D9A53596FE73F543563BB5943869B51EB7D5D92CFDEC5FA34D`
- `output/test_report.xlsx`: `8A1CE5C0A7D3E4252FF0CF9A503AB6C486BBA9560BB69FEAB77BF20B78E55DDD`
- `docs/evidence/kpis.png`: `C0CA078B1F2C014D2F10BD401A714C68DC7C400ECAFF20108C797AEA1F28A74E`
- `docs/evidence/rag.png`: `C0CA078B1F2C014D2F10BD401A714C68DC7C400ECAFF20108C797AEA1F28A74E`

## Excel evidence

- `docs/evidence/kpis.png`: rendered/exported by installed Microsoft Excel.
- `docs/evidence/rag.png`: rendered/exported by installed Microsoft Excel.
- `output/test_report.xlsx`: structurally verified and opened by Microsoft Excel.

## Notes

- No LinkedIn or CV changes are part of this project.
- Runtime dependencies remain empty.
- No LLM or external service is used by the v0.1 runtime.
