@echo off
setlocal enabledelayedexpansion

echo Creating project structure...

:: === Project Root ===
mkdir dgdo
mkdir dgdo\backend
mkdir dgdo\cpp
mkdir dgdo\proto
mkdir dgdo\tests
mkdir dgdo\scripts
mkdir dgdo\docs
mkdir dgdo\config

:: === Backend Structure ===
mkdir dgdo\backend\app
mkdir dgdo\backend\app\api
mkdir dgdo\backend\app\api\v1
mkdir dgdo\backend\app\core
mkdir dgdo\backend\app\services
mkdir dgdo\backend\app\models
mkdir dgdo\backend\tests

type NUL > dgdo\backend\app\__init__.py
type NUL > dgdo\backend\app\main.py
type NUL > dgdo\backend\requirements.txt
type NUL > dgdo\backend\pyproject.toml

:: === C++ Module Structure ===
mkdir dgdo\cpp\src
mkdir dgdo\cpp\include
mkdir dgdo\cpp\build

type NUL > dgdo\cpp\CMakeLists.txt
type NUL > dgdo\cpp\src\module.cpp
type NUL > dgdo\cpp\include\module.h

:: === Proto ===
type NUL > dgdo\proto\dgdo.proto

:: === Tests ===
mkdir dgdo\tests\backend
mkdir dgdo\tests\cpp
mkdir dgdo\tests\grpc

type NUL > dgdo\tests\backend\test_backend.py
type NUL > dgdo\tests\cpp\test_cpp_module.cpp
type NUL > dgdo\tests\grpc\test_grpc.py

:: === Scripts ===
type NUL > dgdo\scripts\build_cpp.sh
type NUL > dgdo\scripts\run_backend.sh

:: === Config ===
type NUL > dgdo\config\dev.env
type NUL > dgdo\config\prod.env

:: === Docs ===
type NUL > dgdo\docs\architecture.md
type NUL > dgdo\docs\README.md

echo Done! Project skeleton created.

pause
