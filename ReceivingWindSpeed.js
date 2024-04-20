const { createBluetooth } = require( 'node-ble' );

// TODO: Replace this with your Arduino's Bluetooth address
// as found by running the 'scan on' command in bluetoothctl
const ARDUINO_BLUETOOTH_ADDR = '0F:6C:A4:0D:7F:B4';

const UART_SERVICE_UUID      = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E';
const TX_CHARACTERISTIC_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E';
const RX_CHARACTERISTIC_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E';

const ESS_SERVICE_UUID       = '0000181a-0000-1000-8000-00805f9b34fb';
const WIND_CHAR_UUID         = '00002a70-0000-1000-8000-00805f9b34fb';

async function main( )
{
    // Reference the BLE adapter and begin device discovery...
    const { bluetooth, destroy } = createBluetooth();
    const adapter = await bluetooth.defaultAdapter();
    const discovery =  await adapter.startDiscovery();
    console.log( 'discovering...' );

    // Attempt to connect to the device with specified BT address
    const device = await adapter.waitDevice( ARDUINO_BLUETOOTH_ADDR.toUpperCase() );
    console.log( 'found device. attempting connection...' );
    await device.connect();
    console.log( 'connected to device!' );

    // Get references to the desired UART service and its characteristics
    const gattServer = await device.gatt();
    const uartService = await gattServer.getPrimaryService( UART_SERVICE_UUID.toLowerCase() );
    const txChar = await uartService.getCharacteristic( TX_CHARACTERISTIC_UUID.toLowerCase() );
    const rxChar = await uartService.getCharacteristic( RX_CHARACTERISTIC_UUID.toLowerCase() );

    // Get references to the desired ESS service and its temparature characteristic.
    // TODO

    const essServer = await device.gatt();
    const windService = await essServer.getPrimaryService(ESS_SERVICE_UUID.toLowerCase() );
    const windChar = await windService.getCharacteristic( WIND_CHAR_UUID.toLowerCase() );

    // Register for notifications on the RX characteristic
    await rxChar.startNotifications( );

    // Callback for when data is received on RX characteristic
    rxChar.on( 'valuechanged', buffer =>
    {
        console.log('Received: ' + buffer.toString());
    });

    // Register for notifications on the temperature characteristic
    // TODO 

    await windChar.startNotifications( );

    // Callback for when data is received on the temp characteristic
    // TODO 
    

    // listener for temperature
    windChar.on( 'valuechanged', buffer =>
    {   
        // checks to format wind speed correctly once received
        let windVal = buffer.readUInt16LE(0);
        if(windVal == 0) {
            windFormatted = "0.00";
        }
        else if(windVal < 100) {
            windVal = windVal.toString();
            windFormatted = "0." + windVal;
        }
        else if(windVal < 1000) {
            windVal = windVal.toString();
            windFormatted = windVal.substring(0,1) + "." + windVal.substring(1);
        }
        else {
            windVal = windVal.toString();
            windFormatted = windVal.substring(0,2) + "." + windVal.substring(2);

        }
        console.log("Wind Speed Received: " + windFormatted); // print temp val to console
    });
    
    // Set up listener for console input.
    // When console input is received, write it to TX characteristic
    const stdin = process.openStdin( );
    stdin.addListener( 'data', async function( d )
    {
        let inStr = d.toString( ).trim( );

        // Disconnect and exit if user types 'exit'
        if (inStr === 'exit')
        {
            console.log( 'disconnecting...' );
            await device.disconnect();
            console.log( 'disconnected.' );
            destroy();
            process.exit();
        }

        // Specification limits packets to 20 bytes; truncate string if too long.
        inStr = (inStr.length > 20) ? inStr.slice(0,20) : inStr;

        // Attempt to write/send value to TX characteristic
        await txChar.writeValue(Buffer.from(inStr)).then(() =>
        {
            console.log('Sent: ' + inStr);
        });
    });


// firebase stuff: 

var firebase = require('firebase/app');
var admin = require('firebase-admin');

var serviceAccount = require('/home/pi/Desktop/FinalProject/credentials.json');

const {getDatabase, ref, onValue, set, update, get, DataSnapshot, child} = require('firebase/database');
const { getAuth } = require("firebase-admin/auth"); 

const firebaseConfig = {
    apiKey: "AIzaSyCdaEOfC_g2YZJcF-QJzNIs_KXIVSCWyH4",
    authDomain: "finalproject-89a6e.firebaseapp.com",
    projectId: "finalproject-89a6e",
    storageBucket: "finalproject-89a6e.appspot.com",
    messagingSenderId: "494748373915",
    appId: "1:494748373915:web:b104a7efc5e9ebb142873e",
    measurementId: "G-B2T1J58M80",
    databaseURL: "https://finalproject-89a6e-default-rtdb.firebaseio.com",
    };

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: "https://finalproject-89a6e-default-rtdb.firebaseio.com",
});

const database = admin.database();
const dRef = database.ref();

var counter = 0;

database.ref('Data/').set({
    WindSpeed0: 3, 
    WindSpeed1: 3,
    WindSpeed2: 3, 
    WindSpeed3: 3, 
    WindSpeed4: 3, 
    WindSpeed5: 3, 
    WindSpeed6: 10, 
    WindSpeed7: 3, 
    WindSpeed8: 3, 
    WindSpeed9: 3, 
});

database.ref('Start Recording/').set({Start: false});

  const updateStartRef = database.ref('Start Recording/');
  

  updateStartRef.on("child_changed", snapshot => {
    const state = snapshot.val();
    console.log(state);
    if(state) {
        counter = 0;
        recordWindSpeed();
        const recordingUpdate = {}
        recordingUpdate['Start Recording/Start/'] = false;
        database.ref().update(recordingUpdate);


    }
  })

  function recordWindSpeed() {
    if(counter < 10){
        var updates = {};
        var updatePosition = 'Data/WindSpeed' + counter.toString() + "/";
        updates[updatePosition] = parseFloat(windFormatted);
        database.ref().update(updates);
        console.log('Sending wind speed to database');
        setTimeout(recordWindSpeed, 500);
        counter++;
    }
  }
}

main().then((ret) =>
{
    if (ret) console.log( ret );
}).catch((err) =>
{
    if (err) console.error( err );
});
