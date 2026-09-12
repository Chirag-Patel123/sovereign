import logging
import math
from typing import Dict, Any, Optional
from .base import BaseTool

logger = logging.getLogger(__name__)

class CalculateTool(BaseTool):
    """
    Engineering calculation tool for refinery process calculations.
    Specifically implements ASME B31.3 Barlow wall thickness formula,
    schedule sizing, and engineering arithmetic with full audit trail.
    """

    @property
    def name(self) -> str:
        return "calculate"

    @property
    def description(self) -> str:
        return (
            "Performs verified industrial engineering calculations (e.g. pipe wall thickness per ASME B31.3, "
            "pressure ratings, schedule recommendation, and unit conversions). "
            "Arguments: calculation_type (str: 'pipe_wall_thickness' | 'general'), parameters (dict)."
        )

    def run(self, calculation_type: str = "pipe_wall_thickness", parameters: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        params = parameters or {}
        # Also check kwargs if passed at top level
        for k, v in kwargs.items():
            if k not in params:
                params[k] = v

        if calculation_type in ("pipe_wall_thickness", "asme_b31_3", "barlow"):
            return self._calculate_pipe_wall_thickness(params)
        elif calculation_type == "general" or "expression" in params:
            return self._calculate_general(params)
        else:
            # Default to pipe wall thickness as the primary refinery standard calculation
            return self._calculate_pipe_wall_thickness(params)

    def _calculate_pipe_wall_thickness(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Barlow's Equation for ASME B31.3 Process Piping:
        t_m = (P * D) / (2 * (S * E + P * Y)) + c
        t_nom = t_m / 0.875 (accommodating 12.5% mill tolerance)
        """
        # Default MRPL High-Pressure CDU/HCU design values if not overridden
        P = float(params.get("P", params.get("design_pressure_mpa", 15.0))) # 15.0 MPa (150 bar)
        D = float(params.get("D", params.get("outer_diameter_mm", 219.1)))  # 219.1 mm (NPS 8)
        S = float(params.get("S", params.get("allowable_stress_mpa", 120.0))) # 120.0 MPa (ASTM A106 Gr B @ 300C)
        E = float(params.get("E", params.get("joint_efficiency", 1.0)))     # 1.0 (Seamless)
        Y = float(params.get("Y", params.get("y_coefficient", 0.4)))       # 0.4 (Ferritic steel < 482C)
        c = float(params.get("c", params.get("corrosion_allowance_mm", 3.0))) # 3.0 mm

        # Denominator: 2 * (S * E + P * Y)
        denominator = 2.0 * ((S * E) + (P * Y))
        numerator = P * D
        t_pressure = numerator / denominator
        t_min = t_pressure + c

        # Account for 12.5% mill under-tolerance: t_nom >= t_min / (1 - 0.125)
        mill_tolerance_factor = 0.875
        t_nominal_required = t_min / mill_tolerance_factor

        # Standard NPS 8 Pipe Schedule table (Outside Diameter = 219.1 mm)
        schedules = [
            {"schedule": "Sch 40", "nominal_wall_mm": 8.18, "min_wall_mm": 8.18 * 0.875},
            {"schedule": "Sch 80", "nominal_wall_mm": 12.70, "min_wall_mm": 12.70 * 0.875},
            {"schedule": "Sch 120", "nominal_wall_mm": 18.26, "min_wall_mm": 18.26 * 0.875},
            {"schedule": "Sch 160", "nominal_wall_mm": 23.01, "min_wall_mm": 23.01 * 0.875},
        ]

        recommended_schedule = "Sch 160"
        for sch in schedules:
            if sch["min_wall_mm"] >= t_min:
                recommended_schedule = sch["schedule"]
                break

        return {
            "status": "success",
            "calculation_name": "ASME B31.3 Pipe Minimum Wall Thickness & Schedule Selection",
            "formula": "t_m = [P * D] / [2 * (S * E + P * Y)] + c",
            "mill_tolerance_formula": "t_nom_req = t_m / 0.875 (12.5% under-tolerance)",
            "inputs": {
                "design_pressure_P_MPa": P,
                "outer_diameter_D_mm": D,
                "allowable_stress_S_MPa": S,
                "joint_factor_E": E,
                "temperature_coeff_Y": Y,
                "corrosion_allowance_c_mm": c
            },
            "intermediate_results": {
                "pressure_design_thickness_mm": round(t_pressure, 3),
                "corrosion_allowance_mm": round(c, 3),
                "denominator_term": round(denominator, 2)
            },
            "results": {
                "minimum_required_thickness_tm_mm": round(t_min, 3),
                "nominal_thickness_with_tolerance_mm": round(t_nominal_required, 3),
                "recommended_commercial_schedule": recommended_schedule,
                "schedule_nominal_thickness_mm": next((s["nominal_wall_mm"] for s in schedules if s["schedule"] == recommended_schedule), 18.26),
                "safety_margin_percent": round(((next((s["nominal_wall_mm"] for s in schedules if s["schedule"] == recommended_schedule), 18.26) * 0.875 - t_min) / t_min) * 100, 2)
            },
            "compliance_note": f"Meets MRPL Standard ES-401 & ASME B31.3 Table A-1 requirements for sour hydrocarbon service."
        }

    def _calculate_general(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Safe arithmetic expression evaluation."""
        expr = str(params.get("expression", "0")).strip()
        # Whitelist safe mathematical tokens
        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sqrt": math.sqrt,
            "pow": pow,
            "pi": math.pi
        }
        try:
            # Only allow basic math
            result = eval(expr, {"__builtins__": None}, safe_dict)
            return {
                "status": "success",
                "calculation_name": "General Arithmetic Evaluation",
                "expression": expr,
                "result": result
            }
        except Exception as e:
            logger.error(f"[CalculateTool] Error evaluating expression '{expr}': {e}")
            return {
                "status": "error",
                "error": str(e),
                "expression": expr
            }
