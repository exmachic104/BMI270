# -*- coding: utf-8 -*-
import spidev
import time
import ast

spi = spidev.SpiDev()
spi.open(1, 2)
spi.mode = 0
spi.max_speed_hz = 50000

spi.xfer2([0x80|0x00,0x00,0x00])
if(spi.xfer2([0x80|0x21,0x00,0x00])[2]!=1):
    #disable PWR_CONF
    spi.xfer3([0x7C,0x00])
    #wait at least 450μs
    time.sleep(0.001)
    #START INIT_CTRL
    spi.xfer3([0x59,0x00])
    # JSONファイルから読み込む
    with open('bmi270_init.json', 'r') as f:
        data = f.read()
    # 文字列を配列に変換
    data_array = ast.literal_eval(data)
    # アドレス0x5Eにバースト書き込み
    address = 0x5E
    spi.xfer3([address] + data_array)
    #COMPLETE INIT_CTRL
    spi.xfer3([0x59,0x01])
    
    #enable temp, acc, gyro
    spi.xfer2([0x7D,0x0E])
    #set acc_conf as same as reset
    spi.xfer2([0x40,0xA8])
    #set gyro_conf as same as reset
    spi.xfer2([0x42,0xA9])
    #set pwr_conf as same sa reset
    spi.xfer2([0x7C,0x03])
    
    f.close()

try:
    while True:
        accel_x_block = spi.xfer2([0x80|0x0C,0x00,0x00,0x00])
        accel_y_block = spi.xfer2([0x80|0x0E,0x00,0x00,0x00])
        accel_z_block = spi.xfer2([0x80|0x10,0x00,0x00,0x00])
        accel_x_data = accel_x_block[2] | accel_x_block[3] << 8
        accel_y_data = accel_y_block[2] | accel_y_block[3] << 8
        accel_z_data = accel_z_block[2] | accel_z_block[3] << 8
        if(accel_x_data & 0x8000):
            accel_x_data = ((~accel_x_data & 0xFFFF) + 1)* -1
        accel_x_value = 8 * 9.8 * accel_x_data / 0x7FFF
        if(accel_y_data & 0x8000):
            accel_y_data = ((~accel_y_data & 0xFFFF) + 1)* -1
        accel_y_value = 8 * 9.8 * accel_y_data / 0x7FFF
        if(accel_z_data & 0x8000):
            accel_z_data = ((~accel_z_data & 0xFFFF) + 1)* -1
        accel_z_value = 8 * 9.8 * accel_z_data / 0x7FFF
        
        gyro_x_block = spi.xfer2([0x80|0x12,0x00,0x00,0x00])
        gyro_y_block = spi.xfer2([0x80|0x14,0x00,0x00,0x00])
        gyro_z_block = spi.xfer2([0x80|0x16,0x00,0x00,0x00])
        gyro_x_data = gyro_x_block[2] | gyro_x_block[3] << 8
        gyro_y_data = gyro_y_block[2] | gyro_y_block[3] << 8
        gyro_z_data = gyro_z_block[2] | gyro_z_block[3] << 8
        if(gyro_x_data & 0x8000):
            gyro_x_data = ((~gyro_x_data & 0xFFFF) + 1)* -1
        gyro_x_value = 2000 * gyro_x_data / 0x7FFF
        if(gyro_y_data & 0x8000):
            gyro_y_data = ((~gyro_y_data & 0xFFFF) + 1)* -1
        gyro_y_value = 2000 * gyro_y_data / 0x7FFF
        if(gyro_z_data & 0x8000):
            gyro_z_data = ((~gyro_z_data & 0xFFFF) + 1)* -1
        gyro_z_value = 2000 * gyro_z_data / 0x7FFF
        spi.close()
        #UNIT : accel_x_value, accel_y_value, accel_zvalue = [m/s^2]
        #UNIT : gyro_x_value, gyro_y_value, gyro_z_value = [deg/s]
        print(accel_x_value, accel_y_value, accel_z_value, gyro_x_value, gyro_y_value, gyro_z_value)
        time.sleep(1)

except KeyboardInterrupt:
    print('!Finish!')
