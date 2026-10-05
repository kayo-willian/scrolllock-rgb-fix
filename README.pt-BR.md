# Correção de RGB do Teclado via Scroll Lock

[![Linux](https://img.shields.io/badge/Linux-Suportado-brightgreen?logo=linux&logoColor=white)](https://kernel.org)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![systemd](https://img.shields.io/badge/systemd-integrado-orange?logo=linux)](https://systemd.io)
[![Wayland](https://img.shields.io/badge/Wayland-GNOME%2049%2B-informational)](https://wayland.freedesktop.org)
[![Licença: MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](LICENSE)

*Disponível em outros idiomas:* [English](README.md)

---

Um serviço leve e automatizado para Linux que restaura o funcionamento da iluminação RGB em teclados gamer genéricos que utilizam o LED de **Scroll Lock** como gatilho de firmware, especialmente em sistemas **GNOME no Wayland**.

Desenvolvido para distribuições Linux modernas (como Ubuntu 26.04+ onde o GNOME removeu o suporte a sessões Xorg), nas quais o compositor gráfico não sincroniza o estado do LED de Scroll Lock com o hardware físico do teclado.

---

## 💡 O Problema

Muitos teclados gamer de baixo custo (frequentemente vendidos como "semi-mecânicos RGB") não acompanham drivers proprietários para Linux. Em vez disso, o firmware interno do teclado acende o RGB sempre que o sistema operacional ativa o LED padrão de **Scroll Lock**.

Esse comportamento funciona perfeitamente no Windows e no modo texto puro do Linux (TTY):

* No **GNOME com Wayland**, o compositor gráfico intercepta a tecla, mas não repassa a atualização de estado do LED para o teclado USB físico.
* A partir do GNOME 49 (Ubuntu 25.10+ / 26.04 LTS), as sessões Xorg foram totalmente removidas, tornando impossível contornar o problema mudando de servidor gráfico.
* Ao pressionar a tecla Scroll Lock, nada acontece e o teclado permanece apagado.

---

## ⚡ A Solução

Este projeto fornece um daemon nativo em Python e um serviço `systemd` que interage diretamente com o subsistema de entrada do kernel Linux:

```text
[ Teclado Físico ]
        │
        │  Pressiona tecla Scroll Lock
        ▼
[ /dev/input/eventX ]
        │
        │  Loop de eventos nativo do kernel (python3-evdev)
        ▼
[ scrolllock-rgb.py ] ──► Inverte o estado interno (0 <-> 1)
        │
        │  Escrita direta no sysfs
        ▼
[ /sys/class/leds/*scrolllock*/brightness ]
        │
        │  Gatilho de hardware
        ▼
[ Firmware do Teclado ] ──► Iluminação RGB LIGA / DESLIGA ✨
```

### Principais Recursos (v2.0)
- **Detecção Dinâmica:** Encontra o teclado e o nó do LED no sysfs (`/sys/class/leds/`) automaticamente, sem caminhos fixos (funciona mesmo se a numeração dos dispositivos mudar no boot).
- **Filtro Inteligente de Dispositivos:** Identifica o teclado real testando suporte às teclas `Scroll Lock` e `A`, descartando nós secundários (como "Consumer Control" e "System Control").
- **Recuperação de Hotplug (Reconexão USB):** Trata a desconexão ou troca de porta USB em tempo de execução sem travar o daemon ou sobrecarregar o systemd.
- **Recuperação de Conflito com Caps Lock / Num Lock:** O GNOME atualiza todos os LEDs ao apertar Caps ou Num Lock, o que acidentalmente desligava o Scroll Lock. O daemon detecta essa atualização do compositor e restaura o estado correto do RGB imediatamente.
- **Instalador Multi-Distribuição:** Instalação em um único comando com suporte automático para Ubuntu, Debian, Fedora, Arch Linux, openSUSE e Alpine.

---

## 📦 Compatibilidade e Requisitos

* **Sistema Operacional:** Qualquer distribuição Linux com `systemd`
* **Ambiente Gráfico:** GNOME (Wayland ou X11), KDE Plasma, Hyprland, Sway, etc.
* **Dependências:** Python 3 e `python3-evdev` (instaladas automaticamente pelo script de instalação)
* **Hardware:** Teclados cujo RGB dependa do LED de Scroll Lock

| Distribuição | Gerenciador | Suporte |
| :--- | :--- | :--- |
| **Ubuntu / Debian / Linux Mint** | `apt` | ✅ Suportado |
| **Fedora / RHEL** | `dnf` | ✅ Suportado |
| **Arch Linux / Manjaro** | `pacman` | ✅ Suportado |
| **openSUSE (Tumbleweed / Leap)** | `zypper` | ✅ Suportado |
| **Alpine Linux** | `apk` | ✅ Suportado |

---

## 🚀 Instalação Rápida Automatizada

Clone o repositório e execute o instalador:

```bash
# 1. Clone o repositório
git clone https://github.com/kayo-willian/scrolllock-rgb-fix.git
cd scrolllock-rgb-fix

# 2. Execute o instalador (requer sudo)
sudo ./install.sh
```

O instalador irá:
1. Detectar o gerenciador de pacotes e instalar `python3-evdev` caso necessário;
2. Copiar o script para `/usr/local/bin/scrolllock-rgb.py`;
3. Configurar a unidade no systemd (`scrolllock-rgb.service`);
4. Iniciar o serviço imediatamente e habilitá-lo para iniciar junto ao boot do sistema.

Pressione a tecla **Scroll Lock** para acender ou apagar o LED RGB do seu teclado!

---

## 🔍 Verificação e Logs

Verifique se o serviço está ativo e rodando:

```bash
systemctl status scrolllock-rgb.service --no-pager
```

Acompanhe os logs em tempo real:

```bash
journalctl -u scrolllock-rgb.service -f
```

---

## 🛠️ Desinstalação

Para remover completamente o serviço e os arquivos instalados:

```bash
sudo ./uninstall.sh
```

---

## 🧪 Testes e Desenvolvimento

Execute a suíte de testes automatizados:

```bash
# Testes estáticos de sintaxe e presença de arquivos
./tests/test_syntax.sh

# Testes unitários com mocks de hardware
python3 ./tests/test_daemon.py
```

Para guia passo a passo de diagnóstico de hardware, consulte [docs/troubleshooting.md](docs/troubleshooting.md).

Para entender a linha de raciocínio e os comandos de terminal utilizados para criar esta solução, veja o guia técnico em PDF [docs/RGB_ScrollLock_Ubuntu_EN.pdf](docs/RGB_ScrollLock_Ubuntu_EN.pdf).

---

## 📄 Licença

Este projeto é um software de código aberto licenciado sob a [Licença MIT](LICENSE).
