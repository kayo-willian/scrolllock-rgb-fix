# Como contribuir com o Scroll Lock Keyboard RGB Fix

[English](../CONTRIBUTING.md) · [Documentação em português](README.md)

Contribuições são bem-vindas. Este é um utilitário Linux independente para teclados cujo firmware responde ao LED físico de Scroll Lock. Você pode fazer um fork, melhorar a documentação, relatar resultados em hardware ou enviar uma correção específica. Estas diretrizes se aplicam às contribuições ao projeto original, não aos forks independentes sob a [licença MIT](../LICENSE).

## Escopo

Mantenha as alterações focadas na sincronização do LED de Scroll Lock, descoberta de dispositivos, hotplug, ciclo de vida do serviço, compatibilidade com distribuições e instalação segura. Este não é um driver RGB genérico, remapeador de teclas nem ferramenta de gravação de entradas. Discuta novas dependências, mudanças de privilégios ou mudanças arquiteturais significativas em uma issue antes de implementá-las.

Relatos de hardware são valiosos mesmo sem código. Informe o modelo do teclado, se conhecido, a distribuição Linux, o ambiente gráfico/compositor, o kernel e as versões de systemd, Python e evdev. Separe os resultados observados das suposições sobre outros sistemas.

Consulte a [lista de colaboradores do GitHub](https://github.com/kayo-willian/scrolllock-rgb-fix/graphs/contributors) para os créditos dos commits.

## Primeiros passos

Use uma máquina Linux de desenvolvimento com Git, Bash, Python e evdev. No Debian/Ubuntu, instale a dependência de desenvolvimento com `sudo apt install -y python3-evdev`. Os testes offline são executados como usuário comum e não exigem teclado, root ou systemd em execução.

1. Faça um fork do repositório e clone seu fork.
2. Adicione o remoto upstream e crie uma branch:

   ```sh
   git clone https://github.com/YOUR-USERNAME/scrolllock-rgb-fix.git
   cd scrolllock-rgb-fix
   git remote add upstream https://github.com/kayo-willian/scrolllock-rgb-fix.git
   git fetch upstream
   git switch -c fix/descriptive-name upstream/main
   ```

3. Execute os testes existentes:

   ```sh
   bash tests/test_syntax.sh
   python3 tests/test_daemon.py
   ```

4. Faça a menor alteração coerente. Adicione testes de regressão e execute novamente as verificações. Revise o diff, faça commit, envie as alterações e abra um pull request para a branch `main` do projeto original.

   ```sh
   git diff --check
   git status --short
   git add -- path/to/changed-file
   git commit -m "fix: describe the change"
   git push -u origin fix/descriptive-name
   ```

Substitua o nome de usuário, a branch e o caminho do arquivo dos exemplos.

## Segurança e compatibilidade

- Mantenha a descoberta dinâmica; nunca fixe caminhos numerados de evdev ou sysfs. Verifique se o dispositivo de entrada e o LED pertencem um ao outro e trate ambiguidades de forma conservadora.
- Não grave teclas arbitrárias, sequências de teclas, dados de entrada ou informações pessoais. Nunca adicione telemetria ou acesso à rede ao daemon sem um projeto revisado.
- Trate nomes e caminhos de dispositivos como não confiáveis. Restrinja as escritas ao LED de Scroll Lock pretendido; não modifique dispositivos não relacionados, permissões, autenticação ou outros serviços do sistema.
- Preserve a recuperação, liberação de recursos, tratamento de hotplug e encerramento explícito. Teste erros de dispositivos, nós ausentes, desconexões e cenários com múltiplos dispositivos utilizando mocks e caminhos temporários.
- Revise operações com root no instalador, desinstalador e unidade. Evite alterações de pacotes não relacionadas, sobrescritas inseguras, mudanças amplas de permissões ou falhas silenciosas. Preserve os dados existentes e as alterações do administrador.
- Diferencie uma rotina de gerenciador de pacotes do suporte comprovado a uma distribuição. Não afirme suporte ao OpenRC apenas porque apk é reconhecido.

Testes reais são opcionais. Use um teclado não crítico e um método de entrada alternativo, revise o [guia de diagnóstico](docs/diagnostico.md) e saiba como parar o serviço. Verifique alternâncias de Scroll Lock, interação com Caps/Num Lock, reconexão, parada/reinicialização e logs. Teste múltiplos dispositivos somente com controle explícito do alvo. Registre a revisão exata, o ambiente e o resultado observado. Não deduza resultados em hardware a partir de testes simulados.

## Issues e revisão

Pesquise issues e pull requests existentes antes de abrir outro. Use o modelo de relato de bug ou proposta de funcionalidade; inclua reprodução mínima, comportamento esperado e observado e evidências sanitizadas. Issues e modelos criados pelo projeto são bilíngues. Colaboradores podem escrever em inglês ou português brasileiro sem precisar traduzir seus próprios relatos.

Não publique eventos brutos de teclado, texto digitado, logs privados, números de série, caminhos pessoais ou credenciais. Relate suspeitas de vulnerabilidades por [SEGURANCA.md](SEGURANCA.md).

Mantenha código, comentários, commits e descrições de PR em inglês. Mantenha os documentos comunitários em inglês alinhados às traduções em português brasileiro dentro de `pt-BR/`. Atualize ambas as versões na mesma alteração, com contagens de linhas idênticas, seções, parágrafos, tabelas, comandos, evidências correspondentes e links recíprocos. Use nomes em português para documentos traduzidos, exceto o convencional README.md; mídias compartilhadas e caminhos de código permanecem inalterados. Atualize a seção Unreleased do [HISTORICO.md](HISTORICO.md) para mudanças relevantes. Explique compatibilidade, validação efetivamente realizada e casos não testados. Para alterações exclusivamente documentais, confira links, comandos e precisão.

Declare assistência relevante de IA, verifique as alterações, credite trabalhos externos e envie somente material que tenha direito de contribuir sob MIT. Não invente autoria, resultados de testes ou plataformas suportadas.

PRs são revisados antes do merge. Não há prazo prometido de resposta ou lançamento. Siga o [código de conduta](CODIGO-DE-CONDUTA.md).
