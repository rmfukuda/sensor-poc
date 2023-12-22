idf_component_register(SRCS "bleconfig.c"
                    REQUIRES bt
                    REQUIRES nvs_flash
                    INCLUDE_DIRS "include")
