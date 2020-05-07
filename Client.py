// SendApp.cpp : Defines the entry point for the application.
//
#include "stdafx.h"
#include <winsock2.h>
#pragma comment (lib,"ws2_32.lib")
#include "SendApp.h"
#include <string>
using namespace std;

#define ID_CONNECT 1
#define ID_COUNT 9
#define ID_EDIT1 2
#define ID_EDIT2 3
#define ID_EDIT3 4
#define ID_EDIT4 5
#define ID_EXIT 6
#define ID_STATIC 7
#define ID_STATIC1 8

#define PORT 2206
#define PORTS 2207

#define MAX_LOADSTRING 100

// Global Variables:
HINSTANCE hInst;								// current instance
TCHAR szTitle[MAX_LOADSTRING];					// The title bar text
TCHAR szWindowClass[MAX_LOADSTRING];			// the main window class name

//------------------���������� ����������
HWND					hEdit, hEditIP, hEditLogin, hEditSend;
char					szServerName[1024], szMessage[1024], szClientLogin[1024], szClientIP[1024];

// Forward declarations of functions included in this code module:
ATOM				MyRegisterClass(HINSTANCE hInstance);
BOOL				InitInstance(HINSTANCE, int);
LRESULT CALLBACK	WndProc(HWND, UINT, WPARAM, LPARAM);

// ������� ����������� ����� � ������ ������
void GetLocalIP()
{
	char chInfo[64];
		if (!gethostname(chInfo,sizeof(chInfo)))
		{
			hostent *sh;
			sh=gethostbyname((char*)&chInfo);
			if (sh!=NULL)
			{
				int nAdapter = 0;
					struct sockaddr_in adr;
					memcpy(&adr.sin_addr,sh->h_addr_list[nAdapter],sh->h_length); 
					//SendMessage(hEditIP, EM_REPLACESEL, 0, LPARAM(inet_ntoa(adr.sin_addr)));
					strcpy_s(szClientIP,(inet_ntoa(adr.sin_addr)));
			}
		}
		else
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("Error local host "));
}

//������� ������� �������.
	int clear_massiv (char *MAS)
	{
		for(int i=0; i<1024; i++)
			MAS[i] = NULL;
		return 0;
	}

//������� �������� �������� �� �������
DWORD WINAPI ClientThread(LPVOID lpParam)
{
    SOCKET        sock = (SOCKET)lpParam;
    char          szRecvBuff[1024];
    int           ret;

    while(1)
    {
		ret = recv(sock, szRecvBuff, 1024, 0);
		szRecvBuff[ret] = 0;
        if (ret == 0)
            break;
        else if (ret == SOCKET_ERROR)
        {
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("���� �������\r\n"));
            break;
        }
		else
		{
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("������: "));
			SendMessage(hEdit, EM_REPLACESEL, 0, LPARAM(szRecvBuff));
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("\r\n"));
		}
	}

	clear_massiv(szRecvBuff);
    return 0;
}

