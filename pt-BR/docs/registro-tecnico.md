# Correção de RGB com Scroll Lock

[English](../../docs/technical-record.md) · [PDF original](../../docs/RGB_ScrollLock_Ubuntu_EN.pdf) · [Início](../README.md) · [Índice](README.md)

**Ubuntu 26.04 com GNOME (Wayland) — teclado gamer USB genérico**

Este registro histórico descreve como o autor recuperou a iluminação RGB do seu teclado no Ubuntu 26.04. Ele guardou os passos para entender ou reaplicar a solução após uma atualização de sistema ou troca de teclado. Os caminhos e exemplos de código pertencem ao protótipo de julho de 2026. Para a versão do repositório, consulte a [instalação](../README.md#instalação) e o [diagnóstico](diagnostico.md).

Este texto preserva o relato do protótipo e não descreve necessariamente o daemon atual. Os exemplos históricos não são instruções de instalação; use o guia atual e não execute comandos com caminhos de dispositivos antigos.

## O problema

No teclado gamer genérico semimecânico do kit, o firmware aciona a iluminação RGB quando o computador liga o LED padrão de Scroll Lock, um recurso encontrado em teclados de baixo custo. Segundo o registro, isso costumava funcionar no Windows e no terminal de texto do Linux (TTY), onde o kernel aciona diretamente o LED. No Ubuntu 26.04, o GNOME usava Wayland por padrão após o encerramento do suporte a Xorg no GNOME 49. Nessa sessão, o indicador físico não acompanhava automaticamente o estado de Scroll Lock. Pressionar a tecla não produzia efeito.

## A solução

O autor usou um pequeno programa em Python que permanecia em segundo plano, lendo o teclado diretamente. A cada acionamento de Scroll Lock, o programa escrevia no arquivo do sistema que controla o LED para ligar ou desligar a iluminação. Uma unidade systemd iniciava o programa automaticamente a cada boot. Os arquivos criados foram o script `/usr/local/bin/scrolllock-rgb.py` e a unidade `/etc/systemd/system/scrolllock-rgb.service`.

## 1. O script Python — scrolllock-rgb.py

O programa que mantinha o RGB funcionando está reproduzido abaixo por partes, na ordem do documento original.

### 1.1. Importações

```python
#!/usr/bin/env python3
import evdev
from evdev import ecodes
import glob
import time
```

A primeira linha seleciona o Python 3. A biblioteca evdev, instalada com `sudo apt install python3-evdev`, permite ler eventos de teclado e mouse. O módulo ecodes fornece os códigos padronizados de cada tecla, inclusive Scroll Lock. O glob procura arquivos por padrão de nome para localizar o LED automaticamente. O módulo time permite pequenas pausas na execução.

### 1.2. Localização do LED de Scroll Lock

```python
def find_led_path():
    matches = glob.glob("/sys/class/leds/*scrolllock*")
    if matches:
        return matches[0] + "/brightness"
    return None
```

O Linux expõe o LED em `/sys/class/leds/`. O número em nomes como `input2::scrolllock` ou `input24::scrolllock` depende da ordem de detecção dos dispositivos USB e pode mudar após reiniciar. Fixar esse número no código fez o script parar de funcionar depois de um boot. O protótipo passou a procurar uma pasta contendo “scrolllock” na inicialização e usava a primeira correspondência.

### 1.3. Localização do teclado

```python
def find_keyboard():
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        caps = dev.capabilities().get(ecodes.EV_KEY, [])
        if ecodes.KEY_SCROLLLOCK in caps and ecodes.KEY_A in caps:
            return dev
    return None
```

Um computador pode expor teclado, mouse e botões de mídia como dispositivos de entrada separados. A função percorria os dispositivos conectados e aceitava um que pudesse enviar tanto Scroll Lock quanto a tecla A. Assim distinguia o teclado principal das interfaces secundárias “Consumer Control” e “System Control” que podiam aparecer separadamente no mesmo teclado USB.

### 1.4. Preparação para ouvir eventos

```python
LED_PATH = find_led_path()
device = find_keyboard()

if LED_PATH is None or device is None:
    raise SystemExit("Keyboard or LED not found yet")

state = 0
```

As duas funções localizavam o LED e o teclado. Se algum ainda estivesse ausente, como durante a detecção do teclado no boot, o programa encerrava com a mensagem de erro. O systemd tentava iniciá-lo novamente conforme a seção 2. A variável `state` guardava o estado desejado, 1 para ligado ou 0 para desligado.

### 1.5. Acionamento do LED

```python
def set_led(value):
    with open(LED_PATH, "w") as f:
        f.write(str(value))
```

A função abria o arquivo do LED e escrevia 0 ou 1. O efeito era o mesmo da escrita manual usada no teste inicial com `echo 1 | sudo tee /sys/class/leds/.../brightness`.

### 1.6. Laço principal

```python
for event in device.read_loop():
    if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_SCROLLLOCK and event.value == 1:
        state = 1 - state
        set_led(state)
    elif event.type == ecodes.EV_LED:
        time.sleep(0.05)
        set_led(state)
```

O laço aguardava eventos continuamente.

- Ao pressionar Scroll Lock, `event.value == 1` identificava o pressionamento e excluía a soltura. O programa alternava de 0 para 1 ou de 1 para 0 e enviava o novo estado ao LED.
- Quando o GNOME alterava um indicador, como Caps Lock ou Num Lock, o teclado recebia um pacote com o estado dos três LEDs juntos. Isso podia apagar Scroll Lock. Ao receber EV_LED, o script esperava 0,05 segundo pela escrita do GNOME e reaplicava o estado guardado.

## 2. A unidade systemd — scrolllock-rgb.service

O systemd gerencia o início automático de programas no Ubuntu, inclusive no boot. O autor criou uma unidade para executar o script a cada inicialização sem abrir um terminal.

```ini
[Unit]
Description=Syncs the Scroll Lock LED with the keyboard's RGB
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/scrolllock-rgb.py
Restart=always
RestartSec=2
User=root

[Install]
WantedBy=multi-user.target
```

| Seção ou chave | Explicação |
|---|---|
| `[Unit]` | Informações gerais da unidade. |
| `Description=...` | Nome apresentado ao consultar o estado do serviço. |
| `After=multi-user.target` | Ordena o início depois que o alvo multiusuário estiver ativo, evitando uma tentativa antecipada. |
| `[Service]` | Configura a execução do programa. |
| `ExecStart=...` | Indica o comando exato que chama o Python 3 com o script. |
| `Restart=always` | O systemd tenta reiniciar o programa após saída ou erro. |
| `RestartSec=2` | Espera dois segundos antes da próxima tentativa. Quando o teclado ainda não havia sido reconhecido no boot, o script podia falhar e voltar a tentar até funcionar. |
| `User=root` | Executa como administrador, com permissão para escrever no arquivo do LED. |
| `[Install]` | Define como o serviço se integra à inicialização. |
| `WantedBy=multi-user.target` | Ao habilitar a unidade, associa seu início ao alvo multiusuário a cada boot. |

## 3. Comandos usados no terminal

A sequência a seguir reproduz as investigações e alterações do autor na máquina original. O nome `input24::scrolllock` correspondia ao seu teclado naquele momento. Os dois exemplos de `tee` com `...` abreviam o conteúdo dos arquivos no PDF.

| Ordem | Comando registrado | Uso e observação |
|---|---|---|
| 1 | `echo $XDG_SESSION_TYPE` | Mostrou se a sessão gráfica usava Wayland ou Xorg (X11). O resultado identificou Wayland, relevante para a falta de sincronização do LED. |
| 2 | `lsusb` | Listou os dispositivos USB conectados, incluindo o teclado, com informações de fabricante. |
| 3 | `ls /usr/share/xsessions/` | Procurou sessões Xorg instaladas. O autor encontrou um erro de diretório inexistente e registrou a retirada de Xorg no GNOME do Ubuntu 25.10/26.04. |
| 4 | `sudo apt update` | Atualizou a lista de pacotes disponíveis antes das instalações. |
| 5 | `sudo apt install xserver-xorg gnome-session` | Tentativa de instalar Xorg e a sessão GNOME. O autor abandonou esse caminho porque o GNOME 49 já não oferecia sessão Xorg. |
| 6 | `dpkg -L gnome-session \| grep xsessions` | Filtrou os arquivos do pacote relacionados a sessões gráficas. Confirmou que o pacote não incluía uma sessão Xorg, apenas Wayland. |
| 7 | `ls /sys/class/leds/ \| grep -i scroll` | Procurou o termo “scroll” entre os LEDs e localizou o arquivo que controlava o indicador e o RGB naquele teclado. |
| 8 | `echo 1 \| sudo tee /sys/class/leds/input24::scrolllock/brightness` | Escreveu 1 no nó identificado. O RGB acendeu, confirmando nessa máquina o acionamento por escrita direta, independentemente do GNOME. |
| 9 | `cat /proc/bus/input/devices \| grep -A 5 -i keyboard` | Examinou nomes, identificadores e arquivos de evento dos dispositivos reconhecidos para localizar o teclado principal. |
| 10 | `sudo apt install python3-evdev` | Instalou a biblioteca usada pelo script para ler eventos diretamente do sistema. |
| 11 | `sudo mkdir -p /usr/local/bin && sudo tee /usr/local/bin/scrolllock-rgb.py > /dev/null << 'EOF' ... EOF` | Criou o diretório, se necessário, e gravou o programa Python usando o conteúdo entre os marcadores EOF, sem editor interativo. |
| 12 | `sudo chmod +x /usr/local/bin/scrolllock-rgb.py` | Deu permissão de execução para chamar o arquivo como programa. |
| 13 | `sudo python3 /usr/local/bin/scrolllock-rgb.py` | Testou o script no terminal antes de automatizá-lo. Ele aguardava eventos até o encerramento com Ctrl+C. |
| 14 | `sudo tee /etc/systemd/system/scrolllock-rgb.service > /dev/null << 'EOF' ... EOF` | Gravou a unidade systemd que configurava a execução, inclusive nos boots seguintes. |
| 15 | `sudo systemctl daemon-reload` | Pediu ao systemd para reler as definições novas ou alteradas. |
| 16 | `sudo systemctl enable scrolllock-rgb.service` | Habilitou o serviço para iniciar automaticamente no boot. |
| 17 | `sudo systemctl start scrolllock-rgb.service` | Iniciou o serviço imediatamente, sem reinicializar a máquina. |
| 18 | `sudo systemctl restart scrolllock-rgb.service` | Reiniciou o serviço para que uma alteração do script entrasse em uso. |
| 19 | `systemctl status scrolllock-rgb.service --no-pager` | Exibiu o estado, tempo de execução e últimas linhas do log sem abrir um paginador. |
| 20 | `systemctl is-enabled scrolllock-rgb.service` | Conferiu o início automático. A resposta esperada era “enabled”. |
| 21 | `journalctl -u scrolllock-rgb.service --no-pager` | Consultou o histórico completo de mensagens desse serviço para diagnóstico. |
| 22 | `sudo reboot` | Reiniciou o computador para verificar no ambiente original o início automático sem ação manual. |

O documento original orienta guardar o registro e, se Scroll Lock voltar a falhar, começar pelos comandos de estado e de logs da seção 3, `systemctl status` e `journalctl`.
