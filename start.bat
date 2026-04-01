@echo off
chcp 65001 >nul
REM PyWeChat Bridge 启动脚本 (Windows)

set "SCRIPT_DIR=%~dp0"
set "PIDFILE=%TEMP%\pywechat-bridge.pid"

if "%~1"=="" goto :start
if "%~1"=="start" goto :start
if "%~1"=="stop" goto :stop
if "%~1"=="restart" goto :restart
if "%~1"=="status" goto :status
goto :usage

:start
cd /d "%SCRIPT_DIR%"
echo 正在启动 PyWeChat Bridge...

REM 检查是否已在运行
if exist "%PIDFILE%" (
    set /p PID=<"%PIDFILE%"
    tasklist /FI "PID eq %PID%" 2>nul | find "%PID%" >nul
    if %ERRORLEVEL% equ 0 (
        echo PyWeChat Bridge 已在运行 (PID: %PID%)
        exit /b 0
    )
)

REM 启动服务
start /b python "pywechat_bridge_simple.py" --init >"%TEMP%\pywechat-bridge.log" 2>&1

REM 等待服务启动
timeout /t 2 /nobreak >nul

REM 查找进程 ID
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /B "PID:"') do (
    echo %%a > "%PIDFILE%"
    echo PyWeChat Bridge 启动成功!
    echo 服务地址: http://127.0.0.1:8765
    echo PID: %%a
    echo 日志文件: %TEMP%\pywechat-bridge.log
    goto :eof
)

echo 启动失败，请检查日志: %TEMP%\pywechat-bridge.log
goto :eof

:stop
echo 正在停止 PyWeChat Bridge...
if exist "%PIDFILE%" (
    set /p PID=<"%PIDFILE%"
    taskkill /PID %PID% /F 2>nul
    if %ERRORLEVEL% equ 0 (
        echo 已停止 (PID: %PID%)
    ) else (
        echo 进程已不存在
    )
    del "%PIDFILE%" 2>nul
) else (
    REM 尝试查找并终止 pywechat_bridge_simple.py
    taskkill /FI "WINDOWTITLE eq pywechat_bridge_simple.py" /F 2>nul
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" ^| findstr python') do (
        wmic process where "ProcessId=%%a" get CommandLine 2>nul | find "pywechat_bridge_simple" >nul
        if !ERRORLEVEL! equ 0 taskkill /PID %%a /F 2>nul
    )
    echo 已尝试停止相关进程
)
goto :eof

:restart
call :stop
timeout /t 1 /nobreak >nul
call :start
goto :eof

:status
echo 检查 PyWeChat Bridge 状态...
if exist "%PIDFILE%" (
    set /p PID=<"%PIDFILE%"
    tasklist /FI "PID eq %PID%" 2>nul | find "%PID%" >nul
    if %ERRORLEVEL% equ 0 (
        echo PyWeChat Bridge 运行中 (PID: %PID%)
        echo 服务地址: http://127.0.0.1:8765
    ) else (
        echo PyWeChat Bridge 未运行 (PID 文件存在但进程不存在)
    )
) else (
    echo PyWeChat Bridge 未运行
)
goto :eof

:usage
echo 用法: %~nx0 {start^|stop^|restart^|status}
echo.
echo   start   - 启动服务
echo   stop    - 停止服务
echo   restart - 重启服务
echo   status  - 查看状态
goto :eof