//������� �������� �������, �������, ������� ��������� �������(���� ��������� �� ������� ��� ��������).
DWORD WINAPI NetThread(LPVOID lpParam)
{
SOCKET					SendSocket;
int						ret;
struct sockaddr_in		server;
struct hostent			*host = NULL; 

	//�������� �������
	SendSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    if (SendSocket == INVALID_SOCKET)
    {
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("���������� ������� �����\r\n"));
        return 1;
    }
	else
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("����� ������\r\n"));

	//����� � ������
    server.sin_family = AF_INET;
	server.sin_port = htons(2206);
    server.sin_addr.s_addr = inet_addr(szServerName);

	if (server.sin_addr.s_addr == INADDR_NONE)
    {
        host = gethostbyname(szServerName);
        if (host == NULL)
        {
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("���������� ���������� �������\r\n"));
            return 1;
        }
		else
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("������ ��������\r\n"));
        CopyMemory(&server.sin_addr, host->h_addr_list[0], host->h_length);
    }
	//�������
    if (connect(SendSocket, (struct sockaddr *)&server, sizeof(server)) == SOCKET_ERROR)
    {
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("���������� ��������\r\n"));
        return 1;
    }
	else
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("������������\r\n"));

	// ���� � ������� ������
	ret = send(SendSocket, szMessage, int(strlen(szMessage)), 0);
    if (ret == SOCKET_ERROR)
    {
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("�������� ��������\r\n"));
    }

	clear_massiv(szMessage);

    char	szRecvBuff[1024];
    ret = recv(SendSocket, szRecvBuff, 1024, 0);
	szRecvBuff[ret] = 0;
    if (ret == SOCKET_ERROR)
    {
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("���� �������\r\n"));
    }
	else
	{
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("������ ��������: "));
		SendMessage(hEdit, EM_REPLACESEL, 0, LPARAM(szRecvBuff));
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("\r\n"));
	}

	clear_massiv(szRecvBuff);

    closesocket(SendSocket);
	return 0;
}

//������� ������������� ���������� ������
DWORD WINAPI NetThreadListen(LPVOID lpParam)
{

	SOCKET					sListen, sClient;
	struct sockaddr_in		localaddr, clientaddr;
	struct hostent			*host = NULL; 
	int						iSize;
	HANDLE					hThreadl;
	DWORD					dwThreadIdl;

	sListen = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    if (sListen == INVALID_SOCKET)
    {
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("���������� ������� ����� ��� �����\r\n"));
        return 1;
    }
	else
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("����� ��� ����� ������\r\n"));

	ZeroMemory (&localaddr, sizeof (localaddr));
	localaddr.sin_family = AF_INET;
	localaddr.sin_addr.s_addr = inet_addr(INADDR_ANY);
	localaddr.sin_port = htons(2207);
   
	//�������� ���������� ������
	if (bind(sListen, (struct sockaddr *)&localaddr, sizeof(localaddr)) == SOCKET_ERROR)
    {
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("������ ������� Bind( )\r\n"));
		int error = WSAGetLastError();
        return 1;
    }
	else
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("�������� ���������� ������� Bind( )\r\n"));

	listen(sListen, 2);

	SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("�������� ���������� ������� Listen( )\r\n"));

	while (1)
    {
        iSize = sizeof(clientaddr);
        sClient = accept(sListen, (struct sockaddr *)&clientaddr, &iSize);        
        if (sClient == INVALID_SOCKET)
        {        
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("������ ������\r\n"));
            break;
        }
		else
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("������ ��������\r\n"));

        hThreadl = CreateThread(NULL, 0, ClientThread, (LPVOID)sClient, 0, &dwThreadIdl);
        if (hThreadl == NULL)
        {
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("�������� ������ ��������\r\n"));
            break;
        }
		else
			SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("����� ������\r\n"));
        CloseHandle(hThreadl);
    }

	closesocket(sListen);

	return 0;
}


// ��� ������� ����� ���...
int APIENTRY _tWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPTSTR lpCmdLine, int nCmdShow)
{
	UNREFERENCED_PARAMETER(hPrevInstance);
	UNREFERENCED_PARAMETER(lpCmdLine);

 	// TODO: Place code here.
	MSG msg;
	HACCEL hAccelTable;

	// Initialize global strings
	LoadString(hInstance, IDS_APP_TITLE, szTitle, MAX_LOADSTRING);
	LoadString(hInstance, IDC_SENDAPP, szWindowClass, MAX_LOADSTRING);
	MyRegisterClass(hInstance);

	// Perform application initialization:
	if (!InitInstance (hInstance, nCmdShow))
	{
		return FALSE;
	}

	hAccelTable = LoadAccelerators(hInstance, MAKEINTRESOURCE(IDC_SENDAPP));
// ����������� ����������
	WSADATA       wsd;
    if (WSAStartup(MAKEWORD(2,2), &wsd) != 0)
	{
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("���������� ��������� WinSock\r\n"));
	}
	else
		SendMessage(hEdit, EM_REPLACESEL, 0, (LPARAM)TEXT("WinSock ���������\r\n"));
