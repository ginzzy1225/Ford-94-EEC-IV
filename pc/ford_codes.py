"""Ford EEC-IV three-digit service codes (1991-95 trucks and vans, including the 7.5L E-series).

Each entry: code -> (plain description, tests it can appear in).
Tests: O = key on engine off, R = engine running, C = continuous memory (stored from driving).

This is the general EEC-IV list collected from published code charts. Not every code applies to
a 7.5L E-350 (it has no EDIS coil packs, for instance). A code points to a circuit, not a part:
confirm with a service manual or wiring test before replacing anything.
"""

CODES = {
    "111": ("System pass, no faults found in this test", "ORC"),
    # air and coolant temperature
    "112": ("Intake air temp (IAT/ACT) sensor reads too hot (above 240 F): signal shorted to ground", "OC"),
    "113": ("Intake air temp (IAT/ACT) sensor reads too cold (below -40 F): circuit open", "ORC"),
    "114": ("Intake air temp (IAT/ACT) out of self-test range", "OR"),
    "116": ("Coolant temp (ECT) out of self-test range: engine not warmed up, or sensor off", "OR"),
    "117": ("Coolant temp (ECT) sensor reads too hot (above 240 F): signal shorted to ground", "OC"),
    "118": ("Coolant temp (ECT) sensor reads too cold (below -40 F): circuit open", "OC"),
    # throttle position
    "121": ("Throttle position (TP) sensor out of self-test range: check idle stop / sensor", "ORC"),
    "122": ("Throttle position (TP) sensor voltage too low", "OC"),
    "123": ("Throttle position (TP) sensor voltage too high", "OC"),
    "124": ("Throttle position (TP) voltage higher than expected", "C"),
    "125": ("Throttle position (TP) voltage lower than expected", "C"),
    "126": ("MAP / barometric sensor out of range", "ORC"),
    "128": ("MAP sensor vacuum not sensed: check the MAP vacuum hose", "C"),
    "129": ("Not enough MAP or MAF change during the dynamic response (throttle snap) test", "R"),
    "167": ("Not enough throttle position change during the dynamic response (throttle snap) test", "R"),
    # oxygen sensors and fuel control (sensor 1 = right bank, sensor 2 = left bank)
    "136": ("Left oxygen sensor (HO2S-2) not switching: system lean", "R"),
    "137": ("Left oxygen sensor (HO2S-2) not switching: system rich", "R"),
    "139": ("Left oxygen sensor (HO2S-2) not detected", "C"),
    "144": ("Right oxygen sensor (HO2S-1) not detected / no switching", "C"),
    "157": ("Mass air flow (MAF) sensor voltage too low", "ORC"),
    "158": ("Mass air flow (MAF) sensor voltage too high", "ORC"),
    "159": ("Mass air flow (MAF) out of self-test range", "OR"),
    "171": ("Right bank fuel control at its limit: oxygen sensor not switching", "C"),
    "172": ("Right oxygen sensor (HO2S-1) shows lean: vacuum leak, low fuel pressure, weak injectors", "RC"),
    "173": ("Right oxygen sensor (HO2S-1) shows rich: leaking injector, high fuel pressure", "RC"),
    "174": ("Right oxygen sensor (HO2S-1) switching slowly", "C"),
    "175": ("Left bank fuel control at its limit: oxygen sensor not switching", "C"),
    "176": ("Left oxygen sensor (HO2S-2) shows lean", "C"),
    "177": ("Left oxygen sensor (HO2S-2) shows rich", "C"),
    "178": ("Left oxygen sensor (HO2S-2) switching slowly", "C"),
    "179": ("Right bank running lean at part throttle (fuel correction at its limit)", "C"),
    "181": ("Right bank running rich at part throttle (fuel correction at its limit)", "C"),
    "182": ("Right bank running lean at idle (fuel correction at its limit)", "C"),
    "183": ("Right bank running rich at idle (fuel correction at its limit)", "C"),
    "184": ("Mass air flow (MAF) higher than expected", "C"),
    "185": ("Mass air flow (MAF) lower than expected", "C"),
    "186": ("Injector pulse width higher than expected", "C"),
    "187": ("Injector pulse width lower than expected", "C"),
    "188": ("Left bank running lean at part throttle (fuel correction at its limit)", "C"),
    "189": ("Left bank running rich at part throttle (fuel correction at its limit)", "C"),
    "191": ("Left bank running lean at idle (fuel correction at its limit)", "C"),
    "192": ("Left bank running rich at idle (fuel correction at its limit)", "C"),
    # ignition
    "211": ("Profile ignition pickup (PIP) signal fault: distributor pickup / ignition module", "C"),
    "212": ("Loss of ignition diagnostic (IDM) signal, or SPOUT circuit grounded", "C"),
    "213": ("Spark output (SPOUT) circuit open: check the SPOUT connector at the distributor", "R"),
    "214": ("Cylinder identification (CID) circuit fault", "C"),
    "219": ("Spark timing defaulted to 10 degrees: SPOUT circuit open", "R"),
    "225": ("Knock not sensed during the dynamic response test", "R"),
    # EGR and air injection
    "311": ("Air injection (AIR) system inoperative (right side)", "R"),
    "312": ("Air injection (AIR) misdirected: not going upstream when it should", "R"),
    "313": ("Air injection (AIR) not bypassed", "R"),
    "314": ("Air injection (AIR) system inoperative (left side)", "R"),
    "326": ("EGR pressure feedback (PFE/DPFE) lower than expected", "RC"),
    "327": ("EGR position/pressure sensor (EVP/PFE/DPFE) voltage too low", "ORC"),
    "328": ("EGR valve position (EVP) closed voltage lower than expected", "ORC"),
    "332": ("Not enough EGR flow detected", "RC"),
    "334": ("EGR valve position (EVP) closed voltage higher than expected", "ORC"),
    "335": ("EGR pressure feedback (PFE/DPFE) out of self-test range", "O"),
    "336": ("EGR pressure feedback (PFE/DPFE) higher than expected", "RC"),
    "337": ("EGR position/pressure sensor (EVP/PFE/DPFE) voltage too high", "ORC"),
    "338": ("Coolant temperature lower than normal: thermostat stuck open?", "C"),
    "339": ("Coolant temperature higher than normal: overheating", "C"),
    "341": ("Octane adjust service pin open (normal if the shorting bar was removed on purpose)", "O"),
    # idle and speed
    "411": ("Could not control idle rpm during the engine-running low rpm check", "R"),
    "412": ("Could not control idle rpm during the engine-running high rpm check", "R"),
    "452": ("No signal from the vehicle speed sensor (VSS)", "C"),
    # computer and switches
    "511": ("Engine computer ROM test failed", "O"),
    "512": ("Engine computer keep-alive memory failed (battery was disconnected, or power lost)", "C"),
    "513": ("Engine computer internal voltage fault", "O"),
    "519": ("Power steering pressure switch circuit open", "O"),
    "521": ("Power steering pressure switch did not change: turn the wheel during the running test", "R"),
    "522": ("Transmission not in Park or Neutral during the key-on test", "O"),
    "525": ("In gear or A/C on during the self-test: redo in Park with A/C off", "O"),
    "536": ("Brake on/off switch fault, or brake not pressed during the running test", "RC"),
    "538": ("Not enough rpm change during the throttle snap test (often: throttle not snapped)", "R"),
    "539": ("A/C was on during the key-on test", "O"),
    "542": ("Fuel pump secondary circuit fault: computer to ground", "OC"),
    "543": ("Fuel pump secondary circuit fault: battery to computer", "OC"),
    "552": ("Air injection bypass (AIRB) solenoid circuit fault", "O"),
    "553": ("Air injection diverter (AIRD) solenoid circuit fault", "O"),
    "556": ("Fuel pump relay primary circuit fault", "OC"),
    "558": ("EGR vacuum regulator (EVR) solenoid circuit fault", "O"),
    "565": ("Canister purge solenoid circuit fault", "O"),
    # E4OD automatic transmission
    "617": ("Transmission 1-2 shift error", "C"),
    "618": ("Transmission 2-3 shift error", "C"),
    "619": ("Transmission 3-4 shift error", "C"),
    "621": ("Transmission shift solenoid 1 circuit fault", "OC"),
    "622": ("Transmission shift solenoid 2 circuit fault", "OC"),
    "624": ("Transmission electronic pressure control (EPC) circuit fault", "OC"),
    "625": ("Transmission EPC driver open in the computer", "OC"),
    "626": ("Transmission coast clutch solenoid circuit fault", "OC"),
    "627": ("Torque converter clutch solenoid circuit fault", "OC"),
    "628": ("Excessive torque converter clutch slip", "C"),
    "629": ("Torque converter clutch control fault", "C"),
    "631": ("Overdrive cancel indicator light circuit fault", "O"),
    "632": ("Overdrive cancel switch did not change: press the O/D button during the running test", "R"),
    "633": ("4x4 low switch closed during the self-test (4x4 vehicles only)", "O"),
    "634": ("Transmission range (MLP) sensor out of range, or A/C on", "ORC"),
    "636": ("Transmission fluid temperature (TOT) out of range: transmission not warmed up?", "OR"),
    "637": ("Transmission fluid temperature (TOT) sensor reads too cold: circuit open", "OC"),
    "638": ("Transmission fluid temperature (TOT) sensor reads too hot: circuit shorted", "OC"),
    "639": ("No signal from the transmission speed sensor", "RC"),
    "645": ("Transmission wrong gear ratio in 1st", "C"),
    "646": ("Transmission wrong gear ratio in 2nd", "C"),
    "647": ("Transmission wrong gear ratio in 3rd", "C"),
    "648": ("Transmission wrong gear ratio in 4th", "C"),
    "649": ("Transmission EPC range fault", "C"),
    "651": ("Transmission EPC circuit fault", "C"),
    "654": ("Transmission range (MLP) sensor not showing Park", "O"),
    "998": ("Hard fault present: the running test was cancelled. Fix the key-on codes first", "R"),
}

# Codes that usually mean a step of the test was missed, not that a part is bad.
OPERATOR_STEP_CODES = {
    "521": "turn the steering wheel half a turn and back right after the engine ID",
    "536": "press and release the brake right after the engine ID",
    "632": "press the O/D cancel button on and off right after the engine ID",
    "538": "snap the throttle wide open once, quickly, when the single flash comes",
    "129": "snap the throttle wide open once, quickly, when the single flash comes",
    "167": "snap the throttle wide open once, quickly, when the single flash comes",
    "525": "put it in Park and turn the A/C off, then redo the test",
    "539": "turn the A/C off, then redo the test",
    "522": "put it in Park, then redo the test",
}


def describe(code):
    entry = CODES.get(code)
    if entry is None:
        if len(code) == 2:
            return "two-digit code: this computer uses the older 2-digit list, look it up there"
        return "not in this table: look it up in a Ford EEC-IV 3-digit code chart"
    return entry[0]


def tests_for(code):
    entry = CODES.get(code)
    return entry[1] if entry else ""
