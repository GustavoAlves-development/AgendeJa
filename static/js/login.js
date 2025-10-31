// Controle de telas
const loginPage = document.getElementById("page-login");
const cadastroPage = document.getElementById("page-cadastro");

// Links de navegação - com verificação de existência
document.getElementById("link-cadastrar")?.addEventListener("click", () => {
    loginPage?.classList.add("hidden");
    cadastroPage?.classList.remove("hidden");
});

document.getElementById("link-voltar-login")?.addEventListener("click", () => {
    cadastroPage?.classList.add("hidden");
    loginPage?.classList.remove("hidden");
});

// Verificar se os elementos de radio button existem antes de adicionar event listeners
const clienteRadio = document.getElementById("cliente");
const profissionalRadio = document.getElementById("profissional");

if (clienteRadio && profissionalRadio) {
    clienteRadio.addEventListener("change", verificarStatus);
    profissionalRadio.addEventListener("change", verificarStatus);
}

function verificarStatus() {
    let cliente = document.getElementById("cliente");
    let profissional = document.getElementById("profissional");

    // Verifica se os elementos existem
    if (!cliente || !profissional) return;

    // Verifica se o botão de profissional está selecionado
    if (profissional.checked) {
        // Obtém a primeira div com a classe 'escondidoProfissonais'
        let sections = document.getElementsByClassName("escondidoProfissonais");
        if (sections.length > 0) {
            sections[0].classList.remove("hidden");
            // INICIALIZAR O EVENT LISTENER AQUI - quando a seção for mostrada
            inicializarTipoProfissional();
        }
    } else {
        // Caso o cliente seja selecionado, esconde novamente
        let sections = document.getElementsByClassName("escondidoProfissonais");
        if (sections.length > 0) {
            sections[0].classList.add("hidden");
        }
    }
}

// Variável para armazenar a função de evento (para poder remover depois)
let currentTipoChangeHandler = null;

// Função para inicializar o controle do tipo de profissional
function inicializarTipoProfissional() {
    const tipoUsuario = document.getElementById("tipo-profissional");
    const inputTipo = document.getElementById("tipo-outro-input");

    // Só inicializar se os elementos existirem
    if (tipoUsuario && inputTipo) {
        // Remover event listener anterior se existir
        if (currentTipoChangeHandler) {
            tipoUsuario.removeEventListener("change", currentTipoChangeHandler);
        }

        // Criar nova função handler
        currentTipoChangeHandler = function() {
            if (this.value === "Outro") {
                inputTipo.classList.remove("hidden");
            } else {
                inputTipo.classList.add("hidden");
            }
        };

        // Adicionar novo event listener
        tipoUsuario.addEventListener("change", currentTipoChangeHandler);

        // Verificar estado inicial
        currentTipoChangeHandler.call(tipoUsuario);
    }
}

// Código do modal - com verificação de existência
const modal = document.getElementById("modal-agendamento");
document.getElementById("btn-novo-agendamento")?.addEventListener("click", () => {
    modal?.classList.remove("hidden");
});

document.getElementById("btn-cancelar")?.addEventListener("click", () => {
    modal?.classList.add("hidden");
});

document.getElementById("form-agendamento")?.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Agendamento salvo!");
    modal?.classList.add("hidden");
    // Aqui você pode atualizar a lista de agendamentos
});

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Verificar status inicial (caso a página carregue com algum selecionado)
    verificarStatus();

    // Inicializar tipo profissional se já estiver visível
    const profissionalRadio = document.getElementById("profissional");
    if (profissionalRadio && profissionalRadio.checked) {
        inicializarTipoProfissional();
    }
});