/**
 * Правки Marlin/Configuration_adv.h.
 * Пауза DIR у TB6600 по даташиту от 5 мкс. Завод Marlin для TB6600 короче.
 * Таймаут 0: после старта драйверы остаются включёнными. M84 их отпускает.
 * THERMAL_PROTECTION_HOTENDS и THERMAL_PROTECTION_BED не выключать.
 * Wi-Fi: WIFISUPPORT и WEBSUPPORT, не вместе с ESP3D_WIFISUPPORT.
 * WIFI_SSID и WIFI_PWD подставить свои: без сети Marlin перезапускает плату.
 */

#define MINIMUM_STEPPER_POST_DIR_DELAY 5000
#define MINIMUM_STEPPER_PRE_DIR_DELAY  5000
#define MINIMUM_STEPPER_PULSE_NS       4000
#define MAXIMUM_STEPPER_RATE           100000

#define DEFAULT_STEPPER_TIMEOUT_SEC 0

#define WIFISUPPORT
#define WEBSUPPORT
#define WIFI_SSID "CHANGE_ME"
#define WIFI_PWD  "CHANGE_ME"
