pyinstaller --noconfirm --add-data icons;icons --add-data LICENSE;. --add-data README.md;. --add-data documentation;documentation AttractModeListMgr.py
del dist\AttractModeListMgr\Qt5WebEngineCore.dll
del dist\AttractModeListMgr\opengl32sw.dll
del dist\AttractModeListMgr\Qt5Designer.dll
del dist\AttractModeListMgr\d3dcompiler_47.dll
del dist\AttractModeListMgr\Qt5Qml.dll
del dist\AttractModeListMgr\libcrypto-1_1.dll
del dist\AttractModeListMgr\Qt5XmlPatterns.dll
del dist\AttractModeListMgr\Qt5Location.dll
del dist\AttractModeListMgr\Qt5Charts.dll
del dist\AttractModeListMgr\Qt5Network.dll
del dist\AttractModeListMgr\Qt5Quick3dRuntimeRender.dll
del dist\AttractModeListMgr\libcrypto-1_1-x64.dll
del dist\AttractModeListMgr\libGLESv2.dll
del dist\AttractModeListMgr\Qt5QuickTemplates2.dll
del dist\AttractModeListMgr\Qt5Multimedia.dll
del dist\AttractModeListMgr\Qt5Bluetooth.dll
del dist\AttractModeListMgr\Qt5Quick3D.dll
del dist\AttractModeListMgr\Qt5QuickParticles.dll
del dist\AttractModeListMgr\Qt5RemoteObjects.dll
del dist\AttractModeListMgr\Qt5QmlModels.dll
del dist\AttractModeListMgr\Qt5DBus.dll
del dist\AttractModeListMgr\Qt5WebEngine.dll
del dist\AttractModeListMgr\ssleay32.dll
del dist\AttractModeListMgr\Qt5Svg.dll
del dist\AttractModeListMgr\Qt5OpenGL.dll
del dist\AttractModeListMgr\Qt5PrintSupport.dll
del dist\AttractModeListMgr\Qt5Positioning.dll
del dist\AttractModeListMgr\Qt5WebEngineWidgets.dll
del dist\AttractModeListMgr\Qt5Test.dll
del dist\AttractModeListMgr\Qt5Quick3DRender.dll
del dist\AttractModeListMgr\Qt5QuickShapes.dll
del dist\AttractModeListMgr\Qt5Xml.dll
del dist\AttractModeListMgr\Qt5Sql.dll
del dist\AttractModeListMgr\Qt5Sensors.dll
del dist\AttractModeListMgr\Qt5NetworkAuth.dll
del dist\AttractModeListMgr\Qt5WebSockets.dll
del dist\AttractModeListMgr\Qt5WebChannel.dll
del dist\AttractModeListMgr\Qt5QuickTest.dll
del dist\AttractModeListMgr\Qt5Quick3DAssetImport.dll
del dist\AttractModeListMgr\Qt5PositioningQuick.dll
del dist\AttractModeListMgr\Qt5MultimediaWidgets.dll
del dist\AttractModeListMgr\Qt5QmlWorkerScript.dll
del dist\AttractModeListMgr\Qt5TextToSpeech.dll
del dist\AttractModeListMgr\Qt5Quick3DUtils.dll
del dist\AttractModeListMgr\libeay32.dll
del dist\AttractModeListMgr\libssl-1_1.dll
del dist\AttractModeListMgr\libssl-1_1-x64.dll
del dist\AttractModeListMgr\Qt5SerialPort.dll
del dist\AttractModeListMgr\Qt5Nfc.dll
del dist\AttractModeListMgr\Qt5Quick.dll
del dist\AttractModeListMgr\Qt5QuickControls2.dll
del dist\AttractModeListMgr\Qt5QuickWidgets.dll
rmdir /s /q build
del dist\AttractModeListMgr\PyQt5\QtMultimedia.pyd
del dist\AttractModeListMgr\PyQt5\QtChart.pyd
del dist\AttractModeListMgr\PyQt5\QtNetwork.pyd
del dist\AttractModeListMgr\PyQt5\QtQml.pyd
del dist\AttractModeListMgr\PyQt5\QtLocation.pyd
del dist\AttractModeListMgr\PyQt5\QtBluetooth.pyd
del dist\AttractModeListMgr\PyQt5\QtSql.pyd
del dist\AttractModeListMgr\PyQt5\QtDesigner.pyd
del dist\AttractModeListMgr\PyQt5\QtPrintSupport.pyd
del dist\AttractModeListMgr\PyQt5\QtSensors.pyd
del dist\AttractModeListMgr\PyQt5\QtWebEngineWidgets.pyd
del dist\AttractModeListMgr\PyQt5\QtXml.pyd
del dist\AttractModeListMgr\PyQt5\QtPositioning.pyd
del dist\AttractModeListMgr\PyQt5\QtDBus.pyd
del dist\AttractModeListMgr\PyQt5\QtNetworkAuth.pyd
del dist\AttractModeListMgr\PyQt5\QtMultimediaWidgets.pyd
del dist\AttractModeListMgr\PyQt5\QtXmlPatterns.pyd
del dist\AttractModeListMgr\PyQt5\QtOpenGL.pyd
del dist\AttractModeListMgr\PyQt5\QtSvg.pyd
del dist\AttractModeListMgr\PyQt5\QtWebEngineCore.pyd
del dist\AttractModeListMgr\PyQt5\QtRemoteObjects.pyd
del dist\AttractModeListMgr\PyQt5\QtTest.pyd
del dist\AttractModeListMgr\PyQt5\QtWebSockets.pyd
del dist\AttractModeListMgr\PyQt5\QtSerialPort.pyd
del dist\AttractModeListMgr\PyQt5\QtQuickWidgets.pyd
del dist\AttractModeListMgr\PyQt5\QtWebEngine.pyd
del dist\AttractModeListMgr\PyQt5\QtTextToSpeech.pyd
del dist\AttractModeListMgr\PyQt5\QtQuick3D.pyd
del dist\AttractModeListMgr\PyQt5\QtWebChannel.pyd
del dist\AttractModeListMgr\PyQt5\Qt\bin\QtWebEngineProcess.exe
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\plugins\audio
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\plugins\playlistformats
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\plugins\position
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\plugins\printsupport
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\plugins\sensorgestures
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\plugins\sensors
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\plugins\sqldrivers
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\plugins\mediaservice
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\qml
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\resources
rmdir /s /q dist\AttractModeListMgr\PyQt5\Qt\translations







