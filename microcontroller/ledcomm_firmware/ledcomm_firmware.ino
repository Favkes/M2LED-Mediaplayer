#include <FastLED.h>

#define LED_PIN     13
#define NUM_LEDS    185
#define MAX_PACKET_SIZE 800

CRGB leds[NUM_LEDS];
byte packet[MAX_PACKET_SIZE];
int packet_index = 0;
bool in_packet = false;


void processPacket(byte* data, int len) {
  if (len < 1) return;

  int count = data[0];
  if (len != 1 + count * 4) return;
  
  for (int i=0; i<count; i++) {
    int j = i*4;
    int index = data[++j];
    int r = data[++j];
    int g = data[++j];
    int b = data[++j];
    if (index >= 0 && index < NUM_LEDS) {
      leds[index] = CRGB(r, g, b);
    } else {
      if (index == 254) {
        FastLED.show();
      } else
      if (index == 255) {
        FastLED.clear();
      }
    }
  }
}


void setup() {
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.show();
  Serial.begin(115200);
}


bool is_on = 0;
void loop() {
  int tmp = 4*(is_on++);
  leds[0] = CRGB(tmp, tmp, tmp);
  while (Serial.available()) {
    byte b = Serial.read();

    if (!in_packet) {
      if (b == 0xAA) {  // start
        in_packet = true;
        packet_index = 0;
      }
    } else {
      if (b == 0x55) {  // end
        processPacket(packet, packet_index);
        in_packet = false;
      } else {
        if (packet_index < MAX_PACKET_SIZE) {
          packet[packet_index++] = b;
        }
        else {  // overflow -> reset
          in_packet = false;
        }
      }
    }
  }
}





