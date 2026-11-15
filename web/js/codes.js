// GENERATED from pc/ford_codes.py by tools/gen_codes_js.py. Edit that file, then rerun.
// Code table checked against Probst, Ford Fuel Injection & Electronic Engine Control 1988-93,
// EEC-IV 3-digit trouble codes, pp. 267-271.

export const CODES = {
 "111": {
  "text": "System pass: no faults found in this test",
  "tests": "ORC"
 },
 "112": {
  "text": "Intake air temp (ACT/IAT) sensor voltage too low, reads 254 F: signal shorted to ground",
  "tests": "OC"
 },
 "113": {
  "text": "Intake air temp (ACT/IAT) sensor voltage too high, reads -40 F: circuit open",
  "tests": "OC"
 },
 "114": {
  "text": "Intake air temp (ACT/IAT) higher or lower than expected during the test",
  "tests": "OR"
 },
 "116": {
  "text": "Coolant temp (ECT) higher or lower than expected during the test: engine not warmed up?",
  "tests": "OR"
 },
 "117": {
  "text": "Coolant temp (ECT) sensor voltage too low, reads 254 F: signal shorted to ground",
  "tests": "OC"
 },
 "118": {
  "text": "Coolant temp (ECT) sensor voltage too high, reads -40 F: circuit open",
  "tests": "OC"
 },
 "121": {
  "text": "Closed-throttle voltage higher or lower than expected: check throttle stop / TP sensor",
  "tests": "ORC"
 },
 "122": {
  "text": "Throttle position (TP) sensor voltage below minimum",
  "tests": "OC"
 },
 "123": {
  "text": "Throttle position (TP) sensor voltage above maximum",
  "tests": "OC"
 },
 "124": {
  "text": "Throttle position (TP) sensor voltage higher than expected",
  "tests": "C"
 },
 "125": {
  "text": "Throttle position (TP) sensor voltage lower than expected",
  "tests": "C"
 },
 "126": {
  "text": "MAP or barometric sensor higher or lower than expected",
  "tests": "ORC"
 },
 "128": {
  "text": "MAP vacuum circuit failure: check the MAP sensor vacuum hose",
  "tests": "R"
 },
 "129": {
  "text": "Not enough mass air flow (MAF) change during the throttle-snap test",
  "tests": "R"
 },
 "157": {
  "text": "Mass air flow (MAF) sensor voltage below minimum",
  "tests": "C"
 },
 "158": {
  "text": "Mass air flow (MAF) sensor voltage above maximum",
  "tests": "OC"
 },
 "159": {
  "text": "Mass air flow (MAF) higher or lower than expected during the test",
  "tests": "OR"
 },
 "167": {
  "text": "Not enough throttle position change during the throttle-snap test",
  "tests": "R"
 },
 "136": {
  "text": "Left oxygen sensor (HO2S-2) shows the system always lean",
  "tests": "R"
 },
 "137": {
  "text": "Left oxygen sensor (HO2S-2) shows the system always rich",
  "tests": "R"
 },
 "139": {
  "text": "No switching seen from the left oxygen sensor (HO2S-2)",
  "tests": "C"
 },
 "144": {
  "text": "No switching seen from the right oxygen sensor (HO2S-1)",
  "tests": "C"
 },
 "171": {
  "text": "Right oxygen sensor (HO2S-1) unable to switch: fuel correction at its limit",
  "tests": "C"
 },
 "172": {
  "text": "Right oxygen sensor (HO2S-1) not switching, shows lean: vacuum leak, low fuel pressure?",
  "tests": "RC"
 },
 "173": {
  "text": "Right oxygen sensor (HO2S-1) not switching, shows rich: high fuel pressure, leaking injector?",
  "tests": "RC"
 },
 "174": {
  "text": "Oxygen sensor switching slowly",
  "tests": "C"
 },
 "175": {
  "text": "Left oxygen sensor (HO2S-2) not switching: fuel correction at its limit",
  "tests": "C"
 },
 "176": {
  "text": "Left oxygen sensor (HO2S-2) shows the system always lean",
  "tests": "C"
 },
 "177": {
  "text": "Left oxygen sensor (HO2S-2) shows the system always rich",
  "tests": "C"
 },
 "178": {
  "text": "Oxygen sensor switching slowly",
  "tests": "C"
 },
 "179": {
  "text": "Running RICH at part throttle: fuel correction at its lean limit",
  "tests": "C"
 },
 "181": {
  "text": "Running LEAN at part throttle: fuel correction at its rich limit",
  "tests": "C"
 },
 "182": {
  "text": "Running RICH at idle: fuel correction at its lean limit",
  "tests": "C"
 },
 "183": {
  "text": "Running LEAN at idle: fuel correction at its rich limit",
  "tests": "C"
 },
 "184": {
  "text": "Mass air flow (MAF) higher than expected",
  "tests": "C"
 },
 "185": {
  "text": "Mass air flow (MAF) lower than expected",
  "tests": "C"
 },
 "186": {
  "text": "Injector on-time higher than expected",
  "tests": "C"
 },
 "187": {
  "text": "Injector on-time lower than expected",
  "tests": "C"
 },
 "188": {
  "text": "Running RICH at part throttle: fuel correction at its lean limit (second sensor)",
  "tests": "C"
 },
 "189": {
  "text": "Running LEAN at part throttle: fuel correction at its rich limit (second sensor)",
  "tests": "C"
 },
 "191": {
  "text": "Running RICH at idle: fuel correction at its lean limit (second sensor)",
  "tests": "C"
 },
 "192": {
  "text": "Running LEAN at idle: fuel correction at its rich limit (second sensor)",
  "tests": "C"
 },
 "211": {
  "text": "Profile ignition pickup (PIP) circuit failure: distributor pickup / ignition module",
  "tests": "C"
 },
 "212": {
  "text": "Loss of ignition diagnostic (IDM) input, or SPOUT circuit grounded",
  "tests": "C"
 },
 "213": {
  "text": "Spark output (SPOUT) circuit open: check the SPOUT connector at the distributor",
  "tests": "R"
 },
 "214": {
  "text": "Cylinder identification (CID) circuit failure",
  "tests": "C"
 },
 "215": {
  "text": "Coil 1 primary circuit failure (distributorless engines only)",
  "tests": "C"
 },
 "216": {
  "text": "Coil 2 primary circuit failure (distributorless engines only)",
  "tests": "C"
 },
 "217": {
  "text": "Coil 3 primary circuit failure (distributorless engines only)",
  "tests": "C"
 },
 "218": {
  "text": "Loss of ignition diagnostic (IDM) signal, left side",
  "tests": "C"
 },
 "219": {
  "text": "Spark timing defaulted to 10 degrees BTDC: SPOUT circuit open",
  "tests": "C"
 },
 "222": {
  "text": "Loss of ignition diagnostic (IDM) signal, right side",
  "tests": "C"
 },
 "223": {
  "text": "Loss of dual plug inhibit (DPI) control",
  "tests": "C"
 },
 "224": {
  "text": "Erratic ignition diagnostic (IDM) input to the computer",
  "tests": "C"
 },
 "225": {
  "text": "Knock not sensed during the throttle-snap test",
  "tests": "R"
 },
 "226": {
  "text": "Ignition diagnostic (IDM) signal not received",
  "tests": "O"
 },
 "311": {
  "text": "Air injection (Thermactor) inoperative, right side",
  "tests": "R"
 },
 "312": {
  "text": "Air injection (Thermactor) going upstream during the self-test",
  "tests": "R"
 },
 "313": {
  "text": "Air injection (Thermactor) not bypassed during the self-test",
  "tests": "R"
 },
 "314": {
  "text": "Air injection (Thermactor) inoperative, left side",
  "tests": "R"
 },
 "326": {
  "text": "EGR pressure feedback (PFE/DPFE) voltage lower than expected",
  "tests": "RC"
 },
 "327": {
  "text": "EGR pressure feedback (PFE/DPFE) circuit voltage below minimum",
  "tests": "ORC"
 },
 "328": {
  "text": "EGR closed-valve voltage lower than expected",
  "tests": "ORC"
 },
 "332": {
  "text": "Not enough EGR flow detected",
  "tests": "RC"
 },
 "334": {
  "text": "EGR closed-valve voltage higher than expected",
  "tests": "ORC"
 },
 "335": {
  "text": "EGR pressure feedback (PFE/DPFE) voltage out of self-test range",
  "tests": "O"
 },
 "336": {
  "text": "EGR pressure feedback (PFE) voltage higher than expected",
  "tests": "RC"
 },
 "337": {
  "text": "EGR pressure feedback (PFE/DPFE) circuit voltage above maximum",
  "tests": "ORC"
 },
 "338": {
  "text": "Coolant temperature lower than normal: thermostat stuck open?",
  "tests": "C"
 },
 "339": {
  "text": "Coolant temperature higher than normal: overheating",
  "tests": "C"
 },
 "341": {
  "text": "Octane adjust service pin in use, or circuit open",
  "tests": "O"
 },
 "411": {
  "text": "Could not control rpm during the engine-running low rpm check",
  "tests": "R"
 },
 "412": {
  "text": "Could not control rpm during the engine-running high rpm check",
  "tests": "R"
 },
 "452": {
  "text": "Not enough signal from the vehicle speed sensor (VSS)",
  "tests": "C"
 },
 "511": {
  "text": "Engine computer ROM test failure",
  "tests": "O"
 },
 "512": {
  "text": "Engine computer keep-alive memory test failure (also set after the battery is disconnected)",
  "tests": "C"
 },
 "513": {
  "text": "Engine computer internal voltage failure",
  "tests": "C"
 },
 "519": {
  "text": "Power steering pressure switch circuit open",
  "tests": "O"
 },
 "521": {
  "text": "Power steering pressure switch did not change during the running test",
  "tests": "R"
 },
 "522": {
  "text": "Not in Park or Neutral during the key-on test",
  "tests": "O"
 },
 "524": {
  "text": "Low speed fuel pump circuit open (battery to computer)",
  "tests": "OC"
 },
 "525": {
  "text": "In gear, or A/C on, during the self-test",
  "tests": "O"
 },
 "526": {
  "text": "Neutral pressure switch circuit closed, or A/C on",
  "tests": "O"
 },
 "527": {
  "text": "Neutral drive switch circuit open, or A/C on",
  "tests": "O"
 },
 "528": {
  "text": "Clutch switch circuit failure",
  "tests": "C"
 },
 "529": {
  "text": "Data communications link (DCL) or engine computer circuit failure",
  "tests": "C"
 },
 "533": {
  "text": "Data communications link (DCL) or electronic instrument cluster circuit failure",
  "tests": "C"
 },
 "536": {
  "text": "Brake on/off switch circuit failure, or brake not pressed during the running test",
  "tests": "RC"
 },
 "538": {
  "text": "Not enough rpm change during the throttle-snap test, or operator error",
  "tests": "R"
 },
 "539": {
  "text": "A/C or defrost on during the key-on test",
  "tests": "O"
 },
 "542": {
  "text": "Fuel pump secondary circuit failure",
  "tests": "OC"
 },
 "543": {
  "text": "Fuel pump secondary circuit failure",
  "tests": "OC"
 },
 "551": {
  "text": "Idle air solenoid (IAS/IAC) circuit failure",
  "tests": "O"
 },
 "552": {
  "text": "Air management 1 (AIR bypass) solenoid circuit failure",
  "tests": "O"
 },
 "553": {
  "text": "Air management 2 (AIR diverter) solenoid circuit failure",
  "tests": "O"
 },
 "554": {
  "text": "Fuel pressure regulator control (FPRC) solenoid circuit failure",
  "tests": "O"
 },
 "556": {
  "text": "Fuel pump relay primary circuit failure",
  "tests": "OC"
 },
 "557": {
  "text": "Fuel pump primary circuit failure",
  "tests": "OC"
 },
 "558": {
  "text": "EGR vacuum regulator (EVR) solenoid circuit failure",
  "tests": "O"
 },
 "559": {
  "text": "A/C on (ACON) relay circuit failure",
  "tests": "O"
 },
 "563": {
  "text": "High speed electric fan (HEDF) circuit failure",
  "tests": "O"
 },
 "564": {
  "text": "Electric fan (EDF) circuit failure",
  "tests": "O"
 },
 "565": {
  "text": "Canister purge (CANP) solenoid circuit failure",
  "tests": "O"
 },
 "566": {
  "text": "3-4 shift solenoid circuit failure",
  "tests": "O"
 },
 "617": {
  "text": "Transmission 1-2 shift error",
  "tests": "C"
 },
 "618": {
  "text": "Transmission 2-3 shift error",
  "tests": "C"
 },
 "619": {
  "text": "Transmission 3-4 shift error",
  "tests": "C"
 },
 "621": {
  "text": "Transmission shift solenoid 1 (SS1) circuit failure",
  "tests": "O"
 },
 "622": {
  "text": "Transmission shift solenoid 2 (SS2) circuit failure",
  "tests": "O"
 },
 "624": {
  "text": "Transmission electronic pressure control (EPC) solenoid or driver circuit failure",
  "tests": "OC"
 },
 "625": {
  "text": "Transmission EPC driver open in the computer",
  "tests": "O"
 },
 "626": {
  "text": "Transmission coast clutch solenoid circuit failure",
  "tests": "O"
 },
 "627": {
  "text": "Torque converter clutch solenoid circuit failure",
  "tests": "OC"
 },
 "628": {
  "text": "Torque converter lock-up failure: excessive clutch slip",
  "tests": "OC"
 },
 "629": {
  "text": "Torque converter clutch control or lock-up solenoid circuit failure",
  "tests": "O"
 },
 "631": {
  "text": "Overdrive cancel indicator light circuit failure",
  "tests": "O"
 },
 "632": {
  "text": "Overdrive cancel switch did not change during the running test",
  "tests": "R"
 },
 "633": {
  "text": "4x4 switch closed during the self-test",
  "tests": "O"
 },
 "634": {
  "text": "Transmission range (MLP) sensor voltage out of range, or A/C on",
  "tests": "C"
 },
 "636": {
  "text": "Transmission fluid temperature (TOT) out of self-test range: transmission not warm?",
  "tests": "OR"
 },
 "637": {
  "text": "Transmission fluid temperature (TOT) sensor voltage above maximum",
  "tests": "OC"
 },
 "638": {
  "text": "Transmission fluid temperature (TOT) sensor voltage below minimum",
  "tests": "OC"
 },
 "639": {
  "text": "Not enough signal from the transmission speed sensor",
  "tests": "RC"
 },
 "641": {
  "text": "Transmission shift solenoid 3 (SS3) circuit failure",
  "tests": "O"
 },
 "643": {
  "text": "Torque converter clutch control circuit failure",
  "tests": "OC"
 },
 "645": {
  "text": "Wrong gear ratio in 1st",
  "tests": "C"
 },
 "646": {
  "text": "Wrong gear ratio in 2nd",
  "tests": "C"
 },
 "647": {
  "text": "Wrong gear ratio in 3rd",
  "tests": "C"
 },
 "648": {
  "text": "Wrong gear ratio in 4th",
  "tests": "C"
 },
 "649": {
  "text": "Transmission EPC range failure",
  "tests": "C"
 },
 "651": {
  "text": "Transmission EPC circuit failure",
  "tests": "C"
 },
 "652": {
  "text": "Modulated converter clutch solenoid output circuit error",
  "tests": "O"
 },
 "654": {
  "text": "Transmission range (MLP) sensor not showing Park",
  "tests": ""
 },
 "656": {
  "text": "Torque converter clutch continuous slip error",
  "tests": ""
 },
 "998": {
  "text": "Hard fault present (limp-home mode): running test cancelled. Fix the key-on codes first",
  "tests": "R"
 }
};

export const OPERATOR_STEP_CODES = {
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
 "522": "put it in Park, then redo the test"
};

export function describe(code) {
  const entry = CODES[code];
  if (entry) return entry.text;
  if (code.length === 2) return "two-digit code: this computer uses the older 2-digit list, look it up there";
  return "not in the 3-digit table: per Probst, a code not listed doesn't apply to this vehicle. Check the decode";
}

export function testsFor(code) {
  return CODES[code] ? CODES[code].tests : "";
}
