# Compatibilidade de hardware

[Índice da documentação](README.md) · [Início](../README.md) · [English](../../docs/hardware-compatibility.md)

Esta é uma referência de compatibilidade baseada em evidências, não uma lista de dispositivos certificados ou sistemas operacionais suportados.

## Evidências de hardware e ambiente

| Item | Estado registrado |
| --- | --- |
| Teclado gamer USB genérico com fio | Dispositivo original de desenvolvimento; modelo exato não registrado aqui |
| Ubuntu 26.04 / GNOME / Wayland | Ambiente original do protótipo histórico |
| Acionamento do firmware via Scroll Lock | Escritas diretas no LED acionaram a iluminação RGB no dispositivo original |
| Outros teclados RGB | Não verificados; podem usar outro protocolo de iluminação |
| Daemon atual em vários dispositivos físicos | Validação mais abrangente ainda pendente |
| Outros ambientes gráficos e distribuições | Não verificados independentemente aqui |

Consulte o [registro histórico](registro-tecnico.md) e o [PDF original](../../docs/RGB_ScrollLock_Ubuntu_EN.pdf) para a investigação do protótipo. As [fotografias originais](../../docs/images/) documentam a aparência física, não resultados de testes da revisão atual.

## Rotinas de instalação

O instalador reconhece os seguintes gerenciadores de pacotes quando o Python não consegue importar evdev. O serviço atual exige um gerenciador systemd funcional, independentemente do gerenciador de pacotes.

| Gerenciador de pacotes | Exemplo de família | Pacote |
| --- | --- | --- |
| apt | Debian / Ubuntu / Linux Mint | python3-evdev |
| dnf | Fedora / RHEL | python3-evdev |
| pacman | Arch / Manjaro | python-evdev |
| zypper | openSUSE | python3-evdev |
| apk | Sistemas com apk | py3-evdev |

A disponibilidade dos pacotes e o comportamento em execução variam. A rotina apk não estabelece compatibilidade com Alpine/OpenRC. O instalador verifica o diretório de execução do systemd ou o comando systemctl, mas essa verificação inicial sozinha não prova que o gerenciador funciona.

## Validação controlada em hardware

Antes de testar, use um dispositivo não crítico, mantenha outro método de entrada e revise o [guia de diagnóstico](diagnostico.md). Registre o commit exato e o ambiente. Não teste nós de LED não identificados nem capture texto digitado.

| Verificação | Evidência a registrar |
| --- | --- |
| Acionamento pelo firmware | Se o LED identificado altera o estado RGB |
| Associação de dispositivos | Se o dispositivo evdev e o LED apontam para o mesmo proprietário de entrada |
| Pressionamento da tecla | Resposta da iluminação ao Scroll Lock |
| Caps Lock / Num Lock | Qualquer redefinição, oscilação ou alteração inesperada |
| Reconexão USB | Se o dispositivo correto é redescoberto e o estado inicial é apagado |
| Parada / reinício | Estado real do serviço, logs e comportamento observado |
| Múltiplos teclados | Se apenas o par elegível pretendido é selecionado |

São verificações sugeridas, não resultados de novos experimentos. Os testes offline não as substituem.

Relate resultados sanitizados pelo [rastreador de issues](https://github.com/kayo-willian/scrolllock-rgb-fix/issues) ou utilize a [política de segurança](../SEGURANCA.md) para resultados sensíveis.

[Arquitetura](arquitetura.md) · [Diagnóstico](diagnostico.md)
