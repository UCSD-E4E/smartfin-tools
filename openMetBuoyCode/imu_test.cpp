//IMPORTANT FILE//

#include "imu_manager.h"

bool IMU_Manager::update_accumulate_Kalman(void){
   // clear measurement accus
   accu_acc_x.clear();
   accu_acc_y.clear();
   accu_acc_z.clear();

   accu_gyr_x.clear();
   accu_gyr_y.clear();
   accu_gyr_z.clear();

   accu_mag_x.clear();
   accu_mag_y.clear();
   accu_mag_z.clear();

  /*
   if (micros() - time_last_Kalman_update_us > nbr_micros_between_Kalman_update){
      Serial.print(F("W behind UAC by ")); Serial.println(micros() - time_last_Kalman_update_us - nbr_micros_between_Kalman_update);
   }

   if (micros() - time_last_accel_gyro_reading_us > 1.7 * nbr_micros_between_accel_gyro_readings){
      Serial.print(F("W behind ACC by ")); Serial.println(micros() - time_last_accel_gyro_reading_us - nbr_micros_between_accel_gyro_readings);
   }

   if (micros() - time_last_mag_reading_us > 1.7 * nbr_micros_between_mag_readings){
      Serial.print(F("W behind MAG by ")); Serial.println(micros() - time_last_mag_reading_us - nbr_micros_between_mag_readings);
   }
   */

   // perform as many measurements as possible while it is time
   while (micros() - time_last_Kalman_update_us < nbr_micros_between_Kalman_update){
      // if time to read acc / gyr, do it
      if (micros() - time_last_accel_gyro_reading_us > nbr_micros_between_accel_gyro_readings){
         time_last_accel_gyro_reading_us += nbr_micros_between_accel_gyro_readings;

        // NOTE: if there are issues with the stability of the reading, it would be possible to:
        // 1 - have a counter of "number of consecutive bad readings"
        // 2 - if more than 5 consecutive bad readings, return false; while less than 5, try again
        // looks like the readings are stable though, so probably no need to implement this workaround.
         if (!ism330dhcx.getEvent(&accel, &gyro, &temp)){
           Serial.println(F("ERROR: unable to read from acc / gyr"));
           return false;
         }

         accu_acc_x.push_back(accel.acceleration.x);
         accu_acc_y.push_back(accel.acceleration.y);
         accu_acc_z.push_back(accel.acceleration.z);

         accu_gyr_x.push_back(gyro.gyro.x);
         accu_gyr_y.push_back(gyro.gyro.y);
         accu_gyr_z.push_back(gyro.gyro.z);
         
         stat_nbr_accel_gyro_readings++;
      }

      // if time to read mag, do it
      if (micros() - time_last_mag_reading_us > nbr_micros_between_mag_readings){
         time_last_mag_reading_us += nbr_micros_between_mag_readings;

         lis3mdl.getEvent(&mag);
         
         accu_mag_x.push_back(mag.magnetic.x);
         accu_mag_y.push_back(mag.magnetic.y);
         accu_mag_z.push_back(mag.magnetic.z);

         stat_nbr_mag_readings++;
      }
      
   }
   time_last_Kalman_update_us += nbr_micros_between_Kalman_update;

   // enableBurstMode();

   // compute the means of the measurements, using a n-sigma filter
   acc_x = float_mean_filter(accu_acc_x);
   acc_y = float_mean_filter(accu_acc_y);
   acc_z = float_mean_filter(accu_acc_z);

   gyr_x = float_mean_filter(accu_gyr_x) * SENSORS_RADS_TO_DPS;
   gyr_y = float_mean_filter(accu_gyr_y) * SENSORS_RADS_TO_DPS;
   gyr_z = float_mean_filter(accu_gyr_z) * SENSORS_RADS_TO_DPS;

   mag_x = float_mean_filter(accu_mag_x);
   mag_y = float_mean_filter(accu_mag_y);
   mag_z = float_mean_filter(accu_mag_z);

   // unsigned long crrt_micros;
   // crrt_micros = micros();

   // feed the means of the measurements to the Kalman filter
   // in case the magnometer is calibrated, we can get direction information
   if (imu_use_magnetometer){
      Kalman_filter.update(gyr_x, gyr_y, gyr_z,
                           acc_x, acc_y, acc_z,
                           mag_x, mag_y, mag_z);
   }
   // in case the magnometer is not calibrated, the magnometer does more harm than good, consider switching off then!
   else{
      Kalman_filter.update(gyr_x, gyr_y, gyr_z,
                           acc_x, acc_y, acc_z,
                           0.0f, 0.0f, 0.0f);
   }

   // Serial.print(F("K took ")); Serial.println(micros() - crrt_micros);
   // crrt_micros = micros();

   // get the Kalman filter information, and apply rotation to get NED
   roll_ = Kalman_filter.getRoll();
   pitch = Kalman_filter.getPitch();
   yaw__ = Kalman_filter.getYaw();

   Kalman_filter.getQuaternion(&qr, &qi, &qj, &qk);

   vec3_setter(&accel_raw, acc_x, acc_y, acc_z);
   quat_setter(&quat_rotation, qr, qi, qj, qk);
   rotate_by_quat_R(&accel_raw, &quat_rotation, &accel_NED);

   // Serial.print(F("Q took ")); Serial.println(micros() - crrt_micros);

   // accumulate Kalman measurements
   accu_acc_N.push_back(accel_NED.i);
   accu_acc_E.push_back(accel_NED.j);
   accu_acc_D.push_back(accel_NED.k);

   accu_yaw__.push_back(yaw__);
   accu_pitch.push_back(pitch);
   accu_roll_.push_back(roll_);

   stat_nbr_kalman_updates++;

   //disableBurstMode();

   return true;
}

