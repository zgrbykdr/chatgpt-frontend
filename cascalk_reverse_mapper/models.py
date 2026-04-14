from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FileRecord:
    path: str
    kind: str
    size: int
    sha256: str
    role: str = "unknown"


@dataclass
class VariableRecord:
    name: str
    source_file: str
    category: str
    dtype: str
    default_value: str | None = None
    enum_values: list[str] = field(default_factory=list)
    domain: str | None = None
    notes: str = ""
    confidence: float = 0.0


@dataclass
class InterfaceCandidate:
    dll_name: str
    function_name: str
    probable_purpose: str
    call_order_guess: int
    parameter_semantics: str
    confidence: float
    evidence: str


@dataclass
class RuntimeObservation:
    session_id: int
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    status: str
    error: str = ""


KNOWN_INPUTS = {
    "InTempSide1", "InTempSide2", "OutTempSide1", "OutTempSide2", "PressureSide1", "PressureSide2",
    "OperatingPressureSide1", "OperatingPressureSide2", "DesignPressureSide1", "DesignPressureSide2",
    "FluidSide1", "FluidSide2", "DutySide1", "DutySide2", "DutyTypeSide1", "DutyTypeSide2", "CoCurrent",
    "IsTwoPhase", "GiveInletqual", "Margin", "Fouling", "PlateType", "PlateTypeUI", "PlateFamily",
    "PlateGroup", "ChannelFamily", "PlateMaterial", "PlateThickness", "PlateThicknessSpec", "MaxNumberOfUnits",
    "MinNumberOfUnits", "CalcMode", "CalcSettingsAccuracy", "CalcSettingsAlphaCold", "CalcSettingsAlphaHot",
    "CalcSettingsLmtd", "CalcSettingsNonNewton", "CalcSettingsPressDropCold", "CalcSettingsPressDropHot",
    "CalcSettingsRwRf", "CalcSettingsSolutionLevel", "CalcSettingsUsePersonalCalcSettings",
    "ConsiderPdropSide1", "ConsiderPdropSide2",
}

KNOWN_OUTPUTS = {
    "HeatLoad", "EffectiveArea", "EffectiveMargin", "EffectiveFouling", "Density", "CondensingTemp",
    "CondensateTemp", "InPressSide1", "InPressSide2", "InQualitySide1", "InQualitySide2", "InConnPdropSide1",
    "InConnPdropSide2", "InPortPdropSide1", "InPortPdropSide2", "AlphaWall1Side1", "AlphaWall1Side2",
    "AlphaWall2Side1", "AlphaWall2Side2", "ChanPerfSide1", "ChanPerfSide2", "ChannelVolumeSide1",
    "ChannelVolumeSide2", "FlowBehaviour", "FlowType", "Errors", "Error",
}

PRIORITY_DLLS = [
    "AlfaCalcInterface.dll", "CasCalc.dll", "PHECalc.dll", "HeCalc.dll", "SHECalc.dll", "P3Calc.dll", "Nips.dll"
]

SUPPORT_DLLS = ["REFPRP64.DLL", "concrt140.dll", "mfc140u.dll", "msvcp140.dll", "vcruntime140.dll"]

PRIORITY_XMLS = [
    "PHE/Application/General_1phase.7235.application.xml",
    "PHE/Application/General_2phase.7135.application.xml",
    "PHE/Views/TotalView.xml",
    "Settings.xml",
    "AvqAddin.xml",
]

API_STRING_CLUES = [
    "Calculate", "CalculateEx", "CheckFluid", "CopyFluid", "GetChannelNames", "GetAltStringValue",
    "CreateItem", "DeleteItem", "GetFluidFileFromName", "MyFluidProperty",
]
