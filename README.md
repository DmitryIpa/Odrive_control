# Odrive_control
This repository contains a procedure for setting up an odrive, as well as an example of how to control an odrive.
Версия odrivetool v0.6.7
## ИНСТРУКЦИЯ ПО НАСТРОЙКЕ ODrive v3.6
# 1. Запускаем команду ниже для того, чтобы сбросить ODrive до настроек по умолчанию:

...
  odrv0.erase_configuration()
...

# 2. Задаём параметры моторов для калибровки:
...
  odrv0.axis0.motor.config.current_control_bandwidth = 1000
  odrv0.axis0.motor.config.pole_pairs = 8
...

При подаче 48В напряжения на ODrive задаём:
...
  odrv0.axis0.motor.config.resistance_calib_max_voltage = 24
...
Если подавать напряжение 24В - уменьшить параметр в два раза! Параметр должен быть меньше половины напряжения питания всего ODrive.

Остальные параметры мотора задаются или подбираются в соответствии со спецификацией вашего мотора:
...
  odrv0.axis0.motor.config.calibration_current = 12
  odrv0.axis0.motor.config.current_lim_margin = 8
  odrv0.axis0.motor.config.requested_current_range = 60
  odrv0.axis0.motor.config.torque_lim = "inf"
  odrv0.axis0.motor.config.torque_constant = 2.2
  odrv0.axis0.motor.config.motor_type = MotorType.HIGH_CURRENT
...

# 3) Задаём параметры энкодеров для калибровки
