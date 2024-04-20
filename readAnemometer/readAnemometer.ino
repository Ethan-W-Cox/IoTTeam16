#include <ArduinoBLE.h>
#include <Arduino_HTS221.h>
#include <Arduino_LSM9DS1.h>
#include "TimeoutTimer.h"
#define BUFSIZE 20

/*   We'll use the ArduinoBLE library to simulate a basic UART connection 
 *   following this UART service specification by Nordic Semiconductors. 
 *   More: https://learn.adafruit.com/introducing-adafruit-ble-bluetooth-low-energy-friend/uart-service
 */
BLEService uartService("6E400001-B5A3-F393-E0A9-E50E24DCCA9E");
BLEStringCharacteristic txChar("6E400002-B5A3-F393-E0A9-E50E24DCCA9E", BLEWrite, 20 );
BLEStringCharacteristic rxChar("6E400003-B5A3-F393-E0A9-E50E24DCCA9E", BLERead | BLENotify, 20 );

/*  Create a Environmental Sensing Service (ESS) and a 
 *  characteristic for its temperature value.
 */
BLEService essService("181A");
BLEShortCharacteristic windChar("2A70", BLERead | BLENotify );

int interval = 1000;
int analogPin = A1; // currently connect to nothing
int val = 0;  // variable to store the value read
float volts = 0;
float windSpeed = 0;

void setup() 
{
  Serial.begin(9600);
  while(!Serial);

  if ( !BLE.begin() )
  {
    Serial.println("Starting BLE failed!");
    while(1);
  }

  // Get the Arduino's BT address
  String deviceAddress = BLE.address();

  // The device name we'll advertise with.
  BLE.setLocalName("ArduinoBLE Lab3");

  // Get UART service ready.
  BLE.setAdvertisedService( uartService );
  uartService.addCharacteristic( txChar );
  uartService.addCharacteristic( rxChar );
  BLE.addService( uartService );

  // Get ESS service ready.
  essService.addCharacteristic( windChar );
  BLE.addService( essService );

  // Start advertising our new service.
  BLE.advertise();
  Serial.println("Bluetooth device (" + deviceAddress + ") active, waiting for connections...");
}

void loop() 
{
  // Wait for a BLE central device.
  BLEDevice central = BLE.central();

  // If a central device is connected to the peripheral...
  if ( central )
  {
    // Print the central's BT address.
    Serial.print("Connected to central: ");
    Serial.println( central.address() );

    // While the central device is connected...
    while( central.connected() )
    {
      // Get input from user, send to central
      char inputs[BUFSIZE+1];
      if ( getUserInput( inputs, BUFSIZE ) )
      {
        Serial.print("[Send] ");
        Serial.println( inputs );
        rxChar.writeValue( inputs );
      }

      // Receive data from central (if written is true)
      if ( txChar.written() )
      {
        String text = txChar.value();
        Serial.print("[Recv] ");
        Serial.println(text);
        if(text.startsWith("Int: ")) {
          interval = text.substring(5).toInt();
        }
        
      }

      /* 
       *  Emit wind speed per ESS' tempChar.
       *  Per the characteristic spec, temp should be in Celsius 
       *  with a resolution of 0.01 degrees. It should also 
       *  be carried within short.
      */

      val = analogRead(analogPin);  // read the input pin
      volts = val * 0.0032226;
      windSpeed = volts * 20.25 - 8.1; // m/s
      if(volts <= 0.42) {
        windSpeed = 0;
      }
    
      Serial.print("Val: ");
      Serial.print(val);         
      Serial.print("\t");
      Serial.print("Volts: ");
      Serial.print(volts);
      Serial.print("\t");
      Serial.print("Wind Speed (m/s): ");
      Serial.print(windSpeed);
      Serial.println();

      // Cast to desired format; multiply by 100 to keep desired precision.
      short shortSpeed = (short) (windSpeed * 100);

      // Send data to centeral for temperature characteristic.
      windChar.writeValue( shortSpeed );

      // TODO: Should get this Interval from Firebase via Pi via UART
      delay(500);
      
    }
    
    Serial.print("Disconnected from central: ");
    Serial.println( central.address() );
    
  }
}

/**************************************************************************/
/*!
    @brief  Checks for user input (via the Serial Monitor)
            From: https://github.com/adafruit/Adafruit_BluefruitLE_nRF51
*/
/**************************************************************************/
bool getUserInput(char buffer[], uint8_t maxSize)
{
  // timeout in 100 milliseconds
  TimeoutTimer timeout(100);

  memset(buffer, 0, maxSize);
  while( (!Serial.available()) && !timeout.expired() ) { delay(1); }

  if ( timeout.expired() ) return false;

  delay(2);
  uint8_t count=0;
  do
  {
    count += Serial.readBytes(buffer+count, maxSize);
    delay(2);
  } while( (count < maxSize) && (Serial.available()) );
  
  return true;
}
