PS B:\Users\gather\python\qa_service_tester> dir


    Directorio: B:\Users\gather\python\qa_service_tester


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       26/05/2026     21:43           3282 comparator.py
-a----       26/05/2026     21:43            525 config.ini
-a----       26/05/2026     21:44           1174 config.py
-a----       26/05/2026     21:45           5429 excel_handler.py
-a----       26/05/2026     21:44        1378257 ListaMetodosServicioQA.xlsm
-a----       26/05/2026     21:45          14440 main.py
-a----       26/05/2026     21:45           7472 response_parser.py
-a----       26/05/2026     21:46           7430 service_caller.py

ERROR01
PS B:\Users\gather\python\qa_service_tester> python .\main.py
Traceback (most recent call last):
  File "B:\Users\gather\python\qa_service_tester\main.py", line 22, in <module>
    from config import cargar_config
ModuleNotFoundError: No module named 'config'

--- Respuesta, revosar que arroja esto.
python -c "import sys; print(sys.path)"

--- Se ejecuta en servidor retornando esto
['B:\\Users\\gather\\python\\python313.zip', 'B:\\Users\\gather\\python', 'B:\\Users\\gather\\AppData\\Roaming\\Python\\Python313\\site-packages', 'B:\\Users\\gather\\python\\Lib\\site-packages']
con esto se corrige

ERROR02
Traceback (most recent call last):
  File "B:\Users\gather\python\qa_service_tester\main.py", line 30, in <module>
    from service_caller import llamar_rpc2, llamar_storm, llamar_gpl, RespuestaServicio
  File "B:\Users\gather\python\qa_service_tester\service_caller.py", line 3, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'

