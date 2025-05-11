@echo off
:: 设置 Anaconda 的安装路径（根据你的实际路径修改）
call C:\ProgramData\Anaconda3\Scripts\activate.bat pytorch_gpu

:: 运行 Django 开发服务器
python manage.py runserver
:: 暂停以便查看错误信息
pause