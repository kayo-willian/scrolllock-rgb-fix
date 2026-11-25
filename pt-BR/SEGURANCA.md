# Política de segurança

[English](../SECURITY.md) · [Documentação em português](README.md)

> Tradução para português brasileiro. Em caso de divergência, consulte a versão original em inglês.

## Escopo

Scroll Lock RGB Fix executa um serviço systemd privilegiado que lê eventos de entrada por evdev e escreve no sysfs. A branch atual de desenvolvimento é `main`. Não há período de suporte, SLA de resposta ou programa de recompensas prometidos.

Problemas relevantes incluem gravação ou divulgação não intencional de entradas, operações privilegiadas inseguras com arquivos, escritas em dispositivos não relacionados, problemas de privilégios no serviço ou instalador e efeitos não intencionais no estado do sistema.

## Relatos

Use a [página de avisos de segurança](https://github.com/kayo-willian/scrolllock-rgb-fix/security/advisories) e **Report a vulnerability** se o relato privado estiver disponível. Caso contrário, abra uma issue pública solicitando um meio de contato privado, sem detalhes de exploração, evidências sensíveis ou identificadores privados. Não presuma que o relato privado esteja habilitado.

Inclua o commit afetado, distribuição, versões relevantes do runtime, limite de segurança esperado, comportamento observado, impacto e reprodução mínima segura. Use mocks e recursos descartáveis quando possível. Diferencie problemas reproduzidos de hipóteses. Não teste sistemas sem autorização nem colete teclas digitadas reais.

Nunca publique texto digitado, fluxos brutos de eventos de entrada, logs privados, credenciais ou informações que identifiquem dispositivos. Dê ao mantenedor uma oportunidade razoável de investigar antes de publicar detalhes exploráveis.

Bugs comuns não sensíveis devem ser relatados em Issues. Consulte [CONTRIBUICAO.md](CONTRIBUICAO.md) e o [guia de diagnóstico](../docs/troubleshooting.md). Caso uma instalação local apresente comportamento inesperado, pare o serviço e inspecione-o em vez de enfraquecer as permissões do sistema.