bool IMU_Manager::get_new_reading(float & acc_N_inout, float & acc_E_inout, float & acc_D_inout,
                   float & yaw___inout,   float & pitch_inout, float & roll__inout
                   ){
   if (blink_when_use_IMU){
     if (counter_nbr_cycles_LED_off == 0){
       digitalWrite(LED, LOW);
     }
     if (counter_nbr_cycles_LED_off >= number_update_between_blink){
       counter_nbr_cycles_LED_off = -1;
       digitalWrite(LED, HIGH);
     }
   }
   counter_nbr_cycles_LED_off += 1;

   // clear the Kalman output accus
   accu_acc_N.clear();
   accu_acc_E.clear();
   accu_acc_D.clear();

   accu_yaw__.clear();
   accu_pitch.clear();
   accu_roll_.clear();

   stat_nbr_accel_gyro_readings = 0;
   stat_nbr_mag_readings = 0;
   stat_nbr_kalman_updates = 0;

   if (micros() - time_last_IMU_update_us > 1.2 * nbr_micros_between_IMU_update){
      Serial.print(F("W: behind GNR by ")); Serial.println(micros() - time_last_IMU_update_us - nbr_micros_between_IMU_update);
   }

   // perform as many kalman updates as possible while it is time
   while (micros() - time_last_IMU_update_us < nbr_micros_between_IMU_update){
      if(!update_accumulate_Kalman()){
        Serial.println(F("ERROR cannot get new IMU Kalman reading"));
        return false;
      }
   }
   time_last_IMU_update_us += nbr_micros_between_IMU_update;

   // enableBurstMode();

   // filter all outputs
   acc_N_inout = float_mean_filter(accu_acc_N);
   acc_E_inout = float_mean_filter(accu_acc_E);
   acc_D_inout = float_mean_filter(accu_acc_D);

   yaw___inout = float_mean_filter(accu_yaw__);
   pitch_inout = float_mean_filter(accu_pitch);
   roll__inout = float_mean_filter(accu_roll_);

   // print stats
   /*
   Serial.println("stats IMU");
   Serial.print(F("nbr reads | acc gyro ")); Serial.print(stat_nbr_accel_gyro_readings);
   Serial.print(F(" | mag ")); Serial.print(stat_nbr_mag_readings);
   Serial.print(F(" | K updates ")); Serial.println(stat_nbr_kalman_updates);
   */

   // disableBurstMode();

   wdt.restart();

   return true;
}

