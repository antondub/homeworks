#pragma once

/**
 * MKS DLC32 V2.1 / V2.2, один экструдер.
 *
 * XY — внешние TB6600 на разъёмах S/D.
 * Экструдер — съёмный драйвер в сокете Z, мотор на клемме Z-MOTOR.
 * Ось Z — TB6600: STEP с BEEPER (135), DIR с EN (128).
 * ENABLE везде -1: бит 128 занят направлением Z.
 *
 * Ножка EN съёмного драйвера отогнута и сидит на GND.
 * Иначе DIR оси Z включает и выключает экструдер.
 *
 * Куда класть: Marlin/src/pins/esp32/pins_MKS_DLC32.h
 * В boards.h: #define BOARD_MKS_DLC32 7012
 * В pins.h:   #elif MB(MKS_DLC32)
 *               #include "esp32/pins_MKS_DLC32.h"
 *
 * Панель Anet: раскомментировать один define и тот же блок в Configuration.h.
 * Шлейф Anet в EXP1 не вставлять.
 */

#include "env_validate.h"

#if HAS_MULTI_HOTEND || E_STEPPERS > 1
  #error "Эта сборка DLC32 — один хотэнд и один экструдер."
#endif

#define BOARD_INFO_NAME "MKS DLC32"

//#define ANET_A8_12864
//#define ANET_A8_2004

#if ENABLED(ANET_A8_12864) && ENABLED(ANET_A8_2004)
  #error "Одна панель: ANET_A8_12864 или ANET_A8_2004."
#endif

#ifndef I2S_STEPPER_STREAM
  #define I2S_STEPPER_STREAM
#endif
#if ENABLED(I2S_STEPPER_STREAM)
  #define I2S_WS                              17
  #define I2S_BCK                             16
  #define I2S_DATA                            21
#endif

// 128 + N — выход 74HC595.
// 0 EN, 1 X_STEP, 2 X_DIR, 3 Z_STEP, 4 Z_DIR, 5 Y_STEP, 6 Y_DIR, 7 BEEPER

#define X_STEP_PIN                           129
#define X_DIR_PIN                            130
#define X_ENABLE_PIN                          -1

#define Y_STEP_PIN                           133
#define Y_DIR_PIN                            134
#define Y_ENABLE_PIN                          -1

#define Z_STEP_PIN                           135  // EXP1 BEEPER → TB6600 PUL+
#define Z_DIR_PIN                            128  // пин E моторного разъёма → TB6600 DIR+
#define Z_ENABLE_PIN                          -1

#define E0_STEP_PIN                          131  // сокет Z, STEP
#define E0_DIR_PIN                           132  // сокет Z, DIR
#define E0_ENABLE_PIN                         -1

#define X_STOP_PIN                            36
#define Y_STOP_PIN                            35
#define Z_STOP_PIN                            34

#define TEMP_0_PIN                            33  // ADC1, хотэнд, EXP1 IO33
#define TEMP_BED_PIN                           4  // ADC2, стол, I2C IO4. Wi-Fi выключен.

#define HEATER_0_PIN                          26  // EXP1 IO26, ШИМ хотэнда
#define HEATER_BED_PIN                         5  // EXP1 IO5, реле стола
#define FAN0_PIN                              32  // TTL S, обдув

#define HEATER_0_INVERTING                 false
#define HEATER_BED_INVERTING               false

#define SD_SCK_PIN                            14
#define SD_MISO_PIN                           12
#define SD_MOSI_PIN                           13
#define SD_SS_PIN                             15

#if ENABLED(ANET_A8_2004)
  #define SD_DETECT_PIN                       -1  // IO39 занят кнопками
  #define LCD_PINS_RS                         25
  #define LCD_PINS_EN                         27
  #define LCD_PINS_D4                         18
  #define LCD_PINS_D5                         19
  #define LCD_PINS_D6                         23
  #define LCD_PINS_D7                          2
  #define ADC_KEYPAD_PIN                      39
#elif ENABLED(ANET_A8_12864)
  #define SD_DETECT_PIN                       39
  #define LCD_PINS_RS                         25  // EXP1 IO25, 5 В
  #define LCD_PINS_EN                         27  // EXP1 IO27, 5 В
  #define LCD_PINS_D4                         18  // EXP2 пин 2
  #define BTN_EN1                             23  // EXP2 пин 6
  #define BTN_EN2                             19  // EXP2 пин 1
  #define BTN_ENC                             22  // Probe S, клик энкодера
#else
  #define SD_DETECT_PIN                       39
#endif
