cmake_minimum_required(VERSION 3.26)
project(cpp_PC_uC_usb_v01)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Dein Executable
add_executable(cpp_PC_uC_usb_v01
        main.cpp
        messure_config_class.h
        ADS8681/src/ADS8681.h
        messure_config.h
)

# Boost include (Header-only Asio)
target_include_directories(cpp_PC_uC_usb_v01 PRIVATE "C:/libs/boost_1_83_0")
