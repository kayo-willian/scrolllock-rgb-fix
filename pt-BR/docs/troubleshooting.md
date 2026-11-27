# Guia de diagnóstico

[English](../../docs/troubleshooting.md) · [Início](../README.md)

Use um teclado não crítico e tenha outro método de entrada disponível. O serviço fornecido executa como root. Evite capturar ou compartilhar eventos arbitrários de teclado.

## 1. Verificar o estado e os logs

```sh
systemctl status scrolllock-rgb.service --no-pager
journalctl -u scrolllock-rgb.service -n 50 --no-pager
```

Mesmo ativo, o serviço pode estar aguardando um dispositivo. Procure o nome e o caminho do teclado monitorado, o nó do LED escolhido, as mensagens de alternância de Scroll Lock e eventuais erros. Confira se o teclado e o LED indicados correspondem ao dispositivo pretendido.

## 2. Verificar a resposta do firmware

Pare o serviço antes de alterar manualmente o estado do LED.

```sh
sudo systemctl stop scrolllock-rgb.service
ls -l /sys/class/leds/*scrolllock*/brightness
```

Identifique **um único** nó de brilho pertencente ao teclado de teste. Usar um curinga com tee poderia escrever em vários dispositivos. O caminho abaixo é fictício. Substitua-o somente após verificar o dispositivo correto pelo vínculo no sysfs. Em caso de dúvida sobre a identificação, interrompa o teste.

```sh
LED=/sys/class/leds/input3::scrolllock/brightness
cat "$LED"
```

Anote o valor original. Com o nó correto e permissão de escrita, teste os dois estados.

```sh
printf '1\n' | sudo tee "$LED"
printf '0\n' | sudo tee "$LED"
```

Restaure o valor anotado se necessário. Uma alteração no RGB demonstra o acionamento pelo firmware nesse dispositivo. A compatibilidade completa com o daemon exige verificações adicionais. A ausência de alteração pode indicar outro protocolo de firmware ou um nó incorreto. Quando apropriado, retome a operação com `sudo systemctl start scrolllock-rgb.service`.

## 3. Teclado ausente ou seleção do teclado errado

```sh
grep -E 'Name|Handlers' /proc/bus/input/devices
ls -l /sys/class/leds/*scrolllock*
```

Se o daemon ignorar um teclado, compare os vínculos de dispositivo das entradas de eventos e de LED no sysfs. Ambos devem apontar para o mesmo dispositivo de entrada, que deve ter exatamente um LED de Scroll Lock. Compartilhar a porta USB ou o dispositivo HID composto pai é insuficiente. Evite contornar isso fixando o número do evento no código ou escrevendo em um LED sem identificação. Ao relatar o problema, descreva a organização dos dispositivos, os nomes e caminhos sanitizados e o comportamento observado.

## 4. Interação com Caps Lock e Num Lock

O daemon reaplica o estado desejado de Scroll Lock após um evento EV_LED, com uma espera de 50 ms para estabilização. O comportamento varia conforme o hardware e o compositor. Pode haver uma breve oscilação. Relate alterações inesperadas ou estados que se desfaçam persistentemente, incluindo o ambiente e os passos para reproduzir.

## 5. Reconexão USB e encerramento

Quando o laço de leitura encontra um erro de conexão, o daemon fecha o dispositivo selecionado e repete a descoberta a cada dois segundos. Também há novas tentativas quando falta o teclado ou o LED. Cada novo processo de escuta inicializa o LED como apagado. A lógica de reconexão e encerramento não garante uma resposta imediata em todas as situações.

Use `sudo systemctl stop scrolllock-rgb.service` para parar ou `sudo systemctl disable --now scrolllock-rgb.service` para parar e desabilitar a inicialização automática. Confira o estado da unidade. Se a parada falhar, investigue o systemd e os logs do daemon antes da remoção.

## 6. Problemas de instalação ou remoção

É necessário um gerenciador systemd funcional. Detectar o gerenciador de pacotes é insuficiente para comprovar suporte integral à distribuição. Verifique a disponibilidade de Python e evdev, os arquivos de destino existentes, os erros de pacotes e o diagnóstico do systemd. O instalador pode substituir o daemon e a unidade em caminhos fixos. O desinstalador ignora erros ao parar ou desabilitar a unidade. Preserve arquivos de outros serviços e evite forçar alterações nos pacotes para contornar uma falha.

Consulte o [README](../README.md) para instalação, atualização e remoção. Use os modelos do repositório para problemas comuns e a [política de segurança](../SEGURANCA.md) para informações sensíveis. Antes de compartilhar evidências, remova logs privados, texto digitado, eventos brutos e dados identificadores.
