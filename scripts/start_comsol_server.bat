@echo off
echo Starting COMSOL 6.1 server on port 2036...
echo Keep this window open while simulations are running.
echo Press Ctrl+C to stop the server.
"C:\Program Files\COMSOL\61\Multiphysics\bin\win64\comsol.exe" mphserver -port 2036 -login off
