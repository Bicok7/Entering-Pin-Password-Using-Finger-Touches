#include <WiFi.h>
#include <ESPAsyncWebServer.h>

const char* ssid     = "DESKTOP-REQJG4M 2894";
const char* password = "y9993:G6";

// LED pin sesuai urutan: thumb, index, middle, ring, pinky
const int greenLedPin = 14;
const int pins[] = {27, 26, 25, 33, 32};
const char* names[] = {"thumb", "index", "middle", "ring", "pinky"};
const char* urls_on[]  = {
  "/led/thumb/on", "/led/index/on", "/led/middle/on", "/led/ring/on", "/led/pinky/on"
};
const char* urls_off[] = {
  "/led/thumb/off", "/led/index/off", "/led/middle/off", "/led/ring/off", "/led/pinky/off"
};

AsyncWebServer server(80);    

void setup() {
  Serial.begin(115200);

  // Setup pin LED
  for (int i = 0; i < 5; i++) {
    pinMode(pins[i], OUTPUT);
    digitalWrite(pins[i], LOW);
  } 

  // WiFi connect
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP: " + WiFi.localIP().toString());  

  // Buat route untuk ON/OFF tiap LED
  for (int i = 0; i < 5; i++) {
    server.on(urls_on[i], HTTP_GET, [i](AsyncWebServerRequest *req) {
      digitalWrite(pins[i], HIGH);
      req->send(200, "text/plain", String(names[i]) + " ON");
    });

    server.on(urls_off[i], HTTP_GET, [i](AsyncWebServerRequest *req) {
      digitalWrite(pins[i], LOW);
      req->send(200, "text/plain", String(names[i]) + " OFF");
    });
  }

  server.begin();
  Serial.println("Server started");
}

void loop() {
  // Nothing here
}
