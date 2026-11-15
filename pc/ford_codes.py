"""Ford EEC-IV three-digit service codes.

Checked against Charles O. Probst, "Ford Fuel Injection & Electronic Engine Control,
1988-1993" (Bentley), EEC-IV 3-Digit Trouble Codes, pp. 267-271. Descriptions are reworded in
plain English; the code numbers and when each code can appear follow that table.

Each entry: code -> (plain description, tests it can appear in).
Tests: O = key on engine off, R = engine running, C = continuous memory (stored while driving).

The book covers 1988-93. A 1994 E-350 with the 7.5L (460) uses the same system, but not every
code applies to it (it has no distributorless coil packs, for instance; the book says a code that
doesn't apply to the vehicle can be ignored). A code points to a circuit, not a part: confirm with
a wiring test before replacing anything.

Oxygen sensors: HO2S-1 is the right bank, HO2S-2 the left (the book's 2-digit list labels the
matching codes right and left). The adaptive-limit codes (179-192) don't say which bank.
"""

CODES = {
    "111": ("System pass: no faults found in this test", "ORC"),
    # air and coolant temperature
    "112": ("Intake air temp (ACT/IAT) sensor voltage too low, reads 254 F: signal shorted to ground", "OC"),
    "113": ("Intake air temp (ACT/IAT) sensor voltage too high, reads -40 F: circuit open", "OC"),
    "114": ("Intake air temp (ACT/IAT) higher or lower than expected during the test", "OR"),
    "116": ("Coolant temp (ECT) higher or lower than expected during the test: engine not warmed up?", "OR"),
    "117": ("Coolant temp (ECT) sensor voltage too low, reads 254 F: signal shorted to ground", "OC"),
    "118": ("Coolant temp (ECT) sensor voltage too high, reads -40 F: circuit open", "OC"),
    # throttle and load sensors
    "121": ("Closed-throttle voltage higher or lower than expected: check throttle stop / TP sensor", "ORC"),
    "122": ("Throttle position (TP) sensor voltage below minimum", "OC"),
    "123": ("Throttle position (TP) sensor voltage above maximum", "OC"),
    "124": ("Throttle position (TP) sensor voltage higher than expected", "C"),
    "125": ("Throttle position (TP) sensor voltage lower than expected", "C"),
    "126": ("MAP or barometric sensor higher or lower than expected", "ORC"),
    "128": ("MAP vacuum circuit failure: check the MAP sensor vacuum hose", "R"),
    "129": ("Not enough mass air flow (MAF) change during the throttle-snap test", "R"),
    "157": ("Mass air flow (MAF) sensor voltage below minimum", "C"),
    "158": ("Mass air flow (MAF) sensor voltage above maximum", "OC"),
    "159": ("Mass air flow (MAF) higher or lower than expected during the test", "OR"),
    "167": ("Not enough throttle position change during the throttle-snap test", "R"),
    # oxygen sensors and fuel control
    "136": ("Left oxygen sensor (HO2S-2) shows the system always lean", "R"),
    "137": ("Left oxygen sensor (HO2S-2) shows the system always rich", "R"),
    "139": ("No switching seen from the left oxygen sensor (HO2S-2)", "C"),
    "144": ("No switching seen from the right oxygen sensor (HO2S-1)", "C"),
    "171": ("Right oxygen sensor (HO2S-1) unable to switch: fuel correction at its limit", "C"),
    "172": ("Right oxygen sensor (HO2S-1) not switching, shows lean: vacuum leak, low fuel pressure?", "RC"),
    "173": ("Right oxygen sensor (HO2S-1) not switching, shows rich: high fuel pressure, leaking injector?", "RC"),
    "174": ("Oxygen sensor switching slowly", "C"),
    "175": ("Left oxygen sensor (HO2S-2) not switching: fuel correction at its limit", "C"),
    "176": ("Left oxygen sensor (HO2S-2) shows the system always lean", "C"),
    "177": ("Left oxygen sensor (HO2S-2) shows the system always rich", "C"),
    "178": ("Oxygen sensor switching slowly", "C"),
    "179": ("Running RICH at part throttle: fuel correction at its lean limit", "C"),
    "181": ("Running LEAN at part throttle: fuel correction at its rich limit", "C"),
    "182": ("Running RICH at idle: fuel correction at its lean limit", "C"),
    "183": ("Running LEAN at idle: fuel correction at its rich limit", "C"),
    "184": ("Mass air flow (MAF) higher than expected", "C"),
    "185": ("Mass air flow (MAF) lower than expected", "C"),
    "186": ("Injector on-time higher than expected", "C"),
    "187": ("Injector on-time lower than expected", "C"),
    "188": ("Running RICH at part throttle: fuel correction at its lean limit (second sensor)", "C"),
    "189": ("Running LEAN at part throttle: fuel correction at its rich limit (second sensor)", "C"),
    "191": ("Running RICH at idle: fuel correction at its lean limit (second sensor)", "C"),
    "192": ("Running LEAN at idle: fuel correction at its rich limit (second sensor)", "C"),
    # ignition
    "211": ("Profile ignition pickup (PIP) circuit failure: distributor pickup / ignition module", "C"),
    "212": ("Loss of ignition diagnostic (IDM) input, or SPOUT circuit grounded", "C"),
    "213": ("Spark output (SPOUT) circuit open: check the SPOUT connector at the distributor", "R"),
    "214": ("Cylinder identification (CID) circuit failure", "C"),
    "215": ("Coil 1 primary circuit failure (distributorless engines only)", "C"),
    "216": ("Coil 2 primary circuit failure (distributorless engines only)", "C"),
    "217": ("Coil 3 primary circuit failure (distributorless engines only)", "C"),
    "218": ("Loss of ignition diagnostic (IDM) signal, left side", "C"),
    "219": ("Spark timing defaulted to 10 degrees BTDC: SPOUT circuit open", "C"),
    "222": ("Loss of ignition diagnostic (IDM) signal, right side", "C"),
    "223": ("Loss of dual plug inhibit (DPI) control", "C"),
    "224": ("Erratic ignition diagnostic (IDM) input to the computer", "C"),
    "225": ("Knock not sensed during the throttle-snap test", "R"),
    "226": ("Ignition diagnostic (IDM) signal not received", "O"),
    # air injection and EGR
    "311": ("Air injection (Thermactor) inoperative, right side", "R"),
    "312": ("Air injection (Thermactor) going upstream during the self-test", "R"),
    "313": ("Air injection (Thermactor) not bypassed during the self-test", "R"),
    "314": ("Air injection (Thermactor) inoperative, left side", "R"),
    "326": ("EGR pressure feedback (PFE/DPFE) voltage lower than expected", "RC"),
    "327": ("EGR pressure feedback (PFE/DPFE) circuit voltage below minimum", "ORC"),
    "328": ("EGR closed-valve voltage lower than expected", "ORC"),
    "332": ("Not enough EGR flow detected", "RC"),
    "334": ("EGR closed-valve voltage higher than expected", "ORC"),
    "335": ("EGR pressure feedback (PFE/DPFE) voltage out of self-test range", "O"),
    "336": ("EGR pressure feedback (PFE) voltage higher than expected", "RC"),
    "337": ("EGR pressure feedback (PFE/DPFE) circuit voltage above maximum", "ORC"),
    "338": ("Coolant temperature lower than normal: thermostat stuck open?", "C"),
    "339": ("Coolant temperature higher than normal: overheating", "C"),
    "341": ("Octane adjust service pin in use, or circuit open", "O"),
    # idle and speed
    "411": ("Could not control rpm during the engine-running low rpm check", "R"),
    "412": ("Could not control rpm during the engine-running high rpm check", "R"),
    "452": ("Not enough signal from the vehicle speed sensor (VSS)", "C"),
    # computer, switches, fuel pump
    "511": ("Engine computer ROM test failure", "O"),
    "512": ("Engine computer keep-alive memory test failure (also set after the battery is disconnected)", "C"),
    "513": ("Engine computer internal voltage failure", "C"),
    "519": ("Power steering pressure switch circuit open", "O"),
    "521": ("Power steering pressure switch did not change during the running test", "R"),
    "522": ("Not in Park or Neutral during the key-on test", "O"),
    "524": ("Low speed fuel pump circuit open (battery to computer)", "OC"),
    "525": ("In gear, or A/C on, during the self-test", "O"),
    "526": ("Neutral pressure switch circuit closed, or A/C on", "O"),
    "527": ("Neutral drive switch circuit open, or A/C on", "O"),
    "528": ("Clutch switch circuit failure", "C"),
    "529": ("Data communications link (DCL) or engine computer circuit failure", "C"),
    "533": ("Data communications link (DCL) or electronic instrument cluster circuit failure", "C"),
    "536": ("Brake on/off switch circuit failure, or brake not pressed during the running test", "RC"),
    "538": ("Not enough rpm change during the throttle-snap test, or operator error", "R"),
    "539": ("A/C or defrost on during the key-on test", "O"),
    "542": ("Fuel pump secondary circuit failure", "OC"),
    "543": ("Fuel pump secondary circuit failure", "OC"),
    "551": ("Idle air solenoid (IAS/IAC) circuit failure", "O"),
    "552": ("Air management 1 (AIR bypass) solenoid circuit failure", "O"),
    "553": ("Air management 2 (AIR diverter) solenoid circuit failure", "O"),
    "554": ("Fuel pressure regulator control (FPRC) solenoid circuit failure", "O"),
    "556": ("Fuel pump relay primary circuit failure", "OC"),
    "557": ("Fuel pump primary circuit failure", "OC"),
    "558": ("EGR vacuum regulator (EVR) solenoid circuit failure", "O"),
    "559": ("A/C on (ACON) relay circuit failure", "O"),
    "563": ("High speed electric fan (HEDF) circuit failure", "O"),
    "564": ("Electric fan (EDF) circuit failure", "O"),
    "565": ("Canister purge (CANP) solenoid circuit failure", "O"),
    "566": ("3-4 shift solenoid circuit failure", "O"),
    # E4OD automatic transmission
    "617": ("Transmission 1-2 shift error", "C"),
    "618": ("Transmission 2-3 shift error", "C"),
    "619": ("Transmission 3-4 shift error", "C"),
    "621": ("Transmission shift solenoid 1 (SS1) circuit failure", "O"),
    "622": ("Transmission shift solenoid 2 (SS2) circuit failure", "O"),
    "624": ("Transmission electronic pressure control (EPC) solenoid or driver circuit failure", "OC"),
    "625": ("Transmission EPC driver open in the computer", "O"),
    "626": ("Transmission coast clutch solenoid circuit failure", "O"),
    "627": ("Torque converter clutch solenoid circuit failure", "OC"),
    "628": ("Torque converter lock-up failure: excessive clutch slip", "OC"),
    "629": ("Torque converter clutch control or lock-up solenoid circuit failure", "O"),
    "631": ("Overdrive cancel indicator light circuit failure", "O"),
    "632": ("Overdrive cancel switch did not change during the running test", "R"),
    "633": ("4x4 switch closed during the self-test", "O"),
    "634": ("Transmission range (MLP) sensor voltage out of range, or A/C on", "C"),
    "636": ("Transmission fluid temperature (TOT) out of self-test range: transmission not warm?", "OR"),
    "637": ("Transmission fluid temperature (TOT) sensor voltage above maximum", "OC"),
    "638": ("Transmission fluid temperature (TOT) sensor voltage below minimum", "OC"),
    "639": ("Not enough signal from the transmission speed sensor", "RC"),
    "641": ("Transmission shift solenoid 3 (SS3) circuit failure", "O"),
    "643": ("Torque converter clutch control circuit failure", "OC"),
    "645": ("Wrong gear ratio in 1st", "C"),
    "646": ("Wrong gear ratio in 2nd", "C"),
    "647": ("Wrong gear ratio in 3rd", "C"),
    "648": ("Wrong gear ratio in 4th", "C"),
    "649": ("Transmission EPC range failure", "C"),
    "651": ("Transmission EPC circuit failure", "C"),
    "652": ("Modulated converter clutch solenoid output circuit error", "O"),
    "654": ("Transmission range (MLP) sensor not showing Park", ""),
    "656": ("Torque converter clutch continuous slip error", ""),
    "998": ("Hard fault present (limp-home mode): running test cancelled. Fix the key-on codes first", "R"),
}