// �������� ��������� �����.
	HANDLE        hNetThreadl;
	DWORD         dwNetThreadIdl;
	hNetThreadl = CreateThread(NULL, 0, NetThreadListen, 0, 0, &dwNetThreadIdl);
// ����������� ip
	GetLocalIP();

	// Main message loop:
	while (GetMessage(&msg, NULL, 0, 0))
	{
		if (!TranslateAccelerator(msg.hwnd, hAccelTable, &msg))
		{
			TranslateMessage(&msg);
			DispatchMessage(&msg);
		}
	}
	WSACleanup();
	return (int) msg.wParam;
}

ATOM MyRegisterClass(HINSTANCE hInstance)
{
	WNDCLASSEX wcex;

	wcex.cbSize = sizeof(WNDCLASSEX);

	wcex.style			= CS_HREDRAW | CS_VREDRAW;
	wcex.lpfnWndProc	= WndProc;
	wcex.cbClsExtra		= 0;
	wcex.cbWndExtra		= 0;
	wcex.hInstance		= hInstance;
	wcex.hIcon			= LoadIcon(hInstance, MAKEINTRESOURCE(IDI_SENDAPP));
	wcex.hCursor		= LoadCursor(NULL, IDC_ARROW);
	wcex.hbrBackground	= CreateSolidBrush(RGB(157,203,255)); //���� ���� ����
	//wcex.lpszMenuName	= MAKEINTRESOURCE(IDC_SENDAPP);
	wcex.lpszMenuName	= 0;
	wcex.lpszClassName	= szWindowClass;
	wcex.hIconSm		= LoadIcon(wcex.hInstance, MAKEINTRESOURCE(IDI_SMALL));

	return RegisterClassEx(&wcex);
}

