@echo off
:: run_prepare_data.cmd - Run prepare_data.py with hyperparameters and save logs
setlocal enabledelayedexpansion

:: Set log directory and ensure it exists
set LOG_DIR=C:\Users\ZY\Desktop\Forecaster\misc\log
if not exist %LOG_DIR% mkdir %LOG_DIR%

:: Set log filename (with timestamp)
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=%LOG_DIR%\task_evaluate_%TIMESTAMP%.log

:: Set Anaconda environment name
set ENV_NAME=pytorch_gpu

:: Display in console and record in log
echo ========================================
echo Start time: %date% %time%
echo Using conda environment: %ENV_NAME%
echo Starting Python script execution...
echo ======================================== > %LOG_FILE%
echo Start time: %date% %time% >> %LOG_FILE%
echo Using conda environment: %ENV_NAME% >> %LOG_FILE%
echo Starting Python script execution... >> %LOG_FILE%

:: Activate conda environment
call activate %ENV_NAME%

:: Run Python script and save output to log file while displaying in console
:: Using a temporary file to be able to display and log the same output
python C:\Users\ZY\Desktop\Forecaster\scripts\task_evaluate.py > %LOG_DIR%\temp_output.txt 2>&1
type %LOG_DIR%\temp_output.txt
type %LOG_DIR%\temp_output.txt >> %LOG_FILE%
del %LOG_DIR%\temp_output.txt

:: Record end time
echo.
echo ========================================
echo End time: %date% %time%
echo Script execution completed, log saved to: %LOG_FILE%
echo ========================================

echo. >> %LOG_FILE%
echo End time: %date% %time% >> %LOG_FILE%
echo Script execution completed >> %LOG_FILE%

:: Exit environment
call conda deactivate

pause