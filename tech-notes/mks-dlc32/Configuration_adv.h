/**
 * Правки Marlin/Configuration_adv.h.
 * Пауза DIR у TB6600 по даташиту от 5 мкс. Завод Marlin для TB6600 короче.
 * Таймаут 0: ENA никуда не приходит, драйверы держат вал, пока есть питание.
 * THERMAL_PROTECTION_HOTENDS и THERMAL_PROTECTION_BED не выключать.
 */

#define MINIMUM_STEPPER_POST_DIR_DELAY 5000
#define MINIMUM_STEPPER_PRE_DIR_DELAY  5000
#define MINIMUM_STEPPER_PULSE_NS       4000
#define MAXIMUM_STEPPER_RATE           100000

#define DEFAULT_STEPPER_TIMEOUT_SEC 0
