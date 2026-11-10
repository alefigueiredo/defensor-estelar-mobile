"""Servidor local para instalar e jogar Defensor Estelar no celular Android via Wi-Fi."""

import http.server
import os
import socket
import socketserver
import webbrowser

PORT = 8080
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobile_android")


def obter_ip_local() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def iniciar_servidor():
    os.chdir(WEB_DIR)
    ip = obter_ip_local()
    url_rede = f"http://{ip}:{PORT}"
    url_local = f"http://localhost:{PORT}"

    print("=" * 65)
    print("  📱 DEFENSOR ESTELAR MOBILE - SERVIDOR DE INSTALAÇÃO ANDROID")
    print("=" * 65)
    print(f"\n1. No PC, acesse:      {url_local}")
    print(f"2. No Android (Wi-Fi): {url_rede}")
    print("\n👉 No Chrome do Android, abra o endereço acima e toque em")
    print("   'Adicionar à tela inicial' / 'Instalar aplicativo' para")
    print("   instalá-lo em tela cheia como App nativo offline!")
    print("\nPressione Ctrl+C para encerrar o servidor.")
    print("=" * 65)

    webbrowser.open(url_local)

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")


if __name__ == "__main__":
    iniciar_servidor()

