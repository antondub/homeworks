/**
 * Правки Marlin bugfix-2.1.x, файл Marlin/Configuration.h.
 * Это не полный Configuration.h. В дереве Marlin меняются эти строки.
 * Панель: раскомментировать тот же вариант, что в pins_MKS_DLC32.h.
 * Wi-Fi не включать: термистор стола на ADC2 (IO4).
 */

#define MOTHERBOARD BOARD_MKS_DLC32
#define CUSTOM_MACHINE_NAME "DLC32 Printer"

#define SERIAL_PORT 0
#define BAUDRATE 250000

#define X_DRIVER_TYPE  TB6600
#define Y_DRIVER_TYPE  TB6600
#define Z_DRIVER_TYPE  TB6600
#define E0_DRIVER_TYPE A4988

#define EXTRUDERS 1
#define DEFAULT_NOMINAL_FILAMENT_DIA 1.75

#define TEMP_SENSOR_0 1
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

#define X_HOME_DIR -1
#define Y_HOME_DIR -1
#define Z_HOME_DIR -1

#define X_BED_SIZE 200
#define Y_BED_SIZE 200
#define Z_MAX_POS 200

#define SDSUPPORT
#define EEPROM_SETTINGS

// --- панель 12864, вместе с ANET_A8_12864 в pins ---
//#define ANET_FULL_GRAPHICS_LCD

// --- панель 2004, пять кнопок, вместе с ANET_A8_2004 в pins ---
//#define ULTRA_LCD
//#define LCD_WIDTH 20
//#define LCD_HEIGHT 4
//#define ZONESTAR_LCD
