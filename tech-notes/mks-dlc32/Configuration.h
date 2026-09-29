/**
 * Правки Marlin bugfix-2.1.x, файл Marlin/Configuration.h.
 * Это не полный Configuration.h. В дереве Marlin меняются эти строки.
 * Экрана нет: FYSETC_MINI_12864_2_1 и NEOPIXEL_LED выключить — это хвост Cheetah.
 * Щуп на J12, не на Z-min: Z_MIN_PROBE_USES_Z_MIN_ENDSTOP_PIN выключить.
 * Хотэнд — MAX6675 (тип -2). Стол — NTC на IO33. Wi-Fi — WIFISUPPORT и WEBSUPPORT.
 */

#define MOTHERBOARD BOARD_MKS_DLC32
#define CUSTOM_MACHINE_NAME "DLC32 Printer"

#define SERIAL_PORT 0
#define BAUDRATE 250000
#define SERIAL_PORT_2 -1
#define BAUDRATE_2 250000

#define X_DRIVER_TYPE  TB6600
#define Y_DRIVER_TYPE  TB6600
#define Z_DRIVER_TYPE  TB6600
#define E0_DRIVER_TYPE A4988

#define EXTRUDERS 1
#define DEFAULT_NOMINAL_FILAMENT_DIA 1.75

#define TEMP_SENSOR_0 -2
#define TEMP_SENSOR_BED 1

#define PIDTEMP
// PIDTEMPBED оставить выключенным: стол на реле.

#define HEATER_0_MAXTEMP 275
#define BED_MAXTEMP 120

#define PREVENT_COLD_EXTRUSION
#define EXTRUDE_MINTEMP 170

#define X_MIN_ENDSTOP_HIT_STATE HIGH
#define Y_MIN_ENDSTOP_HIT_STATE HIGH
#define Z_MIN_ENDSTOP_HIT_STATE HIGH
#define Z_MIN_PROBE_ENDSTOP_HIT_STATE LOW
//#define Z_MIN_PROBE_USES_Z_MIN_ENDSTOP_PIN

#define FIX_MOUNTED_PROBE
#define NOZZLE_TO_PROBE_OFFSET { 0, 0, 0 }

// Ремень GT2, шкив 20 зуб., микрошаг 16 → 80.
// Винт Z T8x8, микрошаг 16 на TB6600 → 400.
// Экструдер: steps/mm под микрошаг DIP сокета Z, стартовое 93 для прямого привода.
#define DEFAULT_AXIS_STEPS_PER_UNIT   { 80, 80, 400, 93 }
#define DEFAULT_MAX_FEEDRATE          { 200, 200, 5, 25 }
#define DEFAULT_MAX_ACCELERATION      { 500, 500, 100, 1000 }
#define DEFAULT_ACCELERATION          500
#define DEFAULT_RETRACT_ACCELERATION  1000
#define DEFAULT_TRAVEL_ACCELERATION   500

#define INVERT_X_DIR false
#define INVERT_Y_DIR false
#define INVERT_Z_DIR false
#define INVERT_E0_DIR false

// X/Y/Z TB6600 с бипера: высокий на 595 включает транзистор и гасит оптопару.
// Экструдер без транзистора, низкий на XYZ_EN включает stepstick.
#define X_ENABLE_ON 0
#define Y_ENABLE_ON 0
#define Z_ENABLE_ON 0
#define E_ENABLE_ON 0

#define X_HOME_DIR -1
#define Y_HOME_DIR -1
#define Z_HOME_DIR -1

#define X_BED_SIZE 200
#define Y_BED_SIZE 200
#define Z_MAX_POS 200

#define SDSUPPORT
#define EEPROM_SETTINGS
//#define FYSETC_MINI_12864_2_1
//#define NEOPIXEL_LED
