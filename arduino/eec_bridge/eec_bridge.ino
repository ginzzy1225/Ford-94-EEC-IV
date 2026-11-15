// EEC-IV self-test bridge: USB serial <-> Ford EEC-IV self-test connector.
//
// Turns a 5 V Arduino Nano (or Uno) into a code reader for 1984-1995 Ford EEC-IV engine
// computers, built for a 1994 E-350 motorhome chassis with the 7.5L (460).
//
// The EEC-IV reports its fault codes as pulses: during a self-test it pulls the Self-Test
// Output (STO) line to ground in groups (3 pulses, pause, 2 pulses... = code 32x). A self-test
// starts when the Self-Test Input (STI) line is grounded. This sketch:
//   - grounds STI on command, through optocoupler U2 (so the Nano never touches STI directly)
//   - watches STO through optocoupler U1 and timestamps every change in milliseconds
// The laptop does all the decoding.
//
// Wiring (see docs/wiring.md):
//   D2  <- U1 phototransistor collector (U1 emitter to Nano GND). Low = STO active.
//   D3  -> 470R -> U2 LED anode (U2 LED cathode to Nano GND). High = ground STI.
//   5V  -> 470R -> U1 LED anode; U1 LED cathode -> 1N4148 anode; diode cathode -> STO wire
//   U2 phototransistor collector -> 470R -> STI wire; U2 emitter -> SIG RTN wire
//   Nano GND -> SIG RTN wire (the same wire)
//
// USB protocol, 115200 baud, one line per message:
//   Nano -> laptop
//     EECBRIDGE 1.0           on reset
//     E <ms> <0|1>            STO changed; 1 = active (EEC pulling it low)
//     K <ms> <0|1> <sti>      keepalive every 500 ms: current STO state and STI (0/1)
//     OK STI <0|1>            reply to STI command
//     PONG                    reply to PING
//     WARN STI TIMEOUT        STI was released automatically (see STI_MAX_MS)
//   laptop -> Nano
//     STI 1 / STI 0           ground / release the self-test input
//     PING

const uint8_t STO_PIN = 2;
const uint8_t STI_PIN = 3;
const long USB_BAUD = 115200;
const unsigned long DEBOUNCE_MS = 3;
const unsigned long KEEPALIVE_MS = 500;
// Never leave the self-test input grounded by accident (e.g. the laptop went to sleep).
const unsigned long STI_MAX_MS = 10UL * 60UL * 1000UL;

bool stoActive = false;      // debounced state
bool rawLast = false;
unsigned long rawChangedAt = 0;
unsigned long lastKeepalive = 0;
bool stiOn = false;
unsigned long stiOnAt = 0;
char line[24];
uint8_t lineLen = 0;

bool readSto() { return digitalRead(STO_PIN) == LOW; }

void setSti(bool on) {
  stiOn = on;
  stiOnAt = millis();
  digitalWrite(STI_PIN, on ? HIGH : LOW);
}

void handleLine() {
  line[lineLen] = 0;
  if (strcmp(line, "STI 1") == 0) {
    setSti(true);
    Serial.println(F("OK STI 1"));
  } else if (strcmp(line, "STI 0") == 0) {
    setSti(false);
    Serial.println(F("OK STI 0"));
  } else if (strcmp(line, "PING") == 0) {
    Serial.println(F("PONG"));
  } else if (lineLen > 0) {
    Serial.print(F("ERR "));
    Serial.println(line);
  }
  lineLen = 0;
}

void setup() {
  pinMode(STO_PIN, INPUT_PULLUP);
  pinMode(STI_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  setSti(false);
  Serial.begin(USB_BAUD);
  stoActive = rawLast = readSto();
  Serial.println(F("EECBRIDGE 1.0"));
}

void loop() {
  unsigned long now = millis();

  bool raw = readSto();
  if (raw != rawLast) {
    rawLast = raw;
    rawChangedAt = now;
  }
  if (raw != stoActive && now - rawChangedAt >= DEBOUNCE_MS) {
    stoActive = raw;
    digitalWrite(LED_BUILTIN, stoActive ? HIGH : LOW);  // the Nano's LED flashes the codes too
    Serial.print(F("E "));
    Serial.print(rawChangedAt);  // time the change started, not when the debounce finished
    Serial.print(' ');
    Serial.println(stoActive ? 1 : 0);
  }

  if (now - lastKeepalive >= KEEPALIVE_MS) {
    lastKeepalive = now;
    Serial.print(F("K "));
    Serial.print(now);
    Serial.print(' ');
    Serial.print(stoActive ? 1 : 0);
    Serial.print(' ');
    Serial.println(stiOn ? 1 : 0);
  }

  if (stiOn && now - stiOnAt >= STI_MAX_MS) {
    setSti(false);
    Serial.println(F("WARN STI TIMEOUT"));
  }

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (lineLen) handleLine();
    } else if (lineLen < sizeof(line) - 1) {
      line[lineLen++] = c;
    }
  }
}
