#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_system.h"
#include "esp_log.h"
#include "driver/temperature_sensor.h"

#include "bleconfig.h"


typedef struct {
    SemaphoreHandle_t semaphore;
    float sensor_data;
} TaskParameters;


TaskParameters params;


void task_ble(void *pvParameters){
    extern uint16_t heart_rate_handle_table[HRS_IDX_NB];
    extern BleInfo bleinfo;

    my_ble_init();

    while(1){
        xSemaphoreTake(params.semaphore, portMAX_DELAY);
        if(bleinfo.ble_is_connected){
            // format the float buffer
            uint16_t len = sizeof(float);
            uint8_t buffer[sizeof(float)];
            memcpy(buffer, &params.sensor_data, len);

            esp_ble_gatts_send_indicate(
            bleinfo.ble_gatts_if, bleinfo.ble_conn_id, heart_rate_handle_table[IDX_CHAR_VAL_A],
            len, buffer, false
        );
        }
    }
    vTaskSuspend(NULL);
}


void task_sensor(void *pvParameters){
    /* For simplicity, we do not require extra hardware.
    The code reads the built-in temperature sensor to measure the chip's internal temperature.
    */
    static const char *TAG = "temperature";

    ESP_LOGI(TAG, "Install temperature sensor, expected temp ranger range: 10~50 ℃");
    temperature_sensor_handle_t temp_sensor = NULL;
    temperature_sensor_config_t temp_sensor_config = TEMPERATURE_SENSOR_CONFIG_DEFAULT(10, 50);
    ESP_ERROR_CHECK(temperature_sensor_install(&temp_sensor_config, &temp_sensor));

    ESP_LOGI(TAG, "Enable temperature sensor");
    ESP_ERROR_CHECK(temperature_sensor_enable(temp_sensor));

    ESP_LOGI(TAG, "Read temperature");
    float tsens_value;

    while (1) {
        ESP_ERROR_CHECK(temperature_sensor_get_celsius(temp_sensor, &tsens_value));
        ESP_LOGI(TAG, "Temperature value %.02f ℃", tsens_value);
        params.sensor_data = tsens_value;
        xSemaphoreGive(params.semaphore);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}


void app_main(void) {
    SemaphoreHandle_t semaphore_sync;
    semaphore_sync = xSemaphoreCreateBinary();

    params.semaphore = semaphore_sync;
    params.sensor_data = 0;

    xTaskCreate(task_ble, "task ble", 12*1024, NULL, 1, NULL);
    xTaskCreate(task_sensor, "task sensor", 12*1024, NULL, 1, NULL);
}
