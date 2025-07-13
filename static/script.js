let historico = [];

function converterMarkdown(texto) {
  return texto
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
}

function criarMensagem(tipo, textoHTML) {
  const div = document.createElement('div');
  div.className = `mensagem ${tipo}`;
  
  const icone = document.createElement('img');
  icone.className = `icone-msg ${tipo}-icone`;
  icone.src = tipo === 'usuario'
    ? '/static/imagens/estrela-mensagem.png'
    : '/static/imagens/pipoca.png';

  div.appendChild(icone);

  const texto = document.createElement('div');
  texto.innerHTML = textoHTML;
  div.appendChild(texto);

  return div;
}

async function enviarPergunta() {
  const texto = document.getElementById('user-input').value;
  const imagemInput = document.getElementById('image-input');
  const btn = document.getElementById('btn-enviar');
  const mensagensDiv = document.getElementById('mensagens');

  if (!texto.trim()) return;

  btn.disabled = true;

  const formData = new FormData();
  formData.append('texto', texto);
  formData.append('historico', JSON.stringify(historico));
  if (imagemInput.files[0]) {
    formData.append('imagem', imagemInput.files[0]);
  }

  // Mensagem do usuário
  const msgUsuario = criarMensagem('usuario', texto);
  mensagensDiv.appendChild(msgUsuario);

  // Mensagem temporária do bot
  const msgBot = criarMensagem('bot', 'CineBot está pensando...');
  mensagensDiv.appendChild(msgBot);

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    const respostaHTML = converterMarkdown(data.resposta || "Sem resposta.");
    
    msgBot.lastChild.innerHTML = respostaHTML;
    historico = data.historico;
  } catch {
    msgBot.lastChild.innerHTML = "<em>❌ Erro ao comunicar com o CineBot.</em>";
  } finally {
    btn.disabled = false;
    document.getElementById('user-input').value = "";
    document.getElementById('image-input').value = "";
    mensagensDiv.scrollTop = mensagensDiv.scrollHeight;
  }
}

function limparConversa() {
  historico = [];
  document.getElementById('mensagens').innerHTML = '';
}

document.getElementById('btn-limpar').addEventListener('click', limparConversa);
