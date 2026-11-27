# Histórico de alterações

[English](../CHANGELOG.md) · [Início](README.md)

Este arquivo documenta as alterações relevantes do projeto.

O formato segue o [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e o projeto adota o [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Corrigido
- Associação do teclado ao seu próprio LED de Scroll Lock. Dispositivos sem correspondência ou com correspondência ambígua são ignorados.

### Adicionado
- Código de conduta, política de comunicação de vulnerabilidades, modelos bilíngues de issues e modelo de pull request em inglês.
- Traduções brasileiras do guia de diagnóstico, do registro técnico histórico e deste histórico de alterações.

### Alterado
- Alinhamento de todos os pares Markdown em inglês e português brasileiro, tradução dos nomes de arquivos, inclusão de referências de arquitetura e compatibilidade de hardware e preservação do PDF e das mídias originais. Alteração apenas documental.
- Atualização das orientações para colaboradores, dos READMEs em inglês e português e das instruções de diagnóstico.
- Esclarecimentos sobre o requisito real de systemd, a seleção independente anterior de dispositivo e LED e sua correção posterior de associação, a execução como root, a instalação e remoção e os limites da validação física. O comportamento do daemon, do instalador e do serviço foi preservado.

As versões abaixo são entradas históricas. Esta atualização documental preserva os números das versões e não cria um lançamento. As afirmações antigas descrevem as mudanças históricas, não suporte verificado independentemente nem garantias de remoção completa.

---

## [2.0.0] - 2026-10-04

### Adicionado
- **Instalador automático para várias distribuições (`install.sh`)**
  - Identifica automaticamente o gerenciador de pacotes (`apt`, `dnf`, `pacman`, `zypper`, `apk`).
  - Instala automaticamente `python3-evdev` se estiver ausente.
  - Acrescenta validação do systemd com suporte registrado para Ubuntu, Debian, Fedora, Arch e openSUSE.
  - Instala executáveis no caminho padrão `/usr/local/bin` e unidades systemd em `/etc/systemd/system`.
- **Desinstalador automático (`uninstall.sh`)**
  - Para e desabilita o serviço e remove a unidade e o daemon.
- **Conexão e reconexão USB no próprio processo**
  - O daemon Python passa a tratar desconexões (`OSError`, remoção do cabo, troca de porta) no processo, evitando falhas e ciclos de reinício pelo systemd.
- **Tratamento de sinais aprimorado**
  - Encerramento com liberação de recursos ao receber `SIGTERM` e `SIGINT`.
- **Suíte de testes automatizados (`tests/`)**
  - Inclusão de `tests/test_syntax.sh` para verificar a sintaxe do shell e do Python.
  - Inclusão de `tests/test_daemon.py`, com testes unitários que simulam descoberta, controle de LED e despacho de eventos de entrada.
- **Documentação**
  - Inclusão do guia específico `docs/troubleshooting.md`.
  - Inclusão de `CONTRIBUTING.md` e `CHANGELOG.md`.
  - Inclusão do README bilíngue (inglês e português brasileiro).
  - Preservação do documento técnico histórico `docs/RGB_ScrollLock_Ubuntu_EN.pdf`.

### Alterado
- Padronização dos logs, com horários capturados pelo `journald`.
- Remoção da dependência obsoleta de `systemd-udev-settle.service`, com detecção assíncrona nativa de dispositivos.

---

## [1.0.0] - 2026-07-17

### Adicionado
- Primeiro protótipo funcional para Ubuntu 26.04 LTS (GNOME / Wayland).
- Detecção dinâmica de dispositivos (`/sys/class/leds/*scrolllock*/brightness` e `/dev/input/event*`).
- Identificação do teclado pelas capacidades `KEY_SCROLLLOCK` e `KEY_A`.
- Mitigação do conflito de Caps Lock e Num Lock no GNOME Wayland pela interceptação de eventos `EV_LED`.
- Unidade básica de serviço do `systemd`.
- Diário técnico detalhado de desenvolvimento em PDF.
