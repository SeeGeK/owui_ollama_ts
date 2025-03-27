cmake_minimum_required(VERSION 3.10)

project(sppd50hg VERSION 1.0 LANGUAGES CXX)

# Установка минимального стандарта C++
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# Поиск необходимых Qt компонентов
find_package(Qt5 COMPONENTS Core Widgets PrintSupport REQUIRED)

# include(PolygonFunctions NO_POLICY_SCOPE)
# include(PolygonPrelude NO_POLICY_SCOPE)
# include(PolygonGIS_ToolKit)
# include(PolygonQT)

#for working gis-demo
# include(PolygonGisDemo)

if(WIN32)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin)
else()
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin)
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin)
endif()




# Добавление подпроекта из директории ppd_globals
add_subdirectory(src)

#=========================================
# resources target