BOOL InitInstance(HINSTANCE hInstance, int nCmdShow)
{
   HWND hWnd;

   hInst = hInstance; // Store instance handle in our global variable

   hWnd = CreateWindow(szWindowClass, szTitle,
	WS_OVERLAPPEDWINDOW|WS_VISIBLE | DS_SETFONT |DS_MODALFRAME | 
	DS_3DLOOK | DS_FIXEDSYS |WS_CAPTION | WS_SYSMENU,
	50,50,600,400,(HWND)NULL,(HMENU)NULL,hInstance,(LPSTR)NULL);

   if (!hWnd)
   {
      return FALSE;
   }

   ShowWindow(hWnd, nCmdShow);
   UpdateWindow(hWnd);

   return TRUE;
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	int wmId, wmEvent;
	PAINTSTRUCT ps;
	HDC hdc;

	switch (message)
	{

	case WM_CREATE:

		//����� ������(�� �������� ����� ������������ ���������������� �������, � ����������)
		/*CreateWindow("static", "�����: ",WS_CHILD|WS_VISIBLE|SS_LEFT,
			265,300,50,16,hWnd, (HMENU)ID_STATIC, hInst, NULL);*/

		//���� ����
		hEditSend = CreateWindow("edit", NULL, WS_CHILD|WS_VISIBLE|ES_LEFT|ES_MULTILINE|WS_BORDER,
		40,240,500,50,hWnd,(HMENU)ID_EDIT1, hInst, NULL);

		//����� ip
		CreateWindow("static", "IP ������a:",
		WS_CHILD|WS_VISIBLE|SS_LEFT,
		40,300,80,16,hWnd, (HMENU)ID_STATIC1, hInst, NULL);

		//���� ����� ���������
		hEdit = CreateWindow("edit", NULL, WS_CHILD|WS_VISIBLE|ES_LEFT|WS_VSCROLL|ES_MULTILINE|ES_READONLY,
		40,20,500,200,hWnd, (HMENU)ID_EDIT2, hInst, NULL);

		//���� ����� IP-������ �������
		hEditIP = CreateWindow("edit", NULL, WS_CHILD|WS_VISIBLE|ES_LEFT|ES_MULTILINE|WS_BORDER,
		130,300,120,16,hWnd, (HMENU)ID_EDIT3, hInst, NULL);

		//���� ����� ������
		/*hEditLogin = CreateWindow("edit", NULL, WS_CHILD|WS_VISIBLE|ES_LEFT|ES_MULTILINE|WS_BORDER,
		320,300,60,16,hWnd, (HMENU)ID_EDIT4, hInst, NULL);*/

		//������ "�����������"
		/*CreateWindow("button", "�����������", WS_CHILD|WS_VISIBLE|BS_DEFPUSHBUTTON,
		450,300,110,20, hWnd, (HMENU)ID_CONNECT, hInst, NULL);*/

		//������ "���������"
		CreateWindow("button", "���������", WS_CHILD|WS_VISIBLE|BS_DEFPUSHBUTTON,
		450,330,110,20, hWnd, (HMENU)ID_COUNT, hInst, NULL);

		break;

	case WM_COMMAND:
		wmId    = LOWORD(wParam);
		wmEvent = HIWORD(wParam);
		// Parse the menu selections:
		switch (wmId)
		{
		case ID_CONNECT:
			{
				/*char szServerName1[1024];
				char szClientLogin1[1024];

				//__debugbreak();

				//���������� ���������� � edit'a, ��� ip, � ���������� ��� ���������.
				SendMessage(hEditIP,WM_GETTEXT,15,(LPARAM)(szServerName1));
				for(int i=0; i<15; i++)
					szServerName[i] = szServerName1[i];

				//���������� ���������� � edit'a, ��� �����, � ���������� ��� ���������.
				SendMessage(hEditLogin,WM_GETTEXT,15,(LPARAM)(szClientLogin1));
				for(int i=0; i<15; i++)
					szClientLogin[i] = szClientLogin1[i];

				//GetLocalIP();

				//�������� ������� �������� ���������. 
				HANDLE        hNetThread;
				DWORD         dwNetThreadId;
				hNetThread = CreateThread(NULL, 0, NetThread, 0, 0, &dwNetThreadId);*/
			}
			break;
		case ID_COUNT:
			{
				char szMessage1[1024];
				char szServerName1[1024];
				//char szClientLogin1[1024];

				//__debugbreak();

				//���������� ���������� � edit'a, ��� ip, � ���������� ��� ���������.
				SendMessage(hEditIP,WM_GETTEXT,15,(LPARAM)(szServerName1));
				for(int i=0; i<15; i++)
					szServerName[i] = szServerName1[i];

				//���������� ���������� � edit'a, ��� �����, � ���������� ��� ���������.
				/*SendMessage(hEditLogin,WM_GETTEXT,15,(LPARAM)(szClientLogin1));
				for(int i=0; i<15; i++)
					szClientLogin[i] = szClientLogin1[i];*/

				//���������� ���������� � edit'a, ��� ���������, � ���������� ��� ���������.
				SendMessage(hEditSend,WM_GETTEXT,100,(LPARAM)(szMessage1));
				for(int i=0; i<100; i++)
					szMessage[i] = szMessage1[i];

				//GetLocalIP();

				//�������� ������� �������� ���������. 
				HANDLE        hNetThread;
				DWORD         dwNetThreadId;
				hNetThread = CreateThread(NULL, 0, NetThread, 0, 0, &dwNetThreadId);

				break;
			}
		default:
			return DefWindowProc(hWnd, message, wParam, lParam);
			}
		break;
	case WM_PAINT:
		hdc = BeginPaint(hWnd, &ps);
		// TODO: Add any drawing code here...
		EndPaint(hWnd, &ps);
		break;
	case WM_DESTROY:
		PostQuitMessage(0);
		break;
	default:
		return DefWindowProc(hWnd, message, wParam, lParam);
	}
	return 0;
}
