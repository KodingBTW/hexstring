::Build config
build_config.py
:: Get requirements
pip freeze > requirements.txt
:: Compile
pyinstaller console.spec
pyinstaller hexstring.spec
:: Copying Files
mkdir dist\resources
copy resources\icon.ico dist\resources\
copy analizer.py dist\src\
copy app.py dist\src\
copy build.bat dist\src
copy build_config.py dist\src\
copy config.json dist\src\
copy config.py dist\src\
copy cli.py dist\src\
copy console.py dist\src\
copy console.spec dist\src\
copy decoder.py dist\src\
copy encoder.py dist\src\
copy hexstring.spec dist\src\
copy lempel_ziv.py dist\src\
copy requirements.txt dist\
copy LICENSE dist\
copy ASCII.tbl dist\
xcopy "build" "dist\src\build\" /E /I /Y
pause