# Codes that usually mean a step of the test was missed, not that a part is bad.
OPERATOR_STEP_CODES = {
    "521": "turn the steering wheel half a turn and release, within 1-2 s of the engine ID",
    "536": "press and release the brake, within 1-2 s of the engine ID",
    "632": "press the O/D cancel button on and off, within 1-2 s of the engine ID",
    "538": "snap the throttle wide open once, briefly, when the single flash comes",
    "129": "snap the throttle wide open once, briefly, when the single flash comes",
    "167": "snap the throttle wide open once, briefly, when the single flash comes",
    "225": "snap the throttle wide open once, briefly, when the single flash comes",
    "116": "warm the engine to operating temperature first, then redo the test",
    "636": "drive until the transmission is warm, then redo the test",
    "525": "put it in Park and turn the A/C off, then redo the test",
    "539": "turn the A/C and defrost off, then redo the test",
    "522": "put it in Park, then redo the test",
}


def describe(code):
    entry = CODES.get(code)
    if entry is None:
        if len(code) == 2:
            return "two-digit code: this computer uses the older 2-digit list, look it up there"
        return ("not in the 3-digit table: per Probst, a code not listed doesn't apply to this vehicle. "
                "Check that it decoded right (--replay)")
    return entry[0]


def tests_for(code):
    entry = CODES.get(code)
    return entry[1] if entry else ""
