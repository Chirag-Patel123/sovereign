from typing import List, Dict, Any

MOCK_REFINERY_CHUNKS: Dict[str, List[Dict[str, Any]]] = {
    "MRPL-STD-PIPE-2024": [
        {
            "chunk_id": "chk-pipe-001",
            "page": 1,
            "score": 0.94,
            "text": (
                "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)\n"
                "STANDARD SPECIFICATION NO: MRPL-ENG-ES-401 (REV 4)\n"
                "TITLE: DESIGN PRESSURE & WALL THICKNESS CRITERIA FOR HIGH-PRESSURE PROCESS PIPING\n"
                "APPLICABLE UNIT: CDU-II, HCU (Hydrocracker Unit), and Vacuum Gas Oil (VGO) Headers.\n"
                "1. Scope: This standard governs the mechanical design, minimum wall thickness calculation, "
                "and material verification for hydrocarbon line sizing under sour service conditions."
            )
        },
        {
            "chunk_id": "chk-pipe-002",
            "page": 2,
            "score": 0.91,
            "text": (
                "2. Design Formula per ASME B31.3 (Process Piping Code):\n"
                "The minimum required pipe wall thickness 't_m' (in mm) shall be computed using Barlow's modified equation:\n"
                "   t_m = [P * D] / [2 * (S * E + P * Y)] + c\n"
                "Where:\n"
                " - P = Internal Design Pressure = 15.0 MPa (150 bar)\n"
                " - D = Outside Diameter of pipe = 219.1 mm (Nominal Pipe Size NPS 8 inch)\n"
                " - S = Allowable Material Stress for ASTM A106 Grade B at 300°C = 120.0 MPa (per ASME Section II-D Table 1A)\n"
                " - E = Longitudinal Weld Quality Factor = 1.00 (Seamless pipe)\n"
                " - Y = Wall Thickness Coefficient for ferritic steels at 300°C = 0.40\n"
                " - c = Mechanical and Corrosion Allowance = 3.0 mm (Mandatory for H2S/sour hydrocarbon service)"
            )
        },
        {
            "chunk_id": "chk-pipe-003",
            "page": 3,
            "score": 0.88,
            "text": (
                "3. Commercial Schedule Selection and Tolerance:\n"
                "Once t_m is calculated, a mill fabrication under-tolerance of 12.5% must be accommodated:\n"
                "   t_nominal >= t_m / 0.875\n"
                "Available Schedules for NPS 8 (D = 219.1 mm):\n"
                " - Schedule 40: Nominal wall = 8.18 mm (NOT SUITABLE for P >= 10 MPa)\n"
                " - Schedule 80: Nominal wall = 12.70 mm (Under tolerance limit = 11.11 mm)\n"
                " - Schedule 120: Nominal wall = 18.26 mm (Under tolerance limit = 15.98 mm)\n"
                " - Schedule 160: Nominal wall = 23.01 mm\n"
                "Conclusion: If computed t_nominal is between 12.7 mm and 18.26 mm, Schedule 120 (18.26 mm) must be selected."
            )
        }
    ],
    "MRPL-STD-VALVE-2024": [
        {
            "chunk_id": "chk-valve-001",
            "page": 1,
            "score": 0.92,
            "text": (
                "MRPL TECHNICAL SPECIFICATION TS-302: PRESSURE SAFETY VALVE (PSV) RELIEF SIZING\n"
                "Applicable Standard: API Standard 520 Part I (10th Edition).\n"
                "Effective Discharge Area A = W / (C * K_d * P_1 * K_b * K_c) * sqrt(T * Z / M)\n"
                "Discharge Coefficient K_d = 0.975 for ASME Section VIII certified nozzle relief valves."
            )
        }
    ]
}

def get_mock_chunks(doc_id: str, query: str = "", top_k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve mock chunks based on doc_id or keyword similarity."""
    if doc_id in MOCK_REFINERY_CHUNKS:
        return MOCK_REFINERY_CHUNKS[doc_id][:top_k]
    
    # Generic fallback mock chunk if unknown doc_id
    return [
        {
            "chunk_id": f"chk-{doc_id}-001",
            "page": 1,
            "score": 0.85,
            "text": (
                f"DOCUMENT REFERENCE: {doc_id}\n"
                f"Engineering inquiry: {query}\n"
                "Standard engineering design parameters apply: Design Pressure P = 15.0 MPa, "
                "Outside Diameter D = 219.1 mm, Allowable Stress S = 120.0 MPa, Joint Factor E = 1.0, "
                "Temperature Factor Y = 0.4, Corrosion Allowance c = 3.0 mm."
            )
        }
    ]
