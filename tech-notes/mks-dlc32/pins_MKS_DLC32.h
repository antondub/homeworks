#pragma once

/**
 * MKS DLC32 V2.1 / V2.2, один экструдер.
 *
 * XY — внешние TB6600 на разъёмах S/D.
 * Экструдер — съёмный драйвер в сокете Z, мотор на клемме Z-MOTOR.
 * Ось Z — TB6600 с EXP1: STEP пин 7 (IO25), DIR пин 5 (IO26).
 * Экструдер — съёмный драйвер в сокете Z (131/132).
 * Z ENA — вместе с X и Y, разъём бипера (135). Транзистор не выпаивать.
 * Экструдер ENA — XYZ_EN (128), ножку EN оставить в сокете.
 * Пин E разъёмов X/Y к TB6600 не подключать.
 * ШИМ хотэнда — EXP1 пин 4 (IO27). Реле стола — EXP1 пин 3 (IO5), U8 инвертирует, HEATER_BED_INVERTING true.
 * Обдув — SPINDLE (IO32). TTL пустой.
 * Щуп — Probe J12 пин 2 (IO22). Концевики: J9 IO36, J10 IO35, J11 IO34.
 * Хотэнд — MAX6675 на EXP2: SCK IO18, DO IO19, CS на LCD_MOSI IO23.
 * Термистор стола — EXP1 пин 8 (IO33).
 * Экрана на плате нет.
 *
 * Куда класть: Marlin/src/pins/esp32/pins_MKS_DLC32.h
 * В boards.h: #define BOARD_MKS_DLC32 7012
 * В pins.h:   #elif MB(MKS_DLC32)
 *               #include "esp32/pins_MKS_DLC32.h"
 *
 */

#include "env_validate.h"

#if HAS_MULTI_HOTEND || E_STEPPERS > 1
  #error "Эта сборка DLC32 — один хотэнд и один экструдер."
#endif

#define BOARD_INFO_NAME "MKS DLC32"

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
#define X_ENABLE_PIN                         135  // бипер, все TB6600

#define Y_STEP_PIN                           133
#define Y_DIR_PIN                            134
#define Y_ENABLE_PIN                         135

#define Z_STEP_PIN                            25  // EXP1 пин 7 → TB6600 PUL+
#define Z_DIR_PIN                             26  // EXP1 пин 5 → TB6600 DIR+
#define Z_ENABLE_PIN                         135

#define E0_STEP_PIN                          131  // сокет Z, STEP
#define E0_DIR_PIN                           132  // сокет Z, DIR
#define E0_ENABLE_PIN                        128  // XYZ_EN, только экструдер

#define X_STOP_PIN                            36
#define Y_STOP_PIN                            35
#define Z_STOP_PIN                            34
#define Z_MIN_PROBE_PIN                       22  // J12 пин 2, магнитный щуп

#define TEMP_0_CS_PIN                         23  // EXP2 пин 6, LCD_MOSI → CS MAX6675
#define TEMP_0_SCK_PIN                        18  // EXP2 пин 2, LCD_SCK
#define TEMP_0_MISO_PIN                       19  // EXP2 пин 1, LCD_MISO / DO
#define TEMP_0_MOSI_PIN              TEMP_0_SCK_PIN  // провода MOSI нет; только шаблон SoftSPI
#define TEMP_0_PIN                TEMP_0_CS_PIN
#define TEMP_BED_PIN                          33  // ADC1, EXP1 пин 8

#define HEATER_0_PIN                          27  // EXP1 пин 4, ШИМ хотэнда
#define HEATER_BED_PIN                         5  // EXP1 пин 3, U8 инвертирует
#define FAN0_PIN                              32  // SPINDLE, обдув детали

#define HEATER_0_INVERTING                 false
#define HEATER_BED_INVERTING                true  // U8: GPIO5 низкий -> на разъёме высокий

#define SD_SCK_PIN                            14
#define SD_MISO_PIN                           12
#define SD_MOSI_PIN                           13
#define SDSS                                  15
#define SD_SS_PIN                          SDSS

#define SD_DETECT_PIN                         39
